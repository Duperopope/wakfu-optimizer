"use client";
import { useState } from "react";
import { useBuild } from "@/lib/BuildContext";
import { ClassSelector } from "@/components/builder/ClassSelector";
import {
  Copy, Link, Eye, EyeOff, Heart,
  TreePine, Gem, Cat, Check
} from "lucide-react";
import { SLOT_LABELS, RARITY_LABELS } from "@/types/wakfu";
import type { WakfuItem } from "@/types/wakfu";

/* ============================================================
   CLASS_RESOURCE  –  icône + couleur de la ressource de classe
   ============================================================ */
const CLASS_RESOURCE: Record<string, { label: string; icon: string; color: string }> = {
  huppermage:  { label: "BQ", icon: "HUPPERMAGE_RESOURCE", color: "#e1b900" },
  cra:         { label: "WP", icon: "WP", color: "#19c1ef" },
  ecaflip:     { label: "WP", icon: "WP", color: "#19c1ef" },
  eliotrope:   { label: "WP", icon: "WP", color: "#19c1ef" },
  eniripsa:    { label: "WP", icon: "WP", color: "#19c1ef" },
  enutrof:     { label: "WP", icon: "WP", color: "#19c1ef" },
  feca:        { label: "WP", icon: "WP", color: "#19c1ef" },
  iop:         { label: "WP", icon: "WP", color: "#19c1ef" },
  osamodas:    { label: "WP", icon: "WP", color: "#19c1ef" },
  ouginak:     { label: "WP", icon: "WP", color: "#19c1ef" },
  pandawa:     { label: "WP", icon: "WP", color: "#19c1ef" },
  roublard:    { label: "WP", icon: "WP", color: "#19c1ef" },
  sacrieur:    { label: "WP", icon: "WP", color: "#19c1ef" },
  sadida:      { label: "WP", icon: "WP", color: "#19c1ef" },
  sram:        { label: "WP", icon: "WP", color: "#19c1ef" },
  steamer:     { label: "WP", icon: "WP", color: "#19c1ef" },
  xelor:       { label: "WP", icon: "WP", color: "#19c1ef" },
  zobal:       { label: "WP", icon: "WP", color: "#19c1ef" },
};

/* ============================================================
   BONUS_DATA  –  Reproduit exactement les bonus de Wakfuli
   (source : chunk 25c3dbf546a727d1.js)
   ============================================================ */
const BONUS_DATA = [
  {
    id: 1, icon: "tree", label: "Arbre",
    stats: { HP: 55, DODGE: 20, TACKLE: 20, INIT: 10,
             WISDOM: 10, PROSPECTION: 10,
             DMG_IN_PERCENT: 8, HEAL_IN_PERCENT: 8,
             RES_IN_PERCENT: 20 },
  },
  {
    id: 2, icon: "gem", label: "Gemme",
    stats: { HP: 10, WISDOM: 10, PROSPECTION: 10 },
  },
  {
    id: 3, icon: "mount", label: "Monture",
    stats: { DMG_IN_PERCENT: 40 },
  },
];

/* ============================================================
   Helpers
   ============================================================ */
function statColor(val: number, base = 0): string {
  if (val > base) return "#64dc29";
  if (val < base) return "#ff4444";
  return "#8899aa";
}

/* ============================================================
   Génération du texte de copie du build
   ============================================================ */
function buildToClipboardText(build: any, computed: any): string {
  const lines: string[] = [];
  lines.push(`--- ${build.name} ---`);
  lines.push(`Classe : ${build.characterClass} | Niveau : ${build.level}`);
  lines.push("");

  // Stats principales
  lines.push(`HP ${computed.HP} | PA ${computed.AP} | PM ${computed.MP} | WP ${computed.WP}`);
  lines.push(
    `Maîtrise Feu ${computed.DMG_FIRE_PERCENT} | Eau ${computed.DMG_WATER_PERCENT} ` +
    `| Terre ${computed.DMG_EARTH_PERCENT} | Air ${computed.DMG_AIR_PERCENT}`
  );
  lines.push(
    `Résistance Feu ${computed.RES_FIRE_PERCENT} | Eau ${computed.RES_WATER_PERCENT} ` +
    `| Terre ${computed.RES_EARTH_PERCENT} | Air ${computed.RES_AIR_PERCENT}`
  );
  lines.push("");

  // Équipements
  const slotKeys = Object.keys(build.equipment || {});
  if (slotKeys.length > 0) {
    lines.push("Equipement :");
    for (const slot of slotKeys) {
      const item = build.equipment[slot] as WakfuItem | null;
      if (item) {
        const rar = RARITY_LABELS[item.rarity] || item.rarity;
        lines.push(`  ${SLOT_LABELS[slot] || slot} : ${item.name} (Niv.${item.level}, ${rar})`);
      }
    }
  }

  lines.push("");
  lines.push("Généré par wakfu-optimizer");
  return lines.join("\n");
}

