"use client";

import React, { useState, useCallback, useMemo } from "react";

// ============================================================
// Types
// ============================================================
interface StatValues {
  HP: number;
  DODGE: number;
  TACKLE: number;
  INIT: number;
  WISDOM: number;
  PROSPECTION: number;
  "DMG%": number;
  "HEAL%": number;
  "RES%": number;
}

interface Bonus {
  label: string;
  active: boolean;
  stats: StatValues;
}

interface BuildState {
  name: string;
  level: number;
  characterClass: string;
  visibility: "public" | "link-only" | "private";
}

// ============================================================
// Constantes par defaut (safe defaults — jamais undefined)
// ============================================================
const EMPTY_STATS: StatValues = {
  HP: 0,
  DODGE: 0,
  TACKLE: 0,
  INIT: 0,
  WISDOM: 0,
  PROSPECTION: 0,
  "DMG%": 0,
  "HEAL%": 0,
  "RES%": 0,
};

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
      "DMG%": 8,
      "HEAL%": 8,
      "RES%": 20,
    },
  },
  {
    label: "Gemme",
    active: false,
    stats: {
      HP: 10,
      DODGE: 0,
      TACKLE: 0,
      INIT: 0,
      WISDOM: 10,
      PROSPECTION: 10,
      "DMG%": 0,
      "HEAL%": 0,
      "RES%": 0,
    },
  },
  {
    label: "Monture",
    active: false,
    stats: {
      HP: 0,
      DODGE: 0,
      TACKLE: 0,
      INIT: 0,
      WISDOM: 0,
      PROSPECTION: 0,
      "DMG%": 40,
      "HEAL%": 0,
      "RES%": 0,
    },
  },
];

const STAT_ICONS: Record<string, string> = {
  HP: "hp",
  DODGE: "dodge",
  TACKLE: "tackle",
  INIT: "initiative",
  WISDOM: "wisdom",
  PROSPECTION: "prospection",
  "DMG%": "damage",
  "HEAL%": "heals",
  "RES%": "resistance",
};

const VISIBILITY_CYCLE: Array<"public" | "link-only" | "private"> = [
  "public",
  "link-only",
  "private",
];

const VISIBILITY_LABELS: Record<string, string> = {
  public: "Public",
  "link-only": "Lien uniquement",
  private: "Prive",
};

// ============================================================
// Helpers
// ============================================================

/** Additionne deux StatValues de maniere safe */
function addStats(a: StatValues, b: StatValues): StatValues {
  const result = { ...EMPTY_STATS };
  for (const key of Object.keys(EMPTY_STATS) as (keyof StatValues)[]) {
    result[key] = (a?.[key] ?? 0) + (b?.[key] ?? 0);
  }
  return result;
}

/** Encode un objet en base64 pour le partage */
function encodePayload(data: unknown): string {
  try {
    return btoa(JSON.stringify(data));
  } catch {
    console.error("[LeftPanel] Erreur encodage payload");
    return "";
  }
}

