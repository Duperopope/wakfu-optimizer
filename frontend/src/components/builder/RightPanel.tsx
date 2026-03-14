"use client";

import { useState, useMemo } from "react";
import { SLOT_ORDER, RARITY_CSS, RARITY_LABELS, POSITION_TO_SLOT, type EquipmentSlot, type BuilderTab, type WakfuItem, type Rarity } from "@/types/wakfu";
import { useWakfuData } from "@/lib/useWakfuData";
import { useBuild } from "@/lib/BuildContext";
import { Funnel, ListOrdered, ArrowDownWideNarrow, LayoutList, Heart, Eye, Search, X, ScrollText, Hammer, Eraser, Plus, ExternalLink, EyeOff, Loader2, Minus } from "lucide-react";

const TABS: { key: BuilderTab; label: string }[] = [
  { key: "items", label: "items" },
  { key: "enchants", label: "enchantement" },
  { key: "aptitudes", label: "aptitudes" },
  { key: "spells", label: "sorts" },
  { key: "notes", label: "notes" },
];

const DISABLED_TABS = [{ label: "variantes" }, { label: "resume" }];
const ITEM_TYPE_IDS = [134,120,136,103,119,132,138,133,518,519,112,189,646,582];
const RARITIES: Rarity[] = ["COMMON","RARE","MYTHICAL","LEGENDARY","MEMORY","EPIC","RELIC"];

export function RightPanel() {
  const [activeTab, setActiveTab] = useState<BuilderTab>("items");

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between bg-bg-darker border-b border-gray-700 px-4 py-5 gap-6">
        <div className="flex flex-col xl:flex-row items-center gap-4">
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-md bg-bg-light hover:bg-bg-lighter cursor-pointer border-2 border-bg-lighter text-sm">Resistances auto.</button>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
            {SLOT_ORDER.map((slot) => <EquipmentSlotIcon key={slot} slot={slot} />)}
          </div>
        </div>
      </div>

      <nav className="bg-bg-darker flex h-[40px] items-center justify-between p-4">
        <div className="flex items-center gap-8">
          {TABS.map((tab) => (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`relative flex items-center justify-center text-sm font-medium transition-colors uppercase cursor-pointer ${activeTab === tab.key ? "text-primary" : "text-primary/75 hover:text-primary"}`}>
              {tab.label}
              {activeTab === tab.key && <span className="absolute -bottom-1 left-0 h-[2px] w-full bg-primary transition-all duration-300" />}
            </button>
          ))}
        </div>
        <div className="flex gap-8">
          {DISABLED_TABS.map((tab) => (
            <span key={tab.label} className="relative flex cursor-not-allowed items-center justify-center text-sm font-medium text-primary/40 uppercase">{tab.label}</span>
          ))}
        </div>
      </nav>

      <div className="flex-1 overflow-y-auto min-h-0 no-scrollbar">
        {activeTab === "items" && <ItemsTab />}
        {activeTab === "enchants" && <EnchantsTab />}
        {activeTab === "aptitudes" && <PlaceholderTab label="Aptitudes" />}
        {activeTab === "spells" && <PlaceholderTab label="Sorts" />}
        {activeTab === "notes" && <PlaceholderTab label="Notes" />}
      </div>

      <RingSlotModal />
    </div>
  );
}

