"use client";

import React, { useState, useCallback, useMemo } from "react";
import { useBuild } from "@/lib/BuildContext";

// ============================================================
// LeftPanel — Panneau gauche du builder
// Sources de reference:
//   - reference/wakfuli/pages/builder_public.html (structure HTML)
//   - reference/wakfuli_all.css (couleurs + variables CSS Wakfuli)
//   - CDN icons: cdn.wakfuli.com/stats/{STAT_NAME}.webp (PROJECT_MEMORY)
//   - CDN breeds: cdn.wakfuli.com/breeds/{classname}.webp (PROJECT_MEMORY)
//   - Stats: BuildContext.tsx -> computeStats() (35 stats)
// ============================================================

// --- Definition des stats affichees, groupees comme Wakfuli ---
interface StatDef {
  key: string;
  label: string;
  category: "general" | "combat" | "mastery" | "resist";
}

const STAT_DEFS: StatDef[] = [
  // General
  { key: "HP",               label: "PV",             category: "general" },
  { key: "AP",               label: "PA",             category: "general" },
  { key: "MP",               label: "PM",             category: "general" },
  { key: "WP",               label: "PW",             category: "general" },
  { key: "RANGE",            label: "PO",             category: "general" },
  // Combat
  { key: "DODGE",            label: "Esquive",        category: "combat" },
  { key: "TACKLE",           label: "Tacle",          category: "combat" },
  { key: "INIT",             label: "Initiative",     category: "combat" },
  { key: "BLOCK",            label: "Parade",         category: "combat" },
  { key: "WILLPOWER",        label: "Volonté",        category: "combat" },
  { key: "WISDOM",           label: "Sagesse",        category: "combat" },
  { key: "PROSPECTION",      label: "Prospection",    category: "combat" },
  { key: "FEROCITY",         label: "Férocité",       category: "combat" },
  // Maitrise
  { key: "DMG_IN_PERCENT",   label: "Maîtrise Élem.", category: "mastery" },
  { key: "HEAL_IN_PERCENT",  label: "Maîtrise Soin",  category: "mastery" },
  { key: "CRITICAL_BONUS",   label: "Maîtrise Crit.", category: "mastery" },
  { key: "BACKSTAB_BONUS",   label: "Maîtrise Dos",   category: "mastery" },
  { key: "MELEE_DMG",        label: "Maîtrise Mêlée", category: "mastery" },
  { key: "RANGED_DMG",       label: "Maîtrise Dist.", category: "mastery" },
  { key: "BERSERK_DMG",      label: "Maîtrise Bers.", category: "mastery" },
  // Resistance
  { key: "RES_FIRE_PERCENT",   label: "Rés. Feu",     category: "resist" },
  { key: "RES_WATER_PERCENT",  label: "Rés. Eau",     category: "resist" },
  { key: "RES_EARTH_PERCENT",  label: "Rés. Terre",   category: "resist" },
  { key: "RES_AIR_PERCENT",    label: "Rés. Air",     category: "resist" },
  { key: "CRITICAL_RES",       label: "Rés. Critique", category: "resist" },
  { key: "RES_BACKSTAB",       label: "Rés. Dos",      category: "resist" },
];

const CATEGORY_LABELS: Record<string, string> = {
  general: "Général",
  combat: "Combat",
  mastery: "Maîtrise",
  resist: "Résistance",
};

// Map stat key -> icon filename sur cdn.wakfuli.com/stats/
// Verifie dans PROJECT_MEMORY: cdn.wakfuli.com/stats/{STAT_NAME}.webp (WP pas WAKFU_POINT)
const STAT_ICON_MAP: Record<string, string> = {
  HP: "HP", AP: "AP", MP: "MP", WP: "WP", RANGE: "RANGE",
  DODGE: "DODGE", TACKLE: "TACKLE", INIT: "INIT", BLOCK: "BLOCK",
  WILLPOWER: "WILLPOWER", WISDOM: "WISDOM", PROSPECTION: "PROSPECTION",
  FEROCITY: "FEROCITY",
  DMG_IN_PERCENT: "DMG_IN_PERCENT", HEAL_IN_PERCENT: "HEAL_IN_PERCENT",
  CRITICAL_BONUS: "CRITICAL_BONUS", BACKSTAB_BONUS: "BACKSTAB_BONUS",
  MELEE_DMG: "MELEE_DMG", RANGED_DMG: "RANGED_DMG", BERSERK_DMG: "BERSERK_DMG",
  RES_FIRE_PERCENT: "RES_FIRE_PERCENT", RES_WATER_PERCENT: "RES_WATER_PERCENT",
  RES_EARTH_PERCENT: "RES_EARTH_PERCENT", RES_AIR_PERCENT: "RES_AIR_PERCENT",
  CRITICAL_RES: "CRITICAL_RES", RES_BACKSTAB: "RES_BACKSTAB",
};

