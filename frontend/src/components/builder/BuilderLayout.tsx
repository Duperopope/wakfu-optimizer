"use client";

import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from "react-resizable-panels";
import { Navbar } from "@/components/shared/Navbar";
import { LeftPanel } from "@/components/builder/LeftPanel";
import { RightPanel } from "@/components/builder/RightPanel";

export function BuilderLayout() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-1 min-h-0 flex flex-col">
        <main className="h-[calc(100vh-50px)] overflow-hidden">
          <PanelGroup direction="horizontal" className="flex h-full w-full flex-1">
            {/* --- Panneau gauche: Stats (30%) --- */}
            <Panel defaultSize={30} minSize={20} maxSize={45}>
              <LeftPanel />
            </Panel>

            {/* --- Separateur draggable --- */}
            <PanelResizeHandle className="relative flex w-px items-center justify-center bg-border after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2 hover:bg-cyan-wakfuli/30 transition-colors" />

            {/* --- Panneau droit: Equipement (70%) --- */}
            <Panel defaultSize={70}>
              <RightPanel />
            </Panel>
          </PanelGroup>
        </main>
      </div>
    </div>
  );
}
