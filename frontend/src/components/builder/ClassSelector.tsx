"use client";

import { useState } from "react";
import { useBuild, CLASSES } from "@/lib/BuildContext";
import type { WakfuClass } from "@/types/wakfu";
import { X } from "lucide-react";

export function ClassSelector() {
  const { build, setClass } = useBuild();
  const [open, setOpen] = useState(false);

  const handleSelect = (cls: WakfuClass) => {
    setClass(cls);
    setOpen(false);
  };

  return (
    <>
      <div className="flex items-center gap-3 w-full">
        {/* Icone de classe : clic ouvre la modale */}
        <img
          width={72}
          height={72}
          alt={build.characterClass}
          className="h-[72px] w-[72px] cursor-pointer shrink-0 rounded-lg hover:ring-2 hover:ring-cyan-wakfuli/40 transition-all"
          src={`https://cdn.wakfuli.com/breeds/${build.characterClass}.webp`}
          onClick={() => setOpen(true)}
        />
        {/* Infos texte : nom de classe (clic ouvre modale) + niveau (clic independant) */}
        <div className="flex flex-col justify-center text-left gap-0.5 min-w-0">
          <span
            className="capitalize cursor-pointer font-bagnard text-base truncate hover:text-cyan-wakfuli transition-colors"
            onClick={() => setOpen(true)}
          >
            {build.characterClass}
          </span>
          <LevelEditor />
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70" onClick={() => setOpen(false)}>
          <div className="bg-bg-dark rounded-lg p-6 w-[600px] max-h-[80vh] overflow-y-auto border border-gray-700" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bagnard text-primary">Choisir une classe</h2>
              <button onClick={() => setOpen(false)} className="text-primary/50 hover:text-primary cursor-pointer">
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="grid grid-cols-6 gap-3">
              {CLASSES.map((cls) => (
                <button
                  key={cls}
                  onClick={() => handleSelect(cls)}
                  className={`flex flex-col items-center gap-1 p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                    build.characterClass === cls
                      ? "bg-cyan-wakfuli/20 border border-cyan-wakfuli/50"
                      : "bg-bg-light hover:bg-bg-lighter border border-transparent"
                  }`}
                >
                  <img width={56} height={56} alt={cls} className="h-14 w-14" src={`https://cdn.wakfuli.com/breeds/${cls}.webp`} />
                  <span className="text-xs capitalize text-primary/80">{cls}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function LevelEditor() {
  const { build, setLevel } = useBuild();
  const [editing, setEditing] = useState(false);
  const [tempLevel, setTempLevel] = useState(String(build.level));

  const commit = () => {
    const n = parseInt(tempLevel, 10);
    if (!isNaN(n) && n >= 1 && n <= 230) setLevel(n);
    setEditing(false);
  };

  if (editing) {
    return (
      <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
        <span className="text-primary/50 text-sm">Niveau</span>
        <input
          type="number"
          min={1}
          max={230}
          value={tempLevel}
          onChange={(e) => setTempLevel(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => e.key === "Enter" && commit()}
          className="w-16 bg-bg-lighter text-primary text-center rounded px-1.5 py-0.5 text-sm border border-gray-600 focus:border-cyan-wakfuli focus:outline-none"
          autoFocus
        />
      </div>
    );
  }

  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        setTempLevel(String(build.level));
        setEditing(true);
      }}
      className="cursor-pointer text-left text-primary hover:text-cyan-wakfuli transition-colors"
    >
      <span className="text-primary/50 text-sm">Niveau</span> <span className="text-sm">{build.level}</span>
    </button>
  );
}
