// Offline cache: app files + map tiles (OSM tiles and PMTiles byte ranges) viewed while online.
const APP='app-v2',TILES='tiles';
const SHELL=['./','index.html','config.js','lib/leaflet.js','lib/leaflet.css','lib/pmtiles.js','lib/jszip.min.js','lib/fonts/sarabun-400-thai.woff2','lib/fonts/sarabun-400-latin.woff2','lib/fonts/sarabun-700-thai.woff2','lib/fonts/sarabun-700-latin.woff2'];
let offline=true;
self.addEventListener('install',e=>{e.waitUntil(caches.open(APP).then(c=>c.addAll(SHELL)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==APP&&n!==TILES).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener('message',e=>{if(e.data&&'offline' in e.data)offline=!!e.data.offline});
const isOSM=u=>/(^|\.)tile\.openstreetmap\.org$/.test(u.hostname);
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET')return;
  const range=r.headers.get('range');
  if(range&&/\.pmtiles$/i.test(u.pathname))return e.respondWith(rangeFetch(r,range));
  if(isOSM(u))return e.respondWith(tileFetch(r));
  if(u.origin===location.origin)return e.respondWith(appFetch(r));
});
// app files: network first (always newest when online), cache fallback
async function appFetch(r){const c=await caches.open(APP);
  try{const res=await fetch(r);if(res.ok)c.put(r,res.clone());return res}catch(err){return (await c.match(r,{ignoreSearch:true}))||Response.error()}}
// OSM tiles: cache first
async function tileFetch(r){const c=await caches.open(TILES),hit=await c.match(r.url);if(hit)return hit;
  const res=await fetch(r.url,{mode:'cors'});if(res.ok&&offline)c.put(r.url,res.clone());return res}
// PMTiles: store each byte range as its own entry; 206 cannot be cached directly
async function rangeFetch(r,range){const c=await caches.open(TILES),key=r.url+(r.url.includes('?')?'&':'?')+'__range='+encodeURIComponent(range),hit=await c.match(key);
  const mk=(body,h)=>new Response(body,{status:206,headers:h});
  if(hit){const h=new Headers(hit.headers);return mk(await hit.blob(),h)}
  const res=await fetch(r);
  if(res.status===206&&offline){const b=await res.clone().blob();const h=new Headers();
    ['content-range','content-type','etag','content-length'].forEach(k=>{const v=res.headers.get(k);if(v)h.set(k,v)});
    c.put(key,new Response(b,{status:200,headers:h}))}
  return res}