// --- Bonus Wakfuli (source: chunk 25c3dbf546a727d1.js) ---
interface Bonus {
  label: string;
  active: boolean;
  stats: Record<string, number>;
}

const DEFAULT_BONUSES: Bonus[] = [
  {
    label: "Arbre",
    active: false,
    stats: { HP: 55, DODGE: 20, TACKLE: 20, INIT: 10, WISDOM: 10, PROSPECTION: 10, DMG_IN_PERCENT: 8, HEAL_IN_PERCENT: 8, RES_FIRE_PERCENT: 5, RES_WATER_PERCENT: 5, RES_EARTH_PERCENT: 5, RES_AIR_PERCENT: 5 },
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
const VIS_LABELS: Record<string, string> = { "public": "Public", "link-only": "Lien", "private": "Privé" };
const VIS_COLORS: Record<string, string> = {
  "public": "rgb(100, 220, 41)",
  "link-only": "rgb(255, 153, 0)",
  "private": "rgb(255, 61, 71)",
};

// ============================================================
// COMPOSANT — export nomme pour { LeftPanel }
// ============================================================
export function LeftPanel() {
  // Consomme le BuildContext pour les stats reelles
  const { build, stats, setName, setLevel } = useBuild();

  const [bonuses, setBonuses] = useState<Bonus[]>(() =>
    DEFAULT_BONUSES.map(b => ({ ...b, stats: { ...b.stats } }))
  );
  const [visibility, setVisibility] = useState<"public" | "link-only" | "private">("public");
  const [isFav, setIsFav] = useState(false);
  const [toast, setToast] = useState("");

  // Stats totales = stats du BuildContext + bonus actifs
  const totalStats = useMemo(() => {
    const merged: Record<string, number> = {};
    // Commencer par les stats du contexte (items equipes)
    for (const s of STAT_DEFS) {
      merged[s.key] = (stats as Record<string, number>)[s.key] ?? 0;
    }
    // Ajouter les bonus actifs
    for (const b of bonuses) {
      if (!b.active) continue;
      for (const [k, v] of Object.entries(b.stats)) {
        if (k in merged) {
          merged[k] = (merged[k] ?? 0) + (v ?? 0);
        }
      }
    }
    return merged;
  }, [stats, bonuses]);

  const flash = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2000);
  }, []);

  // --- Actions ---
  const onCopy = useCallback(async () => {
    const txt = JSON.stringify({ name: build.name, level: build.level, class: build.characterClass, stats: totalStats }, null, 2);
    try {
      await navigator.clipboard.writeText(txt);
      flash("Build copié !");
    } catch { flash("Erreur copie"); }
  }, [build, totalStats, flash]);

  const onLink = useCallback(() => {
    try {
      const payload = btoa(encodeURIComponent(JSON.stringify({ name: build.name, level: build.level, class: build.characterClass })));
      const url = `${window.location.origin}/builder?b=${payload}`;
      navigator.clipboard.writeText(url).then(() => flash("Lien copié !"), () => flash("Lien généré"));
    } catch { flash("Erreur lien"); }
  }, [build, flash]);

  const onVis = useCallback(() => {
    setVisibility(prev => {
      const i = VIS_CYCLE.indexOf(prev);
      return VIS_CYCLE[(i + 1) % VIS_CYCLE.length];
    });
  }, []);

  const onFav = useCallback(() => {
    setIsFav(prev => {
      const next = !prev;
      try {
        const raw = localStorage.getItem("wk_fav");
        let list: string[] = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(list)) list = [];
        list = next ? [...new Set([...list, build.name])] : list.filter(x => x !== build.name);
        localStorage.setItem("wk_fav", JSON.stringify(list));
      } catch { /* noop */ }
      return next;
    });
  }, [build.name]);

  const toggleBonus = useCallback((i: number) => {
    setBonuses(prev => prev.map((b, j) => j === i ? { ...b, active: !b.active } : b));
  }, []);

  // Grouper les stats par categorie
  const categories = useMemo(() => {
    const cats: { id: string; label: string; items: StatDef[] }[] = [];
    const seen = new Set<string>();
    for (const s of STAT_DEFS) {
      if (!seen.has(s.category)) {
        seen.add(s.category);
        cats.push({ id: s.category, label: CATEGORY_LABELS[s.category] ?? s.category, items: [] });
      }
      cats.find(c => c.id === s.category)!.items.push(s);
    }
    return cats;
  }, []);

  return (
    <aside className="h-full overflow-y-auto bg-bg-dark border-r border-border flex flex-col text-sm"
           style={{ scrollbarWidth: "thin", scrollbarColor: "#2a2e37 transparent" }}>

      {/* === HEADER === */}
      <div className="p-3 border-b border-border">
        {/* Classe + nom + niveau */}
        <div className="flex items-center gap-3 mb-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={`https://cdn.wakfuli.com/breeds/${build.characterClass}.webp`}
            alt={build.characterClass}
            className="w-10 h-10 rounded-lg bg-bg-lighter flex-shrink-0"
            onError={e => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
          <div className="flex-1 min-w-0">
            <input
              type="text"
              value={build.name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-transparent text-primary font-bold text-base outline-none border-b border-transparent hover:border-border-light focus:border-cyan-wakfuli transition-colors truncate"
              spellCheck={false}
            />
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-neutral-400 capitalize text-xs">{build.characterClass}</span>
              <span className="text-neutral-400 text-xs">·</span>
              <span className="text-xs text-neutral-400">Niv.</span>
              <input
                type="number"
                value={build.level}
                onChange={e => setLevel(Number(e.target.value))}
                min={1}
                max={230}
                className="w-10 bg-transparent text-primary text-xs font-semibold outline-none border-b border-transparent hover:border-border-light focus:border-cyan-wakfuli text-center"
              />
            </div>
          </div>
        </div>

        {/* Boutons d'action */}
        <div className="flex gap-1.5">
          <button
            onClick={onCopy}
            title="Copier le build"
            className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md bg-bg-lighter border border-border text-neutral-400 hover:text-primary hover:border-border-light transition-colors cursor-pointer"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          <button
            onClick={onLink}
            title="Copier le lien"
            className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md bg-bg-lighter border border-border text-neutral-400 hover:text-primary hover:border-border-light transition-colors cursor-pointer"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
          </button>
          <button
            onClick={onVis}
            title={VIS_LABELS[visibility]}
            className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md bg-bg-lighter border border-border hover:border-border-light transition-colors cursor-pointer text-xs font-medium"
            style={{ color: VIS_COLORS[visibility] }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <span>{VIS_LABELS[visibility]}</span>
          </button>
          <button
            onClick={onFav}
            title="Favori"
            className={`flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md bg-bg-lighter border transition-colors cursor-pointer ${isFav ? "border-pink-400/30 text-pink-400" : "border-border text-neutral-400 hover:text-primary hover:border-border-light"}`}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill={isFav ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 000-7.78z"/></svg>
          </button>
        </div>
      </div>

      {/* === TOAST === */}
      {toast && (
        <div className="mx-3 mt-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-md text-xs text-green-400 text-center animate-pulse">
          {toast}
        </div>
      )}

      {/* === BONUS === */}
      <div className="p-3 border-b border-border">
        <div className="text-[10px] font-bold uppercase tracking-widest text-cyan-wakfuli mb-2">Bonus</div>
        {bonuses.map((b, i) => (
          <label
            key={b.label}
            className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-colors mb-0.5 ${b.active ? "bg-cyan-wakfuli/5" : "hover:bg-bg-lighter"}`}
          >
            <input
              type="checkbox"
              checked={b.active}
              onChange={() => toggleBonus(i)}
              className="w-3.5 h-3.5 rounded accent-cyan-wakfuli cursor-pointer"
            />
            <span className="text-xs font-medium">{b.label}</span>
            {b.active && (
              <span className="ml-auto text-[10px] text-cyan-wakfuli/60">
                +{Object.values(b.stats).reduce((a, v) => a + v, 0)}
              </span>
            )}
          </label>
        ))}
      </div>

      {/* === STATS === */}
      <div className="p-3 flex-1">
        {categories.map(cat => (
          <div key={cat.id} className="mb-3">
            <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5">{cat.label}</div>
            <div className="grid gap-1" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(70px, 1fr))" }}>
              {cat.items.map(s => {
                const val = totalStats[s.key] ?? 0;
                const hasValue = val !== 0;
                return (
                  <div
                    key={s.key}
                    className={`flex flex-col items-center p-1.5 rounded-md border transition-colors ${hasValue ? "bg-cyan-wakfuli/5 border-cyan-wakfuli/10" : "bg-bg-dark border-border/50"}`}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`https://cdn.wakfuli.com/stats/${STAT_ICON_MAP[s.key] ?? s.key}.webp`}
                      alt={s.label}
                      className="w-5 h-5"
                      onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }}
                    />
                    <span className={`text-sm font-bold tabular-nums leading-tight ${hasValue ? "text-cyan-wakfuli" : "text-neutral-600"}`}>
                      {val}
                    </span>
                    <span className={`text-[9px] leading-tight text-center ${hasValue ? "text-neutral-400" : "text-neutral-600"}`}>
                      {s.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* === DEBUG (dev only) === */}
      {process.env.NODE_ENV === "development" && (
        <details className="p-2 opacity-30 text-[9px]">
          <summary className="cursor-pointer">Debug</summary>
          <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap text-[8px]">
            {JSON.stringify({ name: build.name, level: build.level, class: build.characterClass, visibility, bonusesActive: bonuses.filter(b => b.active).map(b => b.label), totalStats }, null, 2)}
          </pre>
        </details>
      )}
    </aside>
  );
}