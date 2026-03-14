"use client";

import React, { useState, useCallback, useMemo } from "react";
import { useBuild } from "@/lib/BuildContext";
import { ClassSelector } from "@/components/builder/ClassSelector";

// ============================================================
// LeftPanel v3
// Sources:
//   - reference/wakfuli/assets/js/25c3dbf546a727d1.js (BONUSES_DATA)
//   - CDN: cdn.wakfuli.com/stats/{KEY}.webp
//   - CDN: cdn.wakfuli.com/bonuses/{tree|gem|mount}.webp
//   - CDN: cdn.wakfuli.com/breeds/{class}.webp
//   - BuildContext.tsx -> computeStats()
// ============================================================

interface PrimaryStat { key: string; label: string; color: string; }
const PRIMARY_STATS: PrimaryStat[] = [
  { key: "HP",    label: "PV", color: "text-hp" },
  { key: "AP",    label: "PA", color: "text-ap" },
  { key: "MP",    label: "PM", color: "text-mp" },
  { key: "WP",    label: "PW", color: "text-wp" },
  { key: "RANGE", label: "PO", color: "text-cyan-wakfuli" },
];

interface StatDef { key: string; label: string; suffix?: string; }
interface StatGroup { id: string; label: string; columns: number; stats: StatDef[]; }
const STAT_GROUPS: StatGroup[] = [
  {
    id: "combat", label: "Combat", columns: 4,
    stats: [
      { key: "DODGE",       label: "Esquive" },
      { key: "TACKLE",      label: "Tacle" },
      { key: "INIT",        label: "Initiative" },
      { key: "BLOCK",       label: "% Parade", suffix: "%" },
      { key: "WILLPOWER",   label: "Volont\u00e9" },
      { key: "WISDOM",      label: "Sagesse" },
      { key: "PROSPECTION", label: "Prospection" },
      { key: "FEROCITY",    label: "% Coup Crit." },
    ],
  },
  {
    id: "mastery", label: "Ma\u00eetrise", columns: 4,
    stats: [
      { key: "DMG_IN_PERCENT",  label: "% Dommages inflig\u00e9s" },
      { key: "HEAL_IN_PERCENT", label: "Ma\u00eetrise Soin" },
      { key: "CRITICAL_BONUS",  label: "Ma\u00eetrise Crit." },
      { key: "BACKSTAB_BONUS",  label: "Ma\u00eetrise Dos" },
      { key: "MELEE_DMG",       label: "Ma\u00eetrise M\u00eal\u00e9e" },
      { key: "RANGED_DMG",      label: "Ma\u00eetrise Dist." },
      { key: "BERSERK_DMG",     label: "Ma\u00eetrise Bers." },
    ],
  },
  {
    id: "resist", label: "R\u00e9sistance", columns: 4,
    stats: [
      { key: "RES_FIRE_PERCENT",  label: "R\u00e9s. Feu" },
      { key: "RES_WATER_PERCENT", label: "R\u00e9s. Eau" },
      { key: "RES_EARTH_PERCENT", label: "R\u00e9s. Terre" },
      { key: "RES_AIR_PERCENT",   label: "R\u00e9s. Air" },
      { key: "CRITICAL_RES",      label: "R\u00e9s. Critique" },
      { key: "RES_BACKSTAB",      label: "R\u00e9s. Dos" },
    ],
  },
];

const ELEMENT_COLORS: Record<string, string> = {
  RES_FIRE_PERCENT:  "drop-shadow(0 0 4px rgba(255,147,51,0.5))",
  RES_WATER_PERCENT: "drop-shadow(0 0 4px rgba(153,249,249,0.5))",
  RES_EARTH_PERCENT: "drop-shadow(0 0 4px rgba(196,221,30,0.5))",
  RES_AIR_PERCENT:   "drop-shadow(0 0 4px rgba(237,153,255,0.5))",
};

// --- Bonus exactement comme Wakfuli (chunk 25c3dbf546a727d1.js) ---
// id:1 icon:"tree" = Bonus de Guilde
// id:2 icon:"gem"  = Bonus de Havre-Monde
// id:3 icon:"mount"= Bonus de Monture
interface Bonus {
  id: number;
  label: string;
  icon: string; // tree | gem | mount -> cdn.wakfuli.com/bonuses/{icon}.webp
  active: boolean;
  stats: Record<string, number>;
}

