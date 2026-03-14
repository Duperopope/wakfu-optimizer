"use client";

export function LeftPanel() {
  return (
    <div className="flex flex-1 flex-col divide-y bg-bg-darker overflow-hidden h-full">
      {/* Build header: nom, classe, niveau */}
      <div className="flex h-10 items-center justify-center p-2 shrink-0">
        <input
          className="w-full bg-transparent border-none p-0 m-0 text-ellipsis whitespace-nowrap font-sans text-primary/50 focus:outline-none focus:ring-0 text-center"
          type="text"
          defaultValue="Mon Build"
        />
      </div>

      {/* Classe + niveau + actions */}
      <div className="flex items-center gap-2 w-full p-2">
        <div className="h-[72px] w-[72px] rounded bg-bg-light flex items-center justify-center">
          <img
            width={72}
            height={72}
            alt="class icon"
            className="h-[72px] w-[72px] cursor-pointer"
            src="https://cdn.wakfuli.com/breeds/huppermage.webp"
          />
        </div>
        <div className="flex flex-col w-28 justify-center text-left p-1">
          <span className="capitalize cursor-pointer font-bagnard">huppermage</span>
          <span>
            <span className="text-primary/50">Niveau</span>{" "}
            <span className="text-primary cursor-pointer">200</span>
          </span>
        </div>
      </div>

      {/* Stats — scrollable */}
      <div className="flex-1 overflow-y-auto min-h-0 no-scrollbar p-4">
        {/* Stats principales */}
        <div className="flex w-full flex-col gap-y-[2px] mb-3 overflow-hidden rounded-md">
          <div className="flex w-full gap-[2px]">
            <StatCell icon="HP" label="PV" value="2050" color="#ff515b" />
            <StatCell icon="AP" label="PA" value="6" color="#19c1ef" />
          </div>
          <div className="flex w-full gap-[2px]">
            <StatCell icon="MP" label="PM" value="3" color="#afd34c" />
            <StatCell icon="HUPPERMAGE_RESOURCE" label="BQ" value="500" color="#e1b900" />
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
            <StatCell icon="FEROCITY" label="% Coup critique" value="3%" color="rgb(var(--wakfuli-color-positive))" />
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
            <StatCell icon="WISDOM" label="Sagesse" value="30" color="rgb(var(--wakfuli-color-positive))" />
            <StatCell icon="PROSPECTION" label="Prospection" value="30" color="rgb(var(--wakfuli-color-positive))" />
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
            <StatCell icon="INDIRECT_DMG" label="Dommage indirects" value="0%" />
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
              style={{ color: color || "rgb(var(--wakfuli-color-neutral))" }}
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
