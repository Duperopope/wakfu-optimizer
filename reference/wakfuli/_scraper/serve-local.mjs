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

// Construire le shell HTML : garder <head> + scripts, vider le contenu rendu du body
let shellHTML = "";
try {
  const raw = fs.readFileSync(path.join(BASE, "index.html"), "utf-8");
  // Extraire tout le <head>...</head>
  const headMatch = raw.match(/<head[\s\S]*?<\/head>/i);
  // Extraire les <script> du body (ceux avec self.__next_f et le bootstrap)
  const bodyScripts = [];
  const scriptRegex = /<script[^>]*>[\s\S]*?<\/script>/gi;
  let m;
  while ((m = scriptRegex.exec(raw)) !== null) {
    // Ne garder que les scripts qui sont APRES </head>
    if (m.index > raw.indexOf("</head>")) {
      bodyScripts.push(m[0]);
    }
  }
  // Extraire les attributs du <body>
  const bodyTagMatch = raw.match(/<body([^>]*)>/i);
  const bodyAttrs = bodyTagMatch ? bodyTagMatch[1] : "";

  shellHTML = `<!DOCTYPE html><html lang="fr" class="min-h-screen flex flex-col">
${headMatch ? headMatch[0] : "<head></head>"}
<body${bodyAttrs}>
<div id="__next"></div>
${bodyScripts.join("\n")}
</body></html>`;

  console.log("[INIT] Shell HTML construit (" + shellHTML.length + " chars)");
  console.log("[INIT] " + bodyScripts.length + " scripts preserves dans le body");
} catch(e) {
  console.error("ERREUR: index.html introuvable dans", BASE, e.message);
  process.exit(1);
}

http.createServer((req,res)=>{
  const u = new URL(req.url, "http://localhost:"+PORT);
  const p = decodeURIComponent(u.pathname);

  if(req.method==="OPTIONS"){
    res.writeHead(204,{"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"*","Access-Control-Allow-Headers":"*"});
    return res.end();
  }

  // 1) API -> proxy vers api.wakfuli.com (401 /auth/me est normal)
  if(p.startsWith("/api/")){
    const apiKey = p.replace(/^\/api\/v1\//,"").split("?")[0];
    const cached = path.join(BASE,"assets","api",apiKey);
    if(fs.existsSync(cached)){
      console.log("[API CACHE]",p);
      return serveFile(res,cached,"application/json;charset=utf-8");
    }
    console.log("[API PROXY]",p+u.search);
    return proxy(res,"https://api.wakfuli.com"+p+u.search);
  }

  // 2) CDN images
  if(/^\/(breeds|items|placeholders|rarity|stats|itemTypes)\//.test(p)){
    const local = path.join(BASE,"assets","images",path.basename(p));
    if(fs.existsSync(local)) return serveFile(res,local);
    return proxy(res,"https://cdn.wakfuli.com"+p);
  }

  // 3) Next.js chunks (local ou proxy)
  if(p.startsWith("/_next/static/chunks/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,f))) return;
    console.log("[CHUNK PROXY]",f);
    return proxy(res,"https://wakfuli.com"+p);
  }

  // 4) Next.js fonts
  if(p.startsWith("/_next/static/media/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,"assets","fonts",f))) return;
    return proxy(res,"https://wakfuli.com"+p);
  }

  // 5) favicon
  if(p.includes("favicon")){
    return proxy(res,"https://wakfuli.com/favicon.ico");
  }

  // 6) Tout le reste -> shell HTML (SPA mode)
  res.writeHead(200,{"Content-Type":"text/html;charset=utf-8"});
  res.end(shellHTML);

}).listen(PORT,()=>{
  console.log("");
  console.log("=== WAKFULI LOCAL ===");
  console.log("http://localhost:"+PORT+"/");
  console.log("http://localhost:"+PORT+"/builder/public");
  console.log("http://localhost:"+PORT+"/builder/trending");
  console.log("");
  console.log("Mode: SPA shell (body vide) + API/CDN proxy");
  console.log("Note: /auth/me retournera 401 = normal (pas connecte)");
  console.log("Ctrl+C pour arreter");
  console.log("");
});