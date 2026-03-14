"""
Wakfu Optimizer - Builder
Version: 2.0
Stack: NiceGUI 3.8+ / Python 3.10
Data: API Wakfuli + Frontend Wakfuli
"""
import json
from pathlib import Path
from nicegui import ui, app

# =============================================================
# CONFIGURATION
# =============================================================
PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"

SLOT_ORDER = [
    "HEAD", "NECK", "CHEST", "BACK", "SHOULDERS", "BELT",
    "LEFT_HAND", "RIGHT_HAND", "LEGS",
    "FIRST_WEAPON", "SECOND_WEAPON", "ACCESSORY",
]

SLOT_LABELS = {
    "HEAD": "Casque", "NECK": "Amulette", "CHEST": "Plastron",
    "BACK": "Cape", "SHOULDERS": "Epaulettes", "BELT": "Ceinture",
    "LEFT_HAND": "Anneau G", "RIGHT_HAND": "Anneau D", "LEGS": "Bottes",
    "FIRST_WEAPON": "Arme 1", "SECOND_WEAPON": "Arme 2", "ACCESSORY": "Embleme",
}

RARITY_COLORS = {
    "COMMON": "#CCCCCC", "RARE": "#33CC33", "EPIC": "#FF9900",
    "LEGENDARY": "#FFCC00", "MYTHICAL": "#FF3366", "RELIC": "#CC33FF",
    "MEMORY": "#33CCFF", "OLD": "#999999",
}

RARITY_ORDER = ["MYTHICAL", "RELIC", "LEGENDARY", "EPIC", "RARE", "COMMON", "MEMORY", "OLD"]

ELEMENT_COLORS = {
    "FIRE": "#FF4444", "WATER": "#4488FF", "AIR": "#44DD44", "EARTH": "#CC8833",
}

CLASSES = [
    "cra", "ecaflip", "eliotrope", "eniripsa", "enutrof", "feca",
    "huppermage", "iop", "osamodas", "ouginak", "pandawa", "roublard",
    "sacrieur", "sadida", "sram", "steamer", "xelor", "zobal",
]

# =============================================================
# CHARGEMENT DES DONNEES
# =============================================================
def load_json(filename):
    path = DATA / filename
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    return []

print("Chargement des donnees...")
ALL_ITEMS = load_json("all_items.json")
ALL_SPELLS = load_json("all_spells.json")
ALL_ACTIONS = load_json("all_actions.json")

# Index items par position
ITEMS_BY_SLOT = {}
for item in ALL_ITEMS:
    for pos in item.get("equipment_position", []):
        if pos not in ITEMS_BY_SLOT:
            ITEMS_BY_SLOT[pos] = []
        ITEMS_BY_SLOT[pos].append(item)

# Trier chaque slot par level desc puis rarity
def rarity_sort_key(item):
    r = item.get("rarity", "COMMON")
    try:
        return RARITY_ORDER.index(r)
    except ValueError:
        return 99

for slot in ITEMS_BY_SLOT:
    ITEMS_BY_SLOT[slot].sort(key=lambda x: (-x.get("level", 0), rarity_sort_key(x)))

# Version
VERSION_DATA = load_json("version.json")
GAME_VERSION = VERSION_DATA.get("version", "inconnue") if isinstance(VERSION_DATA, dict) else "inconnue"

print(f"  Items: {len(ALL_ITEMS)}")
print(f"  Spells: {sum(len(v.get('elementary', [])) + len(v.get('active', [])) + len(v.get('passive', [])) for v in ALL_SPELLS.values()) if isinstance(ALL_SPELLS, dict) else 0}")
print(f"  Actions: {len(ALL_ACTIONS)}")
print(f"  Version: {GAME_VERSION}")
print("Pret.")


