"use client";

import React, { useState, useCallback, useMemo } from "react";

// ============================================================
// Types — basés sur les vraies caractéristiques Wakfu
// Source: https://wakfu.wiki.gg/wiki/Characteristic
// Icônes: https://github.com/Vertylo/wakassets/tree/main/characteristics
// ============================================================
interface StatValues {
  HP: number;
  AP: number;
  MP: number;
  WP: number;
  DODGE: number;
  TACKLE: number;
  INIT: number;
  WISDOM: number;
  PROSPECTION: number;
  BLOCK: number;
  WILLPOWER: number;
  RANGE: number;
  DMG_IN_PERCENT: number;
  HEAL_IN_PERCENT: number;
  RES_IN_PERCENT: number;
  CRITICAL_BONUS: number;
  CRITICAL_RES: number;
  BACKSTAB_BONUS: number;
  RES_BACKSTAB: number;
  MELEE_DMG: number;
  RANGED_DMG: number;
  BERSERK_DMG: number;
  INDIRECT_DMG: number;
}

interface Bonus {
  label: string;
  active: boolean;
  stats: Partial<StatValues>;
}

interface BuildState {
  name: string;
  level: number;
  characterClass: string;
  visibility: "public" | "link-only" | "private";
}

// ============================================================
// CDN des icônes — Vertylo/wakassets via GitHub Pages
// Pattern: https://vertylo.github.io/wakassets/characteristics/{KEY}.png
// ============================================================
const ICON_BASE = "https://vertylo.github.io/wakassets/characteristics";

// ============================================================
// Safe defaults — toutes les stats a 0
// ============================================================
const EMPTY_STATS: StatValues = {
  HP: 0,
  AP: 0,
  MP: 0,
  WP: 0,
  DODGE: 0,
  TACKLE: 0,
  INIT: 0,
  WISDOM: 0,
  PROSPECTION: 0,
  BLOCK: 0,
  WILLPOWER: 0,
  RANGE: 0,
  DMG_IN_PERCENT: 0,
  HEAL_IN_PERCENT: 0,
  RES_IN_PERCENT: 0,
  CRITICAL_BONUS: 0,
  CRITICAL_RES: 0,
  BACKSTAB_BONUS: 0,
  RES_BACKSTAB: 0,
  MELEE_DMG: 0,
  RANGED_DMG: 0,
  BERSERK_DMG: 0,
  INDIRECT_DMG: 0,
};

// ============================================================
// Labels francophones pour l'affichage
// ============================================================
const STAT_LABELS: Record<keyof StatValues, string> = {
  HP: "Points de Vie",
  AP: "PA",
  MP: "PM",
  WP: "PW",
  DODGE: "Esquive",
  TACKLE: "Tacle",
  INIT: "Initiative",
  WISDOM: "Sagesse",
  PROSPECTION: "Prospection",
  BLOCK: "Parade",
  WILLPOWER: "Volonte",
  RANGE: "Portee",
  DMG_IN_PERCENT: "% Degats infliges",
  HEAL_IN_PERCENT: "% Soins realises",
  RES_IN_PERCENT: "% Resistance",
  CRITICAL_BONUS: "Maitr. Critique",
  CRITICAL_RES: "Res. Critique",
  BACKSTAB_BONUS: "Maitr. Dos",
  RES_BACKSTAB: "Res. Dos",
  MELEE_DMG: "Maitr. Melee",
  RANGED_DMG: "Maitr. Distance",
  BERSERK_DMG: "Maitr. Berserk",
  INDIRECT_DMG: "% Degats indirects",
};

// Stats affichées dans le panneau (sous-ensemble pertinent pour les bonus Wakfuli)
const DISPLAYED_STATS: (keyof StatValues)[] = [
  "HP", "AP", "MP", "WP",
  "DODGE", "TACKLE", "INIT",
  "WISDOM", "PROSPECTION",
  "DMG_IN_PERCENT", "HEAL_IN_PERCENT", "RES_IN_PERCENT",
  "BLOCK", "WILLPOWER", "RANGE",
  "CRITICAL_BONUS", "CRITICAL_RES",
  "BACKSTAB_BONUS", "RES_BACKSTAB",
  "MELEE_DMG", "RANGED_DMG",
  "BERSERK_DMG", "INDIRECT_DMG",
];

// ============================================================
// Bonus Wakfuli (extraits du chunk 25c3dbf546a727d1.js)
// ============================================================
const DEFAULT_BONUSES: Bonus[] = [
  {
    label: "Arbre",
    active: false,
    stats: {
      HP: 55,
      DODGE: 20,
      TACKLE: 20,
      INIT: 10,
      WISDOM: 10,
      PROSPECTION: 10,
      DMG_IN_PERCENT: 8,
      HEAL_IN_PERCENT: 8,
      RES_IN_PERCENT: 20,
    },
  },
  {
    label: "Gemme",
    active: false,
    stats: {
      HP: 10,
      WISDOM: 10,
      PROSPECTION: 10,
    },
  },
  {
    label: "Monture",
    active: false,
    stats: {
      DMG_IN_PERCENT: 40,
    },
  },
];

