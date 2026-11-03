# เอา Route Map ขึ้นเว็บ (แผนที่ทั้งชุด 3 GB)

แนวทาง: แปลงแผนที่เป็น **ไฟล์เดียว `map.pmtiles`** แล้วเอาขึ้น **Cloudflare R2** (ฟรีถึง 10 GB [Unverified: เช็คราคาล่าสุด])
browser จะดึงเฉพาะส่วนที่ดูอยู่ ไม่ต้องโหลดทั้ง 3 GB

## A) สร้าง map.pmtiles (เลือก 1 วิธี)
**วิธี 1 – QGIS (แนะนำ, รวมได้หลายระวาง)**
1. ลาก `A.TOC` เข้า QGIS > เลือกชุด TPC/JOG ที่ต้องการ
2. Processing Toolbox > `Generate XYZ tiles (MBTiles)`
   - Extent: คำนวณจาก layer, Min zoom 7, Max zoom 12 (JOG = 13)
   - Tile format: JPG, Quality 75 > Output `map.mbtiles`
3. ดาวน์โหลด `pmtiles.exe` จาก github.com/protomaps/go-pmtiles/releases แล้วรัน
   ```
   pmtiles convert map.mbtiles map.pmtiles
   ```
**วิธี 2 – Command line (1 ชุดแผนที่)** ใน OSGeo4W Shell
```
make_pmtiles.bat "C:\...\RPF\A.TOC"
```

## B) เอาขึ้น Cloudflare R2
1. สมัคร cloudflare.com > R2 > **Create bucket** ชื่อ `routemap`
2. Bucket > Settings > **Public access: r2.dev subdomain = Allow** (จะได้ URL `https://pub-xxxx.r2.dev`)
3. อัปโหลดผ่านหน้าเว็บ (ลากวาง): `index.html` และโฟลเดอร์ `lib/`
4. `map.pmtiles` ไฟล์ใหญ่ ให้ใช้ rclone
   - R2 > Manage API tokens > Create (Object Read & Write) > จด Access Key / Secret / Account ID
   - `rclone config` > new remote ชื่อ `r2` > type `s3` > provider `Cloudflare` > ใส่ key > endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
   ```
   rclone copy map.pmtiles r2:routemap -P --s3-chunk-size 100M
   ```
5. เปิด `https://pub-xxxx.r2.dev/index.html` ใช้งานได้ทุกเครื่อง

## ความปลอดภัย
- r2.dev = ใครมีลิงก์ก็เปิดได้ ถ้าต้องจำกัดคน ใช้ custom domain + Cloudflare Access (ฟรี 50 users) [Unverified]
- เส้นทางที่วาด **ไม่ถูกอัปโหลด** เก็บใน browser ของแต่ละเครื่องเท่านั้น (ส่งต่อด้วย Export CSV/KML)
- ตรวจสอบสิทธิ์การเผยแพร่แผนที่ CADRG กับหน่วยก่อน

## หมายเหตุ
- ใช้ในเครื่อง (offline) แบบ pmtiles ต้องใช้ server ที่รองรับ Range เช่น `npx http-server -p 8000`
  (python http.server ใช้ไม่ได้กับ pmtiles; ใช้โฟลเดอร์ `tiles/` แทนได้)
- เปิดแผนที่ไฟล์อื่น: `index.html?map=ชื่อไฟล์.pmtiles`