# =============================================================
# ETAT DU BUILDER
# =============================================================
class BuildState:
    def __init__(self):
        self.character_class = "cra"
        self.level = 200
        self.equipment = {}
        self.active_spells = []
        self.passive_spells = []

    def get_items_for_slot(self, slot, search="", rarity_filter=None, level_max=None):
        items = ITEMS_BY_SLOT.get(slot, [])
        if level_max is None:
            level_max = self.level
        filtered = []
        for it in items:
            if it.get("level", 0) > level_max:
                continue
            if rarity_filter and it.get("rarity") != rarity_filter:
                continue
            if search:
                name = it.get("name", "").lower()
                if search.lower() not in name:
                    continue
            filtered.append(it)
        return filtered[:50]

    def equip_item(self, slot, item):
        self.equipment[slot] = item

    def unequip_slot(self, slot):
        if slot in self.equipment:
            del self.equipment[slot]

    def get_total_stats(self):
        stats = {
            "HP": 0, "AP": 0, "MP": 0, "WP": 0, "RANGE": 0,
            "MASTERY": 0, "RESISTANCE": 0,
            "CRITICAL_HIT": 0, "CRITICAL_MASTERY": 0,
            "BLOCK": 0, "DODGE": 0, "LOCK": 0, "INITIATIVE": 0,
            "HEAL_MASTERY": 0, "BACK_MASTERY": 0, "BERSERK_MASTERY": 0,
            "DISTANCE_MASTERY": 0, "MELEE_MASTERY": 0,
            "FIRE_RES": 0, "WATER_RES": 0, "AIR_RES": 0, "EARTH_RES": 0,
        }
        type_map = {
            "HP": "HP", "AP": "AP", "MP": "MP", "WP": "WP", "RANGE": "RANGE",
            "DMG_IN_PERCENT": "MASTERY", "RES_IN_PERCENT": "RESISTANCE",
            "CRITICAL_HIT": "CRITICAL_HIT", "CRITICAL_MASTERY": "CRITICAL_MASTERY",
            "BLOCK": "BLOCK", "DODGE": "DODGE", "LOCK": "LOCK", "INIT": "INITIATIVE",
            "HEAL_IN_PERCENT": "HEAL_MASTERY", "REAR_MASTERY": "BACK_MASTERY",
            "BERSERK_MASTERY": "BERSERK_MASTERY",
            "DISTANCE_MASTERY": "DISTANCE_MASTERY", "MELEE_MASTERY": "MELEE_MASTERY",
            "FIRE_RES": "FIRE_RES", "WATER_RES": "WATER_RES",
            "AIR_RES": "AIR_RES", "EARTH_RES": "EARTH_RES",
        }
        for slot, item in self.equipment.items():
            for eff in item.get("effects", []):
                etype = eff.get("type")
                val = eff.get("value", 0)
                if etype and etype in type_map:
                    stats[type_map[etype]] += val
        return stats

    def get_class_spells(self):
        if not isinstance(ALL_SPELLS, dict):
            return {"elementary": [], "active": [], "passive": []}
        class_data = ALL_SPELLS.get(self.character_class, {})
        return {
            "elementary": class_data.get("elementary", []),
            "active": class_data.get("active", []),
            "passive": class_data.get("passive", []),
        }


