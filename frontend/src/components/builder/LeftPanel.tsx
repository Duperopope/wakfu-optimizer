"use client";

import { useBuild } from "@/lib/BuildContext";
import { ClassSelector } from "@/components/builder/ClassSelector";
import { Copy, Link, Eye, Heart, TreePine, Gem, Cat } from "lucide-react";

// Mapping des ressources de classe (BQ = Wakfu Points, etc.)
const CLASS_RESOURCE: Record<string, { label: string; icon: string; color: string }> = {
  huppermage: { label: "BQ", icon: "HUPPERMAGE_RESOURCE", color: "#e1b900" },
  cra: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  ecaflip: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  eliotrope: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  eniripsa: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  enutrof: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  feca: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  iop: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  osamodas: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  ouginak: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  pandawa: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  roublard: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  sacrieur: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  sadida: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  sram: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  steamer: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  xelor: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
  zobal: { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" },
};

export function LeftPanel() {
  const { build, setName } = useBuild();
  const resource = CLASS_RESOURCE[build.characterClass] || { label: "WP", icon: "WAKFU_POINT", color: "#19c1ef" };

  return (
    <div className="flex flex-1 flex-col divide-y divide-border bg-bg-darker overflow-hidden h-full">
      {/* Build header: nom editable */}
      <div className="flex h-10 items-center justify-center p-2 shrink-0">
        <input
          className="w-full bg-transparent border-none p-0 m-0 text-ellipsis whitespace-nowrap font-sans text-primary/50 focus:text-primary focus:outline-none focus:ring-0 text-center"
          type="text"
          value={build.name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      {/* Classe + niveau + actions */}
      <div className="flex items-center gap-2 w-full p-2 shrink-0">
        <ClassSelector />
        {/* Action icons */}
        <div className="flex items-center gap-1 ml-auto">
          <ActionIcon title="Copier le build"><Copy className="h-4 w-4" /></ActionIcon>
          <ActionIcon title="Lien de partage"><Link className="h-4 w-4" /></ActionIcon>
          <ActionIcon title="Visibilite"><Eye className="h-4 w-4" /></ActionIcon>
          <ActionIcon title="Favori"><Heart className="h-4 w-4" /></ActionIcon>
        </div>
      </div>

      {/* Bonus checkboxes */}
      <div className="flex items-center gap-4 p-2 shrink-0">
        <BonusCheck icon={<TreePine className="h-4 w-4 text-green-400" />} label="Arbre" />
        <BonusCheck icon={<Gem className="h-4 w-4 text-purple-400" />} label="Gemme" />
        <BonusCheck icon={<Cat className="h-4 w-4 text-amber-400" />} label="Monture" />
      </div>

      {/* Stats — scrollable */}
      <div className="flex-1 overflow-y-auto min-h-0 no-scrollbar p-4">
        {/* Stats principales — 2x2 grid */}
        <div className="flex w-full flex-col gap-y-[2px] mb-3 overflow-hidden rounded-md">
          <div className="flex w-full gap-[2px]">
            <StatCell icon="HP" label="PV" value="2050" color="#ff515b" />
            <StatCell icon="AP" label="PA" value="6" color="#19c1ef" />
          </div>
          <div className="flex w-full gap-[2px]">
            <StatCell icon="MP" label="PM" value="3" color="#afd34c" />
            <StatCell icon={resource.icon} label={resource.label} value="6" color={resource.color} />
          </div>
        </div>

        {/* Section Maitrises et Resistances */}
        <div className="flex justify-between w-full px-3 items-center mb-2">
          <span className="text-lg font-bagnard">Maitrises et Resistances</span>
        </div>
        <div className="flex w-full flex-col gap-y-[2px] mb-3 overflow-hidden rounded-md">
          <div className="flex w-full gap-[2px]">
            <div className="flex flex-col flex-1 gap-[2px]">
              <ElementStatCell icon="DMG_FIRE_PERCENT" value="0" color="#ff9333" />
              <ElementStatCell icon="RES_FIRE_PERCENT" value="0% (0)" color="#ff9333" />
            </div>
            <div className="flex flex-col flex-1 gap-[2px]">
              <ElementStatCell icon="DMG_WATER_PERCENT" value="0" color="#99f9f9" />
              <ElementStatCell icon="RES_WATER_PERCENT" value="0% (0)" color="#99f9f9" />
            </div>
          </div>
          <div className="flex w-full gap-[2px]">
            <div className="flex flex-col flex-1 gap-[2px]">
              <ElementStatCell icon="DMG_EARTH_PERCENT" value="0" color="#c4dd1e" />
              <ElementStatCell icon="RES_EARTH_PERCENT" value="0% (0)" color="#c4dd1e" />
            </div>
            <div className="flex flex-col flex-1 gap-[2px]">
              <ElementStatCell icon="DMG_AIR_PERCENT" value="0" color="#ed99ff" />
              <ElementStatCell icon="RES_AIR_PERCENT" value="0% (0)" color="#ed99ff" />
            </div>
          </div>
        </div>

        {/* Section Combat */}
        <div className="w-full text-lg px-3 font-bagnard mb-2">Combat</div>
        <div className="flex w-full flex-col gap-y-[2px] mb-3 overflow-hidden rounded-md">
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="FINAL_DMG_IN_PERCENT" label="Dommages infliges" value="0%" />
            <StatCell icon="FINAL_HEAL_IN_PERCENT" label="Soins realises" value="0%" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="FEROCITY" label="% Coup critique" value="3%" color="#64dc29" />
            <StatCell icon="BLOCK" label="% Parade" value="0%" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="INIT" label="Initiative" value="0" />
            <StatCell icon="RANGE" label="Portee" value="0" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="DODGE" label="Esquive" value="0" />
            <StatCell icon="TACKLE" label="Tacle" value="0" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="WISDOM" label="Sagesse" value="30" color="#64dc29" />
            <StatCell icon="PROSPECTION" label="Prospection" value="30" color="#64dc29" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="WILLPOWER" label="Volonte" value="0" />
            <div className="flex-1 min-w-0" />
          </div>
        </div>

        {/* Section Secondaire */}
        <div className="w-full text-lg px-3 font-bagnard mb-2">Secondaire</div>
        <div className="flex w-full flex-col gap-y-[2px] mb-3 overflow-hidden rounded-md">
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="CRITICAL_BONUS" label="Maitrise critique" value="0" />
            <StatCell icon="CRITICAL_RES" label="Resistance critique" value="0" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="BACKSTAB_BONUS" label="Maitrise dos" value="0" />
            <StatCell icon="RES_BACKSTAB" label="Resistance dos" value="0" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="MELEE_DMG" label="Maitrise melee" value="0" />
            <StatCell icon="ARMOR_GIVEN" label="Armure donnee" value="0%" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="RANGED_DMG" label="Maitrise distance" value="0" />
            <StatCell icon="ARMOR_RECEIVED" label="Armure recue" value="0%" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="HEAL_IN_PERCENT" label="Maitrise soin" value="0" />
            <StatCell icon="INDIRECT_DMG" label="Dommages indirects" value="0%" />
          </div>
          <div className="flex w-full gap-x-[2px]">
            <StatCell icon="BERSERK_DMG" label="Maitrise berserk" value="0" />
            <div className="flex-1 min-w-0" />
          </div>
        </div>
      </div>
    </div>
  );
}

/* --- Action icon button --- */
function ActionIcon({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <button
      title={title}
      className="flex h-8 w-8 items-center justify-center rounded text-primary/50 hover:text-primary hover:bg-bg-light cursor-pointer transition-colors"
    >
      {children}
    </button>
  );
}

/* --- Bonus checkbox --- */
function BonusCheck({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <label className="flex items-center gap-1.5 cursor-pointer text-sm text-primary/60 hover:text-primary/80 transition-colors">
      <input type="checkbox" className="accent-cyan-wakfuli h-3.5 w-3.5 cursor-pointer" />
      {icon}
      <span>{label}</span>
    </label>
  );
}

/* --- Composant stat cell reutilisable --- */
function StatCell({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label?: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center rounded-xs bg-bg-light p-1 gap-1">
        <div className="flex items-center justify-start gap-1">
          <img
            width={22}
            height={22}
            alt={icon}
            className="h-[22px] w-[22px]"
            src={`https://cdn.wakfuli.com/stats/${icon}.webp`}
          />
          {label && <span className="w-full truncate text-sm">{label}</span>}
        </div>
        <div className="flex-1">
          <div className="w-fit float-right rounded-md px-1">
            <button
              className="cursor-pointer text-sm text-right"
              style={{ color: color || "#8899aa" }}
            >
              {value}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* --- Element stat cell (sans label texte) --- */
function ElementStatCell({
  icon,
  value,
  color,
}: {
  icon: string;
  value: string;
  color: string;
}) {
  return (
    <div className="flex items-center rounded-xs bg-bg-light p-1 gap-1">
      <div className="flex items-center justify-start gap-1">
        <img
          width={22}
          height={22}
          alt={icon}
          className="h-[22px] w-[22px]"
          src={`https://cdn.wakfuli.com/stats/${icon}.webp`}
        />
      </div>
      <div className="flex-1">
        <div className="w-fit float-right rounded-md px-1">
          <button className="cursor-pointer text-sm" style={{ color }}>
            {value}
          </button>
        </div>
      </div>
    </div>
  );
}
