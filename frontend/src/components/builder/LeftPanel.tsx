"use client";

import React, { useState, useCallback, useMemo } from "react";
import { useBuild } from "@/lib/BuildContext";
import { ClassSelector } from "@/components/builder/ClassSelector";

// ============================================================
// LeftPanel v4 – SVG inline, zero CDN
// Sources:
//   - reference/wakfuli/assets/js/25c3dbf546a727d1.js (BONUSES_DATA)
//   - BuildContext.tsx -> computeStats()
//   - Wakfu game: https://www.gamosaurus.com/jeux/wakfu/comprendre-les-caracteristiques-de-wakfu-le-guide-complet
// ============================================================

// ---- Icônes SVG inline pour les stats (remplace cdn.wakfuli.com/stats/) ----
// Chaque stat a un petit SVG 20x20 avec sa couleur thématique
function StatIcon({ statKey, size = 20 }: { statKey: string; size?: number }) {
  const icons: Record<string, { color: string; path: string }> = {
    HP:               { color: "#ff515b", path: "M10 4C8 2 4 2 4 6c0 5 6 9 6 9s6-4 6-9c0-4-4-4-6-2z" },
    AP:               { color: "#19c1ef", path: "M10 2l2.5 5H17l-4 3.5 1.5 5.5L10 13l-4.5 3 1.5-5.5L3 7h4.5z" },
    MP:               { color: "#afd34c", path: "M4 16l3-5 3 3 3-7 3 9H4z" },
    WP:               { color: "#e1b900", path: "M10 3a7 7 0 100 14 7 7 0 000-14zm0 2a5 5 0 110 10 5 5 0 010-10z" },
    RANGE:            { color: "#71f2ff", path: "M3 10h14M10 3v14M6 6l8 8M14 6l-8 8" },
    DODGE:            { color: "#8899aa", path: "M7 17c-2-3-3-5-1-8 1-2 3-3 5-3s4 1 5 3l-2 1c-1-1-2-2-3-2s-2 1-3 2c-1 2 0 4 1 6z" },
    TACKLE:           { color: "#8899aa", path: "M10 3v5l4 3-4 3v5l-6-8z" },
    INIT:             { color: "#8899aa", path: "M12 2L4 14h6l-2 6 8-12h-6z" },
    BLOCK:            { color: "#8899aa", path: "M10 2L3 6v5c0 4 3 7 7 9 4-2 7-5 7-9V6z" },
    WILLPOWER:        { color: "#8899aa", path: "M10 2c-3 0-6 3-6 7 0 5 6 9 6 9s6-4 6-9c0-4-3-7-6-7zm0 3a4 4 0 110 8 4 4 0 010-8z" },
    WISDOM:           { color: "#8899aa", path: "M10 2a8 8 0 100 16 8 8 0 000-16zm0 3c1 0 2 1 2 2l-1 3h-2L8 7c0-1 1-2 2-2zm-1 8h2v2H9z" },
    PROSPECTION:      { color: "#8899aa", path: "M8 2l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" },
    FEROCITY:         { color: "#ff515b", path: "M10 1l2 6h6l-5 4 2 6-5-4-5 4 2-6-5-4h6z" },
    DMG_IN_PERCENT:   { color: "#64dc29", path: "M5 3l5 7 5-7v14l-5-4-5 4z" },
    HEAL_IN_PERCENT:  { color: "#64dc29", path: "M8 4h4v4h4v4h-4v4H8v-4H4V8h4z" },
    CRITICAL_BONUS:   { color: "#64dc29", path: "M10 1l2 6h6l-5 4 2 6-5-4-5 4 2-6-5-4h6z" },
    BACKSTAB_BONUS:   { color: "#64dc29", path: "M10 2L5 10h3v8h4v-8h3z" },
    MELEE_DMG:        { color: "#64dc29", path: "M14 2l-8 8 2 2 8-8zM4 14l-2 4 4-2z" },
    RANGED_DMG:       { color: "#64dc29", path: "M3 10h10M13 7l4 3-4 3" },
    BERSERK_DMG:      { color: "#64dc29", path: "M10 2l3 5 5 1-3 4 1 5-5-2-5 2 1-5-3-4 5-1z" },
    RES_FIRE_PERCENT: { color: "#ff9333", path: "M10 2C8 6 5 8 5 12a5 5 0 0010 0c0-4-3-6-5-10z" },
    RES_WATER_PERCENT:{ color: "#99f9f9", path: "M10 2C8 6 5 9 5 12a5 5 0 0010 0c0-3-3-6-5-10z" },
    RES_EARTH_PERCENT:{ color: "#c4dd1e", path: "M3 14l3-5 4 3 4-7 3 9H3z" },
    RES_AIR_PERCENT:  { color: "#ed99ff", path: "M4 12c2-1 4-4 6-4s4 3 6 4M4 8c2-1 4-4 6-4s4 3 6 4" },
    CRITICAL_RES:     { color: "#ff4444", path: "M10 2L3 6v5c0 4 3 7 7 9 4-2 7-5 7-9V6zM10 7l1 3h3l-2 2 1 3-3-2-3 2 1-3-2-2h3z" },
    RES_BACKSTAB:     { color: "#ff4444", path: "M10 2L3 6v5c0 4 3 7 7 9 4-2 7-5 7-9V6z" },
    ARMOR_GIVEN:      { color: "#8899aa", path: "M10 2L3 6v5c0 4 3 7 7 9 4-2 7-5 7-9V6z" },
    ARMOR_RECEIVED:   { color: "#8899aa", path: "M10 2L3 6v5c0 4 3 7 7 9 4-2 7-5 7-9V6z" },
    INDIRECT_DMG:     { color: "#8899aa", path: "M12 2L4 14h6l-2 6 8-12h-6z" },
  };
  const icon = icons[statKey];
  if (!icon) return <span className="inline-block rounded-full bg-neutral-700" style={{ width: size, height: size }} />;
  const isStroke = statKey === "RANGE" || statKey === "RANGED_DMG" || statKey === "RES_AIR_PERCENT";
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      {isStroke
        ? <path d={icon.path} stroke={icon.color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
        : <path d={icon.path} fill={icon.color} />
      }
    </svg>
  );
}

