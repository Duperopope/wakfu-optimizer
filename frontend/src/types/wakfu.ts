// ============================================
// WAKFU OPTIMIZER — Types principaux
// Mappes depuis l API Wakfuli
// ============================================

export const CLASSES = [
  "cra","ecaflip","eliotrope","eniripsa","enutrof","feca",
  "huppermage","iop","osamodas","ouginak","pandawa","roublard",
  "sacrieur","sadida","sram","steamer","xelor","zobal"
] as const;

export type WakfuClass = typeof CLASSES[number];

export type Rarity = "COMMON" | "RARE" | "MYTHICAL" | "LEGENDARY" | "MEMORY" | "EPIC" | "RELIC";

export const RARITY_LABELS: Record<Rarity, string> = {
  COMMON: "Commun",
  RARE: "Rare",
  MYTHICAL: "Mythique",
  LEGENDARY: "Legendaire",
  MEMORY: "Souvenir",
  EPIC: "Epique",
  RELIC: "Relique",
};

export const RARITY_CSS: Record<Rarity, string> = {
  COMMON: "text-rarity-common",
  RARE: "text-rarity-rare",
  MYTHICAL: "text-rarity-mythical",
  LEGENDARY: "text-rarity-legendary",
  MEMORY: "text-rarity-memory",
  EPIC: "text-rarity-epic",
  RELIC: "text-rarity-relic",
};

export const RARITY_FADE: Record<Rarity, string> = {
  COMMON: "bg-rarity-common-fade",
  RARE: "bg-rarity-rare-fade",
  MYTHICAL: "bg-rarity-3-fade",
  LEGENDARY: "bg-rarity-4-fade",
  MEMORY: "bg-rarity-memory-fade",
  EPIC: "bg-rarity-epic-fade",
  RELIC: "bg-rarity-relic-fade",
};

// Mapping equipment_position API -> slot interne
export const POSITION_TO_SLOT: Record<string, EquipmentSlot> = {
  HEAD: "helmet",
  NECK: "amulet",
  CHEST: "chestplate",
  LEFT_HAND: "ring-left",
  RIGHT_HAND: "ring-right",
  LEGS: "boots",
  BACK: "cape",
  SHOULDERS: "shoulderguard",
  BELT: "belt",
  FIRST_WEAPON: "weapon-left",
  SECOND_WEAPON: "weapon-right",
  ACCESSORY: "accessory",
  PET: "pet",
};

export type EquipmentSlot =
  | "helmet" | "amulet" | "chestplate" | "ring-left" | "ring-right"
  | "boots" | "cape" | "shoulderguard" | "belt"
  | "weapon-left" | "weapon-right" | "accessory" | "pet";

export const SLOT_ORDER: EquipmentSlot[] = [
  "helmet","amulet","chestplate","ring-left","ring-right",
  "boots","cape","shoulderguard","belt",
  "weapon-left","weapon-right","accessory","pet"
];

export const SLOT_LABELS: Record<EquipmentSlot, string> = {
  "helmet": "Casque",
  "amulet": "Amulette",
  "chestplate": "Plastron",
  "ring-left": "Anneau gauche",
  "ring-right": "Anneau droit",
  "boots": "Bottes",
  "cape": "Cape",
  "shoulderguard": "Epaulettes",
  "belt": "Ceinture",
  "weapon-left": "Arme principale",
  "weapon-right": "Seconde arme",
  "accessory": "Embleme",
  "pet": "Familier",
};

export interface ItemEffect {
  id: number;
  type: string;
  format: string;
  value: number;
  elementCount?: number;
}

export interface WakfuItem {
  id: number;
  name: string;
  level: number;
  rarity: Rarity;
  image_id: string;
  types: number[];
  item_type_label: string;
  equipment_position: string[];
  equipment_disabled_position: string[];
  encyclopedia_link: string;
  effects: ItemEffect[];
  total_mastery: number;
  total_resistance: number;
  total_secondary_masteries: number;
  is_unraveling: boolean;
}

export interface StatLine {
  key: string;
  label: string;
  value: number | string;
  icon: string;
  color?: string;
}

export type BuilderTab = "items" | "enchants" | "aptitudes" | "spells" | "notes";
