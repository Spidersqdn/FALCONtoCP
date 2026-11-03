// แก้บรรทัดนี้ให้เป็น URL ของแผนที่บน Cloudflare R2 (Public URL ของ bucket + /map.pmtiles)
// แผนที่อื่น: เปิดเว็บด้วย ?map=<URL>/map500k.pmtiles
window.CONFIG = {
  MAP_URL: "https://pub-7591a6eb62fa48edac57d65672e452bb.r2.dev/map250k.pmtiles",
  DEFAULT_KT: 90
};