function RingSlotModal() {
  const { pendingRingItem, setPendingRingItem, equipItem } = useBuild();
  if (!pendingRingItem) return null;

  const handlePick = (slot: "ring-left" | "ring-right") => {
    equipItem(slot, pendingRingItem as unknown as Record<string, unknown>);
    setPendingRingItem(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70" onClick={() => setPendingRingItem(null)}>
      <div className="bg-bg-dark rounded-lg p-6 border border-gray-700 flex flex-col items-center gap-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-bagnard text-primary">Choisir le slot d anneau</h3>
        <div className="flex items-center gap-2 mb-2">
          <img width={32} height={32} alt={pendingRingItem.name} className="h-8 w-8" src={`https://cdn.wakfuli.com/items/${pendingRingItem.image_id}.webp`} />
          <span className="text-sm text-primary">{pendingRingItem.name}</span>
        </div>
        <div className="flex gap-6">
          <button onClick={() => handlePick("ring-left")}
            className="flex flex-col items-center gap-2 p-4 rounded-lg bg-bg-light hover:bg-cyan-wakfuli/10 border border-gray-700 hover:border-cyan-wakfuli/50 cursor-pointer transition-all">
            <img width={50} height={50} alt="ring-left" className="h-12 w-12" src="https://cdn.wakfuli.com/placeholders/ring-left.webp" />
            <span className="text-sm text-primary/80">Anneau gauche</span>
          </button>
          <button onClick={() => handlePick("ring-right")}
            className="flex flex-col items-center gap-2 p-4 rounded-lg bg-bg-light hover:bg-cyan-wakfuli/10 border border-gray-700 hover:border-cyan-wakfuli/50 cursor-pointer transition-all">
            <img width={50} height={50} alt="ring-right" className="h-12 w-12" src="https://cdn.wakfuli.com/placeholders/ring-right.webp" />
            <span className="text-sm text-primary/80">Anneau droit</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function EquipmentSlotIcon({ slot }: { slot: EquipmentSlot }) {
  const { build, unequipItem } = useBuild();
  const equipped = build.equipment[slot];
  const equippedItem = equipped?.item as WakfuItem | undefined;

  return (
    <div className="relative bg-bg-dark group">
      <div className={`relative flex items-center justify-center rounded-sm border-2 transition-colors duration-200 h-13 w-13 cursor-pointer ${equipped ? "border-cyan-wakfuli/60 bg-cyan-wakfuli/10" : "border-transparent hover:border-primary/80 hover:bg-bg-light/30"}`}
        onClick={() => equipped && unequipItem(slot)}
        title={equipped ? `${equippedItem?.name || slot} - clic pour retirer` : slot}>
        <span className="flex items-center justify-center h-13 w-13">
          <div className="h-full aspect-square flex items-center justify-center rounded bg-bg-dark p-1 border border-gray-700 transition-colors duration-200 hover:border-primary/80 hover:bg-bg-light/30">
            <div className="h-full w-full relative">
              {equippedItem ? (
                <img alt={equippedItem.name} width={50} height={50} className="w-full h-full object-contain"
                  src={`https://cdn.wakfuli.com/items/${equippedItem.image_id}.webp`}
                  onError={(e) => { (e.target as HTMLImageElement).src = `https://cdn.wakfuli.com/placeholders/${slot}.webp`; }} />
              ) : (
                <img alt={slot} width={50} height={50} className="w-full h-full object-contain" src={`https://cdn.wakfuli.com/placeholders/${slot}.webp`} />
              )}
            </div>
          </div>
        </span>
      </div>
      {equipped && (
        <div className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <Minus className="h-2.5 w-2.5 text-white" />
        </div>
      )}
    </div>
  );
}

function ItemsTab() {
  const { data: allItems, loading, error } = useWakfuData<WakfuItem[]>("all_items.json");
  const [search, setSearch] = useState("");
  const [levelMin, setLevelMin] = useState(186);
  const [levelMax, setLevelMax] = useState(230);
  const [activeTypes, setActiveTypes] = useState<Set<number>>(new Set());
  const [activeRarities, setActiveRarities] = useState<Set<Rarity>>(new Set());

  const toggleType = (id: number) => {
    setActiveTypes((prev) => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  };
  const toggleRarity = (r: Rarity) => {
    setActiveRarities((prev) => { const next = new Set(prev); if (next.has(r)) next.delete(r); else next.add(r); return next; });
  };
  const clearFilters = () => { setActiveTypes(new Set()); setActiveRarities(new Set()); setSearch(""); setLevelMin(1); setLevelMax(230); };

  const filteredItems = useMemo(() => {
    if (!allItems) return [];
    let items = allItems;
    items = items.filter((it) => it.level >= levelMin && it.level <= levelMax);
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter((it) => it.name.toLowerCase().includes(q) || String(it.id).includes(q));
    }
    if (activeTypes.size > 0) {
      items = items.filter((it) => it.types && it.types.some((t) => activeTypes.has(t)));
    }
    if (activeRarities.size > 0) {
      items = items.filter((it) => activeRarities.has(it.rarity));
    }
    return items.slice(0, 200);
  }, [allItems, search, levelMin, levelMax, activeTypes, activeRarities]);

  return (
    <div className="bg-bg-darker flex h-full flex-col gap-0 p-2">
      <div className="sticky top-0 z-10 bg-bg-darker pb-2">
        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex w-full items-center rounded-md text-sm justify-between relative h-12 min-w-48 flex-1 bg-bg-lighter">
              <div className="flex h-full items-center justify-center px-3 text-primary absolute pointer-events-none"><Search className="h-4 w-4" /></div>
              <input className="h-10 w-full bg-transparent py-2 text-sm outline-none placeholder:text-gray-500 flex-1 border-none px-10" placeholder="Rechercher des objets..." value={search} onChange={(e) => setSearch(e.target.value)} />
              {search && <button onClick={() => setSearch("")} className="flex h-full items-center justify-center px-3 text-primary hover:text-white/70 cursor-pointer absolute right-0"><X className="h-4 w-4" /></button>}
            </div>
            <div className="w-[500px] 2xl:w-[600px] flex items-center bg-bg-light px-4 py-2 rounded-md h-12 gap-3">
              <div className="text-sm text-white whitespace-nowrap">{levelMin} - {levelMax}</div>
              <div className="flex-1 flex items-center gap-2">
                <input type="range" min={1} max={230} value={levelMin} onChange={(e) => setLevelMin(Math.min(Number(e.target.value), levelMax))} className="flex-1 accent-cyan-wakfuli h-1" />
                <input type="range" min={1} max={230} value={levelMax} onChange={(e) => setLevelMax(Math.max(Number(e.target.value), levelMin))} className="flex-1 accent-cyan-wakfuli h-1" />
              </div>
            </div>
            <ActionButton icon={<Funnel />} />
            <ActionButton icon={<><ListOrdered /><ArrowDownWideNarrow /></>} />
            <ActionButton icon={<LayoutList />} />
            <ActionButton icon={<Heart className="text-primary" />} />
            <ActionButton icon={<Eye className="text-primary" />} />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="h-12 rounded-sm bg-bg-lighter p-2">
              <div className="flex items-center justify-center gap-2">
                {ITEM_TYPE_IDS.map((tid) => (
                  <button key={tid} onClick={() => toggleType(tid)} className={`inline-flex items-center justify-center rounded-md h-9 w-9 min-w-9 p-0 cursor-pointer transition-all ${activeTypes.has(tid) ? "bg-cyan-wakfuli/20 ring-1 ring-cyan-wakfuli" : "bg-bg-dark hover:bg-[#64769B]/50"}`}>
                    <img width={32} height={32} alt={`type-${tid}`} className="h-7 w-7" src={`https://cdn.wakfuli.com/itemTypes/${tid}.webp`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="flex h-12 items-center justify-center rounded-sm bg-bg-lighter px-2">
              <div className="flex items-center justify-center gap-2">
                {RARITIES.map((r) => (
                  <button key={r} onClick={() => toggleRarity(r)} className={`inline-flex items-center justify-center rounded-md h-9 w-9 min-w-9 p-0 cursor-pointer transition-all ${activeRarities.has(r) ? "bg-cyan-wakfuli/20 ring-1 ring-cyan-wakfuli" : "bg-bg-dark hover:bg-[#64769B]/50"}`}>
                    <img width={28} height={28} alt={r} className="h-[28px] w-[28px]" src={`https://cdn.wakfuli.com/rarity/${r}.webp`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="flex gap-2">
              <ActionButton icon={<ScrollText />} disabled />
              <ActionButton icon={<Hammer />} disabled />
              <ActionButton icon={<Eraser className="text-red-500" />} onClick={clearFilters} />
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar">
        {loading && <div className="flex items-center justify-center py-20 gap-3 text-primary/50"><Loader2 className="h-6 w-6 animate-spin" /><span>Chargement des items...</span></div>}
        {error && <div className="text-center text-red-400 py-20">Erreur: {error}<br /><span className="text-sm text-primary/40">Verifie que data/wakfuli/all_items.json existe</span></div>}
        {!loading && !error && (
          <>
            <div className="text-xs text-primary/30 px-2 pb-1">{filteredItems.length} items affiches{allItems ? ` / ${allItems.length} total` : ""}</div>
            <div className="grid grid-cols-2 gap-1">
              {filteredItems.length === 0
                ? <div className="text-center text-primary/40 col-span-2 py-20">Aucun item ne correspond aux filtres</div>
                : filteredItems.map((item, idx) => <ItemCard key={item.id} item={item} index={idx} />)
              }
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function ItemCard({ item, index }: { item: WakfuItem; index: number }) {
  const { equipItem, setPendingRingItem } = useBuild();
  const rc = RARITY_CSS[item.rarity] || "text-gray-400";
  const rl = RARITY_LABELS[item.rarity] || item.rarity;
  const bg = index % 2 === 0 ? "bg-bg-dark" : "bg-bg-light";

  const handleEquip = () => {
    if (!item.equipment_position || item.equipment_position.length === 0) return;
    const positions = item.equipment_position;

    // Si l item va sur LEFT_HAND ou RIGHT_HAND (anneau), ouvrir le choix
    if (positions.includes("LEFT_HAND") && positions.includes("RIGHT_HAND")) {
      setPendingRingItem(item);
      return;
    }

    const pos = positions[0];
    const slot = POSITION_TO_SLOT[pos];
    if (slot) {
      equipItem(slot, item as unknown as Record<string, unknown>);
    }
  };

  return (
    <div className={`${bg} rounded-md p-2 flex flex-col gap-1 border border-transparent hover:border-primary/20 transition-colors`}>
      <div className="flex items-start gap-2">
        <div className="h-10 w-10 rounded bg-bg-darker flex items-center justify-center shrink-0 overflow-hidden">
          <img width={40} height={40} alt={item.name} className="h-full w-full object-contain"
            src={`https://cdn.wakfuli.com/items/${item.image_id}.webp`}
            onError={(e) => { (e.target as HTMLImageElement).src = "https://cdn.wakfuli.com/placeholders/helmet.webp"; }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium truncate ${rc}`}>{item.name}</span>
            <span className="text-xs text-primary/30">#{item.id}</span>
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs bg-bg-card px-1.5 py-0.5 rounded">Niv. {item.level}</span>
            <span className={`text-xs px-1.5 py-0.5 rounded bg-bg-card ${rc}`}>{rl}</span>
          </div>
        </div>
      </div>
      {item.effects && item.effects.length > 0 && (
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
          {item.effects.slice(0, 4).map((eff, i) => (
            <span key={i} className="text-xs text-primary/60">
              {eff.format || `${eff.value > 0 ? "+" : ""}${eff.value} ${eff.type}`}
            </span>
          ))}
          {item.effects.length > 4 && <span className="text-xs text-primary/30">+{item.effects.length - 4}</span>}
        </div>
      )}
      <div className="flex items-center gap-1 mt-1">
        <button onClick={handleEquip} className="h-6 w-6 flex items-center justify-center rounded bg-bg-card hover:bg-cyan-wakfuli/20 cursor-pointer transition-colors" title="Equiper"><Plus className="h-3.5 w-3.5 text-cyan-wakfuli" /></button>
        <button className="h-6 w-6 flex items-center justify-center rounded bg-bg-card hover:bg-bg-lighter cursor-pointer transition-colors" title="Favori"><Heart className="h-3.5 w-3.5 text-primary/50" /></button>
        {item.encyclopedia_link && (
          <a href={item.encyclopedia_link} target="_blank" rel="noopener noreferrer" className="h-6 w-6 flex items-center justify-center rounded bg-bg-card hover:bg-bg-lighter cursor-pointer transition-colors" title="Encyclopedie">
            <ExternalLink className="h-3.5 w-3.5 text-primary/50" />
          </a>
        )}
        <button className="h-6 w-6 flex items-center justify-center rounded bg-bg-card hover:bg-bg-lighter cursor-pointer transition-colors" title="Masquer"><EyeOff className="h-3.5 w-3.5 text-primary/50" /></button>
      </div>
    </div>
  );
}

function ActionButton({ icon, disabled, onClick }: { icon: React.ReactNode; disabled?: boolean; onClick?: () => void }) {
  return (
    <button onClick={onClick} className={`aspect-square flex justify-center items-center h-12 w-auto gap-2 rounded-sm bg-bg-lighter p-2 ${disabled ? "cursor-not-allowed text-white/70" : "cursor-pointer hover:bg-bg-light"}`}>
      {icon}
    </button>
  );
}

// ============================================================
// Onglet Enchantement
// Source: reference/wakfuli/assets/api/builds -> runes[], sublimations[]
// Les runes augmentent les stats des slots d equipement
// Les sublimations sont des bonus speciaux (parchemins)
// ============================================================

const RUNE_SLOTS = [
  { slot: "helmet",      label: "Casque" },
  { slot: "neck",        label: "Amulette" },
  { slot: "chest",       label: "Plastron" },
  { slot: "ring-left",   label: "Anneau G." },
  { slot: "ring-right",  label: "Anneau D." },
  { slot: "legs",        label: "Bottes" },
  { slot: "back",        label: "Cape" },
  { slot: "shoulders",   label: "Epaulettes" },
  { slot: "belt",        label: "Ceinture" },
  { slot: "weapon-main", label: "Arme 1" },
  { slot: "weapon-off",  label: "Arme 2" },
  { slot: "accessory",   label: "Accessoire" },
  { slot: "pet",         label: "Familier" },
] as const;

const RUNE_STATS = [
  { key: "HP",          label: "PV",          max: 20 },
  { key: "DODGE",       label: "Esquive",     max: 10 },
  { key: "TACKLE",      label: "Tacle",       max: 10 },
  { key: "INIT",        label: "Initiative",  max: 10 },
  { key: "WILLPOWER",   label: "Volonté",     max: 10 },
  { key: "WISDOM",      label: "Sagesse",     max: 10 },
  { key: "PROSPECTION", label: "Prospection", max: 10 },
  { key: "DMG_IN_PERCENT", label: "Maîtrise Élem.", max: 20 },
] as const;

function EnchantsTab() {
  const { build } = useBuild();
  const [selectedSlot, setSelectedSlot] = useState<string>("helmet");
  const [runeValues, setRuneValues] = useState<Record<string, Record<string, number>>>({});

  const slotRunes = runeValues[selectedSlot] ?? {};
  const equippedItem = build.equipment[selectedSlot as keyof typeof build.equipment];
  const itemName = equippedItem
    ? (equippedItem.item as { name?: string })?.name ?? "Objet équipé"
    : null;

  const setRuneValue = (stat: string, val: number) => {
    setRuneValues(prev => ({
      ...prev,
      [selectedSlot]: {
        ...(prev[selectedSlot] ?? {}),
        [stat]: Math.max(0, Math.min(val, 20)),
      }
    }));
  };

  const totalRunePoints = Object.values(slotRunes).reduce((a, b) => a + b, 0);

  return (
    <div className="bg-bg-darker flex h-full flex-col p-3">
      {/* Selection du slot */}
      <div className="mb-3">
        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-2">
          Slot à enchanter
        </div>
        <div className="grid grid-cols-4 gap-1">
          {RUNE_SLOTS.map(rs => {
            const hasItem = !!build.equipment[rs.slot as keyof typeof build.equipment];
            return (
              <button
                key={rs.slot}
                onClick={() => setSelectedSlot(rs.slot)}
                className={`flex flex-col items-center gap-1 p-2 rounded text-[10px] transition-all cursor-pointer border ${
                  selectedSlot === rs.slot
                    ? "bg-cyan-wakfuli/10 border-cyan-wakfuli/30 text-cyan-wakfuli"
                    : hasItem
                      ? "bg-bg-light border-border text-primary/70 hover:border-border-light"
                      : "bg-bg-dark border-border/50 text-neutral-600"
                }`}
              >
                <img
                  src={hasItem
                    ? `https://cdn.wakfuli.com/items/${(build.equipment[rs.slot as keyof typeof build.equipment]?.item as { image_id?: number })?.image_id}.webp`
                    : `https://cdn.wakfuli.com/placeholders/${rs.slot}.webp`
                  }
                  alt={rs.label}
                  className="w-8 h-8"
                  onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }}
                />
                <span className="truncate w-full text-center">{rs.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Enchantement du slot selectionne */}
      <div className="flex-1">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold text-primary">
            {itemName ?? <span className="text-neutral-500 italic">Aucun objet équipé</span>}
          </div>
          <div className="text-xs text-neutral-500">
            Points: <span className={`font-bold ${totalRunePoints > 0 ? "text-cyan-wakfuli" : "text-neutral-600"}`}>{totalRunePoints}</span>
          </div>
        </div>

        {!equippedItem ? (
          <div className="flex items-center justify-center py-16 text-neutral-500 text-sm">
            Équipe un objet dans ce slot pour l&apos;enchanter
          </div>
        ) : (
          <div className="space-y-1">
            {RUNE_STATS.map(rs => {
              const val = slotRunes[rs.key] ?? 0;
              return (
                <div key={rs.key} className="flex items-center gap-2 bg-bg-dark rounded px-2 py-1.5">
                  <img
                    src={`https://cdn.wakfuli.com/stats/${rs.key}.webp`}
                    alt={rs.label}
                    className="w-5 h-5 flex-shrink-0"
                    onError={e => { (e.target as HTMLImageElement).style.visibility = "hidden"; }}
                  />
                  <span className="text-xs text-neutral-400 flex-1">{rs.label}</span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setRuneValue(rs.key, val - 1)}
                      className="w-5 h-5 flex items-center justify-center rounded bg-bg-lighter text-neutral-400 hover:text-primary hover:bg-bg-card cursor-pointer transition-colors text-xs"
                    >-</button>
                    <span className={`w-6 text-center text-xs font-bold tabular-nums ${val > 0 ? "text-cyan-wakfuli" : "text-neutral-600"}`}>
                      {val}
                    </span>
                    <button
                      onClick={() => setRuneValue(rs.key, val + 1)}
                      className="w-5 h-5 flex items-center justify-center rounded bg-bg-lighter text-neutral-400 hover:text-primary hover:bg-bg-card cursor-pointer transition-colors text-xs"
                    >+</button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section Sublimations */}
      <div className="mt-3 pt-3 border-t border-border">
        <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-2">
          Sublimations
        </div>
        <div className="text-xs text-neutral-500 text-center py-6 bg-bg-dark rounded">
          Recherche de sublimations — à implémenter
        </div>
      </div>
    </div>
  );
}

function PlaceholderTab({ label }: { label: string }) {
  return <div className="flex items-center justify-center h-full text-primary/40 text-lg">Onglet {label} - a implementer</div>;
}

