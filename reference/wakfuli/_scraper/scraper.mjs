// ============================================================
// wakfuli-scraper — Telechargement complet du site SPA
// Utilise Playwright pour rendre le JS et capturer tout
// ============================================================
import { chromium } from "playwright";
import { writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { URL } from "url";
import path from "path";

const BASE_URL = "https://wakfuli.com";
const OUTPUT   = path.resolve("..", "");  // reference/wakfuli/

// Routes a visiter (SPA Next.js — pas de sitemap complet)
const ROUTES = [
  "/",
  "/builder/my",
  "/builder/public",
  "/legal/privacy",
  "/legal/terms",
  "/legal/imprint",
];

// Compteurs pour le log
let assetCount = 0;
let pageCount  = 0;

// Helper : creer un chemin safe pour le fichier
function safePath(urlStr) {
  try {
    const u = new URL(urlStr);
    let p = u.pathname;
    if (p === "/" || p === "") p = "/index";
    // Retirer les query params du nom
    p = p.split("?")[0];
    return p;
  } catch {
    return "/unknown_" + Date.now();
  }
}

// Helper : determiner le dossier de sortie selon le type
function assetDir(contentType, urlPath) {
  if (contentType?.includes("css") || urlPath.endsWith(".css"))   return "assets/css";
  if (contentType?.includes("javascript") || urlPath.endsWith(".js")) return "assets/js";
  if (contentType?.includes("font") || /\.(woff2?|ttf|otf|eot)$/i.test(urlPath)) return "assets/fonts";
  if (contentType?.includes("image") || /\.(png|jpg|jpeg|gif|webp|svg|ico|avif)$/i.test(urlPath)) return "assets/images";
  if (urlPath.includes("/api/")) return "assets/api";
  return "assets/other";
}

// Helper : ecrire un fichier avec creation du dossier parent
async function saveFile(relPath, data) {
  const full = path.join(OUTPUT, relPath);
  const dir  = path.dirname(full);
  if (!existsSync(dir)) await mkdir(dir, { recursive: true });
  await writeFile(full, data);
  assetCount++;
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log("=== WAKFULI SCRAPER ===");
  console.log(`Output: ${OUTPUT}`);
  console.log(`Routes: ${ROUTES.length}`);
  console.log("");

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  });

  // Set pour eviter les doublons d'assets
  const savedAssets = new Set();

  // Intercepter TOUTES les reponses reseau
  context.on("response", async (response) => {
    const url = response.url();
    const status = response.status();

    // Ignorer les erreurs et les data: URLs
    if (status >= 400 || url.startsWith("data:")) return;

    // Calculer un chemin relatif
    const urlPath = safePath(url);
    const assetKey = urlPath;

    // Eviter les doublons
    if (savedAssets.has(assetKey)) return;
    savedAssets.add(assetKey);

    try {
      const contentType = response.headers()["content-type"] ?? "";
      const body = await response.body();

      // Determiner ou sauvegarder
      const isPage = contentType.includes("text/html");
      if (isPage) return; // Les pages HTML sont gerees separement

      const dir = assetDir(contentType, urlPath);
      const fileName = path.basename(urlPath) || "unknown";
      const savePath = `${dir}/${fileName}`;

      await saveFile(savePath, body);

      // Log discret
      if (assetCount % 20 === 0) {
        process.stdout.write(`\r  Assets: ${assetCount}...`);
      }
    } catch {
      // Certaines reponses ne peuvent pas etre lues (streaming, etc.)
    }
  });

  // Visiter chaque route
  for (const route of ROUTES) {
    const url = `${BASE_URL}${route}`;
    console.log(`\n[PAGE] ${url}`);

    const page = await context.newPage();

    try {
      // Naviguer et attendre le rendu complet
      await page.goto(url, {
        waitUntil: "networkidle",
        timeout: 30000,
      });

      // Attendre un peu plus pour les animations/lazy loads
      await page.waitForTimeout(3000);

      // Sauvegarder le HTML rendu (apres execution JS)
      const html = await page.content();
      const pageName = route === "/"
        ? "index"
        : route.replace(/^\//, "").replace(/\//g, "_");
      await saveFile(`pages/${pageName}.html`, html);
      console.log(`  -> HTML sauvegarde: pages/${pageName}.html`);

      // Screenshot full page
      await page.screenshot({
        path: path.join(OUTPUT, `screenshots/${pageName}.png`),
        fullPage: true,
      });
      console.log(`  -> Screenshot: screenshots/${pageName}.png`);

      // Extraire les URLs d'images depuis le DOM rendu
      const imgUrls = await page.evaluate(() => {
        const imgs = Array.from(document.querySelectorAll("img"));
        return imgs.map(img => img.src).filter(s => s && !s.startsWith("data:"));
      });
      console.log(`  -> Images dans le DOM: ${imgUrls.length}`);

      // Extraire les URLs de background-image en CSS
      const bgUrls = await page.evaluate(() => {
        const all = Array.from(document.querySelectorAll("*"));
        const urls = [];
        for (const el of all) {
          const bg = getComputedStyle(el).backgroundImage;
          if (bg && bg !== "none") {
            const match = bg.match(/url\(["']?(.+?)["']?\)/);
            if (match && match[1] && !match[1].startsWith("data:")) {
              urls.push(match[1]);
            }
          }
        }
        return urls;
      });
      console.log(`  -> Background images: ${bgUrls.length}`);

      // Telecharger les images manquantes
      for (const imgUrl of [...imgUrls, ...bgUrls]) {
        const imgPath = safePath(imgUrl);
        const imgKey  = imgPath;
        if (savedAssets.has(imgKey)) continue;
        savedAssets.add(imgKey);

        try {
          const resp = await page.request.get(imgUrl);
          if (resp.ok()) {
            const body = await resp.body();
            const fileName = path.basename(imgPath) || "img_" + Date.now();
            await saveFile(`assets/images/${fileName}`, body);
          }
        } catch {}
      }

      // Extraire les font-face URLs depuis les stylesheets
      const fontUrls = await page.evaluate(() => {
        const urls = [];
        for (const sheet of document.styleSheets) {
          try {
            for (const rule of sheet.cssRules) {
              if (rule.cssText?.includes("@font-face")) {
                const match = rule.cssText.match(/url\(["']?(.+?)["']?\)/g);
                if (match) {
                  for (const m of match) {
                    const u = m.replace(/url\(["']?/, "").replace(/["']?\)/, "");
                    if (u && !u.startsWith("data:")) urls.push(u);
                  }
                }
              }
            }
          } catch {}
        }
        return urls;
      });
      console.log(`  -> Fonts trouvees: ${fontUrls.length}`);

      for (const fontUrl of fontUrls) {
        const fPath = safePath(fontUrl);
        if (savedAssets.has(fPath)) continue;
        savedAssets.add(fPath);
        try {
          const resp = await page.request.get(fontUrl);
          if (resp.ok()) {
            const body = await resp.body();
            const fileName = path.basename(fPath);
            await saveFile(`assets/fonts/${fileName}`, body);
          }
        } catch {}
      }

      pageCount++;

    } catch (err) {
      console.error(`  ERREUR: ${err.message}`);
    } finally {
      await page.close();
    }
  }

  await browser.close();

  // Resume final
  console.log("\n");
  console.log("=== SCRAPING TERMINE ===");
  console.log(`Pages:  ${pageCount}/${ROUTES.length}`);
  console.log(`Assets: ${assetCount}`);
  console.log(`Output: ${OUTPUT}`);
  console.log("");

  // Generer le manifeste
  const manifest = {
    date: new Date().toISOString(),
    source: BASE_URL,
    pages: pageCount,
    assets: assetCount,
    routes: ROUTES,
    savedAssets: Array.from(savedAssets).sort(),
  };
  await saveFile("SCRAPE_MANIFEST.json", JSON.stringify(manifest, null, 2));
  console.log("SCRAPE_MANIFEST.json genere.");
}

main().catch(console.error);
