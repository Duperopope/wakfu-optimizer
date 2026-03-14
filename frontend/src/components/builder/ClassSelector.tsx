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
      <div
        className="flex items-center gap-2 w-full cursor-pointer"
        onClick={() => setOpen(true)}
      >
        <img
          width={72}
          height={72}
          alt={`${build.characterClass} icon`}
          className="h-[72px] w-[72px]"
          src={`https://cdn.wakfuli.com/breeds/${build.characterClass}.webp`}
        />
        <div className="flex flex-col w-28 justify-center text-left p-1">
          <span className="capitalize cursor-pointer font-bagnard">
            {build.characterClass}
          </span>
          <LevelEditor />
        </div>
      </div>

      {/* Modal de selection de classe */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="bg-bg-dark rounded-lg p-6 w-[600px] max-h-[80vh] overflow-y-auto border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bagnard text-primary">
                Choisir une classe
              </h2>
              <button
                onClick={() => setOpen(false)}
                className="text-primary/50 hover:text-primary cursor-pointer"
              >
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
                  <img
                    width={56}
                    height={56}
                    alt={cls}
                    className="h-14 w-14"
                    src={`https://cdn.wakfuli.com/breeds/${cls}.webp`}
                  />
                  <span className="text-xs capitalize text-primary/80">
                    {cls}
                  </span>
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
    if (!isNaN(n)) setLevel(n);
    setEditing(false);
  };

  if (editing) {
    return (
      <div className="flex items-center gap-1">
        <span className="text-primary/50">Niveau</span>
        <input
          type="number"
          min={1}
          max={230}
          value={tempLevel}
          onChange={(e) => setTempLevel(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => e.key === "Enter" && commit()}
          className="w-14 bg-bg-lighter text-primary text-center rounded px-1 py-0.5 text-sm border border-gray-600 focus:border-cyan-wakfuli focus:outline-none"
          autoFocus
        />
      </div>
    );
  }

  return (
    <button
      onClick={() => {
        setTempLevel(String(build.level));
        setEditing(true);
      }}
      className="cursor-pointer text-left text-primary"
    >
      <span className="text-primary/50">Niveau</span> {build.level}
    </button>
  );
}