const DEFAULT_BONUSES: Bonus[] = [
  {
    id: 1, label: "Bonus de Guilde", icon: "tree", active: false,
    stats: {
      HP: 55, DODGE: 20, TACKLE: 20, INIT: 10, WISDOM: 10, PROSPECTION: 10,
      DMG_IN_PERCENT: 8, HEAL_IN_PERCENT: 8,
      RES_FIRE_PERCENT: 5, RES_WATER_PERCENT: 5, RES_EARTH_PERCENT: 5, RES_AIR_PERCENT: 5,
    },
  },
  {
    id: 2, label: "Bonus de Havre-Monde", icon: "gem", active: false,
    stats: { HP: 10, WISDOM: 10, PROSPECTION: 10 },
  },
  {
    id: 3, label: "Bonus de Monture", icon: "mount", active: false,
    stats: { DMG_IN_PERCENT: 40 },
  },
];

const VIS_CYCLE: ("public" | "link-only" | "private")[] = ["public", "link-only", "private"];
const VIS_LABELS: Record<string, string> = { "public": "Public", "link-only": "Lien", "private": "Priv\u00e9" };
const VIS_COLORS: Record<string, string> = {
  "public": "rgb(100, 220, 41)", "link-only": "rgb(255, 153, 0)", "private": "rgb(255, 61, 71)",
};

