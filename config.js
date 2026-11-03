// แก้บรรทัดนี้ให้เป็น URL ของแผนที่บน Cloudflare R2 (Public URL ของ bucket + /map.pmtiles)
// เพิ่ม/แก้รายการแผนที่ใน MAPS (แสดงเป็นตัวเลือกในเว็บ)
window.CONFIG = {
  MAP_URL: "https://pub-7591a6eb62fa48edac57d65672e452bb.r2.dev/map250k.pmtiles",
  MAPS: [
    { name: "JOG 1:250,000", url: "https://pub-7591a6eb62fa48edac57d65672e452bb.r2.dev/map250k.pmtiles" },
    { name: "TPC 1:500,000", url: "https://pub-7591a6eb62fa48edac57d65672e452bb.r2.dev/map500k.pmtiles" },
    { name: "TLM 1:50,000", url: "https://pub-7591a6eb62fa48edac57d65672e452bb.r2.dev/map50k.pmtiles" }
  ],
  DEFAULT_KT: 90
};
