"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";
import type { WakfuClass, EquipmentSlot, WakfuItem } from "@/types/wakfu";
import { CLASSES } from "@/types/wakfu";

interface EquippedItem {
  slotIndex: number;
  item: WakfuItem;
}

interface BuildState {
  name: string;
  characterClass: WakfuClass;
  level: number;
  equipment: Record<string, EquippedItem | null>;
  activeSpells: number[];
  passiveSpells: number[];
}

// Stats calculees depuis les items equipes
interface ComputedStats {
  HP: number;
  AP: number;
  MP: number;
  WP: number;
  RANGE: number;
  FEROCITY: number;
  BLOCK: number;
  INIT: number;
  DODGE: number;
  TACKLE: number;
  WISDOM: number;
  PROSPECTION: number;
  WILLPOWER: number;
  DMG_FIRE_PERCENT: number;
  DMG_WATER_PERCENT: number;
  DMG_EARTH_PERCENT: number;
  DMG_AIR_PERCENT: number;
  RES_FIRE_PERCENT: number;
  RES_WATER_PERCENT: number;
  RES_EARTH_PERCENT: number;
  RES_AIR_PERCENT: number;
  RES_IN_PERCENT: number;
  DMG_IN_PERCENT: number;
  FINAL_DMG_IN_PERCENT: number;
  FINAL_HEAL_IN_PERCENT: number;
  CRITICAL_BONUS: number;
  CRITICAL_RES: number;
  BACKSTAB_BONUS: number;
  RES_BACKSTAB: number;
  MELEE_DMG: number;
  RANGED_DMG: number;
  HEAL_IN_PERCENT: number;
  BERSERK_DMG: number;
  ARMOR_GIVEN: number;
  ARMOR_RECEIVED: number;
  INDIRECT_DMG: number;
}

interface BuildContextType {
  build: BuildState;
  stats: ComputedStats;
  setName: (name: string) => void;
  setClass: (cls: WakfuClass) => void;
  setLevel: (level: number) => void;
  equipItem: (slot: string, item: Record<string, unknown>) => void;
  unequipItem: (slot: string) => void;
  pendingRingItem: WakfuItem | null;
  setPendingRingItem: (item: WakfuItem | null) => void;
}

const BASE_STATS: ComputedStats = {
  HP: 50, AP: 6, MP: 3, WP: 6, RANGE: 0,
  FEROCITY: 3, BLOCK: 0, INIT: 0, DODGE: 0, TACKLE: 0,
  WISDOM: 0, PROSPECTION: 0, WILLPOWER: 0,
  DMG_FIRE_PERCENT: 0, DMG_WATER_PERCENT: 0, DMG_EARTH_PERCENT: 0, DMG_AIR_PERCENT: 0,
  RES_FIRE_PERCENT: 0, RES_WATER_PERCENT: 0, RES_EARTH_PERCENT: 0, RES_AIR_PERCENT: 0,
  RES_IN_PERCENT: 0, DMG_IN_PERCENT: 0,
  FINAL_DMG_IN_PERCENT: 0, FINAL_HEAL_IN_PERCENT: 0,
  CRITICAL_BONUS: 0, CRITICAL_RES: 0, BACKSTAB_BONUS: 0, RES_BACKSTAB: 0,
  MELEE_DMG: 0, RANGED_DMG: 0, HEAL_IN_PERCENT: 0, BERSERK_DMG: 0,
  ARMOR_GIVEN: 0, ARMOR_RECEIVED: 0, INDIRECT_DMG: 0,
};

// HP de base par niveau (approximation Wakfu)
function baseHpForLevel(level: number): number {
  return 50 + (level * 10);
}

