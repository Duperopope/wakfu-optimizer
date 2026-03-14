import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import https from "node:https";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = path.resolve(__dirname, "..");
const PORT = 8090;

const MIME = {
  ".html":"text/html;charset=utf-8", ".js":"application/javascript;charset=utf-8",
  ".css":"text/css;charset=utf-8", ".json":"application/json;charset=utf-8",
  ".woff2":"font/woff2", ".otf":"font/otf", ".webp":"image/webp",
  ".png":"image/png", ".svg":"image/svg+xml", ".ico":"image/x-icon"
};

function mime(f){ return MIME[path.extname(f).toLowerCase()] || "application/octet-stream"; }

function serveFile(res, fp, ct){
  if(!fs.existsSync(fp)) return false;
  const d = fs.readFileSync(fp);
  res.writeHead(200,{"Content-Type":ct||mime(fp),"Access-Control-Allow-Origin":"*"});
  res.end(d); return true;
}

function proxy(res, url){
  https.get(url,{headers:{"User-Agent":"WakfuOpt/1.0"}}, pr=>{
    const ch=[]; pr.on("data",c=>ch.push(c)); pr.on("end",()=>{
      const body=Buffer.concat(ch);
      res.writeHead(pr.statusCode,{"Content-Type":pr.headers["content-type"]||"application/octet-stream","Access-Control-Allow-Origin":"*"});
      res.end(body);
    });
  }).on("error",e=>{
    res.writeHead(502,{"Content-Type":"application/json"});
    res.end(JSON.stringify({error:e.message}));
  });
}

// Lire index.html et vider le body pour eviter l'erreur d'hydratation React
let shellHTML = "";
try {
  const raw = fs.readFileSync(path.join(BASE, "index.html"), "utf-8");
  // Garder le <head> intact (scripts, CSS, meta) mais vider le contenu du <body>
  shellHTML = raw.replace(
    /(<body[^>]*>)[\s\S]*?(<script)/i,
    '$1<div id="__next"></div>$2'
  );
} catch(e) {
  console.error("ERREUR: index.html introuvable dans", BASE);
  process.exit(1);
}

http.createServer((req,res)=>{
  const u = new URL(req.url, "http://localhost:"+PORT);
  const p = decodeURIComponent(u.pathname);

  if(req.method==="OPTIONS"){
    res.writeHead(204,{"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"*","Access-Control-Allow-Headers":"*"});
    return res.end();
  }

  // 1) API -> proxy vers api.wakfuli.com
  if(p.startsWith("/api/")){
    const cached = path.join(BASE,"assets","api",p.replace(/^\/api\/v1\//,"").split("?")[0]);
    if(fs.existsSync(cached)) return serveFile(res,cached,"application/json;charset=utf-8");
    console.log("[API]",p+u.search);
    return proxy(res,"https://api.wakfuli.com"+p+u.search);
  }

  // 2) CDN images -> proxy vers cdn.wakfuli.com
  if(/^\/(breeds|items|placeholders|rarity|stats|itemTypes)\//.test(p)){
    const local = path.join(BASE,"assets","images",path.basename(p));
    if(fs.existsSync(local)) return serveFile(res,local);
    console.log("[CDN]",p);
    return proxy(res,"https://cdn.wakfuli.com"+p);
  }

  // 3) Next.js chunks
  if(p.startsWith("/_next/static/chunks/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,f))) return;
    // Chunk manquant -> proxy vers wakfuli.com
    console.log("[CHUNK MISS]",f);
    return proxy(res,"https://wakfuli.com"+p);
  }

  // 4) Next.js fonts
  if(p.startsWith("/_next/static/media/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,"assets","fonts",f))) return;
  }

  // 5) Tout le reste -> shell HTML (SPA)
  res.writeHead(200,{"Content-Type":"text/html;charset=utf-8","Access-Control-Allow-Origin":"*"});
  res.end(shellHTML);

}).listen(PORT,()=>{
  console.log("=== WAKFULI LOCAL ===");
  console.log("http://localhost:"+PORT+"/");
  console.log("http://localhost:"+PORT+"/builder/public");
  console.log("Mode: SPA shell + API/CDN proxy");
  console.log("Ctrl+C pour arreter");
});