"""Route CSV -> KMZ (PZ/CP/LZ markers, label+table, dashed legs, leg arrow boxes).
Usage: python make_route_kmz.py route.csv out.kmz --kt 90 --var 0
CSV cols: type,name,lat,lon,alt_ft   (alt_ft = altitude for leg starting at this point)
"""
import csv, math, sys, os, zipfile, argparse, io
from PIL import Image, ImageDraw, ImageFont

COL = {"PZ": "#FF66CC", "LZ": "#FFD700", "CP": "#22BB33"}
FONT_TRY = ["C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/LeelawUI.ttf",
            "/usr/share/fonts/opentype/tlwg/Loma.otf"]

def font(sz):
    for f in FONT_TRY:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def leg(a, b):  # great-circle NM + true course
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    d = 2*math.asin(math.sqrt(math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2))
    y = math.sin(lo2-lo1)*math.cos(la2)
    x = math.cos(la1)*math.sin(la2) - math.sin(la1)*math.cos(la2)*math.cos(lo2-lo1)
    return d*3440.065, (math.degrees(math.atan2(y, x)) + 360) % 360

def mmss(m):  # minutes -> H:MM
    if m is None: return "-"
    m = round(m); return f"{m//60}:{m%60:02d}"

def color_of(t):
    for k, v in COL.items():
        if t.upper().startswith(k): return v
    return "#22BB33"

