"use client";

import React, { useState, useCallback, useMemo } from "react";

// ============================================================
// Wakfuli-style LeftPanel — fidele au design original
// Sources:
//   - Chunks JS Wakfuli (25c3dbf546a727d1.js, 16de6c976c6b691d.js)
//   - Icones: https://github.com/Vertylo/wakassets/tree/main/characteristics
//   - Stats: https://wakfu.wiki.gg/wiki/Characteristic
// ============================================================

// --- Types ---
interface StatDef {
  key: string;
  label: string;
  icon: string;    // nom fichier dans wakassets/characteristics/
  category: string;
}

interface Bonus {
  label: string;
  active: boolean;
  stats: Record<string, number>;
}

interface BuildState {
  name: string;
  level: number;
  characterClass: string;
  visibility: "public" | "link-only" | "private";
}

// --- CDN icones Wakfu (Vertylo/wakassets GitHub Pages) ---
const ICON_CDN = "https://vertylo.github.io/wakassets/characteristics";

// --- Definition des stats affichees, groupees par categorie Wakfuli ---
const STATS: StatDef[] = [
  // Generale
  { key: "HP",               label: "PV",                icon: "HP",               category: "general" },
  { key: "AP",               label: "PA",                icon: "AP",               category: "general" },
  { key: "MP",               label: "PM",                icon: "MP",               category: "general" },
  { key: "WP",               label: "PW",                icon: "WP",               category: "general" },
  { key: "RANGE",            label: "PO",                icon: "RANGE",            category: "general" },
  // Combat
  { key: "DODGE",            label: "Esquive",           icon: "DODGE",            category: "combat" },
  { key: "TACKLE",           label: "Tacle",             icon: "TACKLE",           category: "combat" },
  { key: "INIT",             label: "Initiative",        icon: "INIT",             category: "combat" },
  { key: "BLOCK",            label: "Parade",            icon: "BLOCK",            category: "combat" },
  { key: "WILLPOWER",        label: "Volonte",           icon: "WILLPOWER",        category: "combat" },
  { key: "WISDOM",           label: "Sagesse",           icon: "WISDOM",           category: "combat" },
  { key: "PROSPECTION",      label: "Prospection",       icon: "PROSPECTION",      category: "combat" },
  // Maitrise
  { key: "DMG_IN_PERCENT",   label: "% Degats",          icon: "DMG_IN_PERCENT",   category: "mastery" },
  { key: "HEAL_IN_PERCENT",  label: "% Soins",           icon: "HEAL_IN_PERCENT",  category: "mastery" },
  { key: "CRITICAL_BONUS",   label: "Critique",          icon: "CRITICAL_BONUS",   category: "mastery" },
  { key: "BACKSTAB_BONUS",   label: "Dos",               icon: "BACKSTAB_BONUS",   category: "mastery" },
  { key: "MELEE_DMG",        label: "Melee",             icon: "MELEE_DMG",        category: "mastery" },
  { key: "RANGED_DMG",       label: "Distance",          icon: "RANGED_DMG",       category: "mastery" },
  { key: "BERSERK_DMG",      label: "Berserk",           icon: "BERSERK_DMG",      category: "mastery" },
  // Resistance
  { key: "RES_IN_PERCENT",   label: "% Res.",            icon: "RES_IN_PERCENT",   category: "resist" },
  { key: "CRITICAL_RES",     label: "Res. Crit.",        icon: "CRITICAL_RES",     category: "resist" },
  { key: "RES_BACKSTAB",     label: "Res. Dos",          icon: "RES_BACKSTAB",     category: "resist" },
];

const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  combat: "Combat",
  mastery: "Maitrise",
  resist: "Resistance",
};

// --- Bonus Wakfuli (chunk 25c3dbf546a727d1.js) ---
const DEFAULT_BONUSES: Bonus[] = [
  {
    label: "Arbre",
    active: false,
    stats: { HP: 55, DODGE: 20, TACKLE: 20, INIT: 10, WISDOM: 10, PROSPECTION: 10, DMG_IN_PERCENT: 8, HEAL_IN_PERCENT: 8, RES_IN_PERCENT: 20 },
  },
  {
    label: "Gemme",
    active: false,
    stats: { HP: 10, WISDOM: 10, PROSPECTION: 10 },
  },
  {
    label: "Monture",
    active: false,
    stats: { DMG_IN_PERCENT: 40 },
  },
];

const VIS_CYCLE: ("public" | "link-only" | "private")[] = ["public", "link-only", "private"];
const VIS_LABEL: Record<string, string> = { public: "Public", "link-only": "Lien", private: "Prive" };
const VIS_ICON: Record<string, string>  = { public: "\u{1F30D}", "link-only": "\u{1F517}", private: "\u{1F512}" };

// --- Helpers ---
function computeStats(bonuses: Bonus[]): Record<string, number> {
  const result: Record<string, number> = {};
  for (const s of STATS) result[s.key] = 0;
  for (const b of bonuses) {
    if (!b.active || !b.stats) continue;
    for (const [k, v] of Object.entries(b.stats)) {
      result[k] = (result[k] ?? 0) + (v ?? 0);
    }
  }
  return result;
}