export function LeftPanel() {
  const { build, stats, setName, setLevel } = useBuild();
  const [bonuses, setBonuses] = useState<Bonus[]>(() =>
    DEFAULT_BONUSES.map(b => ({ ...b, stats: { ...b.stats } }))
  );
  const [visibility, setVisibility] = useState<"public" | "link-only" | "private">("private");
  const [isFav, setIsFav] = useState(false);
  const [toast, setToast] = useState("");
  const [enchantEnabled, setEnchantEnabled] = useState(false);

  const allStatKeys = useMemo(() => {
    const keys = new Set<string>();
    PRIMARY_STATS.forEach(s => keys.add(s.key));
    STAT_GROUPS.forEach(g => g.stats.forEach(s => keys.add(s.key)));
    return keys;
  }, []);

  const totalStats = useMemo(() => {
    const merged: Record<string, number> = {};
    for (const k of allStatKeys) {
      merged[k] = (stats as Record<string, number>)[k] ?? 0;
    }
    for (const b of bonuses) {
      if (!b.active) continue;
      for (const [k, v] of Object.entries(b.stats)) {
        if (k in merged) merged[k] += v;
      }
    }
    return merged;
  }, [stats, bonuses, allStatKeys]);

  const totalMastery = useMemo(() => totalStats.DMG_IN_PERCENT ?? 0, [totalStats]);
  const totalResistance = useMemo(() => {
    const resKeys = ["RES_FIRE_PERCENT", "RES_WATER_PERCENT", "RES_EARTH_PERCENT", "RES_AIR_PERCENT"];
    const vals = resKeys.map(k => totalStats[k] ?? 0);
    return vals.length > 0 ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
  }, [totalStats]);

  const flash = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2000);
  }, []);

  const onCopy = useCallback(async () => {
    const txt = JSON.stringify({ name: build.name, level: build.level, class: build.characterClass, stats: totalStats }, null, 2);
    try { await navigator.clipboard.writeText(txt); flash("Build copi\u00e9 !"); } catch { flash("Erreur copie"); }
  }, [build, totalStats, flash]);

  const onLink = useCallback(() => {
    try {
      const payload = btoa(encodeURIComponent(JSON.stringify({ name: build.name, level: build.level, class: build.characterClass })));
      const url = `${window.location.origin}/builder?b=${payload}`;
      navigator.clipboard.writeText(url).then(() => flash("Lien copi\u00e9 !"), () => flash("Lien g\u00e9n\u00e9r\u00e9"));
    } catch { flash("Erreur lien"); }
  }, [build, flash]);

  const onVis = useCallback(() => {
    setVisibility(prev => VIS_CYCLE[(VIS_CYCLE.indexOf(prev) + 1) % VIS_CYCLE.length]);
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

  return (
    <aside className="h-full overflow-y-auto bg-bg-dark border-r border-border flex flex-col text-sm"
      style={{ scrollbarWidth: "thin", scrollbarColor: "#2a2e37 transparent" }}>

      {/* HEADER */}
      <div className="p-3 border-b border-border">
        <ClassSelector />
        <div className="mt-2">
          <input type="text" value={build.name} onChange={e => setName(e.target.value)}
            className="w-full bg-transparent text-primary font-bold text-base outline-none border-b border-transparent hover:border-border-light focus:border-cyan-wakfuli transition-colors truncate"
            placeholder="Nom du build..." spellCheck={false} />
        </div>
        {/* Boutons copie/lien/visibilite/favori */}
        <div className="flex gap-1.5 mt-2">
          <button onClick={onCopy} title="Copier le build"
            className="flex-1 flex items-center justify-center py-1.5 rounded-md bg-bg-lighter border border-border text-neutral-400 hover:text-primary hover:border-border-light transition-colors cursor-pointer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          <button onClick={onLink} title="Copier le lien"
            className="flex-1 flex items-center justify-center py-1.5 rounded-md bg-bg-lighter border border-border text-neutral-400 hover:text-primary hover:border-border-light transition-colors cursor-pointer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
          </button>
          <button onClick={onVis} title={VIS_LABELS[visibility]}
            className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md bg-bg-lighter border border-border hover:border-border-light transition-colors cursor-pointer text-xs font-medium"
            style={{ color: VIS_COLORS[visibility] }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none"><circle cx="12" cy="12" r="6"/></svg>
            <span>{VIS_LABELS[visibility]}</span>
          </button>
          <button onClick={onFav} title="Favori"
            className={`flex-1 flex items-center justify-center py-1.5 rounded-md bg-bg-lighter border transition-colors cursor-pointer ${isFav ? "border-pink-400/30 text-pink-400" : "border-border text-neutral-400 hover:text-primary hover:border-border-light"}`}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill={isFav ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 000-7.78z"/></svg>
          </button>
        </div>
      </div>

      {/* TOAST */}
      {toast && (
        <div className="mx-3 mt-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-md text-xs text-green-400 text-center animate-pulse">{toast}</div>
      )}

      {/* BONUS: Guilde / Havre-Monde / Monture — icones CDN wakfuli */}
      <div className="px-3 pt-2 pb-2 border-b border-border">
        <div className="flex items-center gap-1.5">
          {bonuses.map((b, i) => (
            <button key={b.id} onClick={() => toggleBonus(i)} title={b.label}
              className={`flex items-center gap-1.5 px-2 py-1.5 rounded text-[11px] font-medium transition-all cursor-pointer border ${
                b.active
                  ? "bg-cyan-wakfuli/10 border-cyan-wakfuli/30 text-cyan-wakfuli"
                  : "bg-bg-lighter border-border text-neutral-500 hover:text-primary hover:border-border-light"
              }`}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`https://cdn.wakfuli.com/bonuses/${b.icon}.webp`} alt={b.label}
                className="w-4 h-4" onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
              <span>{b.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* BOUTON ENCHANTEMENTS (toggle on/off) */}
      <div className="px-3 pt-2 pb-2 border-b border-border">
        <button onClick={() => setEnchantEnabled(prev => !prev)}
          className={`w-full flex items-center justify-center gap-2 py-1.5 rounded text-xs font-medium transition-all cursor-pointer border ${
            enchantEnabled
              ? "bg-cyan-wakfuli/10 border-cyan-wakfuli/30 text-cyan-wakfuli"
              : "bg-bg-lighter border-border text-neutral-500 hover:text-primary hover:border-border-light"
          }`}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
          </svg>
          <span>Enchantements {enchantEnabled ? "(actifs)" : "(inactifs)"}</span>
        </button>
      </div>

      {/* STATS PRIMAIRES */}
      <div className="px-3 pt-3 pb-1 border-b border-border">
        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-2">G&eacute;n&eacute;ral</div>
        <div className="flex items-center justify-between gap-1">
          {PRIMARY_STATS.map(s => {
            const val = totalStats[s.key] ?? 0;
            return (
              <div key={s.key} className="flex flex-col items-center flex-1 min-w-0">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`https://cdn.wakfuli.com/stats/${s.key}.webp`} alt={s.label} className="w-5 h-5 mb-0.5"
                  onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }} />
                <span className={`text-lg font-bold tabular-nums leading-none ${s.color}`}>{val}</span>
                <span className="text-[9px] text-neutral-500 mt-0.5">{s.label}</span>
              </div>
            );
          })}
        </div>
        <div className="flex items-center justify-end gap-4 mt-2 text-[10px] text-neutral-500">
          <span>Ma&icirc;trise totale: <span className="text-positive font-semibold">{totalMastery}</span></span>
          <span>R&eacute;sistance totale: <span className="text-positive font-semibold">{totalResistance}</span></span>
        </div>
      </div>

      {/* RESISTANCES ELEMENTAIRES */}
      <div className="px-3 pt-2 pb-1 border-b border-border">
        <div className="flex items-center justify-between gap-1">
          {[
            { key: "RES_FIRE_PERCENT",  label: "Feu",   colorClass: "text-fire" },
            { key: "RES_WATER_PERCENT", label: "Eau",   colorClass: "text-water" },
            { key: "RES_EARTH_PERCENT", label: "Terre", colorClass: "text-earth" },
            { key: "RES_AIR_PERCENT",   label: "Air",   colorClass: "text-air" },
          ].map(el => {
            const val = totalStats[el.key] ?? 0;
            return (
              <div key={el.key} className="flex items-center gap-1 flex-1 justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`https://cdn.wakfuli.com/stats/${el.key}.webp`} alt={el.label} className="w-4 h-4"
                  style={{ filter: ELEMENT_COLORS[el.key] }}
                  onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }} />
                <span className={`text-sm font-semibold tabular-nums ${val > 0 ? el.colorClass : "text-neutral-600"}`}>{val}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* GROUPES DE STATS */}
      <div className="px-3 pt-2 flex-1">
        {STAT_GROUPS.map(group => (
          <div key={group.id} className="mb-3">
            <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5">{group.label}</div>
            <div className="grid gap-x-1 gap-y-1" style={{ gridTemplateColumns: `repeat(${group.columns}, 1fr)` }}>
              {group.stats.map(s => {
                const val = totalStats[s.key] ?? 0;
                const hasVal = val !== 0;
                return (
                  <div key={s.key} className="flex flex-col items-center py-1.5 px-0.5 rounded transition-colors">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`https://cdn.wakfuli.com/stats/${s.key}.webp`} alt={s.label} className="w-5 h-5 mb-0.5"
                      style={{ filter: ELEMENT_COLORS[s.key] ?? "none" }}
                      onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }} />
                    <span className={`text-base font-bold tabular-nums leading-tight ${hasVal ? "text-primary" : "text-neutral-600"}`}>{val}{s.suffix ?? ""}</span>
                    <span className={`text-[8px] leading-tight text-center mt-0.5 ${hasVal ? "text-neutral-400" : "text-neutral-600"}`}>{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* SECONDAIRE */}
      <div className="px-3 pb-2 border-t border-border pt-2">
        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5">Secondaire</div>
        <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
          {[
            { key: "DMG_IN_PERCENT",  label: "Dommages inflig\u00e9s", suffix: "%" },
            { key: "HEAL_IN_PERCENT", label: "Soins r\u00e9alis\u00e9s", suffix: "%" },
            { key: "CRITICAL_BONUS",  label: "Ma\u00eetrise critique" },
            { key: "RES_BACKSTAB",    label: "R\u00e9sistance dos" },
            { key: "BACKSTAB_BONUS",  label: "Ma\u00eetrise dos" },
            { key: "CRITICAL_RES",    label: "R\u00e9sistance critique" },
            { key: "MELEE_DMG",       label: "Ma\u00eetrise m\u00eal\u00e9e" },
            { key: "RANGED_DMG",      label: "Ma\u00eetrise distance" },
            { key: "BERSERK_DMG",     label: "Ma\u00eetrise berserk" },
            { key: "ARMOR_GIVEN",     label: "Armure donn\u00e9e", suffix: "%" },
            { key: "ARMOR_RECEIVED",  label: "Armure re\u00e7ue", suffix: "%" },
            { key: "INDIRECT_DMG",    label: "Dommages indirects", suffix: "%" },
          ].map(s => {
            const val = totalStats[s.key] ?? 0;
            return (
              <div key={s.key} className="flex items-center gap-2 py-0.5">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`https://cdn.wakfuli.com/stats/${s.key}.webp`} alt={s.label} className="w-4 h-4 flex-shrink-0"
                  onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }} />
                <span className="text-xs text-neutral-400 truncate flex-1">{s.label}</span>
                <span className={`text-xs tabular-nums font-semibold ${val > 0 ? "text-positive" : val < 0 ? "text-negative" : "text-neutral-600"}`}>{val}{s.suffix ?? ""}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* DEBUG */}
      {process.env.NODE_ENV === "development" && (
        <details className="p-2 opacity-30 text-[9px]">
          <summary className="cursor-pointer">Debug</summary>
          <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap text-[8px]">
            {JSON.stringify({ name: build.name, level: build.level, class: build.characterClass, visibility, enchantEnabled, bonusesActive: bonuses.filter(b => b.active).map(b => b.label), totalStats }, null, 2)}
          </pre>
        </details>
      )}
    </aside>
  );
}
