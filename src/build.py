import json, pathlib, shutil
D=pathlib.Path('/home/claude/vocab'); P=D/'build'/'pages'
import datetime
vf=D/'build'/'build_no.txt'; no=int(vf.read_text()) + 1 if vf.exists() else 7; vf.write_text(str(no))
from zoneinfo import ZoneInfo; now=datetime.datetime.now(ZoneInfo('Europe/Berlin'))
VER='1.%d vom %s'%(no, now.strftime('%d.%m.%Y %H:%M'))
app=(D/'app.html').read_text().replace('/*__VER__*/"dev"', json.dumps(VER)).replace('/*__DATA__*/""', json.dumps(((D/'data_full.tsv') if (D/'data_full.tsv').exists() else (D/'data.tsv')).read_text(), ensure_ascii=False))
(D/'build'/'artifact.html').write_text(app.replace('<!--PWA-->\n',''))
pwa='<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="icon-180.png">\n<link rel="icon" type="image/png" href="favicon-32.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="default">\n<meta name="apple-mobile-web-app-title" content="Vokabeln">\n<meta name="theme-color" content="#F2F3F5" media="(prefers-color-scheme: light)">\n<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">\n'
idx=app.replace('<!--PWA-->\n',pwa); (P/'index.html').write_text(idx)
import hashlib; ver=hashlib.md5(idx.encode()).hexdigest()[:8]
(P/'sw.js').write_text('''// Vokabeltrainer service worker, build %s
const C='vt-%s';
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
'''%(VER, ver))
m=json.loads((P/'manifest.webmanifest').read_text()); m['background_color']='#F2F3F5'; m['theme_color']='#F2F3F5'; (P/'manifest.webmanifest').write_text(json.dumps(m,ensure_ascii=False,indent=1))
print('ok', len(idx)//1024,'KB', ver, VER)
