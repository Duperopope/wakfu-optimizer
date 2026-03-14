// Serveur local pour naviguer dans la reference Wakfuli offline
// Source: reference/wakfuli/ (scrape du 2026-03-14)
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REF_DIR = path.resolve(__dirname, "..");
const PAGES_DIR = path.join(REF_DIR, "pages");
const ASSETS_DIR = path.join(REF_DIR, "assets");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css":  "text/css; charset=utf-8",
  ".js":   "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webp": "image/webp",
  ".png":  "image/png",
  ".woff2": "font/woff2",
  ".otf":  "font/otf",
  ".ico":  "image/x-icon",
};

function getMime(p) {
  return MIME[path.extname(p).toLowerCase()] || "application/octet-stream";
}

// Cherche le fichier dans plusieurs endroits
function findFile(urlPath) {
  // 1) /_next/static/chunks/xxx.js ou .css -> reference/wakfuli/xxx.js
  const chunkMatch = urlPath.match(/\/_next\/static\/chunks\/(.+)/);
  if (chunkMatch) {
    const f = path.join(REF_DIR, chunkMatch[1]);
    if (fs.existsSync(f)) return f;
  }

  // 2) /_next/static/media/xxx -> reference/wakfuli/assets/fonts/xxx
  const mediaMatch = urlPath.match(/\/_next\/static\/media\/(.+)/);
  if (mediaMatch) {
    const f = path.join(ASSETS_DIR, "fonts", mediaMatch[1]);
    if (fs.existsSync(f)) return f;
  }

  // 3) Images CDN interceptees: /breeds/xxx, /items/xxx, /placeholders/xxx, /rarity/xxx
  for (const prefix of ["breeds", "items", "placeholders", "rarity", "stats", "itemTypes", "etc"]) {
    if (urlPath.startsWith(`/${prefix}/`)) {
      const f = path.join(ASSETS_DIR, "images", urlPath.substring(1));
      if (fs.existsSync(f)) return f;
      // Essayer aussi a plat
      const flat = path.join(ASSETS_DIR, "images", path.basename(urlPath));
      if (fs.existsSync(flat)) return flat;
    }
  }

  // 4) /api/* -> assets/api/
  if (urlPath.startsWith("/api/")) {
    // Transformer /api/v1/builds -> assets/api/v1_builds.json (ou similaire)
    const safeName = urlPath.replace(/^\//, "").replace(/\//g, "_") + ".json";
    const f = path.join(ASSETS_DIR, "api", safeName);
    if (fs.existsSync(f)) return f;
  }

  // 5) Pages: /builder/public -> pages/builder_public.html
  const pageName = urlPath === "/" ? "index" : urlPath.replace(/^\//, "").replace(/\//g, "_");
  const pageFile = path.join(PAGES_DIR, pageName + ".html");
  if (fs.existsSync(pageFile)) return pageFile;

  // 6) Fichier direct dans REF_DIR
  const direct = path.join(REF_DIR, urlPath.replace(/^\//, ""));
  if (fs.existsSync(direct) && fs.statSync(direct).isFile()) return direct;

  return null;
}

const PORT = 8090;

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split("?")[0]);
  const filePath = findFile(urlPath);

  if (!filePath) {
    // Fallback: si c'est un path de navigation, servir index.html
    if (!path.extname(urlPath) || urlPath.includes("/builder/")) {
      const indexPath = path.join(PAGES_DIR, "index.html");
      if (fs.existsSync(indexPath)) {
        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        fs.createReadStream(indexPath).pipe(res);
        return;
      }
    }
    console.log(`[404] ${urlPath}`);
    res.writeHead(404);
    res.end("Not found");
    return;
  }

  const mime = getMime(filePath);
  res.writeHead(200, {
    "Content-Type": mime,
    "Cache-Control": "max-age=3600",
    "Access-Control-Allow-Origin": "*",
  });
  fs.createReadStream(filePath).pipe(res);
  console.log(`[200] ${urlPath} -> ${path.relative(REF_DIR, filePath)}`);
});

server.listen(PORT, () => {
  console.log(`\n=== Serveur reference Wakfuli ===`);
  console.log(`http://localhost:${PORT}/`);
  console.log(`http://localhost:${PORT}/builder/my`);
  console.log(`http://localhost:${PORT}/builder/public`);
  console.log(`\nFichiers servis depuis: ${REF_DIR}`);
  console.log(`Pages: ${fs.readdirSync(PAGES_DIR).length} HTML`);
  console.log(`Assets: ${fs.readdirSync(REF_DIR).filter(f => f.endsWith(".js")).length} JS, ${fs.readdirSync(REF_DIR).filter(f => f.endsWith(".css")).length} CSS`);
  console.log(`\nCtrl+C pour arreter\n`);
});