const VISIBILITY_CYCLE: Array<"public" | "link-only" | "private"> = [
  "public",
  "link-only",
  "private",
];

const VISIBILITY_LABELS: Record<string, string> = {
  public: "Public",
  "link-only": "Lien seul",
  private: "Prive",
};

const VISIBILITY_ICONS: Record<string, string> = {
  public: "\u{1F30D}",
  "link-only": "\u{1F517}",
  private: "\u{1F512}",
};

// ============================================================
// Helpers
// ============================================================
function addPartialStats(
  base: StatValues,
  partial: Partial<StatValues>
): StatValues {
  const result = { ...base };
  for (const key of Object.keys(partial) as (keyof StatValues)[]) {
    result[key] = (result[key] ?? 0) + (partial[key] ?? 0);
  }
  return result;
}

function encodePayload(data: unknown): string {
  try {
    return btoa(encodeURIComponent(JSON.stringify(data)));
  } catch {
    console.error("[LeftPanel] Erreur encodage payload");
    return "";
  }
}

function formatBonusPreview(stats: Partial<StatValues>): string {
  return Object.entries(stats)
    .filter(([, v]) => (v ?? 0) > 0)
    .map(([k, v]) => `${STAT_LABELS[k as keyof StatValues] ?? k} +${v}`)
    .join(", ");
}