// ---- Icônes SVG inline pour les bonus ----
function BonusIcon({ type, size = 18 }: { type: "tree" | "gem" | "mount"; size?: number }) {
  const paths: Record<string, { color: string; d: string; stroke?: boolean }> = {
    tree:  { color: "#64dc29", d: "M9 18V11H5l4-5H6l4-5 4 5h-3l4 5H11v7z" },
    gem:   { color: "#71f2ff", d: "M4 8l5-6h2l5 6-6 10z" },
    mount: { color: "#e1b900", d: "M3 14c0-3 2-5 4-6l1 2c2-3 5-3 6 0l1-2c2 1 4 3 4 6H3zM6 14v3M14 14v3M10 8V6M8 6h4" },
  };
  const p = paths[type];
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d={p.d} fill={p.stroke ? "none" : p.color} stroke={p.stroke ? p.color : "none"} strokeWidth={p.stroke ? "1.5" : "0"} />
    </svg>
  );
}

// ---- Données ----

interface PrimaryStat { key: string; label: string; colorClass: string; }
const PRIMARY_STATS: PrimaryStat[] = [
  { key: "HP",    label: "PV", colorClass: "text-hp" },
  { key: "AP",    label: "PA", colorClass: "text-ap" },
  { key: "MP",    label: "PM", colorClass: "text-mp" },
  { key: "WP",    label: "PW", colorClass: "text-wp" },
  { key: "RANGE", label: "PO", colorClass: "text-cyan-wakfuli" },
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
      { key: "FEROCITY",    label: "% Coup Crit.", suffix: "%" },
    ],
  },
  {
    id: "mastery", label: "Ma\u00eetrise", columns: 4,
    stats: [
      { key: "DMG_IN_PERCENT",  label: "% Dommages" },
      { key: "HEAL_IN_PERCENT", label: "Ma\u00eet. Soin" },
      { key: "CRITICAL_BONUS",  label: "Ma\u00eet. Crit." },
      { key: "BACKSTAB_BONUS",  label: "Ma\u00eet. Dos" },
      { key: "MELEE_DMG",       label: "Ma\u00eet. M\u00eal\u00e9e" },
      { key: "RANGED_DMG",      label: "Ma\u00eet. Dist." },
      { key: "BERSERK_DMG",     label: "Ma\u00eet. Bers." },
    ],
  },
  {
    id: "resist", label: "R\u00e9sistance", columns: 4,
    stats: [
      { key: "RES_FIRE_PERCENT",  label: "R\u00e9s. Feu" },
      { key: "RES_WATER_PERCENT", label: "R\u00e9s. Eau" },
      { key: "RES_EARTH_PERCENT", label: "R\u00e9s. Terre" },
      { key: "RES_AIR_PERCENT",   label: "R\u00e9s. Air" },
      { key: "CRITICAL_RES",      label: "R\u00e9s. Crit." },
      { key: "RES_BACKSTAB",      label: "R\u00e9s. Dos" },
    ],
  },
];