/* ============================================================
   Génération d'un lien partageable (encodé dans l'URL)
   ============================================================ */
function buildToShareLink(build: any): string {
  const payload = {
    n: build.name,
    c: build.characterClass,
    l: build.level,
    e: Object.entries(build.equipment || {}).reduce((acc: any, [slot, item]: any) => {
      if (item) acc[slot] = item.id;
      return acc;
    }, {}),
  };
  const encoded = btoa(
    encodeURIComponent(JSON.stringify(payload))
  );
  return `${window.location.origin}/builder?b=${encoded}`;
}

/* ============================================================
   LeftPanel
   ============================================================ */
export function LeftPanel() {
  const { build, computed, setBuildName } = useBuild();
  const res = CLASS_RESOURCE[build.characterClass] || CLASS_RESOURCE.cra;

  // --- Button states ---
  const [copied, setCopied] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);
  const [visibility, setVisibility] = useState<"public" | "link-only" | "private">("public");
  const [favorited, setFavorited] = useState(false);

  // --- Bonus toggles (reproduit Wakfuli) ---
  const [bonuses, setBonuses] = useState<Record<number, boolean>>({
    1: false,
    2: false,
    3: false,
  });

  /* -------- Actions des 4 boutons -------- */

  // 1. COPY  –  Copie le résumé texte du build
  const handleCopy = async () => {
    const text = buildToClipboardText(build, computed);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback pour les navigateurs sans Clipboard API
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // 2. LINK  –  Génère et copie un lien partageable
  const handleLink = async () => {
    const url = buildToShareLink(build);
    try {
      await navigator.clipboard.writeText(url);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    }
  };

  // 3. VISIBILITY  –  Bascule public → link-only → private
  const handleVisibility = () => {
    setVisibility((prev) => {
      if (prev === "public") return "link-only";
      if (prev === "link-only") return "private";
      return "public";
    });
  };

  // 4. FAVORITE  –  Sauvegarde en localStorage
  const handleFavorite = () => {
    setFavorited((prev) => {
      const next = !prev;
      try {
        const favs: any[] = JSON.parse(localStorage.getItem("wakfu_favorites") || "[]");
        if (next) {
          const entry = {
            name: build.name,
            characterClass: build.characterClass,
            level: build.level,
            savedAt: new Date().toISOString(),
          };
          favs.push(entry);
        } else {
          const idx = favs.findIndex(
            (f: any) =>
              f.name === build.name && f.characterClass === build.characterClass
          );
          if (idx !== -1) favs.splice(idx, 1);
        }
        localStorage.setItem("wakfu_favorites", JSON.stringify(favs));
      } catch {
        // silently ignore storage errors
      }
      return next;
    });
  };

  /* -------- Toggle d'un bonus -------- */
  const toggleBonus = (id: number) => {
    setBonuses((prev) => ({ ...prev, [id]: !prev[id] }));
    // TODO : appliquer / retirer les stats du bonus dans computeStats
  };

  /* -------- Rendu -------- */
  return (
    <div className="flex flex-col h-full overflow-y-auto hide-scrollbar p-3 gap-3">

      {/* Nom du build */}
      <input
        type="text"
        value={build.name}
        onChange={(e) => setBuildName(e.target.value)}
        className="bg-background-card border border-border rounded px-3 py-1.5 text-sm text-primary w-full focus:outline-none focus:border-cyan-wakfuli"
        placeholder="Nom du build"
      />

      {/* Classe + Niveau */}
      <ClassSelector />

      {/* ---- Action buttons ---- */}
      <div className="flex items-center gap-1">
        <ActionIcon
          icon={copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
          tooltip={copied ? "Copié !" : "Copier le build"}
          onClick={handleCopy}
        />
        <ActionIcon
          icon={linkCopied ? <Check size={16} className="text-green-400" /> : <Link size={16} />}
          tooltip={linkCopied ? "Lien copié !" : "Copier le lien du build"}
          onClick={handleLink}
        />
        <ActionIcon
          icon={
            visibility === "private" ? (
              <EyeOff size={16} />
            ) : (
              <Eye size={16} />
            )
          }
          tooltip={
            visibility === "public"
              ? "Visibilité : Public"
              : visibility === "link-only"
              ? "Visibilité : Lien uniquement"
              : "Visibilité : Privé"
          }
          onClick={handleVisibility}
        />
        <ActionIcon
          icon={
            <Heart
              size={16}
              className={favorited ? "fill-red-500 text-red-500" : ""}
            />
          }
          tooltip={favorited ? "Retirer des favoris" : "Ajouter aux favoris"}
          onClick={handleFavorite}
        />
      </div>

      {/* ---- Bonus checkboxes ---- */}
      <div className="flex items-center gap-2">
        {BONUS_DATA.map((b) => (
          <BonusCheck
            key={b.id}
            icon={
              b.icon === "tree" ? <TreePine size={16} /> :
              b.icon === "gem"  ? <Gem size={16} /> :
                                  <Cat size={16} />
            }
            label={b.label}
            active={bonuses[b.id]}
            onClick={() => toggleBonus(b.id)}
          />
        ))}
      </div>

      {/* ---- Stats Principales ---- */}
      <div className="text-[11px] font-medium text-primary/50 uppercase tracking-wider mt-1">
        Stats principales
      </div>
      <div className="grid grid-cols-4 gap-1">
        <StatCell icon="HP" label="HP" value={computed.HP} color={statColor(computed.HP, 50 + build.level * 10)} />
        <StatCell icon="AP" label="PA" value={computed.AP} color={statColor(computed.AP, 6)} />
        <StatCell icon="MP" label="PM" value={computed.MP} color={statColor(computed.MP, 3)} />
        <StatCell icon={res.icon} label={res.label} value={computed.WP} color={res.color} />
      </div>

      {/* ---- Dégâts élémentaires ---- */}
      <div className="text-[11px] font-medium text-primary/50 uppercase tracking-wider">
        Maîtrise élémentaire
      </div>
      <div className="grid grid-cols-2 gap-1">
        <ElementStatCell icon="DMG_FIRE_PERCENT" label="Feu" dmg={computed.DMG_FIRE_PERCENT} res={computed.RES_FIRE_PERCENT} />
        <ElementStatCell icon="DMG_WATER_PERCENT" label="Eau" dmg={computed.DMG_WATER_PERCENT} res={computed.RES_WATER_PERCENT} />
        <ElementStatCell icon="DMG_EARTH_PERCENT" label="Terre" dmg={computed.DMG_EARTH_PERCENT} res={computed.RES_EARTH_PERCENT} />
        <ElementStatCell icon="DMG_AIR_PERCENT" label="Air" dmg={computed.DMG_AIR_PERCENT} res={computed.RES_AIR_PERCENT} />
      </div>

      {/* ---- Stats de combat ---- */}
      <div className="text-[11px] font-medium text-primary/50 uppercase tracking-wider">
        Combat
      </div>
      <div className="grid grid-cols-3 gap-1">
        <StatCell icon="DMG_IN_PERCENT" label="Dégâts" value={computed.DMG_IN_PERCENT} color={statColor(computed.DMG_IN_PERCENT)} />
        <StatCell icon="HEAL_IN_PERCENT" label="Soins" value={computed.HEAL_IN_PERCENT} color={statColor(computed.HEAL_IN_PERCENT)} />
        <StatCell icon="FEROCITY" label="Coup crit." value={computed.CRITICAL_HIT} color={statColor(computed.CRITICAL_HIT)} />
        <StatCell icon="BLOCK" label="Parade" value={computed.BLOCK} color={statColor(computed.BLOCK)} />
        <StatCell icon="INIT" label="Initiative" value={computed.INITIATIVE} color={statColor(computed.INITIATIVE)} />
        <StatCell icon="RANGE" label="Portée" value={computed.RANGE} color={statColor(computed.RANGE)} />
        <StatCell icon="DODGE" label="Esquive" value={computed.DODGE} color={statColor(computed.DODGE)} />
        <StatCell icon="TACKLE" label="Tacle" value={computed.LOCK} color={statColor(computed.LOCK)} />
        <StatCell icon="WISDOM" label="Sagesse" value={computed.WISDOM} color={statColor(computed.WISDOM)} />
        <StatCell icon="PROSPECTING" label="Prospec." value={computed.PROSPECTION} color={statColor(computed.PROSPECTION)} />
        <StatCell icon="WILLPOWER" label="Volonté" value={computed.WILLPOWER} color={statColor(computed.WILLPOWER)} />
      </div>

      {/* ---- Stats secondaires ---- */}
      <div className="text-[11px] font-medium text-primary/50 uppercase tracking-wider">
        Secondaires
      </div>
      <div className="grid grid-cols-3 gap-1">
        <StatCell icon="CRITICAL_BONUS" label="Maît. crit." value={computed.CRITICAL_BONUS} color={statColor(computed.CRITICAL_BONUS)} />
        <StatCell icon="CRITICAL_RES" label="Rés. crit." value={computed.CRITICAL_RES} color={statColor(computed.CRITICAL_RES)} />
        <StatCell icon="BACKSTAB_BONUS" label="Maît. dos" value={computed.BACKSTAB_BONUS} color={statColor(computed.BACKSTAB_BONUS)} />
        <StatCell icon="RES_BACKSTAB" label="Rés. dos" value={computed.RES_BACKSTAB} color={statColor(computed.RES_BACKSTAB)} />
        <StatCell icon="MELEE_DMG" label="Mêlée" value={computed.MELEE_DMG} color={statColor(computed.MELEE_DMG)} />
        <StatCell icon="RANGED_DMG" label="Distance" value={computed.RANGED_DMG} color={statColor(computed.RANGED_DMG)} />
        <StatCell icon="ARMOR_GIVEN" label="Armure don." value={computed.ARMOR_GIVEN} color={statColor(computed.ARMOR_GIVEN)} />
        <StatCell icon="ARMOR_RECEIVED" label="Armure reçue" value={computed.ARMOR_RECEIVED} color={statColor(computed.ARMOR_RECEIVED)} />
        <StatCell icon="HEAL_IN_PERCENT" label="Soins %" value={computed.HEAL_PERCENT} color={statColor(computed.HEAL_PERCENT)} />
        <StatCell icon="INDIRECT_DMG" label="Indirect" value={computed.INDIRECT_DMG} color={statColor(computed.INDIRECT_DMG)} />
        <StatCell icon="BERSERK_DMG" label="Berserk" value={computed.BERSERK_DMG} color={statColor(computed.BERSERK_DMG)} />
      </div>
    </div>
  );
}

/* ============================================================
   Sub-components
   ============================================================ */
function ActionIcon({
  icon,
  tooltip,
  onClick,
}: {
  icon: React.ReactNode;
  tooltip: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      title={tooltip}
      className="p-2 rounded hover:bg-background-lighter text-primary/60 hover:text-primary transition-colors"
    >
      {icon}
    </button>
  );
}

function BonusCheck({
  icon,
  label,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className={`p-1.5 rounded border transition-colors ${
        active
          ? "border-cyan-wakfuli bg-cyan-wakfuli/10 text-cyan-wakfuli"
          : "border-border text-primary/40 hover:text-primary/60"
      }`}
    >
      {icon}
    </button>
  );
}

function StatCell({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="flex items-center gap-1.5 bg-background-card rounded px-2 py-1">
      <img
        src={`https://cdn.wakfuli.com/stats/${icon}.webp`}
        alt={label}
        width={16}
        height={16}
        className="shrink-0"
        loading="lazy"
      />
      <span className="text-[10px] text-primary/50 truncate">{label}</span>
      <span className="ml-auto text-xs font-medium" style={{ color }}>
        {value}
      </span>
    </div>
  );
}

function ElementStatCell({
  icon,
  label,
  dmg,
  res,
}: {
  icon: string;
  label: string;
  dmg: number;
  res: number;
}) {
  return (
    <div className="flex items-center gap-1.5 bg-background-card rounded px-2 py-1">
      <img
        src={`https://cdn.wakfuli.com/stats/${icon}.webp`}
        alt={label}
        width={16}
        height={16}
        className="shrink-0"
        loading="lazy"
      />
      <span className="text-[10px] text-primary/50 truncate">{label}</span>
      <div className="ml-auto flex gap-2 text-xs font-medium">
        <span style={{ color: statColor(dmg) }}>{dmg}</span>
        <span style={{ color: statColor(res) }}>{res}</span>
      </div>
    </div>
  );
}