// ============================================================
// Composant principal
// ============================================================
export default function LeftPanel() {
  // --- State du build -------------------------------------------------------
  const [build, setBuild] = useState<BuildState>({
    name: "Mon Build",
    level: 20,
    characterClass: "huppermage",
    visibility: "public",
  });

  // --- Bonus toggles -------------------------------------------------------
  const [bonuses, setBonuses] = useState<Bonus[]>(
    () => structuredClone(DEFAULT_BONUSES) // copie profonde pour eviter mutation
  );

  // --- Favoris (localStorage) -----------------------------------------------
  const [isFavorite, setIsFavorite] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    try {
      const stored = localStorage.getItem("wakfuli_favorites");
      if (!stored) return false;
      const list: string[] = JSON.parse(stored);
      return Array.isArray(list) && list.includes("current");
    } catch {
      return false;
    }
  });

  // --- Feedback utilisateur --------------------------------------------------
  const [feedback, setFeedback] = useState<string>("");

  // --- Stats calculees (SAFE : part toujours de EMPTY_STATS) ----------------
  const totalStats: StatValues = useMemo(() => {
    let computed = { ...EMPTY_STATS };
    for (const bonus of bonuses) {
      if (bonus.active && bonus.stats) {
        computed = addStats(computed, bonus.stats);
      }
    }
    return computed;
  }, [bonuses]);

  // --- Handlers -------------------------------------------------------------

  const showFeedback = useCallback((msg: string) => {
    setFeedback(msg);
    setTimeout(() => setFeedback(""), 2000);
  }, []);

  /** COPY — copie le build dans le presse-papier */
  const handleCopy = useCallback(async () => {
    const payload = JSON.stringify({ build, stats: totalStats }, null, 2);
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(payload);
      } else {
        // Fallback textarea
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
      console.info("[LeftPanel] Build copie dans le presse-papier");
    } catch (err) {
      console.error("[LeftPanel] Erreur copie :", err);
      showFeedback("Erreur lors de la copie");
    }
  }, [build, totalStats, showFeedback]);

  /** LINK — genere un lien de partage */
  const handleLink = useCallback(() => {
    const encoded = encodePayload({ build, stats: totalStats });
    if (!encoded) {
      showFeedback("Erreur generation lien");
      return;
    }
    const url = `${window.location.origin}/builder?data=${encoded}`;
    navigator?.clipboard?.writeText(url).then(
      () => {
        showFeedback("Lien copie !");
        console.info("[LeftPanel] Lien de partage copie :", url);
      },
      () => showFeedback("Lien genere (copie echouee)")
    );
  }, [build, totalStats, showFeedback]);

  /** EYE — cycle de visibilite */
  const handleVisibility = useCallback(() => {
    setBuild((prev) => {
      const currentIndex = VISIBILITY_CYCLE.indexOf(prev.visibility);
      const nextIndex = (currentIndex + 1) % VISIBILITY_CYCLE.length;
      const next = VISIBILITY_CYCLE[nextIndex];
      console.info(`[LeftPanel] Visibilite : ${prev.visibility} -> ${next}`);
      return { ...prev, visibility: next };
    });
  }, []);

  /** HEART — toggle favori */
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
        if (next && !list.includes("current")) {
          list.push("current");
        } else if (!next) {
          list = list.filter((id) => id !== "current");
        }
        localStorage.setItem("wakfuli_favorites", JSON.stringify(list));
        console.info(`[LeftPanel] Favori : ${next ? "ajoute" : "retire"}`);
      } catch (err) {
        console.error("[LeftPanel] Erreur localStorage :", err);
      }
      return next;
    });
  }, []);

  /** Toggle un bonus par index */
  const toggleBonus = useCallback((index: number) => {
    setBonuses((prev) =>
      prev.map((b, i) => (i === index ? { ...b, active: !b.active } : b))
    );
  }, []);

  // --- Rendu ----------------------------------------------------------------
  return (
    <aside
      style={{
        width: 320,
        padding: 16,
        backgroundColor: "#1a1a2e",
        color: "#e0e0e0",
        borderRight: "1px solid #333",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        overflowY: "auto",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}
    >
      {/* ---- Header ---- */}
      <div>
        <h2 style={{ margin: 0, fontSize: 18, color: "#7ecbff" }}>
          {build.name}
        </h2>
        <p style={{ margin: "4px 0 0", fontSize: 13, opacity: 0.7 }}>
          {build.characterClass.charAt(0).toUpperCase() +
            build.characterClass.slice(1)}{" "}
          — Niv. {build.level}
        </p>
      </div>

      {/* ---- 4 boutons d action ---- */}
      <div style={{ display: "flex", gap: 8 }}>
        <button
          onClick={handleCopy}
          title="Copier le build"
          style={btnStyle}
        >
          📋 Copy
        </button>
        <button
          onClick={handleLink}
          title="Generer un lien de partage"
          style={btnStyle}
        >
          🔗 Link
        </button>
        <button
          onClick={handleVisibility}
          title={`Visibilite : ${VISIBILITY_LABELS[build.visibility]}`}
          style={btnStyle}
        >
          👁️ {VISIBILITY_LABELS[build.visibility]}
        </button>
        <button
          onClick={handleFavorite}
          title={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
          style={{
            ...btnStyle,
            color: isFavorite ? "#ff6b81" : "#e0e0e0",
          }}
        >
          {isFavorite ? "❤️" : "🤍"} Fav
        </button>
      </div>

      {/* ---- Feedback ephemere ---- */}
      {feedback && (
        <div
          style={{
            padding: "6px 10px",
            backgroundColor: "#2d4a22",
            borderRadius: 6,
            fontSize: 13,
            textAlign: "center",
          }}
        >
          {feedback}
        </div>
      )}

      {/* ---- Bonus toggles ---- */}
      <div>
        <h3 style={{ fontSize: 14, margin: "8px 0 6px", color: "#a78bfa" }}>
          Bonus
        </h3>
        {bonuses.map((bonus, i) => (
          <label
            key={bonus.label}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "4px 0",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            <input
              type="checkbox"
              checked={bonus.active}
              onChange={() => toggleBonus(i)}
              style={{ accentColor: "#7ecbff" }}
            />
            <span>{bonus.label}</span>
            <span style={{ opacity: 0.5, marginLeft: "auto", fontSize: 11 }}>
              {Object.entries(bonus.stats ?? {})
                .filter(([, v]) => v > 0)
                .map(([k, v]) => `${k} +${v}`)
                .join(", ")}
            </span>
          </label>
        ))}
      </div>

      {/* ---- Stats completes ---- */}
      <div>
        <h3 style={{ fontSize: 14, margin: "8px 0 6px", color: "#a78bfa" }}>
          Statistiques
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {(Object.keys(EMPTY_STATS) as (keyof StatValues)[]).map((key) => (
            <div
              key={key}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                fontSize: 13,
              }}
            >
              <img
                src={`https://cdn.wakfuli.com/stats/${STAT_ICONS[key] ?? key.toLowerCase()}.webp`}
                alt={key}
                width={18}
                height={18}
                style={{ imageRendering: "pixelated" }}
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
              <span style={{ minWidth: 80 }}>{key}</span>
              <span
                style={{
                  marginLeft: "auto",
                  fontWeight: totalStats[key] > 0 ? 700 : 400,
                  color: totalStats[key] > 0 ? "#7ecbff" : "#888",
                }}
              >
                {totalStats[key]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ---- Debug info (dev only) ---- */}
      {process.env.NODE_ENV === "development" && (
        <details style={{ fontSize: 11, opacity: 0.5, marginTop: "auto" }}>
          <summary>Debug</summary>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 10 }}>
            {JSON.stringify({ build, bonuses, totalStats, isFavorite }, null, 2)}
          </pre>
        </details>
      )}
    </aside>
  );
}

// ============================================================
// Style commun boutons
// ============================================================
const btnStyle: React.CSSProperties = {
  flex: 1,
  padding: "6px 4px",
  fontSize: 12,
  border: "1px solid #444",
  borderRadius: 6,
  backgroundColor: "#2a2a40",
  color: "#e0e0e0",
  cursor: "pointer",
  transition: "background-color 0.15s",
  textAlign: "center",
};