// Bonus exactement comme Wakfuli chunk 25c3dbf546a727d1.js
// id:1 icon:"tree" = Guilde | id:2 icon:"gem" = Havre-Monde | id:3 icon:"mount" = Monture
interface Bonus {
  id: number;
  label: string;
  shortLabel: string;
  icon: "tree" | "gem" | "mount";
  iconSize: number;
  active: boolean;
  stats: Record<string, number>;
}

const DEFAULT_BONUSES: Bonus[] = [
  {
    id: 1, label: "Bonus de Guilde", shortLabel: "Guilde", icon: "tree", iconSize: 20, active: false,
    stats: { HP: 55, DODGE: 20, TACKLE: 20, INIT: 10, WISDOM: 10, PROSPECTION: 10, DMG_IN_PERCENT: 8, HEAL_IN_PERCENT: 8, RES_FIRE_PERCENT: 5, RES_WATER_PERCENT: 5, RES_EARTH_PERCENT: 5, RES_AIR_PERCENT: 5 },
  },
  {
    id: 2, label: "Bonus de Havre-Monde", shortLabel: "Havre", icon: "gem", iconSize: 22, active: false,
    stats: { HP: 10, WISDOM: 10, PROSPECTION: 10 },
  },
  {
    id: 3, label: "Bonus de Monture", shortLabel: "Monture", icon: "mount", iconSize: 22, active: false,
    stats: { DMG_IN_PERCENT: 40 },
  },
];

const VIS_CYCLE: ("public" | "link-only" | "private")[] = ["public", "link-only", "private"];
const VIS_LABELS: Record<string, string> = { "public": "Public", "link-only": "Lien", "private": "Priv\u00e9" };
const VIS_COLORS: Record<string, string> = { "public": "#64dc29", "link-only": "#ff9333", "private": "#ff515b" };

// ---- Composant ----