// ============================================================
// Composant — EXPORT NOMME pour BuilderLayout.tsx
// ============================================================
export function LeftPanel() {
  const [build, setBuild] = useState<BuildState>({
    name: "Mon Build",
    level: 20,
    characterClass: "huppermage",
    visibility: "public",
  });

  const [bonuses, setBonuses] = useState<Bonus[]>(() =>
    structuredClone(DEFAULT_BONUSES)
  );

  const [isFavorite, setIsFavorite] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    try {
      const stored = localStorage.getItem("wakfuli_favorites");
      if (!stored) return false;
      const list = JSON.parse(stored);
      return Array.isArray(list) && list.includes("current");
    } catch {
      return false;
    }
  });

  const [feedback, setFeedback] = useState<string>("");

  // Calcul stats — safe, part de EMPTY_STATS
  const totalStats: StatValues = useMemo(() => {
    let computed = { ...EMPTY_STATS };
    for (const bonus of bonuses) {
      if (bonus.active && bonus.stats) {
        computed = addPartialStats(computed, bonus.stats);
      }
    }
    return computed;
  }, [bonuses]);

  const showFeedback = useCallback((msg: string) => {
    setFeedback(msg);
    setTimeout(() => setFeedback(""), 2500);
  }, []);

  // ---- COPY ----
  const handleCopy = useCallback(async () => {
    const payload = JSON.stringify(
      { build, stats: totalStats, bonuses: bonuses.filter((b) => b.active).map((b) => b.label) },
      null,
      2
    );
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(payload);
      } else {
        const ta = document.createElement("textarea");
        ta.value = payload;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      showFeedback("Build copie !");
      console.info("[LeftPanel] Build copie");
    } catch (err) {
      console.error("[LeftPanel] Erreur copie :", err);
      showFeedback("Erreur copie");
    }
  }, [build, totalStats, bonuses, showFeedback]);

  // ---- LINK ----
  const handleLink = useCallback(() => {
    const encoded = encodePayload({ build, stats: totalStats });
    if (!encoded) {
      showFeedback("Erreur lien");
      return;
    }
    const url = `${window.location.origin}/builder?data=${encoded}`;
    navigator?.clipboard?.writeText(url).then(
      () => {
        showFeedback("Lien copie !");
        console.info("[LeftPanel] Lien :", url);
      },
      () => showFeedback("Lien genere")
    );
  }, [build, totalStats, showFeedback]);

  // ---- VISIBILITY ----
  const handleVisibility = useCallback(() => {
    setBuild((prev) => {
      const idx = VISIBILITY_CYCLE.indexOf(prev.visibility);
      const next = VISIBILITY_CYCLE[(idx + 1) % VISIBILITY_CYCLE.length];
      console.info(`[LeftPanel] Visibilite: ${prev.visibility} -> ${next}`);
      return { ...prev, visibility: next };
    });
  }, []);

  // ---- FAVORITE ----
  const handleFavorite = useCallback(() => {
    setIsFavorite((prev) => {
      const next = !prev;
      try {
        const stored = localStorage.getItem("wakfuli_favorites");
        let list: string[] = [];
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) list = parsed;
        }
        if (next && !list.includes("current")) list.push("current");
        else if (!next) list = list.filter((id) => id !== "current");
        localStorage.setItem("wakfuli_favorites", JSON.stringify(list));
        console.info(`[LeftPanel] Favori: ${next ? "+" : "-"}`);
      } catch (err) {
        console.error("[LeftPanel] localStorage err:", err);
      }
      return next;
    });
  }, []);

  const toggleBonus = useCallback((index: number) => {
    setBonuses((prev) =>
      prev.map((b, i) => (i === index ? { ...b, active: !b.active } : b))
    );
  }, []);

  // ---- RENDU ----
  return (
    <aside style={panelStyle}>
      {/* Header */}
      <div style={{ padding: "16px 16px 0" }}>
        <h2 style={{ margin: 0, fontSize: 17, color: "#7ecbff", fontWeight: 700 }}>
          {build.name}
        </h2>
        <p style={{ margin: "4px 0 0", fontSize: 13, color: "#999" }}>
          {build.characterClass.charAt(0).toUpperCase() + build.characterClass.slice(1)}
          {" \u2014 Niv. "}
          {build.level}
        </p>
      </div>

      {/* 4 boutons */}
      <div style={{ display: "flex", gap: 6, padding: "8px 16px" }}>
        {[
          { label: "Copier", icon: "\u{1F4CB}", handler: handleCopy },
          { label: "Lien", icon: "\u{1F517}", handler: handleLink },
          {
            label: VISIBILITY_LABELS[build.visibility],
            icon: VISIBILITY_ICONS[build.visibility],
            handler: handleVisibility,
          },
          {
            label: "Favori",
            icon: isFavorite ? "\u2764\uFE0F" : "\u{1F90D}",
            handler: handleFavorite,
            activeColor: isFavorite ? "#ff6b81" : undefined,
          },
        ].map((btn) => (
          <button
            key={btn.label}
            onClick={btn.handler}
            title={btn.label}
            style={{
              ...btnStyle,
              color: btn.activeColor ?? "#c0c0c0",
            }}
          >
            <span style={{ fontSize: 14 }}>{btn.icon}</span>
            <span style={{ fontSize: 11 }}>{btn.label}</span>
          </button>
        ))}
      </div>

      {/* Feedback */}
      {feedback && (
        <div style={feedbackStyle}>
          {feedback}
        </div>
      )}

      {/* Bonus */}
      <div style={{ padding: "0 16px" }}>
        <h3 style={sectionTitle}>Bonus</h3>
        {bonuses.map((bonus, i) => (
          <label key={bonus.label} style={bonusRow}>
            <input
              type="checkbox"
              checked={bonus.active}
              onChange={() => toggleBonus(i)}
              style={{ accentColor: "#7ecbff", width: 15, height: 15, cursor: "pointer" }}
            />
            <span style={{ fontWeight: 600, fontSize: 13 }}>{bonus.label}</span>
            <span style={{ opacity: 0.45, marginLeft: "auto", fontSize: 10, maxWidth: 160, textAlign: "right" }}>
              {formatBonusPreview(bonus.stats)}
            </span>
          </label>
        ))}
      </div>

      {/* Statistiques */}
      <div style={{ padding: "0 16px", flex: 1, overflowY: "auto" }}>
        <h3 style={sectionTitle}>Statistiques</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {DISPLAYED_STATS.map((key) => {
            const value = totalStats[key] ?? 0;
            const hasValue = value !== 0;
            return (
              <div key={key} style={statRow}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${ICON_BASE}/${key}.png`}
                  alt={key}
                  width={20}
                  height={20}
                  style={{ flexShrink: 0 }}
                  onError={(e) => {
                    const img = e.target as HTMLImageElement;
                    img.style.display = "none";
                  }}
                />
                <span style={{ fontSize: 12, color: hasValue ? "#ddd" : "#666" }}>
                  {STAT_LABELS[key]}
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontSize: 13,
                    fontWeight: hasValue ? 700 : 400,
                    color: hasValue ? "#7ecbff" : "#555",
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {value}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Debug dev only */}
      {process.env.NODE_ENV === "development" && (
        <details style={{ fontSize: 10, opacity: 0.4, padding: "8px 16px" }}>
          <summary style={{ cursor: "pointer" }}>Debug state</summary>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 9, marginTop: 4 }}>
            {JSON.stringify({ build, bonuses, totalStats, isFavorite }, null, 2)}
          </pre>
        </details>
      )}
    </aside>
  );
}

// ============================================================
// Styles
// ============================================================
const panelStyle: React.CSSProperties = {
  width: 320,
  backgroundColor: "#12122a",
  color: "#e0e0e0",
  borderRight: "1px solid #2a2a45",
  fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif",
  height: "100vh",
  display: "flex",
  flexDirection: "column",
  gap: 8,
  overflowY: "auto",
};

const btnStyle: React.CSSProperties = {
  flex: 1,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 2,
  padding: "6px 2px",
  border: "1px solid #333",
  borderRadius: 8,
  backgroundColor: "#1e1e3a",
  color: "#c0c0c0",
  cursor: "pointer",
  transition: "background-color 0.15s, border-color 0.15s",
};

const feedbackStyle: React.CSSProperties = {
  margin: "0 16px",
  padding: "6px 10px",
  backgroundColor: "#1a3a1a",
  border: "1px solid #2d5a22",
  borderRadius: 6,
  fontSize: 12,
  textAlign: "center",
  color: "#8fc98f",
};

const sectionTitle: React.CSSProperties = {
  fontSize: 12,
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  color: "#a78bfa",
  margin: "12px 0 8px",
};

const bonusRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "5px 0",
  cursor: "pointer",
  borderBottom: "1px solid #1e1e3a",
};

const statRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "3px 0",
};
