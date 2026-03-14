"use client";

import { useState } from "react";
import { SLOT_ORDER, type EquipmentSlot, type BuilderTab } from "@/types/wakfu";
import { Funnel, ListOrdered, ArrowDownWideNarrow, LayoutList, Heart, Eye, Search, X, ScrollText, Hammer, Eraser } from "lucide-react";

const TABS: { key: BuilderTab; label: string; disabled?: boolean }[] = [
  { key: "items", label: "items" },
  { key: "enchants", label: "enchantement" },
  { key: "aptitudes", label: "aptitudes" },
  { key: "spells", label: "sorts" },
  { key: "notes", label: "notes" },
];

const DISABLED_TABS = [
  { label: "variantes", disabled: true },
  { label: "resume", disabled: true },
];

export function RightPanel() {
  const [activeTab, setActiveTab] = useState<BuilderTab>("items");
  const [search, setSearch] = useState("");

  return (
    <div className="flex flex-col h-full">
      {/* --- Barre equipement --- */}
      <div className="flex justify-between bg-bg-darker border-b border-gray-700 px-4 py-5 gap-6">
        <div className="flex flex-col xl:flex-row items-center gap-4">
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-md bg-bg-light hover:bg-bg-lighter cursor-pointer border-2 border-bg-lighter text-sm">
              Resistances auto.
            </button>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
            {SLOT_ORDER.map((slot) => (
              <EquipmentSlotIcon key={slot} slot={slot} />
            ))}
          </div>
        </div>
      </div>

      {/* --- Navigation onglets --- */}
      <nav className="bg-bg-darker flex h-[40px] items-center justify-between p-4">
        <div className="flex items-center gap-8">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`relative flex items-center justify-center text-sm font-medium transition-colors uppercase cursor-pointer ${
                activeTab === tab.key
                  ? "text-primary"
                  : "text-primary/75 hover:text-primary"
              }`}
            >
              {tab.label}
              {activeTab === tab.key && (
                <span className="absolute -bottom-1 left-0 h-[2px] w-full bg-primary transition-all duration-300" />
              )}
            </button>
          ))}
        </div>
        <div className="flex gap-8">
          {DISABLED_TABS.map((tab) => (
            <span
              key={tab.label}
              className="relative flex cursor-not-allowed items-center justify-center text-sm font-medium text-primary/40 uppercase"
            >
              {tab.label}
            </span>
          ))}
        </div>
      </nav>

      {/* --- Contenu de l onglet actif --- */}
      <div className="flex-1 overflow-y-auto min-h-0 no-scrollbar">
        {activeTab === "items" && <ItemsTab search={search} setSearch={setSearch} />}
        {activeTab === "enchants" && <PlaceholderTab label="Enchantements" />}
        {activeTab === "aptitudes" && <PlaceholderTab label="Aptitudes" />}
        {activeTab === "spells" && <PlaceholderTab label="Sorts" />}
        {activeTab === "notes" && <PlaceholderTab label="Notes" />}
      </div>
    </div>
  );
}

function EquipmentSlotIcon({ slot }: { slot: EquipmentSlot }) {
  return (
    <div className="relative bg-bg-dark">
      <div className="relative flex items-center justify-center rounded-sm border-2 border-transparent transition-colors duration-200 ease-in-out h-13 w-13 hover:border-primary/80 hover:bg-bg-light/30 cursor-pointer">
        <span className="flex items-center justify-center h-13 w-13">
          <div className="h-full aspect-square flex items-center justify-center rounded bg-bg-dark p-1 border border-gray-700 transition-colors duration-200 hover:border-primary/80 hover:bg-bg-light/30">
            <div className="h-full w-full relative">
              <img
                alt={slot}
                width={50}
                height={50}
                className="w-full h-full object-contain"
                src={`https://cdn.wakfuli.com/placeholders/${slot}.webp`}
              />
            </div>
          </div>
        </span>
      </div>
    </div>
  );
}