export function LeftPanel() {
  const { build, stats, setName } = useBuild();
  const [bonuses, setBonuses] = useState<Bonus[]>(() =>
    DEFAULT_BONUSES.map(b => ({ ...b, stats: { ...b.stats } }))
  );
  const [visibility, setVisibility] = useState<"public" | "link-only" | "private">("private");
  const [isFav, setIsFav] = useState(false);
  const [toast, setToast] = useState("");
  const [enchantEnabled, setEnchantEnabled] = useState(false);

  // Collecter toutes les clés de stats
  const allStatKeys = useMemo(() => {
    const keys = new Set<string>();
    PRIMARY_STATS.forEach(s => keys.add(s.key));
    STAT_GROUPS.forEach(g => g.stats.forEach(s => keys.add(s.key)));
    ["ARMOR_GIVEN", "ARMOR_RECEIVED", "INDIRECT_DMG"].forEach(k => keys.add(k));
    return keys;
  }, []);

  // Fusionner stats du BuildContext + bonus actifs
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

      {/* ═══════════ ZONE 1 : HEADER (Classe + Nom + Actions) ═══════════ */}
      <div className="p-3 border-b border-border">
        <ClassSelector />
        <div className="mt-2">
          <input type="text" value={build.name} onChange={e => setName(e.target.value)}
            className="w-full bg-transparent text-primary font-bold text-base outline-none border-b border-transparent hover:border-border-light focus:border-cyan-wakfuli transition-colors truncate"
            placeholder="Nom du build..." spellCheck={false} />
        </div>
        <div className="flex gap-1.5 mt-2">
          <button onClick={onCopy} title="Copier le build (JSON)"
            className="flex-1 flex items-center justify-center py-1.5 rounded-md bg-bg-lighter border border-border text-neutral-400 hover:text-primary hover:border-border-light transition-colors cursor-pointer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          <button onClick={onLink} title="Copier le lien de partage"
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

      {/* ═══════════ ZONE 2 : BONUS (Guilde / Havre-Monde / Monture) ═══════════ */}
      <div className="px-3 pt-2 pb-2 border-b border-border">
        <div className="flex items-center gap-1.5">
          {bonuses.map((b, i) => (
            <button key={b.id} onClick={() => toggleBonus(i)} title={b.label}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] font-medium transition-all cursor-pointer border ${
                b.active
                  ? "bg-cyan-wakfuli/10 border-cyan-wakfuli/30 text-cyan-wakfuli"
                  : "bg-bg-lighter border-border text-neutral-500 hover:text-primary hover:border-border-light"
              }`}>
              <span className="w-5 h-5 flex items-center justify-center flex-shrink-0"><img src={`/icons/bonuses/${b.icon}.png`} alt={b.label} width={b.iconSize} height={b.iconSize} className="object-contain" /></span>
              <span className="hidden xl:inline">{b.shortLabel}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ═══════════ ZONE 3 : TOGGLE ENCHANTEMENTS ═══════════ */}
      <div className="px-3 pt-2 pb-2 border-b border-border">
        <button onClick={() => setEnchantEnabled(prev => !prev)}
          className={`w-full flex items-center justify-center gap-2 py-1.5 rounded text-xs font-medium transition-all cursor-pointer border ${
            enchantEnabled
              ? "bg-cyan-wakfuli/10 border-cyan-wakfuli/30 text-cyan-wakfuli"
              : "bg-bg-lighter border-border text-neutral-500 hover:text-primary hover:border-border-light"
          }`}>
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 2L2 7l8 4 8-4-8-5z" fill={enchantEnabled ? "#71f2ff" : "#8899aa"} opacity="0.8" />
            <path d="M2 13l8 4 8-4" stroke={enchantEnabled ? "#71f2ff" : "#8899aa"} strokeWidth="1.5" strokeLinecap="round" fill="none" />
            <path d="M2 10l8 4 8-4" stroke={enchantEnabled ? "#71f2ff" : "#8899aa"} strokeWidth="1.5" strokeLinecap="round" fill="none" />
          </svg>
          <span>Enchantements {enchantEnabled ? "(actifs)" : "(inactifs)"}</span>
        </button>
      </div>

      {/* ═══════════ ZONE 4 : STATS PRIMAIRES ═══════════ */}
      <div className="px-3 pt-3 pb-1 border-b border-border">
        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-2">G&eacute;n&eacute;ral</div>
        <div className="flex items-center justify-between gap-1">
          {PRIMARY_STATS.map(s => {
            const val = totalStats[s.key] ?? 0;
            return (
              <div key={s.key} className="flex flex-col items-center flex-1 min-w-0">
                <StatIcon statKey={s.key} size={20} />
                <span className={`text-lg font-bold tabular-nums leading-none mt-0.5 ${s.colorClass}`}>{val}</span>
                <span className="text-[9px] text-neutral-500 mt-0.5">{s.label}</span>
              </div>
            );
          })}
        </div>
        <div className="flex items-center justify-end gap-4 mt-2 text-[10px] text-neutral-500">
          <span>Ma&icirc;trise: <span className="text-positive font-semibold">{totalMastery}</span></span>
          <span>R&eacute;sistance: <span className="text-positive font-semibold">{totalResistance}</span></span>
        </div>
      </div>

      {/* ═══════════ ZONE 5 : RÉSISTANCES ÉLÉMENTAIRES ═══════════ */}
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
                <StatIcon statKey={el.key} size={16} />
                <span className={`text-sm font-semibold tabular-nums ${val > 0 ? el.colorClass : val < 0 ? "text-negative" : "text-neutral-600"}`}>{val}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ═══════════ ZONE 6 : GROUPES DE STATS ═══════════ */}
      <div className="px-3 pt-2 flex-1">
        {STAT_GROUPS.map(group => (
          <div key={group.id} className="mb-3">
            <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5">{group.label}</div>
            <div className="grid gap-x-1 gap-y-1" style={{ gridTemplateColumns: `repeat(${group.columns}, 1fr)` }}>
              {group.stats.map(s => {
                const val = totalStats[s.key] ?? 0;
                const hasVal = val !== 0;
                return (
                  <div key={s.key} className="flex flex-col items-center py-1.5 px-0.5 rounded transition-colors hover:bg-bg-lighter/50" title={s.label}>
                    <StatIcon statKey={s.key} size={20} />
                    <span className={`text-base font-bold tabular-nums leading-tight mt-0.5 ${hasVal ? (val > 0 ? "text-primary" : "text-negative") : "text-neutral-600"}`}>{val}{s.suffix ?? ""}</span>
                    <span className={`text-[8px] leading-tight text-center mt-0.5 ${hasVal ? "text-neutral-400" : "text-neutral-600"}`}>{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* ═══════════ ZONE 7 : SECONDAIRE ═══════════ */}
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
                <StatIcon statKey={s.key} size={16} />
                <span className="text-xs text-neutral-400 truncate flex-1">{s.label}</span>
                <span className={`text-xs tabular-nums font-semibold ${val > 0 ? "text-positive" : val < 0 ? "text-negative" : "text-neutral-600"}`}>{val}{s.suffix ?? ""}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ═══════════ DEBUG (dev uniquement) ═══════════ */}
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





