# FalCon2CP – Mission Route Map

เว็บวาดเส้นทางบิน PZ / CP / LZ บนแผนที่ FalconView (CADRG) พร้อมกล่อง leg (HDG / NM / เวลา / ALT)
และตาราง TOTAL / ACTUAL / REMAIN ใช้ได้ทั้งมือถือ, iPad และคอม

🔗 **ใช้งาน:** https://spidersqdn.github.io/FalCon2CP/

![preview](docs/preview.png)

## ใช้งาน
**วาดเส้นทาง**
- แตะแผนที่ = เพิ่มจุด (จุดแรก = PZ, จุดสุดท้าย = LZ, จุดกลาง = CP) ลากจุด / ป้าย / กล่อง leg ได้
- แตะจุดเพื่อแก้: ชนิดจุด (PZ / LZ / CP หลัก / CP สำรอง), ข้อความป้าย, พิกัด LAT/LONG (DDM) หรือ MGRS, FLY OVER / FLY BY, แทรก / ลบ / เลื่อนจุด
- ตั้ง GS (kt) แล้วคำนวณ HDG / NM / เวลา / ALT อัตโนมัติ
  - เวลา: +5 นาที ปัดเป็น 0/5 นาที กระจายเวลาส่วนเกินให้แต่ละ leg
  - ALT: ความสูงภูมิประเทศสูงสุด ปัดขึ้น 100 + 500 ft (แก้เองได้)
- กราฟความสูงภูมิประเทศ (elevation profile) และสถิติเส้นทาง

**เส้นทางหลัก / สำรอง**
- Add ROUTE = เพิ่มเส้นทางสำรอง ใช้ PZ/LZ ร่วมกัน มีตารางแยก, เลข CP ต่อเนื่อง
- ตั้งเส้นทึบ / เส้นประ และความหนาเส้นแยกต่อเส้นทาง, ⇆ สลับหลัก/สำรอง
- ⇄ BACK TRACK = กลับทิศ, ↶ UNDO (Ctrl+Z), CLEAR = ล้างทั้งหมด
- SHOW: เลือกแสดง PZ / CPs / LZ, DOG LEGs

**IMPORT / EXPORT / SLIDE**
- IMPORT: CSV / KML / KMZ / GPX (รับไฟล์จาก AirNavFlow ได้)
- EXPORT: KML / KMZ / GPX / CSV (ทั้งสองเส้นทาง)
- Export PDF / Print: ดูตัวอย่างก่อน, มาตราส่วนจริง 1:50k–1:1M, A4/A3 ตั้ง/นอน, แบ่งแผ่นทับขอบมีขีดบอกแนวต่อ + scale bar (ตอน Print ตั้ง Scale 100%)
- SLIDE: ภาพ Mission Overview 16:9 (PNG) แบบแผนที่แผนสมบูรณ์ ใส่ PowerPoint ได้ทันที

**อื่น ๆ**
- ปรับขนาดสัญลักษณ์ / ป้าย / ตาราง / ฟอนต์แผนที่ (TH SarabunPSK) ด้วยปุ่ม + / −
- เลือกแผนที่: JOG 1:250,000 / TPC 1:500,000 (ตั้งใน `config.js`)
- ติดตั้งเป็นแอปบนหน้าจอ (PWA) อัปเดตเวอร์ชันใหม่อัตโนมัติ
- เส้นทางเก็บใน browser ของแต่ละเครื่อง ไม่ถูกอัปโหลด
- ใช้แบบไม่มีเน็ต: MAP > 📁 IMPORT MAP (.pmtiles) เลือกไฟล์จากเครื่อง ระบบเก็บไว้ให้
- ปุ่ม ◀ ซ่อน/แสดงแถบ (จับภาพแผนที่เต็มจอ), เปิดแผนที่อื่นชั่วคราว: `?map=https://.../other.pmtiles`

## โครงสร้าง
```
index.html      ตัว app (Leaflet)
config.js       ★ URL แผนที่ (MAP_URL, MAPS) + GS เริ่มต้น
sw.js           service worker (PWA / offline cache)
lib/            leaflet, jszip, pmtiles
tools/          สคริปต์แปลงแผนที่ / สร้าง KMZ / start.bat (ใช้ในเครื่อง)
docs/ONLINE.md  คู่มือทำแผนที่ + Cloudflare R2
```

## ระบบ
```
GitHub (repo นี้, main) ──auto deploy──> GitHub Pages (ตัวเว็บ)
Cloudflare R2  map250k / map500k.pmtiles ──> เว็บดึงแผนที่เฉพาะส่วนที่ดู
```

## ทำแผนที่ใหม่ (ในเครื่อง)
1. OSGeo4W Shell: `C:\PFPS\map1\make_rpf.bat <folder>` แล้วแปลงเป็น `.pmtiles` ด้วย `pmtiles.exe` → ดู [docs/ONLINE.md](docs/ONLINE.md)
2. อัปโหลดขึ้น R2 bucket `map` (ตั้ง CORS อนุญาต GET/HEAD, header `range`)
3. เพิ่ม URL ใน `config.js` > Commit → เว็บอัปเดตเองใน ~1 นาที
