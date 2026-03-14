"use client";

import { useState, useCallback } from "react";
import { Navbar } from "@/components/shared/Navbar";
import { LeftPanel } from "@/components/builder/LeftPanel";
import { RightPanel } from "@/components/builder/RightPanel";

export function BuilderLayout() {
  const [leftWidth, setLeftWidth] = useState(30);
  const [dragging, setDragging] = useState(false);

  const handleMouseDown = useCallback(() => {
    setDragging(true);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!dragging) return;
      const container = e.currentTarget;
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const pct = (x / rect.width) * 100;
      const clamped = Math.min(Math.max(pct, 18), 50);
      setLeftWidth(clamped);
    },
    [dragging]
  );

  const handleMouseUp = useCallback(() => {
    setDragging(false);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-1 min-h-0 flex flex-col">
        <main className="h-[calc(100vh-50px)] overflow-hidden">
          <div
            className="flex h-full w-full"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            {/* --- Panneau gauche: Stats --- */}
            <div
              className="flex flex-col min-h-0 overflow-hidden"
              style={{ width: `${leftWidth}%`, flexShrink: 0 }}
            >
              <LeftPanel />
            </div>

            {/* --- Separateur draggable --- */}
            <div
              onMouseDown={handleMouseDown}
              className={`relative flex-shrink-0 w-[6px] cursor-col-resize group ${
                dragging ? "bg-cyan-wakfuli/40" : "bg-border hover:bg-cyan-wakfuli/30"
              } transition-colors`}
            >
              <div className="absolute inset-y-0 left-1/2 w-[2px] -translate-x-1/2 bg-gray-600 group-hover:bg-cyan-wakfuli/60 transition-colors" />
            </div>

            {/* --- Panneau droit: Equipement --- */}
            <div className="flex-1 min-w-0 flex flex-col overflow-hidden">
              <RightPanel />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
