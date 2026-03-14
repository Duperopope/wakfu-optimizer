"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import type { WakfuClass, EquipmentSlot } from "@/types/wakfu";
import { CLASSES } from "@/types/wakfu";

interface EquippedItem {
  slotIndex: number;
  item: Record<string, unknown>;
}

interface BuildState {
  name: string;
  characterClass: WakfuClass;
  level: number;
  equipment: Record<string, EquippedItem | null>;
  activeSpells: number[];
  passiveSpells: number[];
}

interface BuildContextType {
  build: BuildState;
  setName: (name: string) => void;
  setClass: (cls: WakfuClass) => void;
  setLevel: (level: number) => void;
  equipItem: (slot: string, item: Record<string, unknown>) => void;
  unequipItem: (slot: string) => void;
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
        [slot]: { slotIndex: 0, item },
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
      value={{ build, setName, setClass, setLevel, equipItem, unequipItem }}
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
