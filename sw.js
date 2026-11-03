// Offline cache: app files + map tiles (OSM tiles and PMTiles byte ranges) viewed while online.
// Bump APP when sw.js changes. App files are always revalidated with the server, so index.html changes
// reach installed (home-screen) apps without a bump; the page also checks for a new version on resume.
const APP='app-v9',TILES='tiles';
const SHELL=['./','index.html','config.js','lib/leaflet.js','lib/leaflet.css','lib/pmtiles.js','lib/jszip.min.js','icon.svg','icon-192.png','manifest.webmanifest','lib/fonts/sarabun-400-thai.woff2','lib/fonts/sarabun-400-latin.woff2','lib/fonts/sarabun-700-thai.woff2','lib/fonts/sarabun-700-latin.woff2'];
let offline=true;
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(APP).then(c=>c.addAll(SHELL.map(u=>new Request(u,{cache:'reload'})))).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==APP&&n!==TILES).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener('message',e=>{if(e.data&&'offline' in e.data)offline=!!e.data.offline});
const isOSM=u=>/(^|\.)tile\.openstreetmap\.org$/.test(u.hostname)||(u.hostname==='s3.amazonaws.com'&&u.pathname.startsWith('/elevation-tiles-prod/'));
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET')return;
  const range=r.headers.get('range');
  if(range&&/\.pmtiles$/i.test(u.pathname))return e.respondWith(rangeFetch(r,range));
  if(isOSM(u))return e.respondWith(tileFetch(r));
  if(u.origin===location.origin)return e.respondWith(appFetch(r));
});
// app files: network first, revalidated with the server (bypasses the 10-min browser HTTP cache), cache fallback
async function appFetch(r){const c=await caches.open(APP);
  try{const res=await fetch(r.url,{cache:'no-cache',credentials:'same-origin'});
    if(res.ok){const k=new URL(r.url);k.search='';c.put(k.href,res.clone())}return res}
  catch(err){return (await c.match(r,{ignoreSearch:true}))||(r.mode==='navigate'&&await c.match('./'))||Response.error()}}
// OSM tiles: cache first
async function tileFetch(r){const c=await caches.open(TILES),hit=await c.match(r.url);if(hit)return hit;
  const res=await fetch(r.url,{mode:'cors'});if(res.ok&&offline)c.put(r.url,res.clone());return res}
// PMTiles: store each byte range as its own entry; 206 cannot be cached directly.
// pmtiles.js asks with cache:'reload' after an ETag mismatch (file replaced on R2): skip the cache then and
// drop the old file's ranges, otherwise the stale header is served forever and the map never loads.
const rkey=(u,range)=>u+(u.includes('?')?'&':'?')+'__range='+encodeURIComponent(range);
async function rangeFetch(r,range){const c=await caches.open(TILES),key=rkey(r.url,range),fresh=r.cache==='reload'||r.cache==='no-store';
  const hit=fresh?null:await c.match(key);
  if(hit)return new Response(await hit.blob(),{status:206,headers:new Headers(hit.headers)});
  const res=await fetch(r);
  if(res.status===206){const et=res.headers.get('etag');
    if(fresh&&et)await purge(c,r.url,et);
    if(offline){const b=await res.clone().blob(),h=new Headers();
      ['content-range','content-type','etag','content-length'].forEach(k=>{const v=res.headers.get(k);if(v)h.set(k,v)});
      await c.put(key,new Response(b,{status:200,headers:h}))}}
  return res}
async function purge(c,url,et){const p=rkey(url,'');
  for(const q of await c.keys()){if(!q.url.startsWith(p))continue;const m=await c.match(q);if(m&&m.headers.get('etag')!==et)await c.delete(q)}}