function encodeBuild(data: unknown): string {
  try { return btoa(encodeURIComponent(JSON.stringify(data))); }
  catch { return ""; }
}

// ============================================================
// COMPOSANT — export nomme pour { LeftPanel }
// ============================================================
export function LeftPanel() {
  const [build, setBuild] = useState<BuildState>({
    name: "Mon Build",
    level: 20,
    characterClass: "huppermage",
    visibility: "public",
  });

  const [bonuses, setBonuses] = useState<Bonus[]>(() => structuredClone(DEFAULT_BONUSES));
  const [isFav, setIsFav] = useState(false);
  const [toast, setToast] = useState("");

  const stats = useMemo(() => computeStats(bonuses), [bonuses]);

  const flash = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2000);
  }, []);

  // Actions
  const onCopy = useCallback(async () => {
    const txt = JSON.stringify({ ...build, stats }, null, 2);
    try {
      await navigator.clipboard.writeText(txt);
      flash("Copie !");
    } catch { flash("Erreur"); }
  }, [build, stats, flash]);

  const onLink = useCallback(() => {
    const enc = encodeBuild({ ...build, stats });
    if (!enc) return flash("Erreur");
    const url = `${window.location.origin}/builder?b=${enc}`;
    navigator.clipboard.writeText(url).then(() => flash("Lien copie !"), () => flash("Lien genere"));
  }, [build, stats, flash]);

  const onVis = useCallback(() => {
    setBuild(p => {
      const i = VIS_CYCLE.indexOf(p.visibility);
      return { ...p, visibility: VIS_CYCLE[(i + 1) % VIS_CYCLE.length] };
    });
  }, []);

  const onFav = useCallback(() => {
    setIsFav(p => {
      const n = !p;
      try {
        const s = localStorage.getItem("wk_fav");
        let l: string[] = s ? JSON.parse(s) : [];
        if (!Array.isArray(l)) l = [];
        l = n ? [...new Set([...l, "current"])] : l.filter(x => x !== "current");
        localStorage.setItem("wk_fav", JSON.stringify(l));
      } catch {}
      return n;
    });
  }, []);

  const toggleBonus = useCallback((i: number) => {
    setBonuses(p => p.map((b, j) => j === i ? { ...b, active: !b.active } : b));
  }, []);

  // Grouper les stats par categorie
  const categories = useMemo(() => {
    const cats: { id: string; label: string; items: StatDef[] }[] = [];
    const seen = new Set<string>();
    for (const s of STATS) {
      if (!seen.has(s.category)) {
        seen.add(s.category);
        cats.push({ id: s.category, label: CATEGORY_LABELS[s.category] ?? s.category, items: [] });
      }
      cats.find(c => c.id === s.category)!.items.push(s);
    }
    return cats;
  }, []);

  return (
    <aside className="wk-panel">
      <style>{panelCSS}</style>

      {/* === BUILD HEADER === */}
      <div className="wk-header">
        <div className="wk-header-info">
          <span className="wk-class-badge">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`https://vertylo.github.io/wakassets/breedsIcons/14.png`}
              alt="class"
              width={28}
              height={28}
              onError={e => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          </span>
          <div>
            <div className="wk-build-name">{build.name}</div>
            <div className="wk-build-meta">
              {build.characterClass.charAt(0).toUpperCase() + build.characterClass.slice(1)}
              {" \u00B7 Niv. "}
              {build.level}
            </div>
          </div>
        </div>

        {/* Actions row */}
        <div className="wk-actions">
          <button className="wk-btn" onClick={onCopy} title="Copier le build">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          <button className="wk-btn" onClick={onLink} title="Lien de partage">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
          </button>
          <button className="wk-btn" onClick={onVis} title={VIS_LABEL[build.visibility]}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <span className="wk-btn-label">{VIS_LABEL[build.visibility]}</span>
          </button>
          <button className={`wk-btn ${isFav ? "wk-btn-active" : ""}`} onClick={onFav} title="Favori">
            <svg width="14" height="14" viewBox="0 0 24 24" fill={isFav ? "#e74c6f" : "none"} stroke={isFav ? "#e74c6f" : "currentColor"} strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 000-7.78z"/></svg>
          </button>
        </div>
      </div>

      {/* === TOAST === */}
      {toast && <div className="wk-toast">{toast}</div>}

      {/* === BONUS === */}
      <div className="wk-section">
        <div className="wk-section-title">Bonus</div>
        {bonuses.map((b, i) => (
          <label key={b.label} className={`wk-bonus-row ${b.active ? "wk-bonus-active" : ""}`}>
            <input type="checkbox" checked={b.active} onChange={() => toggleBonus(i)} />
            <span className="wk-bonus-label">{b.label}</span>
          </label>
        ))}
      </div>

      {/* === STATS === */}
      <div className="wk-section wk-stats-section">
        {categories.map(cat => (
          <div key={cat.id} className="wk-stat-group">
            <div className="wk-stat-group-title">{cat.label}</div>
            <div className="wk-stat-grid">
              {cat.items.map(s => {
                const val = stats[s.key] ?? 0;
                return (
                  <div key={s.key} className={`wk-stat-cell ${val > 0 ? "wk-stat-active" : ""}`}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`${ICON_CDN}/${s.icon}.png`}
                      alt={s.label}
                      className="wk-stat-icon"
                      onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }}
                    />
                    <span className="wk-stat-val">{val}</span>
                    <span className="wk-stat-label">{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* === DEBUG (dev) === */}
      {process.env.NODE_ENV === "development" && (
        <details className="wk-debug">
          <summary>Debug</summary>
          <pre>{JSON.stringify({ build, stats, bonuses }, null, 2)}</pre>
        </details>
      )}
    </aside>
  );
}

// ============================================================
// CSS — Fidele au style Wakfuli (dark theme, compact grid stats)
// ============================================================
const panelCSS = `
/* Panel principal */
.wk-panel {
  width: 280px;
  min-width: 280px;
  height: 100vh;
  background: #0f0e17;
  border-right: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
  color: #c4c4d4;
  font-size: 13px;
  scrollbar-width: thin;
  scrollbar-color: #2a2940 transparent;
}
.wk-panel::-webkit-scrollbar { width: 4px; }
.wk-panel::-webkit-scrollbar-thumb { background: #2a2940; border-radius: 2px; }

/* Header build */
.wk-header {
  padding: 14px 14px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.wk-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.wk-class-badge {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #1a1933;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.wk-class-badge img { width: 28px; height: 28px; }
.wk-build-name {
  font-size: 15px;
  font-weight: 700;
  color: #eeeef6;
  line-height: 1.2;
}
.wk-build-meta {
  font-size: 11px;
  color: #7a7a95;
  margin-top: 1px;
}

/* Boutons d'action — icones SVG style Wakfuli */
.wk-actions {
  display: flex;
  gap: 6px;
}
.wk-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 7px 0;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  background: #16152a;
  color: #8888a8;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 10px;
}
.wk-btn:hover {
  background: #1e1d38;
  border-color: rgba(255,255,255,0.14);
  color: #b8b8d0;
}
.wk-btn-active { color: #e74c6f !important; border-color: rgba(231,76,111,0.3); }
.wk-btn-label { font-size: 10px; }

/* Toast */
.wk-toast {
  margin: 0 14px;
  padding: 6px 10px;
  background: rgba(76,175,80,0.12);
  border: 1px solid rgba(76,175,80,0.25);
  border-radius: 6px;
  font-size: 11px;
  text-align: center;
  color: #81c784;
  animation: wk-fade 0.2s ease;
}
@keyframes wk-fade { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Sections */
.wk-section {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.wk-section-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6c5ce7;
  margin-bottom: 8px;
}

/* Bonus rows */
.wk-bonus-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.12s;
  margin-bottom: 2px;
}
.wk-bonus-row:hover { background: rgba(255,255,255,0.03); }
.wk-bonus-active { background: rgba(108,92,231,0.08); }
.wk-bonus-row input[type="checkbox"] {
  width: 14px;
  height: 14px;
  accent-color: #6c5ce7;
  cursor: pointer;
}
.wk-bonus-label {
  font-size: 12px;
  font-weight: 500;
}

/* Stats section */
.wk-stats-section {
  padding-bottom: 20px;
  flex: 1;
  border-bottom: none;
}
.wk-stat-group { margin-bottom: 10px; }
.wk-stat-group-title {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #5a5a75;
  margin-bottom: 6px;
  padding-left: 2px;
}

/* Grille compacte des stats — style Wakfuli */
.wk-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(78px, 1fr));
  gap: 3px;
}
.wk-stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 4px 5px;
  border-radius: 6px;
  background: #13122a;
  border: 1px solid rgba(255,255,255,0.03);
  transition: all 0.15s;
  gap: 2px;
}
.wk-stat-cell:hover { background: #1a1936; }
.wk-stat-active {
  border-color: rgba(108,92,231,0.2);
  background: rgba(108,92,231,0.06);
}
.wk-stat-icon {
  width: 20px;
  height: 20px;
  image-rendering: auto;
}
.wk-stat-val {
  font-size: 14px;
  font-weight: 700;
  color: #444460;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}
.wk-stat-active .wk-stat-val { color: #a89aec; }
.wk-stat-label {
  font-size: 9px;
  color: #55556e;
  text-align: center;
  line-height: 1.1;
}
.wk-stat-active .wk-stat-label { color: #7a7a95; }

/* Debug */
.wk-debug {
  padding: 8px 14px;
  font-size: 9px;
  opacity: 0.4;
}
.wk-debug pre {
  white-space: pre-wrap;
  font-size: 8px;
  margin-top: 4px;
  max-height: 200px;
  overflow: auto;
}
`;