function computeStats(build: BuildState): ComputedStats {
  const s = { ...BASE_STATS };
  s.HP = baseHpForLevel(build.level);

  for (const slot of Object.keys(build.equipment)) {
    const eq = build.equipment[slot];
    if (!eq || !eq.item) continue;
    const item = eq.item;
    if (!item.effects) continue;

    for (const eff of item.effects) {
      const t = eff.type;
      const v = eff.value;
      if (t === "HP") s.HP += v;
      else if (t === "AP") s.AP += v;
      else if (t === "MP") s.MP += v;
      else if (t === "WP") s.WP += v;
      else if (t === "RANGE") s.RANGE += v;
      else if (t === "FEROCITY") s.FEROCITY += v;
      else if (t === "BLOCK") s.BLOCK += v;
      else if (t === "INIT") s.INIT += v;
      else if (t === "DODGE") s.DODGE += v;
      else if (t === "TACKLE") s.TACKLE += v;
      else if (t === "WISDOM") s.WISDOM += v;
      else if (t === "PROSPECTION") s.PROSPECTION += v;
      else if (t === "WILLPOWER") s.WILLPOWER += v;
      else if (t === "DMG_FIRE_PERCENT") s.DMG_FIRE_PERCENT += v;
      else if (t === "DMG_WATER_PERCENT") s.DMG_WATER_PERCENT += v;
      else if (t === "DMG_EARTH_PERCENT") s.DMG_EARTH_PERCENT += v;
      else if (t === "DMG_AIR_PERCENT") s.DMG_AIR_PERCENT += v;
      else if (t === "RES_FIRE_PERCENT") s.RES_FIRE_PERCENT += v;
      else if (t === "RES_WATER_PERCENT") s.RES_WATER_PERCENT += v;
      else if (t === "RES_EARTH_PERCENT") s.RES_EARTH_PERCENT += v;
      else if (t === "RES_AIR_PERCENT") s.RES_AIR_PERCENT += v;
      else if (t === "RES_IN_PERCENT") {
        s.RES_FIRE_PERCENT += v; s.RES_WATER_PERCENT += v;
        s.RES_EARTH_PERCENT += v; s.RES_AIR_PERCENT += v;
      }
      else if (t === "DMG_IN_PERCENT") s.DMG_IN_PERCENT += v;
      else if (t === "FINAL_DMG_IN_PERCENT") s.FINAL_DMG_IN_PERCENT += v;
      else if (t === "FINAL_HEAL_IN_PERCENT") s.FINAL_HEAL_IN_PERCENT += v;
      else if (t === "CRITICAL_BONUS") s.CRITICAL_BONUS += v;
      else if (t === "CRITICAL_RES") s.CRITICAL_RES += v;
      else if (t === "BACKSTAB_BONUS") s.BACKSTAB_BONUS += v;
      else if (t === "RES_BACKSTAB") s.RES_BACKSTAB += v;
      else if (t === "MELEE_DMG") s.MELEE_DMG += v;
      else if (t === "RANGED_DMG") s.RANGED_DMG += v;
      else if (t === "HEAL_IN_PERCENT") s.HEAL_IN_PERCENT += v;
      else if (t === "BERSERK_DMG") s.BERSERK_DMG += v;
      else if (t === "ARMOR_GIVEN") s.ARMOR_GIVEN += v;
      else if (t === "ARMOR_RECEIVED") s.ARMOR_RECEIVED += v;
      else if (t === "INDIRECT_DMG") s.INDIRECT_DMG += v;
    }
  }
  return s;
}

const defaultBuild: BuildState = {
  name: "Mon Build",
  characterClass: "huppermage",
  level: 200,
  equipment: {},
  activeSpells: [],
  passiveSpells: [],
};

const BuildContext = createContext<BuildContextType | null>(null);

export function BuildProvider({ children }: { children: ReactNode }) {
  const [build, setBuild] = useState<BuildState>(defaultBuild);
  const [pendingRingItem, setPendingRingItem] = useState<WakfuItem | null>(null);

  const stats = useMemo(() => computeStats(build), [build]);

  const setName = useCallback((name: string) => {
    setBuild((prev) => ({ ...prev, name }));
  }, []);

  const setClass = useCallback((characterClass: WakfuClass) => {
    setBuild((prev) => ({ ...prev, characterClass }));
  }, []);

  const setLevel = useCallback((level: number) => {
    const clamped = Math.min(Math.max(level, 1), 230);
    setBuild((prev) => ({ ...prev, level: clamped }));
  }, []);

  const equipItem = useCallback((slot: string, item: Record<string, unknown>) => {
    setBuild((prev) => ({
      ...prev,
      equipment: {
        ...prev.equipment,
        [slot]: { slotIndex: 0, item: item as unknown as WakfuItem },
      },
    }));
  }, []);

  const unequipItem = useCallback((slot: string) => {
    setBuild((prev) => ({
      ...prev,
      equipment: { ...prev.equipment, [slot]: null },
    }));
  }, []);

  return (
    <BuildContext.Provider
      value={{ build, stats, setName, setClass, setLevel, equipItem, unequipItem, pendingRingItem, setPendingRingItem }}
    >
      {children}
    </BuildContext.Provider>
  );
}

export function useBuild() {
  const ctx = useContext(BuildContext);
  if (!ctx) throw new Error("useBuild must be used within BuildProvider");
  return ctx;
}

export { CLASSES };