def label_png(title, color, rows):
    f, fs = font(26), font(20)
    W, rh = 330, 34
    tw = max(W, int(f.getlength(title)) + 40)
    im = Image.new("RGBA", (tw, 56 + rh*4 + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, tw-1, 50], fill=color, outline="black", width=2)
    d.text((tw//2, 25), title, font=f, fill="black", anchor="mm")
    x0 = (tw - W)//2; y0 = 56; cw = [130, 100, 100]
    for r, row in enumerate([["", "NM", "MIN"]] + rows):
        x = x0
        for c, txt in enumerate(row):
            d.rectangle([x, y0+r*rh, x+cw[c], y0+(r+1)*rh], fill="white", outline="black")
            d.text((x+cw[c]//2, y0+r*rh+rh//2), str(txt), font=fs, fill="black", anchor="mm")
            x += cw[c]
    return im

def arrow_png(crs, nm, mins, alt):
    """Arrow box like sample: 4 cells, tip points along course (screen-up = north)."""
    fs = font(22)
    cells = [f"{round(crs):03d}", f"{round(nm)} NM", mmss(mins), f"{alt}'" if alt else "-"]
    L, H, tip = 4*58, 84, 38
    im = Image.new("RGBA", (L + tip + 4, H + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    poly = [(tip, 2), (tip+L, 2), (tip+L, H+2), (tip, H+2), (2, H//2+2)]
    d.polygon(poly, fill="white", outline="#1F4E79", width=4)
    for i in range(1, 4):
        x = tip + i*58; d.line([(x, 2), (x, H+2)], fill="#1F4E79", width=3)
    for i, t in enumerate(cells):  # vertical text in each cell
        tl = Image.new("RGBA", (H, 44), (0, 0, 0, 0))
        ImageDraw.Draw(tl).text((H//2, 22), t, font=fs, fill="black", anchor="mm")
        tl = tl.rotate(90, expand=True)
        cx = tip + i*58 + 24 - (i == 0)*0
        im.alpha_composite(tl, (cx - tl.width//2, 2 + (H - tl.height)//2))
    # image tip points LEFT (= 270 deg). rotate so tip points along course
    big = Image.new("RGBA", (int(im.width*1.5), int(im.width*1.5)), (0, 0, 0, 0))
    big.alpha_composite(im, ((big.width-im.width)//2, (big.height-im.height)//2))
    return big.rotate(-(crs - 270), expand=False, resample=Image.BICUBIC)

def marker_png(t, color):
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if t.upper().startswith("PZ"): d.polygon([(32, 4), (60, 58), (4, 58)], fill="#F5A800", outline="#1F4E79", width=4)
    elif t.upper().startswith("LZ"): d.ellipse([4, 4, 60, 60], fill="#F5A800", outline="#1F4E79", width=4)
    else: d.rectangle([14, 14, 50, 50], outline="black", width=6)
    return im

def kml_color(hexrgb, a="ff"):
    h = hexrgb.lstrip("#"); return a + h[4:6] + h[2:4] + h[0:2]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("out")
    ap.add_argument("--kt", type=float, default=90, help="ground speed knots")
    ap.add_argument("--var", type=float, default=0, help="mag var, E=+ (MH = TC - var)")
    ap.add_argument("--dash", type=float, default=0.4, help="dash length NM")
    a = ap.parse_args()
    pts = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    for p in pts: p["lat"], p["lon"] = float(p["lat"]), float(p["lon"])
    legs = []
    for i in range(len(pts)-1):
        nm, tc = leg(pts[i], pts[i+1])
        legs.append(dict(nm=nm, crs=(tc - a.var) % 360, min=nm/a.kt*60, alt=pts[i].get("alt_ft", "")))
    tot_nm = sum(l["nm"] for l in legs); tot_min = sum(l["min"] for l in legs)
    files, pm = {}, []
    cum_nm = cum_min = 0
    for i, p in enumerate(pts):
        if i > 0: cum_nm += legs[i-1]["nm"]; cum_min += legs[i-1]["min"]
        first, last = i == 0, i == len(pts)-1
        rows = [["TOTAL", round(tot_nm), mmss(tot_min)],
                ["ACTUAL", "-" if first else round(cum_nm), "-" if first else mmss(cum_min)],
                ["REMAIN", "-" if last else round(tot_nm-cum_nm), "-" if last else mmss((tot_min-cum_min))]]
        c = color_of(p["type"])
        for tag, img in (("lbl", label_png(f'{p["type"]} {p["name"]}', c, rows)), ("mk", marker_png(p["type"], c))):
            fn = f"files/{tag}{i}.png"; b = io.BytesIO(); img.save(b, "PNG"); files[fn] = b.getvalue()
        sc_l = 2.6
        pm.append(f'<Placemark><name>{p["type"]}</name><Style><IconStyle><scale>0.8</scale><Icon><href>files/mk{i}.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style><Point><coordinates>{p["lon"]},{p["lat"]},0</coordinates></Point></Placemark>')
        pm.append(f'<Placemark><name>{p["type"]} table</name><Style><IconStyle><scale>{sc_l}</scale><hotSpot x="0.5" y="-0.15" xunits="fraction" yunits="fraction"/><Icon><href>files/lbl{i}.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style><Point><coordinates>{p["lon"]},{p["lat"]},0</coordinates></Point></Placemark>')
    for i, l in enumerate(legs):
        A, B = pts[i], pts[i+1]
        n = max(2, int(l["nm"]/a.dash)); segs = []
        for k in range(0, n, 2):
            f1, f2 = k/n, min((k+1)/n, 1)
            P = lambda f: f'{A["lon"]+(B["lon"]-A["lon"])*f},{A["lat"]+(B["lat"]-A["lat"])*f},0'
            segs.append(f"<LineString><tessellate>1</tessellate><coordinates>{P(f1)} {P(f2)}</coordinates></LineString>")
        pm.append(f'<Placemark><name>Leg {i+1}</name><Style><LineStyle><color>ff000000</color><width>4</width></LineStyle></Style><MultiGeometry>{"".join(segs)}</MultiGeometry></Placemark>')
        img = arrow_png(l["crs"], l["nm"], l["min"], l["alt"])
        fn = f"files/leg{i}.png"; b = io.BytesIO(); img.save(b, "PNG"); files[fn] = b.getvalue()
        # place box offset south of leg midpoint (~3 NM)
        mlat = (A["lat"]+B["lat"])/2 - 0.05; mlon = (A["lon"]+B["lon"])/2
        pm.append(f'<Placemark><name>Leg {i+1} box</name><Style><IconStyle><scale>2.4</scale><Icon><href>{fn}</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style><Point><coordinates>{mlon},{mlat},0</coordinates></Point></Placemark>')
    kml = ('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Route</name>'
           + "".join(pm) + "</Document></kml>")
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", kml)
        for k, v in files.items(): z.writestr(k, v)
    for i, l in enumerate(legs):
        print(f'Leg {i+1} {pts[i]["type"]}->{pts[i+1]["type"]}: {l["crs"]:03.0f}  {l["nm"]:.1f} NM  {mmss(l["min"])}')
    print(f"TOTAL {tot_nm:.1f} NM {mmss(tot_min)} -> {a.out}")

if __name__ == "__main__": main()
