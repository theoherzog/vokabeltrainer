// Vokabeltrainer service worker, build 1.9 vom 09.11.2026 07:43
const C='vt-86f82a12';
const FILES=['./','./index.html','./manifest.webmanifest','./icon-180.png','./icon-192.png','./icon-512.png','./favicon-32.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES.map(u=>new Request(u,{cache:'reload'})))).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
// Page: network first with 4 s timeout, so online you always get the newest version; offline the cached copy
function fromNet(req){ return new Promise((res,rej)=>{ const t=setTimeout(()=>rej('timeout'),4000);
  fetch(req,{cache:'no-store'}).then(r=>{ clearTimeout(t); if(!r.ok) return rej('status'); const cp=r.clone(); caches.open(C).then(c=>c.put('./index.html',cp)); res(r); }).catch(err=>{ clearTimeout(t); rej(err); }); }); }
self.addEventListener('fetch',e=>{ const req=e.request; if(req.method!=='GET') return;
  const url=new URL(req.url);
  if (req.mode==='navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')) {
    e.respondWith(fromNet(req).catch(()=>caches.match('./index.html'))); return; }
  e.respondWith(caches.match(req,{ignoreSearch:true}).then(r=>r||fetch(req))); });