# =============================================================
# INTERFACE NICEGUI
# =============================================================
@ui.page("/")
def main_page():
    state = BuildState()
    slot_containers = {}
    item_panel_visible = {"value": False}
    current_slot = {"value": None}
    search_input = {"value": ""}
    rarity_select = {"value": None}

    ui.dark_mode(True)

    # --- CSS ---
    ui.add_head_html("""
    <style>
        .slot-card { cursor: pointer; transition: all 0.2s; border: 2px solid #333; border-radius: 8px; padding: 8px; min-height: 80px; }
        .slot-card:hover { border-color: #FFD700; transform: scale(1.02); }
        .slot-card.equipped { border-color: #44AA44; }
        .item-row { cursor: pointer; padding: 8px; border-radius: 4px; transition: background 0.15s; }
        .item-row:hover { background: rgba(255, 215, 0, 0.1); }
        .rarity-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        .stat-bar { background: #1a1a2e; border-radius: 4px; padding: 4px 8px; margin: 2px 0; }
        .spell-card { border: 1px solid #444; border-radius: 6px; padding: 6px; transition: border-color 0.2s; }
        .spell-card:hover { border-color: #FFD700; }
        .element-fire { color: #FF4444; } .element-water { color: #4488FF; }
        .element-air { color: #44DD44; } .element-earth { color: #CC8833; }
        .tab-active { border-bottom: 3px solid #FFD700 !important; }
        body { font-family: 'Segoe UI', sans-serif; }
    </style>
    """)

    # ==========================================================
    # FONCTIONS DE MISE A JOUR
    # ==========================================================
    def refresh_stats():
        stats_container.clear()
        stats = state.get_total_stats()
        with stats_container:
            ui.label("Stats totales").classes("text-lg font-bold text-yellow-400 mb-2")
            primary = [("HP", stats["HP"]), ("AP", stats["AP"]), ("MP", stats["MP"]),
                       ("WP", stats["WP"]), ("Range", stats["RANGE"])]
            for name, val in primary:
                if val != 0:
                    with ui.row().classes("stat-bar w-full justify-between"):
                        ui.label(name).classes("text-white text-sm")
                        ui.label(str(val)).classes("text-yellow-300 text-sm font-bold")

            if stats["MASTERY"] > 0:
                ui.separator()
                ui.label("Maitrises").classes("text-sm font-bold text-blue-300 mt-1")
                masteries = [("Elementaire", stats["MASTERY"]), ("Critique", stats["CRITICAL_MASTERY"]),
                             ("Dos", stats["BACK_MASTERY"]), ("Berserk", stats["BERSERK_MASTERY"]),
                             ("Soin", stats["HEAL_MASTERY"]), ("Distance", stats["DISTANCE_MASTERY"]),
                             ("Melee", stats["MELEE_MASTERY"])]
                for name, val in masteries:
                    if val != 0:
                        with ui.row().classes("stat-bar w-full justify-between"):
                            ui.label(name).classes("text-white text-xs")
                            ui.label(str(val)).classes("text-blue-300 text-xs font-bold")

            if stats["RESISTANCE"] > 0:
                ui.separator()
                ui.label("Resistances").classes("text-sm font-bold text-green-300 mt-1")
                resistances = [("Elementaire", stats["RESISTANCE"]), ("Feu", stats["FIRE_RES"]),
                               ("Eau", stats["WATER_RES"]), ("Air", stats["AIR_RES"]),
                               ("Terre", stats["EARTH_RES"])]
                for name, val in resistances:
                    if val != 0:
                        with ui.row().classes("stat-bar w-full justify-between"):
                            ui.label(name).classes("text-white text-xs")
                            ui.label(str(val)).classes("text-green-300 text-xs font-bold")

            secondary = [("Coup Critique", stats["CRITICAL_HIT"]), ("Parade", stats["BLOCK"]),
                         ("Esquive", stats["DODGE"]), ("Tacle", stats["LOCK"]),
                         ("Initiative", stats["INITIATIVE"])]
            has_secondary = any(v != 0 for _, v in secondary)
            if has_secondary:
                ui.separator()
                ui.label("Secondaires").classes("text-sm font-bold text-purple-300 mt-1")
                for name, val in secondary:
                    if val != 0:
                        with ui.row().classes("stat-bar w-full justify-between"):
                            ui.label(name).classes("text-white text-xs")
                            ui.label(str(val)).classes("text-purple-300 text-xs font-bold")

    def refresh_slot(slot):
        container = slot_containers.get(slot)
        if not container:
            return
        container.clear()
        item = state.equipment.get(slot)
        with container:
            if item:
                rcolor = RARITY_COLORS.get(item.get("rarity", "COMMON"), "#CCC")
                ui.label(SLOT_LABELS.get(slot, slot)).classes("text-xs text-gray-400")
                ui.label(item.get("name", "?")).classes("text-sm font-bold").style(f"color: {rcolor}")
                lvl = item.get("level", 0)
                ui.label(f"Nv.{lvl}").classes("text-xs text-gray-500")
                with ui.row().classes("gap-1 flex-wrap"):
                    for eff in item.get("effects", [])[:4]:
                        fmt = eff.get("format", "")
                        if fmt:
                            ui.label(fmt).classes("text-xs text-gray-300")
            else:
                ui.label(SLOT_LABELS.get(slot, slot)).classes("text-sm text-gray-500")
                ui.label("Vide").classes("text-xs text-gray-600 italic")

    def open_item_panel(slot):
        current_slot["value"] = slot
        item_panel_visible["value"] = True
        search_input["value"] = ""
        rarity_select["value"] = None
        refresh_item_list()
        item_panel.set_visibility(True)

    def refresh_item_list():
        item_list_container.clear()
        slot = current_slot["value"]
        if not slot:
            return
        items = state.get_items_for_slot(slot, search_input["value"], rarity_select["value"])
        with item_list_container:
            ui.label(f"{SLOT_LABELS.get(slot, slot)} - {len(items)} items").classes("text-sm text-gray-400 mb-1")
            for it in items:
                rcolor = RARITY_COLORS.get(it.get("rarity", "COMMON"), "#CCC")
                with ui.card().classes("item-row w-full p-2").on("click", lambda e, i=it, s=slot: select_item(s, i)):
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.html(f'<span class="rarity-dot" style="background:{rcolor}"></span>')
                        with ui.column().classes("gap-0"):
                            ui.label(it.get("name", "?")).classes("text-sm font-bold").style(f"color: {rcolor}")
                            with ui.row().classes("gap-2"):
                                ui.label(f"Nv.{it.get('level', 0)}").classes("text-xs text-gray-400")
                                mastery = it.get("total_mastery", 0)
                                res = it.get("total_resistance", 0)
                                if mastery:
                                    ui.label(f"M:{mastery}").classes("text-xs text-blue-300")
                                if res:
                                    ui.label(f"R:{res}").classes("text-xs text-green-300")

    def select_item(slot, item):
        state.equip_item(slot, item)
        refresh_slot(slot)
        refresh_stats()
        item_panel.set_visibility(False)

    def unequip(slot):
        state.unequip_slot(slot)
        refresh_slot(slot)
        refresh_stats()

    def on_class_change(value):
        state.character_class = value
        state.equipment.clear()
        state.active_spells.clear()
        state.passive_spells.clear()
        for slot in SLOT_ORDER:
            refresh_slot(slot)
        refresh_stats()
        refresh_spells()

    def on_level_change(value):
        try:
            state.level = int(value)
        except (ValueError, TypeError):
            state.level = 200
        for slot in SLOT_ORDER:
            refresh_slot(slot)
        refresh_stats()

    def refresh_spells():
        spells_container.clear()
        class_spells = state.get_class_spells()
        with spells_container:
            for category, label in [("elementary", "Elementaires"), ("active", "Actifs"), ("passive", "Passifs")]:
                spells = class_spells.get(category, [])
                if not spells:
                    continue
                ui.label(f"{label} ({len(spells)})").classes("text-md font-bold text-yellow-400 mt-2 mb-1")
                with ui.row().classes("flex-wrap gap-2"):
                    for sp in spells:
                        tr = sp.get("translations", {}).get("fr", {})
                        name = tr.get("name", "?")
                        desc = tr.get("description", "")
                        element = sp.get("element", "")
                        ap = sp.get("apCost", 0)
                        mp = sp.get("mpCost", 0)
                        rng = sp.get("maxRange", 0)
                        unlock = sp.get("unlockLevel", 0)
                        eclass = "element-" + element.lower() if element else ""
                        with ui.card().classes("spell-card"):
                            ui.label(name).classes(f"text-sm font-bold {eclass}")
                            with ui.row().classes("gap-1"):
                                if ap: ui.label(f"{ap} PA").classes("text-xs text-blue-300")
                                if mp: ui.label(f"{mp} PM").classes("text-xs text-green-300")
                                if rng: ui.label(f"Po:{rng}").classes("text-xs text-gray-400")
                                if unlock > 1: ui.label(f"Nv.{unlock}").classes("text-xs text-gray-500")
                            if desc:
                                ui.tooltip(desc)

    # ==========================================================
    # LAYOUT PRINCIPAL
    # ==========================================================
    with ui.header().classes("bg-gray-900 border-b border-gray-700"):
        with ui.row().classes("w-full items-center gap-4 px-4"):
            ui.label("WAKFU OPTIMIZER").classes("text-xl font-bold text-yellow-400")
            ui.label(f"v{GAME_VERSION}").classes("text-xs text-gray-500")
            ui.select(
                options={c: c.capitalize() for c in CLASSES},
                value=state.character_class,
                on_change=lambda e: on_class_change(e.value),
            ).classes("w-40").props("dense dark")
            ui.number(
                label="Niveau", value=state.level, min=1, max=245,
                on_change=lambda e: on_level_change(e.value),
            ).classes("w-24").props("dense dark")

    with ui.row().classes("w-full h-full gap-0 p-0"):

        # --- COLONNE GAUCHE : EQUIPEMENT ---
        with ui.column().classes("w-1/4 p-3 bg-gray-800 overflow-y-auto").style("min-height: calc(100vh - 60px)"):
            ui.label("Equipement").classes("text-lg font-bold text-yellow-400 mb-2")
            for slot in SLOT_ORDER:
                slot_card = ui.card().classes("slot-card w-full mb-1")
                slot_card.on("click", lambda e, s=slot: open_item_panel(s))
                with slot_card:
                    slot_container = ui.column().classes("w-full gap-0")
                    slot_containers[slot] = slot_container
                    with slot_container:
                        ui.label(SLOT_LABELS.get(slot, slot)).classes("text-sm text-gray-500")
                        ui.label("Vide").classes("text-xs text-gray-600 italic")
                with ui.row().classes("w-full justify-end -mt-2"):
                    ui.button(icon="close", on_click=lambda e, s=slot: unequip(s)).props("flat dense round size=xs").classes("text-red-400")

        # --- COLONNE CENTRE : SORTS ---
        with ui.column().classes("w-1/2 p-3 overflow-y-auto").style("min-height: calc(100vh - 60px)"):
            spells_container = ui.column().classes("w-full")
            refresh_spells()

        # --- COLONNE DROITE : STATS ---
        with ui.column().classes("w-1/4 p-3 bg-gray-800 overflow-y-auto").style("min-height: calc(100vh - 60px)"):
            stats_container = ui.column().classes("w-full")
            refresh_stats()

    # --- PANEL ITEMS (overlay) ---
    with ui.dialog() as item_panel:
        with ui.card().classes("w-96 max-h-screen bg-gray-900"):
            ui.label("Choisir un item").classes("text-lg font-bold text-yellow-400 mb-2")
            with ui.row().classes("w-full gap-2 mb-2"):
                ui.input(
                    placeholder="Rechercher...",
                    on_change=lambda e: (search_input.update({"value": e.value}), refresh_item_list()),
                ).classes("flex-grow").props("dense dark clearable")
                ui.select(
                    options={"": "Toutes", **{r: r.capitalize() for r in RARITY_ORDER}},
                    value="",
                    on_change=lambda e: (rarity_select.update({"value": e.value if e.value else None}), refresh_item_list()),
                ).classes("w-32").props("dense dark")
            item_list_container = ui.column().classes("w-full overflow-y-auto gap-1").style("max-height: 70vh")


# =============================================================
# LANCEMENT
# =============================================================
print("=" * 50)
print("WAKFU OPTIMIZER")
print(f"  Version jeu : {GAME_VERSION}")
print(f"  Items       : {len(ALL_ITEMS)}")
print(f"  Classes     : {len(CLASSES)}")
print("  URL         : http://localhost:8080")
print("=" * 50)

ui.run(title="Wakfu Optimizer", port=8080, reload=False)
