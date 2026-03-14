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

function proxyTo(res, url){
  https.get(url,{headers:{"User-Agent":"WakfuOpt/1.0","Accept":"*/*"}}, pr=>{
    const ch=[]; pr.on("data",c=>ch.push(c)); pr.on("end",()=>{
      const body=Buffer.concat(ch);
      const hdrs = {"Access-Control-Allow-Origin":"*"};
      if(pr.headers["content-type"]) hdrs["Content-Type"] = pr.headers["content-type"];
      if(pr.headers["x-action-redirect"]) hdrs["x-action-redirect"] = pr.headers["x-action-redirect"];
      res.writeHead(pr.statusCode, hdrs);
      res.end(body);
    });
  }).on("error",e=>{
    res.writeHead(502,{"Content-Type":"text/plain"});
    res.end("Proxy error: "+e.message);
  });
}

// Shell HTML
let shellHTML = "";
try {
  const raw = fs.readFileSync(path.join(BASE, "index.html"), "utf-8");
  const headMatch = raw.match(/<head[\s\S]*?<\/head>/i);
  const bodyTagMatch = raw.match(/<body([^>]*)>/i);
  const bodyAttrs = bodyTagMatch ? bodyTagMatch[1] : "";
  const bodyScripts = [];
  const re = /<script[^>]*>[\s\S]*?<\/script>/gi;
  let m; const headEnd = raw.indexOf("</head>");
  while ((m = re.exec(raw)) !== null) {
    if (m.index > headEnd) bodyScripts.push(m[0]);
  }
  shellHTML = '<!DOCTYPE html><html lang="fr" class="min-h-screen flex flex-col">\n'
    + (headMatch ? headMatch[0] : "<head></head>") + "\n"
    + "<body" + bodyAttrs + ">\n"
    + '<div id="__next"></div>\n'
    + bodyScripts.join("\n") + "\n"
    + "</body></html>";
  console.log("[INIT] Shell: "+shellHTML.length+" chars, "+bodyScripts.length+" scripts");
} catch(e) {
  console.error("ERREUR:",e.message); process.exit(1);
}

http.createServer((req,res)=>{
  const u = new URL(req.url, "http://localhost:"+PORT);
  const p = decodeURIComponent(u.pathname);
  const qs = u.search || "";

  if(req.method==="OPTIONS"){
    res.writeHead(204,{"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"*","Access-Control-Allow-Headers":"*"});
    return res.end();
  }

  // RSC requests -> proxy vers wakfuli.com (CRUCIAL pour eviter la boucle)
  if(qs.includes("rsc=") || qs.includes("_rsc=")){
    console.log("[RSC PROXY]",p+qs);
    return proxyTo(res,"https://wakfuli.com"+p+qs);
  }

  // API -> proxy vers api.wakfuli.com
  if(p.startsWith("/api/")){
    const apiKey = p.replace(/^\/api\/v1\//,"").split("?")[0];
    const cached = path.join(BASE,"assets","api",apiKey);
    if(req.method==="GET" && fs.existsSync(cached)){
      console.log("[API CACHE]",p);
      return serveFile(res,cached,"application/json;charset=utf-8");
    }
    console.log("[API PROXY]",p+qs);
    return proxyTo(res,"https://api.wakfuli.com"+p+qs);
  }

  // CDN images
  if(/^\/(breeds|items|placeholders|rarity|stats|itemTypes)\//.test(p)){
    const local = path.join(BASE,"assets","images",path.basename(p));
    if(fs.existsSync(local)) return serveFile(res,local);
    return proxyTo(res,"https://cdn.wakfuli.com"+p);
  }

  // Next.js chunks
  if(p.startsWith("/_next/static/chunks/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,f))) return;
    console.log("[CHUNK PROXY]",f);
    return proxyTo(res,"https://wakfuli.com"+p);
  }

  // Next.js fonts
  if(p.startsWith("/_next/static/media/")){
    const f = path.basename(p);
    if(serveFile(res,path.join(BASE,"assets","fonts",f))) return;
    return proxyTo(res,"https://wakfuli.com"+p);
  }

  // Favicon
  if(p.includes("favicon")) return proxyTo(res,"https://wakfuli.com"+p);

  // Pages HTML -> shell
  console.log("[PAGE]",p);
  res.writeHead(200,{"Content-Type":"text/html;charset=utf-8"});
  res.end(shellHTML);

}).listen(PORT,()=>{
  console.log("\n=== WAKFULI LOCAL ===");
  console.log("http://localhost:"+PORT+"/builder/public");
  console.log("RSC requests proxied to wakfuli.com");
  console.log("Ctrl+C pour arreter\n");
});