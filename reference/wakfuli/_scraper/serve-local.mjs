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

// Routes vers pages HTML rendues par Playwright
const PAGE_ROUTES = {
  "/": "index.html",
  "/index": "index.html",
  "/builder/my": "builder_my.html",
  "/builder/public": "builder_public.html",
  "/builder/trending": "builder_public.html",
  "/legal/privacy": "legal_privacy.html",
  "/legal/terms": "legal_terms.html",
  "/legal/imprint": "legal_imprint.html",
};

function findAsset(urlPath) {
  // CSS/JS chunks
  const chunkMatch = urlPath.match(/\/_next\/static\/chunks\/(.+)/);
  if (chunkMatch) {
    const f = path.join(REF_DIR, chunkMatch[1]);
    if (fs.existsSync(f)) return f;
  }
  // Fonts
  const mediaMatch = urlPath.match(/\/_next\/static\/media\/(.+)/);
  if (mediaMatch) {
    const f = path.join(ASSETS_DIR, "fonts", mediaMatch[1]);
    if (fs.existsSync(f)) return f;
  }
  // Images CDN (breeds, items, placeholders, rarity, stats)
  for (const prefix of ["breeds", "items", "placeholders", "rarity", "stats", "itemTypes", "etc"]) {
    if (urlPath.startsWith(`/${prefix}/`)) {
      // Essayer structure complete
      const f = path.join(ASSETS_DIR, "images", urlPath.substring(1));
      if (fs.existsSync(f)) return f;
      // Essayer a plat
      const flat = path.join(ASSETS_DIR, "images", path.basename(urlPath));
      if (fs.existsSync(flat)) return flat;
    }
  }
  // Fichier direct dans REF_DIR
  const direct = path.join(REF_DIR, urlPath.replace(/^\//, ""));
  if (fs.existsSync(direct) && fs.statSync(direct).isFile()) return direct;
  return null;
}

const PORT = 8090;

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split("?")[0]);

  // 1) Pages HTML rendues — priorite absolue
  const pageFile = PAGE_ROUTES[urlPath];
  if (pageFile) {
    const fullPath = path.join(PAGES_DIR, pageFile);
    if (fs.existsSync(fullPath)) {
      // Lire le HTML et SUPPRIMER les scripts pour empecher le SPA de prendre le dessus
      let html = fs.readFileSync(fullPath, "utf-8");
      // Retirer tous les <script> pour garder le HTML statique pur
      html = html.replace(/<script[\s\S]*?<\/script>/gi, "");
      html = html.replace(/<script[^>]*\/>/gi, "");
      res.writeHead(200, {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-cache",
      });
      res.end(html);
      console.log(`[PAGE] ${urlPath} -> pages/${pageFile} (static, no JS)`);
      return;
    }
  }

  // 2) Assets (CSS, images, fonts) — on les sert normalement
  const assetPath = findAsset(urlPath);
  if (assetPath) {
    res.writeHead(200, {
      "Content-Type": getMime(assetPath),
      "Cache-Control": "max-age=3600",
      "Access-Control-Allow-Origin": "*",
    });
    fs.createReadStream(assetPath).pipe(res);
    console.log(`[200] ${urlPath}`);
    return;
  }

  // 3) API calls — retourner des reponses vides mais valides
  if (urlPath.startsWith("/api/")) {
    res.writeHead(200, {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    });
    // Essayer de servir la reponse API capturee
    const apiFile = path.join(ASSETS_DIR, "api", urlPath.replace(/^\//, "").replace(/\//g, "_"));
    if (fs.existsSync(apiFile)) {
      fs.createReadStream(apiFile).pipe(res);
      console.log(`[API] ${urlPath} -> cached`);
    } else {
      res.end(JSON.stringify({ data: [], message: "offline" }));
      console.log(`[API] ${urlPath} -> empty stub`);
    }
    return;
  }

  // 4) Tout autre chemin de navigation -> index.html statique
  if (!path.extname(urlPath) || urlPath.startsWith("/builder/")) {
    const indexPath = path.join(PAGES_DIR, "builder_public.html");
    if (fs.existsSync(indexPath)) {
      let html = fs.readFileSync(indexPath, "utf-8");
      html = html.replace(/<script[\s\S]*?<\/script>/gi, "");
      html = html.replace(/<script[^>]*\/>/gi, "");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(html);
      console.log(`[FALLBACK] ${urlPath} -> builder_public.html (static)`);
      return;
    }
  }

  console.log(`[404] ${urlPath}`);
  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, () => {
  const pages = Object.keys(PAGE_ROUTES);
  console.log(`\n========================================`);
  console.log(`  WAKFULI REFERENCE LOCALE (statique)`);
  console.log(`========================================`);
  console.log(`\nPages disponibles:`);
  pages.forEach(p => console.log(`  http://localhost:${PORT}${p}`));
  console.log(`\nMode: HTML statique (pas de JS SPA)`);
  console.log(`Les pages montrent le rendu exact capture par Playwright.`);
  console.log(`\nCtrl+C pour arreter\n`);
});