function ItemsTab({
  search,
  setSearch,
}: {
  search: string;
  setSearch: (v: string) => void;
}) {
  return (
    <div className="bg-bg-darker flex h-full flex-col gap-0 p-2">
      {/* --- Barre de recherche + filtres --- */}
      <div className="sticky top-0 z-10 bg-bg-darker pb-2">
        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            {/* Search input */}
            <div className="flex w-full items-center rounded-md text-sm justify-between relative h-12 min-w-48 flex-1 bg-bg-lighter">
              <div className="flex h-full items-center justify-center px-3 text-primary absolute pointer-events-none">
                <Search className="h-4 w-4" />
              </div>
              <input
                className="h-10 w-full bg-transparent py-2 text-sm outline-none placeholder:text-gray-500 flex-1 border-none px-10"
                placeholder="Rechercher des objets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              {search && (
                <button
                  onClick={() => setSearch("")}
                  className="flex h-full items-center justify-center px-3 text-primary hover:text-white/70 cursor-pointer absolute right-0"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Level slider placeholder */}
            <div className="w-[500px] 2xl:w-[600px] flex items-center bg-bg-light px-4 py-2 rounded-md h-12">
              <div className="text-sm text-white mr-4">186 - 200</div>
              <div className="flex-1 h-[2px] bg-gray-700 rounded relative">
                <div className="absolute left-[75%] right-[19%] h-full bg-white rounded" />
              </div>
            </div>

            {/* Action buttons */}
            <ActionButton icon={<Funnel />} />
            <ActionButton icon={<><ListOrdered /><ArrowDownWideNarrow /></>} />
            <ActionButton icon={<LayoutList />} />
            <ActionButton icon={<Heart className="text-primary" />} />
            <ActionButton icon={<Eye className="text-primary" />} />
          </div>

          {/* Type filters */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="h-12 rounded-sm bg-bg-lighter p-2">
              <div className="flex items-center justify-center gap-2">
                {[134,120,136,103,119,132,138,133,518,519,112,189,646,582].map((typeId) => (
                  <button
                    key={typeId}
                    className="inline-flex items-center hover:bg-[#64769B]/50 justify-center rounded-md bg-bg-dark h-9 w-9 min-w-9 p-0 cursor-pointer"
                  >
                    <img
                      width={32}
                      height={32}
                      alt={`type-${typeId}`}
                      className="h-7 w-7"
                      src={`https://cdn.wakfuli.com/itemTypes/${typeId}.webp`}
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Rarity filters */}
            <div className="flex h-12 items-center justify-center rounded-sm bg-bg-lighter px-2">
              <div className="flex items-center justify-center gap-2">
                {["COMMON","RARE","MYTHICAL","LEGENDARY","MEMORY","EPIC","RELIC"].map((r) => (
                  <button
                    key={r}
                    className="inline-flex items-center hover:bg-[#64769B]/50 justify-center rounded-md bg-bg-dark h-9 w-9 min-w-9 p-0 cursor-pointer"
                  >
                    <img
                      width={28}
                      height={28}
                      alt={r}
                      className="h-[28px] w-[28px]"
                      src={`https://cdn.wakfuli.com/rarity/${r}.webp`}
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Extra action buttons */}
            <div className="flex gap-2">
              <ActionButton icon={<ScrollText />} disabled />
              <ActionButton icon={<Hammer />} disabled />
              <ActionButton icon={<Eraser className="text-red-500" />} />
            </div>
          </div>
        </div>
      </div>

      {/* --- Item list placeholder --- */}
      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-2 gap-1">
          <div className="text-center text-primary/40 col-span-2 py-20">
            Items charges depuis data/wakfuli/all_items.json
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionButton({ icon, disabled }: { icon: React.ReactNode; disabled?: boolean }) {
  return (
    <button
      className={`aspect-square flex justify-center items-center h-12 w-auto gap-2 rounded-sm bg-bg-lighter p-2 ${
        disabled ? "cursor-not-allowed text-white/70" : "cursor-pointer"
      }`}
    >
      {icon}
    </button>
  );
}

function PlaceholderTab({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-center h-full text-primary/40 text-lg">
      Onglet {label} — a implementer
    </div>
  );
}
