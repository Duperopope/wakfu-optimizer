"""Genere le nouveau app.py v4.0 - Pierre Noire x Wakfuli Layout"""
import json, os
from pathlib import Path

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
MANIFEST = PROJECT / "MANIFEST.json"

# Mettre a jour le manifest pour inclure build_app.py
with open(MANIFEST, "r", encoding="utf-8") as f:
    m = json.load(f)
if "scripts/build_app.py" not in m["protected"]:
    m["protected"].append("scripts/build_app.py")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)

APP = PROJECT / "app.py"

code = r'''# =============================================================================
# WAKFU OPTIMIZER v4.0 — PIERRE NOIRE x WAKFULI LAYOUT
# Theme: Pierre Noire (fond sombre + accents or/bronze + Cinzel/Inter)
# Layout: Wakfuli by Ymoka (sidebar stats, grille slots, tabs underline)
# Moteur: Simulateur calibre < 0.3% + log combat temps reel
# Sources:
#   - Wakfuli CSS: wakfuli.com (variables --wakfuli-*)
#   - Devblog Interface 2.0: wakfu.com/en/mmorpg/news/devblog/tickets/1764381
#   - NiceGUI: nicegui.io/documentation
# =============================================================================

import json, os, sys, re, logging
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# --- Paths ---
PROJECT_ROOT = Path(r'H:\Code\Ankama Dev\wakfu-optimizer')
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR = PROJECT_ROOT / 'data' / 'extracted'
COMBAT_LOG = Path(r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log')

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(LOGS_DIR / 'app.log', encoding='utf-8')])
log = logging.getLogger('wakfu-opt')

from nicegui import ui, app

# =============================================================================
# DATA LOADING
# =============================================================================
def load_json(fn):
    fp = DATA_DIR / fn
    if not fp.exists():
        log.warning(f'Introuvable: {fp}')
        return [] if 'map' not in fn else {}
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    log.info(f'Charge: {fn} ({len(d)} entrees)')
    return d

ALL_ITEMS = load_json('all_items.json')
ALL_SPELLS = load_json('all_spells.json')
BREEDS = load_json('breeds.json')
SPELL_NAMES = load_json('spell_names.json')
ACTION_MAP = load_json('action_map.json')
ITEMS_INDEX = load_json('items_index.json')

CALIBRATION = {}
cal_path = DATA_DIR / 'sram_calibration.json'
if cal_path.exists():
    with open(cal_path, 'r', encoding='utf-8') as f:
        CALIBRATION = json.load(f)
    log.info(f'Calibration: {len(CALIBRATION.get("spells", {}))} sorts')

# =============================================================================
# EQUIPMENT SLOT DEFINITIONS
# =============================================================================
SLOTS = OrderedDict([
    ('HEAD',         {'n':'Casque',     'i':'deployed_code'}),
    ('SHOULDERS',    {'n':'Epaulettes', 'i':'safety_divider'}),
    ('NECK',         {'n':'Amulette',   'i':'token'}),
    ('CHEST',        {'n':'Plastron',   'i':'shield'}),
    ('BACK',         {'n':'Cape',       'i':'curtains'}),
    ('BELT',         {'n':'Ceinture',   'i':'horizontal_rule'}),
    ('LEGS',         {'n':'Bottes',     'i':'do_not_step'}),
    ('FIRST_WEAPON', {'n':'Arme 1H',    'i':'swords'}),
    ('SECOND_WEAPON',{'n':'Arme 2H / Bouclier','i':'security'}),
    ('LEFT_HAND',    {'n':'Anneau G',   'i':'radio_button_checked'}),
    ('RIGHT_HAND',   {'n':'Anneau D',   'i':'radio_button_checked'}),
    ('PET',          {'n':'Familier',   'i':'pets'}),
    ('MOUNT',        {'n':'Monture',    'i':'directions_run'}),
    ('ACCESSORY',    {'n':'Embleme',    'i':'military_tech'}),
])

ELEMENTS = {
    'Feu':     {'c':'#e74c3c','ic':'local_fire_department'},
    'Eau':     {'c':'#3498db','ic':'water_drop'},
    'Air':     {'c':'#2ecc71','ic':'air'},
    'Terre':   {'c':'#8b4513','ic':'landscape'},
    'Lumiere': {'c':'#f1c40f','ic':'light_mode'},
    'Neutre':  {'c':'#95a5a6','ic':'circle'},
}

# =============================================================================
# PLAYER PROFILE — L'Immortel (Sram 179) — Stats reelles 14/03/2026
# =============================================================================
P = {
    'name': "L'Immortel", 'class': 'Sram', 'breed_id': 4, 'level': 179,
    'hp': 8928, 'ap': 13, 'mp': 5, 'wp': 8,
    'mf': 808, 'mw': 808, 'me': 190, 'ma': 425,
    'mm': 1030, 'md': 0, 'mr': 585, 'mb': -90, 'mh': 0, 'mc': 456,
    'cc': 72, 'block': 37, 'dodge': 502, 'tackle': 252,
    'init': 90, 'di': 18, 'range': -1, 'prosp': 40, 'wisdom': 40,
    'heal_perf': 8, 'will': 0,
    'rf': 564, 'rw': 452, 're': 335, 'ra': 546,
    'rc': 0, 'rd': 10, 'armor_given': 0, 'armor_recv': 0, 'indirect_dmg': 0,
}

# =============================================================================
# DAMAGE ENGINE (calibrated)
# =============================================================================
def calc_dmg(name, crit=True, res=0):
    cal = CALIBRATION.get('spells', {}).get(name)
    if not cal:
        return {'d':0,'dot':0,'t':0,'e':'?','pa':0,'b':0,'m':0}
    b = cal.get('base', 0)
    pa = cal.get('pa', 0)
    dr = cal.get('dot_ratio', 0)
    e = cal.get('elem', cal.get('element', 'Feu'))
    em = {'Feu':P['mf'],'Eau':P['mw'],'Air':P['ma'],'Terre':P['me']}.get(e, 0)
    tm = em + P['mm'] + (P['mc'] if crit else 0)
    mult = (1 + tm/100) * (1.25 if crit else 1.0) * (1 + P['di']/100) * max(0, 1 - res/100)
    d = round(b * mult)
    dot = round(b * mult * dr)
    return {'d':d, 'dot':dot, 't':d+dot, 'e':e, 'pa':pa, 'b':b, 'm':round(mult,2)}

def get_mults():
    best = max(P['mf'], P['mw'], P['ma'], P['me'])
    dc = 1 + P['di']/100
    mc = round((1 + (best+P['mm']+P['mc'])/100) * 1.25 * dc, 2)
    mn = round((1 + (best+P['mm'])/100) * 1.0 * dc, 2)
    return mc, mn

MC, MN = get_mults()

def sim_rotation(res=0):
    cs = CALIBRATION.get('spells', {})
    spells = []
    for n, d in cs.items():
        pa = d.get('pa', 0)
        if pa <= 0: continue
        dm = calc_dmg(n, True, res)
        spells.append({'n':n, 'pa':pa, 'dm':dm, 'eff':dm['t']/pa if pa > 0 else 0})
    spells.sort(key=lambda x: -x['eff'])
    rot, left = [], P['ap']
    for s in spells:
        if left >= s['pa']:
            rot.append(s)
            left -= s['pa']
    return rot, P['ap'] - left

def res_pct(val, lvl):
    return round(val / (val + 5*lvl) * 100) if val > 0 else 0

log.info(f'Multiplicateurs: Crit x{MC}, Normal x{MN}')

# =============================================================================
# CSS — THEME PIERRE NOIRE
# =============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
:root {
    --bg-deep:#0d0d1a; --bg-main:#1a1a2e; --bg-panel:#1e1e35;
    --bg-card:#252545; --bg-hover:#2d2d55; --bg-input:#1c1c36;
    --gold:#c9a84c; --gold-light:#e8d48b; --gold-dark:#8b6914;
    --blue:#3a7bd5; --blue-dark:#2a4d6e;
    --text:#e8e6e3; --text-dim:#8a8a9a; --text-bright:#fff;
    --fire:#e74c3c; --water:#3498db; --air:#2ecc71; --earth:#8b4513; --light:#f1c40f;
    --border:#3a3a5c; --shadow:rgba(0,0,0,0.5);
}
body, .q-page { background:var(--bg-deep)!important; color:var(--text)!important; font-family:'Inter',sans-serif!important; }
.q-header { background:var(--bg-main)!important; border-bottom:1px solid var(--border)!important; min-height:48px!important; }
.q-card { background:var(--bg-panel)!important; color:var(--text)!important; }
.q-tab { color:var(--text-dim)!important; font-family:'Cinzel',serif!important; text-transform:uppercase!important; letter-spacing:1.5px!important; font-size:11px!important; }
.q-tab--active { color:var(--gold)!important; }
.q-tab-indicator { background:var(--gold)!important; }
.q-tab-panels { background:transparent!important; }
.q-field__control { background:var(--bg-card)!important; color:var(--text)!important; }

/* === SIDEBAR === */
.sidebar { background:var(--bg-main); border-right:1px solid var(--border); width:300px; overflow-y:auto; padding:16px; flex-shrink:0; }
.sidebar::-webkit-scrollbar { width:4px; }
.sidebar::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }

/* === SECTION TITLE === */
.sec { font-family:'Cinzel',serif; color:var(--gold); font-size:10px; letter-spacing:2px; text-transform:uppercase; margin:14px 0 8px; padding-bottom:4px; border-bottom:1px solid rgba(201,168,76,0.12); }

/* === STAT LINE === */
.sl { display:flex; justify-content:space-between; align-items:center; padding:2px 0; font-size:12px; }
.sl-label { color:var(--text-dim); display:flex; align-items:center; gap:5px; }
.sl-label .material-icons { font-size:14px; }
.sl-val { font-weight:600; }

/* === PANEL === */
.pnl { background:linear-gradient(145deg,var(--bg-panel),var(--bg-main)); border:1px solid var(--border); border-radius:8px; box-shadow:inset 0 1px 0 rgba(255,255,255,0.03), 0 4px 16px var(--shadow); position:relative; overflow:hidden; }
.pnl::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,var(--gold),transparent); opacity:0.3; }

/* === EQUIPMENT GRID (Wakfuli: grid-cols-9 grid-rows-2) === */
.eq-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:6px; padding:10px; background:var(--bg-main); border-radius:8px; border:1px solid var(--border); }
.eq-slot { aspect-ratio:1; border-radius:6px; background:var(--bg-input); border:1px solid var(--border); display:flex; flex-direction:column; align-items:center; justify-content:center; cursor:pointer; transition:all 0.15s; gap:2px; padding:4px; }
.eq-slot:hover { border-color:var(--gold); box-shadow:0 0 12px rgba(201,168,76,0.15); }
.eq-slot .material-icons { font-size:22px; color:var(--text-dim); transition:color 0.15s; }
.eq-slot:hover .material-icons { color:var(--gold); }
.eq-slot-label { font-size:8px; color:var(--text-dim); text-align:center; line-height:1; }

/* === SPELL TABLE === */
.sp-tbl { width:100%; border-collapse:separate; border-spacing:0 3px; }
.sp-tbl th { background:var(--bg-main); color:var(--gold); font-family:'Cinzel',serif; font-size:9px; text-transform:uppercase; letter-spacing:1.5px; padding:8px; text-align:left; }
.sp-tbl td { padding:7px 8px; background:var(--bg-card); font-size:12px; }
.sp-tbl tr:hover td { background:var(--bg-hover); }
.sp-tbl td:first-child { border-radius:5px 0 0 5px; }
.sp-tbl td:last-child { border-radius:0 5px 5px 0; }

/* === ELEMENT BADGE === */
.el { display:inline-flex; align-items:center; gap:3px; padding:2px 7px; border-radius:3px; font-size:10px; font-weight:600; }
.el-feu { background:rgba(231,76,60,0.12); color:var(--fire); }
.el-eau { background:rgba(52,152,219,0.12); color:var(--water); }
.el-air { background:rgba(46,204,113,0.12); color:var(--air); }
.el-terre { background:rgba(139,69,19,0.12); color:var(--earth); }
.el-lumiere { background:rgba(241,196,15,0.12); color:var(--light); }

/* === SUMMARY BOX === */
.sum { background:var(--bg-card); border-radius:6px; padding:12px; border-left:3px solid var(--gold); }

/* === SPELL CARD === */
.sp-card { display:flex; gap:10px; align-items:center; padding:10px; background:var(--bg-card); border-radius:6px; margin-bottom:5px; transition:all 0.15s; }
.sp-card:hover { background:var(--bg-hover); }

/* === CHIP === */
.chip { border-radius:5px; padding:6px 10px; text-align:center; }

/* === GOLD BUTTON === */
.btn-gold { background:linear-gradient(180deg,var(--gold),var(--gold-dark))!important; color:var(--bg-deep)!important; font-family:'Cinzel',serif!important; font-weight:600!important; border:none!important; border-radius:5px!important; text-transform:uppercase!important; letter-spacing:1px!important; }

/* === BIG/MED NUMBERS === */
.big { font-size:22px; font-weight:700; }
.med { font-size:16px; font-weight:600; }

/* === PCT BADGES === */
.pct { padding:1px 6px; border-radius:3px; font-size:11px; font-weight:600; }
.pct-g { background:rgba(46,204,113,0.15); color:var(--air); }
.pct-f { background:rgba(231,76,60,0.15); color:var(--fire); }
.pct-w { background:rgba(52,152,219,0.15); color:var(--water); }
.pct-e { background:rgba(139,69,19,0.15); color:var(--earth); }
.pct-a { background:rgba(46,204,113,0.15); color:var(--air); }

/* === MASTERY ROW === */
.mr { display:flex; align-items:center; gap:5px; font-size:12px; padding:2px 0; }

/* === COMBAT LOG === */
.log-box { font-family:'Courier New',monospace; font-size:11px; color:var(--text-dim); padding:10px; background:var(--bg-deep); border-radius:5px; max-height:450px; overflow-y:auto; border:1px solid var(--border); }

/* === SCROLLBAR === */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:var(--bg-deep); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--gold-dark); }
"""

# =============================================================================
# SIDEBAR HTML
# =============================================================================
def sidebar_html():
    s = P
    lvl = s['level']
    rp = lambda v: res_pct(v, lvl)

    def sl(icon, label, val, color='var(--text)'):
        return f'<div class="sl"><span class="sl-label"><span class="material-icons" style="color:{color}">{icon}</span>{label}</span><span class="sl-val" style="color:{color}">{val}</span></div>'

    return f'''
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,var(--gold),var(--gold-dark));border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(201,168,76,0.25);">
            <span style="font-size:24px;color:var(--bg-deep);font-weight:bold;font-family:Cinzel,serif;">S</span>
        </div>
        <div>
            <div style="font-weight:700;font-size:15px;font-family:Cinzel,serif;">{s["name"]}</div>
            <div style="font-size:11px;color:var(--text-dim);">{s["class"]} — Niveau {s["level"]}</div>
        </div>
    </div>

    <div style="display:flex;gap:10px;margin-bottom:12px;font-size:13px;font-weight:600;">
        <span><span style="color:var(--fire);">&#10084;</span> <span style="color:var(--fire);">{s["hp"]:,}</span></span>
        <span><span style="color:var(--blue);">&#9733;</span> <span style="color:var(--blue);">{s["ap"]}</span> PA</span>
        <span><span style="color:var(--air);">&#9650;</span> <span style="color:var(--air);">{s["mp"]}</span> PM</span>
        <span><span style="color:#9b59b6;">&#9830;</span> <span style="color:#9b59b6;">{s["wp"]}</span> PW</span>
    </div>

    <div class="sec">Maitrises</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:3px 16px;">
        <div class="mr"><span style="color:var(--fire);">&#9632;</span> Feu <strong style="color:var(--fire);margin-left:auto;">{s["mf"]}</strong></div>
        <div class="mr"><span style="color:var(--water);">&#9632;</span> Eau <strong style="color:var(--water);margin-left:auto;">{s["mw"]}</strong></div>
        <div class="mr"><span style="color:var(--earth);">&#9632;</span> Terre <strong style="color:var(--earth);margin-left:auto;">{s["me"]}</strong></div>
        <div class="mr"><span style="color:var(--air);">&#9632;</span> Air <strong style="color:var(--air);margin-left:auto;">{s["ma"]}</strong></div>
    </div>

    <div class="sec">Resistances</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:3px 16px;">
        <div class="mr"><span class="pct pct-f">{rp(s["rf"])}%</span> <span style="color:var(--text-dim);font-size:11px;">{s["rf"]}</span></div>
        <div class="mr"><span class="pct pct-w">{rp(s["rw"])}%</span> <span style="color:var(--text-dim);font-size:11px;">{s["rw"]}</span></div>
        <div class="mr"><span class="pct pct-e">{rp(s["re"])}%</span> <span style="color:var(--text-dim);font-size:11px;">{s["re"]}</span></div>
        <div class="mr"><span class="pct pct-a">{rp(s["ra"])}%</span> <span style="color:var(--text-dim);font-size:11px;">{s["ra"]}</span></div>
    </div>

    <div class="sec">Combat</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px 10px;">
        {sl("bolt","DI",f'<span class="pct pct-g">{s["di"]}%</span>',"var(--air)")}
        {sl("casino","Critique",f'<span class="pct pct-g">{s["cc"]}%</span>',"#e67e22")}
        {sl("block","Parade",f'{s["block"]}%',"var(--water)")}
        {sl("speed","Initiative",str(s["init"]))}
        {sl("swap_horiz","Esquive",str(s["dodge"]),"var(--blue)")}
        {sl("gps_fixed","Tacle",str(s["tackle"]),"#e67e22")}
        {sl("gps_not_fixed","Portee",str(s["range"]))}
        {sl("auto_stories","Sagesse",str(s["wisdom"]))}
    </div>

    <div class="sec">Maitrises secondaires</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px 10px;">
        {sl("sports_martial_arts","Melee",f'<strong style="color:var(--gold);">{s["mm"]}</strong>',"var(--gold)")}
        {sl("radar","Distance",str(s["md"]))}
        {sl("flash_on","Critique",str(s["mc"]),"#e67e22")}
        {sl("visibility","Dos",str(s["mr"]),"#9b59b6")}
        {sl("dangerous","Berserk",str(s["mb"]),"var(--fire)")}
        {sl("healing","Soin",str(s["mh"]))}
    </div>
    '''

# =============================================================================
# MAIN PAGE
# =============================================================================
@ui.page('/')
def main_page():
    ui.add_css(CSS)
    ui.dark_mode().enable()
    ui.colors(primary='#c9a84c', secondary='#2a4d6e', accent='#e67e22',
              dark='#1a1a2e', positive='#2ecc71', negative='#e74c3c',
              info='#3498db', warning='#f1c40f')

    cs = CALIBRATION.get('spells', {})

    # === HEADER ===
    with ui.header().classes('items-center justify-between px-4'):
        with ui.row().classes('items-center gap-3 no-wrap'):
            ui.html('<div style="width:36px;height:36px;background:linear-gradient(135deg,#c9a84c,#8b6914);border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 0 10px rgba(201,168,76,0.3);"><span style="font-size:18px;color:#0d0d1a;font-weight:bold;font-family:Cinzel,serif;">W</span></div>')
            ui.html('<span style="font-family:Cinzel,serif;font-size:16px;color:#c9a84c;letter-spacing:3px;">WAKFU OPTIMIZER</span>')
            ui.html('<span style="font-size:9px;color:#8a8a9a;background:rgba(201,168,76,0.1);padding:2px 6px;border-radius:3px;">v4.0</span>')
        ui.html(f'<span style="font-size:11px;color:#8a8a9a;">{P["name"]} &bull; {P["class"]} {P["level"]}</span>')

    # === BODY ===
    with ui.row().classes('w-full no-wrap items-stretch').style('min-height:calc(100vh - 48px);'):

        # --- SIDEBAR ---
        with ui.element('div').classes('sidebar'):
            ui.html(sidebar_html())

        # --- MAIN ---
        with ui.column().classes('flex-grow p-4 gap-2').style('min-width:0;'):

            # === EQUIPMENT GRID ===
            slots_html = ''
            for key, meta in SLOTS.items():
                slots_html += f'<div class="eq-slot" title="{meta["n"]}"><span class="material-icons">{meta["i"]}</span><span class="eq-slot-label">{meta["n"]}</span></div>'
            ui.html(f'<div class="eq-grid">{slots_html}</div>')

            # === TABS ===
            with ui.tabs().classes('w-full') as tabs:
                t_combat = ui.tab('COMBAT', icon='local_fire_department')
                t_items = ui.tab('ITEMS', icon='inventory_2')
                t_spells = ui.tab('SORTS', icon='auto_fix_high')
                t_stats = ui.tab('STATISTIQUES', icon='bar_chart')
                t_enchant = ui.tab('ENCHANTEMENT', icon='diamond')

            with ui.tab_panels(tabs, value=t_combat).classes('w-full'):

                # =============================================
                # TAB COMBAT (simulateur + log + validation)
                # =============================================
                with ui.tab_panel(t_combat).classes('p-0 pt-2'):
                    with ui.row().classes('w-full gap-3 no-wrap'):

                        # -- Colonne gauche: Simulateur --
                        with ui.column().classes('gap-3').style('flex:2;'):
                            with ui.element('div').classes('pnl p-4'):
                                ui.html('<div class="sec" style="margin-top:0;">Simulateur de degats</div>')
                                ui.html(f'<div style="font-size:11px;color:var(--text-dim);margin-bottom:12px;">Calibre sur Mannequin Kanjedo (0 res) — Ecart &lt; 0.3%</div>')

                                # Multipliers
                                ui.html(f'''<div style="display:flex;gap:10px;margin-bottom:14px;">
                                    <div style="flex:1;background:rgba(230,126,34,0.06);border:1px solid rgba(230,126,34,0.15);border-radius:6px;padding:8px;text-align:center;">
                                        <div style="font-size:9px;color:#e67e22;text-transform:uppercase;letter-spacing:1.5px;">Mult. Critique</div>
                                        <div class="big" style="color:#e67e22;">x{MC}</div>
                                    </div>
                                    <div style="flex:1;background:rgba(58,123,213,0.06);border:1px solid rgba(58,123,213,0.15);border-radius:6px;padding:8px;text-align:center;">
                                        <div style="font-size:9px;color:#3a7bd5;text-transform:uppercase;letter-spacing:1.5px;">Mult. Normal</div>
                                        <div class="big" style="color:#3a7bd5;">x{MN}</div>
                                    </div>
                                </div>''')

                                # Spell table
                                if cs:
                                    rows = ''
                                    for n in sorted(cs, key=lambda x: -cs[x].get('base',0)):
                                        d = calc_dmg(n, True)
                                        pa = d['pa']
                                        e = d['e']
                                        dpa = round(d['t']/pa) if pa > 0 else 0
                                        rows += f'''<tr>
                                            <td style="font-weight:500;">{n}</td>
                                            <td style="color:var(--blue);font-weight:600;text-align:center;">{pa}</td>
                                            <td><span class="el el-{e.lower()}">{e}</span></td>
                                            <td style="color:var(--text-dim);text-align:center;">{d["b"]}</td>
                                            <td style="color:#e67e22;font-weight:600;text-align:right;">{d["d"]:,}</td>
                                            <td style="color:#9b59b6;text-align:right;">{d["dot"]:,}</td>
                                            <td style="color:var(--gold);font-weight:700;text-align:right;">{d["t"]:,}</td>
                                            <td style="color:var(--air);text-align:right;">{dpa:,}</td>
                                        </tr>'''
                                    ui.html(f'''<table class="sp-tbl"><thead><tr>
                                        <th>Sort</th><th style="text-align:center;">PA</th><th>Elem</th>
                                        <th style="text-align:center;">Base</th><th style="text-align:right;">Crit</th>
                                        <th style="text-align:right;">DOT</th><th style="text-align:right;">Total</th>
                                        <th style="text-align:right;">DPT/PA</th></tr></thead>
                                        <tbody>{rows}</tbody></table>''')

                                # Rotation
                                rot, ap_used = sim_rotation()
                                ui.html('<div class="sec">Rotation optimale</div>')
                                chips = ''
                                for r in rot:
                                    ei = ELEMENTS.get(r['dm']['e'], ELEMENTS['Neutre'])
                                    c = ei['c']
                                    rc = f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.08)"
                                    chips += f'''<div class="chip" style="background:{rc};border:1px solid {c}22;">
                                        <div style="font-size:11px;font-weight:600;color:{c};">{r["n"]}</div>
                                        <div style="font-size:10px;color:var(--text-dim);">{r["pa"]} PA &rarr; {r["dm"]["t"]:,}</div>
                                    </div>'''
                                ui.html(f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">{chips}</div>')

                                td = sum(r['dm']['d'] for r in rot)
                                tt = sum(r['dm']['dot'] for r in rot)
                                ui.html(f'''<div class="sum">
                                    <div class="sl"><span class="sl-label">PA utilises</span><span class="sl-val" style="color:var(--blue);">{ap_used}/{P["ap"]}</span></div>
                                    <div class="sl"><span class="sl-label">Degats directs</span><span class="sl-val" style="color:#e67e22;">{td:,}</span></div>
                                    <div class="sl"><span class="sl-label">DOT</span><span class="sl-val" style="color:#9b59b6;">{tt:,}</span></div>
                                    <div style="border-top:1px solid rgba(201,168,76,0.15);margin-top:6px;padding-top:6px;">
                                        <div class="sl"><span style="font-family:Cinzel,serif;color:var(--gold);letter-spacing:1.5px;font-size:12px;">TOTAL</span>
                                        <span class="big" style="color:var(--gold);">{td+tt:,} PV</span></div>
                                    </div>
                                </div>''')

                        # -- Colonne droite: Log combat + Validation --
                        with ui.column().classes('gap-3').style('flex:1;min-width:300px;'):
                            with ui.element('div').classes('pnl p-4'):
                                ui.html('<div class="sec" style="margin-top:0;">Journal de combat</div>')
                                log_box = ui.html('<div class="log-box">En attente du log...</div>')

                                async def refresh_log():
                                    if not COMBAT_LOG.exists():
                                        log_box.content = '<div class="log-box" style="color:var(--fire);">Log introuvable</div>'
                                        return
                                    with open(COMBAT_LOG, 'r', encoding='utf-8', errors='replace') as f:
                                        lines = f.readlines()
                                    cb = [l for l in lines if any(k in l for k in ['combat','PV','lance le sort'])]
                                    last = cb[-50:] if cb else lines[-50:]
                                    h = ''
                                    for ln in last:
                                        lt = ln.rstrip()[:150]
                                        if 'Critiques' in lt or 'critique' in lt.lower():
                                            h += f'<div style="color:#e67e22;">{lt}</div>'
                                        elif 'PV' in lt and '-' in lt:
                                            h += f'<div style="color:var(--fire);">{lt}</div>'
                                        elif '+' in lt and 'PV' in lt:
                                            h += f'<div style="color:var(--air);">{lt}</div>'
                                        elif 'lance le sort' in lt:
                                            h += f'<div style="color:var(--blue);">{lt}</div>'
                                        else:
                                            h += f'<div>{lt}</div>'
                                    log_box.content = f'<div class="log-box">{h}</div>'

                                ui.button('Rafraichir', on_click=refresh_log).classes('btn-gold mt-2').style('font-size:11px;padding:5px 14px;')

                            with ui.element('div').classes('pnl p-4'):
                                ui.html(f'''<div class="sec" style="margin-top:0;">Validation</div>
                                    <div class="sl"><span class="sl-label">Precision</span><span class="sl-val" style="color:var(--air);">&lt; 0.3%</span></div>
                                    <div class="sl"><span class="sl-label">Mult. Crit</span><span class="sl-val" style="color:#e67e22;">x{MC}</span></div>
                                    <div class="sl"><span class="sl-label">Mult. Normal</span><span class="sl-val" style="color:var(--blue);">x{MN}</span></div>
                                    <div class="sl"><span class="sl-label">Sorts calibres</span><span class="sl-val" style="color:var(--gold);">{len(cs)}</span></div>
                                    <div style="margin-top:8px;font-size:10px;color:var(--text-dim);background:var(--bg-deep);padding:8px;border-radius:4px;font-family:monospace;">
                                    & .\\.venv\\Scripts\\python.exe scripts\\combat_validator.py</div>''')

                # =============================================
                # TAB ITEMS
                # =============================================
                with ui.tab_panel(t_items).classes('p-0 pt-2'):
                    with ui.element('div').classes('pnl p-4'):
                        ui.html('<div class="sec" style="margin-top:0;">Equipement</div>')
                        ui.html(f'<div style="color:var(--text-dim);font-size:12px;">Base de donnees: {len(ALL_ITEMS):,} items charges</div>')
                        ui.html('<div style="color:var(--text-dim);font-size:12px;margin-top:8px;">Selection d\'items a venir — cliquer sur un slot dans la grille ci-dessus pour filtrer les items compatibles.</div>')

                # =============================================
                # TAB SORTS
                # =============================================
                with ui.tab_panel(t_spells).classes('p-0 pt-2'):
                    with ui.element('div').classes('pnl p-4'):
                        ui.html('<div class="sec" style="margin-top:0;">Sorts actifs — Deck</div>')
                        if cs:
                            for n in sorted(cs, key=lambda x: -cs[x].get('base',0)):
                                d = calc_dmg(n, True)
                                dn = calc_dmg(n, False)
                                ei = ELEMENTS.get(d['e'], ELEMENTS['Neutre'])
                                ui.html(f'''<div class="sp-card" style="border-left:3px solid {ei["c"]};">
                                    <div style="width:44px;height:44px;background:var(--bg-deep);border-radius:6px;display:flex;align-items:center;justify-content:center;border:1px solid {ei["c"]}22;">
                                        <span class="material-icons" style="color:{ei["c"]};font-size:22px;">{ei["ic"]}</span>
                                    </div>
                                    <div style="flex:1;">
                                        <div style="display:flex;justify-content:space-between;align-items:center;">
                                            <span style="font-weight:600;font-size:14px;">{n}</span>
                                            <span class="el el-{d["e"].lower()}">{d["e"]}</span>
                                        </div>
                                        <div style="display:flex;gap:16px;margin-top:4px;font-size:11px;">
                                            <span style="color:var(--text-dim);">PA: <strong style="color:var(--blue);">{d["pa"]}</strong></span>
                                            <span style="color:var(--text-dim);">Base: <strong>{d["b"]}</strong></span>
                                            <span style="color:var(--text-dim);">Crit: <strong style="color:#e67e22;">{d["d"]:,}</strong></span>
                                            <span style="color:var(--text-dim);">Normal: <strong style="color:var(--blue);">{dn["d"]:,}</strong></span>
                                        </div>
                                    </div>
                                    <div style="text-align:right;">
                                        <div class="med" style="color:var(--gold);">{d["t"]:,}</div>
                                        <div style="font-size:9px;color:var(--text-dim);">total crit</div>
                                    </div>
                                </div>''')

                # =============================================
                # TAB STATISTIQUES
                # =============================================
                with ui.tab_panel(t_stats).classes('p-0 pt-2'):
                    with ui.element('div').classes('pnl p-4'):
                        ui.html('<div class="sec" style="margin-top:0;">Statistiques detaillees</div>')
                        ui.html('<div style="color:var(--text-dim);font-size:12px;">Vue detaillee des caracteristiques a venir — calcul en temps reel selon l\'equipement selectionne.</div>')

                # =============================================
                # TAB ENCHANTEMENT
                # =============================================
                with ui.tab_panel(t_enchant).classes('p-0 pt-2'):
                    with ui.element('div').classes('pnl p-4'):
                        ui.html('<div class="sec" style="margin-top:0;">Enchantements & Sublimations</div>')
                        ui.html('<div style="color:var(--text-dim);font-size:12px;">Systeme de sockets et sublimations a venir — necessite d\'abord l\'equipement d\'items.</div>')

# =============================================================================
# RUN
# =============================================================================
log.info(f'Joueur: {P["name"]} ({P["class"]} {P["level"]})')
log.info(f'Items: {len(ALL_ITEMS)}, Sorts: {len(ALL_SPELLS)}, Calibration: {len(CALIBRATION.get("spells",{}))} sorts')
ui.run(title='Wakfu Optimizer', port=8080, reload=False, show=True)
'''

APP.write_text(code, encoding='utf-8')
print(f"app.py v4.0 ecrit: {len(code):,} caracteres")
print("Lance avec: & \".\\\.venv\\Scripts\\python.exe\" app.py")
