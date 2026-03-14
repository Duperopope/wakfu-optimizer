# =============================================================================
# WAKFU OPTIMIZER v3.2 — PIERRE NOIRE x WAKFULI
# Visuel: Wakfu Interface 2.0/2.1 (pierre noire + or)
# Structure UX: Wakfuli by Ymoka (sidebar stats + slots horizontaux + tabs)
# Notre plus: Simulateur de degats calibre + Validateur combat temps reel
# Sources:
#   - Wakfuli: https://wakfuli.com/builder (Ymoka)
#   - Devblog Interface 2.0: https://www.wakfu.com/en/mmorpg/news/devblog/tickets/1764381
#   - Devblog Build Management: https://www.wakfu.com/en/mmorpg/news/devblog/tickets/1760571
#   - NiceGUI: https://nicegui.io/documentation
# =============================================================================

import json, os, sys, re, logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, OrderedDict

# --- Logging ---
PROJECT_ROOT = Path(r'H:\Code\Ankama Dev\wakfu-optimizer')
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR = PROJECT_ROOT / 'data' / 'extracted'

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(LOGS_DIR / 'app.log', encoding='utf-8')])
log = logging.getLogger('wakfu-optimizer')

from nicegui import ui, app

# =============================================================================
# DATA
# =============================================================================
def load_json(fn):
    fp = DATA_DIR / fn
    if not fp.exists():
        log.warning(f'Introuvable: {fp}')
        return [] if 'map' not in fn else {}
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    log.info(f'{fn}: {len(d)} entrees')
    return d

all_items = load_json('all_items.json')
all_spells = load_json('all_spells.json')
all_static_effects = load_json('all_static_effects.json')
all_states = load_json('all_states.json')
breeds_data = load_json('breeds.json')
spell_names_data = load_json('spell_names.json')
ACTION_MAP = load_json('action_map.json')

calibration_path = DATA_DIR / 'sram_calibration.json'
CALIBRATION = {}
if calibration_path.exists():
    with open(calibration_path, 'r', encoding='utf-8') as f:
        CALIBRATION = json.load(f)
    log.info(f'Calibration: {len(CALIBRATION.get("spells", {}))} sorts')

# =============================================================================
# CONSTANTS
# =============================================================================
SLOTS = OrderedDict([
    ('HEAD',         {'n':'Casque',     'i':'deployed_code'}),
    ('SHOULDERS',    {'n':'Epaulettes', 'i':'safety_divider'}),
    ('NECK',         {'n':'Amulette',   'i':'token'}),
    ('CHEST',        {'n':'Plastron',   'i':'shield'}),
    ('BACK',         {'n':'Cape',       'i':'curtains'}),
    ('BELT',         {'n':'Ceinture',   'i':'horizontal_rule'}),
    ('LEGS',         {'n':'Bottes',     'i':'do_not_step'}),
    ('FIRST_WEAPON', {'n':'Arme',       'i':'swords'}),
    ('SECOND_WEAPON',{'n':'Bouclier',   'i':'security'}),
    ('LEFT_HAND',    {'n':'Anneau G',   'i':'radio_button_checked'}),
    ('RIGHT_HAND',   {'n':'Anneau D',   'i':'radio_button_checked'}),
    ('PET',          {'n':'Familier',   'i':'pets'}),
    ('MOUNT',        {'n':'Monture',    'i':'directions_run'}),
    ('ACCESSORY',    {'n':'Embleme',    'i':'military_tech'}),
])

EI = {
    'Feu':     {'c':'#e74c3c','ic':'local_fire_department'},
    'Eau':     {'c':'#3498db','ic':'water_drop'},
    'Air':     {'c':'#2ecc71','ic':'air'},
    'Terre':   {'c':'#8b4513','ic':'landscape'},
    'Lumiere': {'c':'#f1c40f','ic':'light_mode'},
    'Neutre':  {'c':'#95a5a6','ic':'circle'},
}

BREEDS = {1:'Feca',2:'Osamodas',3:'Enutrof',4:'Sram',5:'Xelor',6:'Ecaflip',
    7:'Eniripsa',8:'Iop',9:'Cra',10:'Sadida',11:'Sacrieur',12:'Pandawa',
    13:'Roublard',14:'Zobal',15:'Ouginak',16:'Steamer',17:'Eliotrope',
    18:'Huppermage',19:'Forgelance'}

# =============================================================================
# PLAYER PROFILE (stats reelles in-game 14/03/2026)
# =============================================================================
S = {
    'name': "L'Immortel", 'class': 'Sram', 'breed_id': 4, 'level': 179,
    'hp': 8928, 'ap': 13, 'mp': 5, 'wp': 8,
    'mf': 808, 'mw': 808, 'me': 190, 'ma': 425,
    'mm': 1030, 'md': 0, 'mr': 585, 'mb': -90, 'mh': 0, 'mc': 456,
    'cc': 72, 'block': 37, 'dodge': 502, 'tackle': 252,
    'init': 90, 'di': 18, 'range': -1,  'prosp': 40, 'wisdom': 40,
    'heal_perf': 8, 'will': 0,
    'rf': 564, 'rw': 452, 're': 335, 'ra': 546,
    'rc': 0, 'rd': 10, 'armor_given': 0, 'armor_recv': 0,
    'indirect_dmg': 0,
}

# =============================================================================
# DAMAGE ENGINE
# =============================================================================
def calc_dmg(spell_name, crit=True, res=0):
    cal = CALIBRATION.get('spells', {}).get(spell_name)
    if not cal:
        return {'d':0,'dot':0,'t':0,'e':'?','pa':0,'b':0,'m':0}
    b = cal.get('base', 0)
    pa = cal.get('pa', 0)
    dr = cal.get('dot_ratio', 0)
    e = cal.get('element', 'Feu')
    em = {'Feu':S['mf'],'Eau':S['mw'],'Air':S['ma'],'Terre':S['me']}.get(e, 0)
    tm = em + S['mm'] + (S['mc'] if crit else 0)
    mm = 1 + tm/100
    cm = 1.25 if crit else 1.0
    dm = 1 + S['di']/100
    rm = max(0, 1 - res/100)
    full = mm * cm * dm * rm
    d = round(b * full)
    dot = round(b * full * dr)
    return {'d':d, 'dot':dot, 't':d+dot, 'e':e, 'pa':pa, 'b':b, 'm':round(full,2)}

def get_mults():
    best = max(S['mf'], S['mw'], S['ma'], S['me'])
    tc = best + S['mm'] + S['mc']
    tn = best + S['mm']
    dc = 1 + S['di']/100
    return round((1+tc/100)*1.25*dc, 2), round((1+tn/100)*1.0*dc, 2)

MC, MN = get_mults()

def sim_rotation(res=0):
    cs = CALIBRATION.get('spells', {})
    spells = []
    for n, d in cs.items():
        pa = d.get('pa', 0)
        if pa <= 0: continue
        dm = calc_dmg(n, True, res)
        spells.append({'n':n,'pa':pa,'dm':dm,'eff':dm['t']/pa})
    spells.sort(key=lambda x: -x['eff'])
    rot, left = [], S['ap']
    for s in spells:
        if left >= s['pa']:
            rot.append(s)
            left -= s['pa']
    return rot, S['ap']-left

def res_pct(val, lvl):
    return round(val/(val+5*lvl)*100) if val > 0 else 0

# =============================================================================
# CSS
# =============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
:root {
    --d0:#0d0d1a; --d1:#1a1a2e; --d2:#1e1e35; --d3:#252545; --d4:#2d2d55; --d5:#1c1c36;
    --g:#c9a84c; --gl:#e8d48b; --gd:#8b6914; --bl:#3a7bd5; --b:#2a4d6e;
    --t:#e8e6e3; --td:#8a8a9a; --tw:#fff;
    --fire:#e74c3c; --water:#3498db; --air:#2ecc71; --earth:#8b4513; --light:#f1c40f;
    --brd:#3a3a5c; --bg:rgba(201,168,76,0.25); --sh:rgba(0,0,0,0.5);
}
body,.q-page{background:var(--d0)!important;color:var(--t)!important;font-family:'Inter',sans-serif!important}
.q-header{background:var(--d1)!important;border-bottom:1px solid var(--brd)!important;min-height:42px!important}
.q-card{background:var(--d2)!important;color:var(--t)!important}
.q-tab{color:var(--td)!important;font-family:'Cinzel',serif!important;text-transform:uppercase!important;letter-spacing:1px!important;font-size:11px!important}
.q-tab--active{color:var(--g)!important}
.q-tab-indicator{background:var(--g)!important}
.q-tab-panels{background:transparent!important}
.q-field__control{background:var(--d3)!important;color:var(--t)!important}

/* Sidebar Wakfuli */
.wk-sidebar{background:var(--d1);border-right:1px solid var(--brd);width:300px;overflow-y:auto;padding:12px;flex-shrink:0}
.wk-sidebar::-webkit-scrollbar{width:5px}
.wk-sidebar::-webkit-scrollbar-thumb{background:var(--brd);border-radius:3px}

/* Section headers (Wakfuli style) */
.wk-section{font-family:'Cinzel',serif;color:var(--g);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;margin:12px 0 6px;padding-bottom:4px;border-bottom:1px solid rgba(201,168,76,0.15)}
.wk-section:first-child{margin-top:0}

/* Stat line Wakfuli */
.wk-sl{display:flex;justify-content:space-between;align-items:center;padding:2px 0;font-size:12px}
.wk-sl-l{color:var(--td);display:flex;align-items:center;gap:5px}
.wk-sl-l .material-icons{font-size:14px}
.wk-sl-v{font-weight:600}

/* Mastery row with icon */
.wk-mr{display:flex;align-items:center;gap:4px;font-size:12px;padding:1px 0}

/* Panel */
.wk-p{background:linear-gradient(145deg,var(--d2),var(--d1));border:1px solid var(--brd);border-radius:8px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.04),0 4px 16px var(--sh);position:relative}
.wk-p::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.35}

/* Equipment bar (horizontal slots like Wakfuli top bar) */
.wk-eqbar{display:flex;gap:4px;flex-wrap:wrap;padding:8px;background:var(--d1);border-radius:6px;border:1px solid var(--brd)}
.wk-eq{width:42px;height:42px;border-radius:5px;background:var(--d5);border:1px solid var(--brd);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all 0.15s}
.wk-eq:hover{border-color:var(--g);box-shadow:0 0 8px rgba(201,168,76,0.2)}
.wk-eq .material-icons{font-size:18px;color:var(--td)}
.wk-eq:hover .material-icons{color:var(--g)}

/* Item card Wakfuli */
.wk-item{background:var(--d3);border:1px solid var(--brd);border-radius:6px;padding:10px;margin-bottom:6px;transition:all 0.15s}
.wk-item:hover{border-color:var(--g);background:var(--d4)}
.wk-item-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.wk-item-name{font-weight:600;font-size:13px}
.wk-item-meta{font-size:10px;color:var(--td)}
.wk-rarity-leg{color:#e8d48b;border:1px solid rgba(232,212,139,0.3);background:rgba(232,212,139,0.08);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.wk-rarity-myth{color:#b070dd;border:1px solid rgba(176,112,221,0.3);background:rgba(176,112,221,0.08);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.wk-rarity-epic{color:#e67e22;border:1px solid rgba(230,126,34,0.3);background:rgba(230,126,34,0.08);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}

/* Spell table */
.wk-tbl{width:100%;border-collapse:separate;border-spacing:0 2px}
.wk-tbl th{background:var(--d1);color:var(--g);font-family:'Cinzel',serif;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:7px 8px;text-align:left}
.wk-tbl td{padding:6px 8px;background:var(--d3);font-size:12px}
.wk-tbl tr:hover td{background:var(--d4)}
.wk-tbl td:first-child{border-radius:4px 0 0 4px}
.wk-tbl td:last-child{border-radius:0 4px 4px 0}

/* Element badge */
.el{display:inline-flex;align-items:center;gap:3px;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.el-feu{background:rgba(231,76,60,0.12);color:var(--fire)}
.el-eau{background:rgba(52,152,219,0.12);color:var(--water)}
.el-air{background:rgba(46,204,113,0.12);color:var(--air)}
.el-terre{background:rgba(139,69,19,0.12);color:var(--earth)}
.el-lumiere{background:rgba(241,196,15,0.12);color:var(--light)}

/* Summary */
.wk-sum{background:var(--d3);border-radius:5px;padding:10px 12px;border-left:3px solid var(--g)}

/* Chip */
.wk-chip{border-radius:4px;padding:5px 8px;text-align:center}

/* Big nums */
.wk-big{font-size:20px;font-weight:700}
.wk-med{font-size:15px;font-weight:600}

/* Gold btn */
.wk-btn{background:linear-gradient(180deg,var(--g),var(--gd))!important;color:var(--d0)!important;font-family:'Cinzel',serif!important;font-weight:600!important;border:none!important;border-radius:4px!important;text-transform:uppercase!important;letter-spacing:1px!important}

/* Green badge for % values (like Wakfuli) */
.wk-pct{background:rgba(46,204,113,0.15);color:var(--air);padding:1px 5px;border-radius:3px;font-size:11px;font-weight:600}
.wk-pct-fire{background:rgba(231,76,60,0.15);color:var(--fire)}
.wk-pct-water{background:rgba(52,152,219,0.15);color:var(--water)}
.wk-pct-air{background:rgba(46,204,113,0.15);color:var(--air)}
.wk-pct-earth{background:rgba(139,69,19,0.15);color:var(--earth)}

/* Aptitude categories (Wakfuli colored cards) */
.wk-apt{border-radius:6px;padding:10px;border:1px solid}
.wk-apt-int{background:rgba(46,204,113,0.06);border-color:rgba(46,204,113,0.25)}
.wk-apt-force{background:rgba(230,126,34,0.06);border-color:rgba(230,126,34,0.25)}
.wk-apt-agi{background:rgba(241,196,15,0.06);border-color:rgba(241,196,15,0.25)}
.wk-apt-chance{background:rgba(176,112,221,0.06);border-color:rgba(176,112,221,0.25)}
.wk-apt-maj{background:rgba(58,123,213,0.06);border-color:rgba(58,123,213,0.25)}

/* Scrollbar */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--d0)}
::-webkit-scrollbar-thumb{background:var(--brd);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--gd)}
"""

# =============================================================================
# SIDEBAR — Replique exacte de la sidebar Wakfuli
# =============================================================================
def build_sidebar_html():
    s = S
    lvl = s['level']
    # Maitrise + Resistances header
    mt = s['mf'] + s['mw'] + s['me'] + s['ma']  # approx total
    rt = s['rf'] + s['rw'] + s['re'] + s['ra']

    def sl(icon, label, val, color='var(--t)'):
        return f'<div class="wk-sl"><span class="wk-sl-l"><span class="material-icons" style="color:{color};">{icon}</span>{label}</span><span class="wk-sl-v" style="color:{color};">{val}</span></div>'

    def rpct(val):
        return res_pct(val, lvl)

    html = f'''
    <!-- Avatar + Class -->
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:48px;height:48px;background:linear-gradient(135deg,var(--g),var(--gd));border-radius:8px;
            display:flex;align-items:center;justify-content:center;box-shadow:0 0 12px rgba(201,168,76,0.3);">
            <span style="font-size:22px;color:var(--d0);font-weight:bold;">S</span>
        </div>
        <div>
            <div style="font-weight:600;font-size:14px;">{s["name"]}</div>
            <div style="font-size:11px;color:var(--td);">{s["class"]} — Niveau {s["level"]}</div>
        </div>
    </div>

    <!-- PA/PM/PW bar (Wakfuli style) -->
    <div style="display:flex;gap:8px;margin:8px 0;font-size:13px;font-weight:600;">
        <span><span style="color:var(--fire);">&#10084;</span> PV <span style="color:var(--fire);">{s["hp"]:,}</span></span>
        <span><span style="color:var(--bl);">&#9733;</span> PA <span style="color:var(--bl);">{s["ap"]}</span></span>
        <span><span style="color:var(--air);">&#9650;</span> PM <span style="color:var(--air);">{s["mp"]}</span></span>
        <span><span style="color:#9b59b6;">W</span> PW <span style="color:#9b59b6;">{s["wp"]}</span></span>
    </div>

    <!-- Maitrises et Resistances -->
    <div class="wk-section">Maitrises et Resistances</div>
    <div style="font-size:11px;color:var(--td);margin-bottom:6px;">
        &#128200; Maitrise totale: <strong style="color:var(--t);">{mt}</strong>
        &nbsp;&bull;&nbsp; Resistance totale: <strong style="color:var(--t);">{rt}</strong>
    </div>

    <!-- Element masteries with colors (Wakfuli grid) -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 12px;margin-bottom:6px;">
        <div class="wk-mr"><span style="color:var(--fire);">&#128293;</span> <strong style="color:var(--fire);">{s["mf"]}</strong></div>
        <div class="wk-mr"><span style="color:var(--water);">&#128167;</span> <strong style="color:var(--water);">{s["mw"]}</strong></div>
        <div class="wk-mr"><span style="color:var(--earth);">&#127759;</span> <strong style="color:var(--earth);">{s["me"]}</strong></div>
        <div class="wk-mr"><span style="color:var(--air);">&#127811;</span> <strong style="color:var(--air);">{s["ma"]}</strong></div>
    </div>
    <!-- Resistance % -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 12px;margin-bottom:4px;font-size:11px;">
        <div class="wk-mr"><span class="wk-pct-fire">{rpct(s["rf"])}% ({s["rf"]})</span></div>
        <div class="wk-mr"><span class="wk-pct-water">{rpct(s["rw"])}% ({s["rw"]})</span></div>
        <div class="wk-mr"><span class="wk-pct-earth">{rpct(s["re"])}% ({s["re"]})</span></div>
        <div class="wk-mr"><span class="wk-pct-air">{rpct(s["ra"])}% ({s["ra"]})</span></div>
    </div>

    <!-- Combat -->
    <div class="wk-section">Combat</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px 8px;">
        {sl("bolt","Dommages infliges",f'<span class="wk-pct">{s["di"]}%</span>',"var(--air)")}
        {sl("favorite","Soins realises",f'{s["heal_perf"]}%',"var(--td)")}
        {sl("casino","% Coup critique",f'<span class="wk-pct">{s["cc"]}%</span>',"#e67e22")}
        {sl("block","% Parade",f'{s["block"]}%',"var(--water)")}
        {sl("speed","Initiative",str(s["init"]),"var(--td)")}
        {sl("gps_not_fixed","Portee",str(s["range"]),"var(--td)")}
        {sl("swap_horiz","Esquive",str(s["dodge"]),"var(--bl)")}
        {sl("gps_fixed","Tacle",str(s["tackle"]),"#e67e22")}
        {sl("auto_stories","Sagesse",str(s["wisdom"]),"var(--td)")}
        {sl("search","Prospection",str(s["prosp"]),"var(--td)")}
        {sl("psychology","Volonte",str(s["will"]),"var(--td)")}
    </div>

    <!-- Secondaire -->
    <div class="wk-section">Secondaire</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px 8px;">
        {sl("flash_on","Maitrise critique",str(S["mc"]),"#e67e22")}
        {sl("shield","Resistance critique",str(S["rc"]),"var(--td)")}
        {sl("visibility","Maitrise dos",str(S["mr"]),"#9b59b6")}
        {sl("shield","Resistance dos",str(S["rd"]),"var(--td)")}
        {sl("sports_martial_arts","Maitrise melee",f'<strong style="color:var(--g);">{S["mm"]}</strong>',"var(--g)")}
        {sl("shield","Armure donnee",f'{S["armor_given"]}%',"var(--td)")}
        {sl("radar","Maitrise distance",str(S["md"]),"var(--td)")}
        {sl("shield","Armure recue",f'{S["armor_recv"]}%',"var(--td)")}
        {sl("healing","Maitrise soin",str(S["mh"]),"var(--td)")}
        {sl("blur_on","Dommage indirects",f'{S["indirect_dmg"]}%',"var(--td)")}
        {sl("dangerous","Maitrise berserk",str(S["mb"]),"var(--fire)")}
    </div>
    '''
    return html


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
    with ui.header().classes('items-center justify-between px-4 py-1'):
        with ui.row().classes('items-center gap-3 no-wrap'):
            ui.html('<div style="width:32px;height:32px;background:linear-gradient(135deg,#c9a84c,#8b6914);border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 0 8px rgba(201,168,76,0.3);"><span style="font-size:16px;color:#0d0d1a;font-weight:bold;">W</span></div>')
            ui.html('<div style="font-family:Cinzel,serif;font-size:15px;color:#c9a84c;letter-spacing:2px;">WAKFU OPTIMIZER</div>')
            ui.html('<div style="font-size:9px;color:#8a8a9a;margin-left:-8px;">v3.2 CALIBRE</div>')
        ui.html(f'<div style="font-size:11px;color:#8a8a9a;">{S["name"]} &bull; {S["class"]} Niv.{S["level"]}</div>')

    # === BODY: Sidebar + Content (Wakfuli layout) ===
    with ui.row().classes('w-full no-wrap items-stretch').style('min-height:calc(100vh - 50px);'):

        # --- SIDEBAR GAUCHE (permanente comme Wakfuli) ---
        with ui.element('div').classes('wk-sidebar'):
            ui.html(build_sidebar_html())

        # --- MAIN CONTENT ---
        with ui.column().classes('flex-grow p-3 gap-0').style('min-width:0;'):

            # Equipment bar horizontale (Wakfuli top)
            slots_html = ''
            for key, meta in SLOTS.items():
                slots_html += f'<div class="wk-eq" title="{meta["n"]}"><span class="material-icons">{meta["i"]}</span></div>'
            ui.html(f'<div class="wk-eqbar" style="margin-bottom:8px;">{slots_html}</div>')

            # Tabs
            with ui.tabs().classes('w-full') as tabs:
                t_items = ui.tab('ITEMS', icon='inventory_2')
                t_spells = ui.tab('SORTS', icon='auto_fix_high')
                t_enchant = ui.tab('ENCHANTEMENT', icon='diamond')
                t_combat = ui.tab('COMBAT', icon='local_fire_department')
                t_calib = ui.tab('CALIBRATION', icon='science')

            with ui.tab_panels(tabs, value=t_items).classes('w-full'):

                # ===== TAB ITEMS =====
                with ui.tab_panel(t_items).classes('p-0 pt-2'):
                    with ui.element('div').classes('wk-p p-4'):
                        ui.html('<div class="wk-section" style="margin-top:0;">SIMULATEUR DE DEGATS</div>')
                        ui.html(f'<div style="font-size:11px;color:var(--td);margin-bottom:10px;">Calibre sur Mannequin Kanjedo (0 res) — Ecart &lt; 0.3%</div>')

                        # Multipliers
                        ui.html(f'''<div style="display:flex;gap:8px;margin-bottom:12px;">
                            <div style="flex:1;background:rgba(230,126,34,0.08);border:1px solid rgba(230,126,34,0.2);border-radius:5px;padding:6px;text-align:center;">
                                <div style="font-size:9px;color:#e67e22;text-transform:uppercase;letter-spacing:1px;">Mult. Critique</div>
                                <div class="wk-big" style="color:#e67e22;">x{MC}</div>
                            </div>
                            <div style="flex:1;background:rgba(58,123,213,0.08);border:1px solid rgba(58,123,213,0.2);border-radius:5px;padding:6px;text-align:center;">
                                <div style="font-size:9px;color:#3a7bd5;text-transform:uppercase;letter-spacing:1px;">Mult. Normal</div>
                                <div class="wk-big" style="color:#3a7bd5;">x{MN}</div>
                            </div>
                        </div>''')

                        # Spell damage table
                        if cs:
                            rows = ''
                            for n in sorted(cs, key=lambda x: -cs[x].get('base',0)):
                                d = calc_dmg(n, True)
                                pa = d['pa']
                                e = d['e']
                                dpa = round(d['t']/pa) if pa > 0 else 0
                                rows += f'''<tr>
                                    <td style="font-weight:500;">{n}</td>
                                    <td style="color:var(--bl);font-weight:600;text-align:center;">{pa}</td>
                                    <td><span class="el el-{e.lower()}">{e}</span></td>
                                    <td style="color:var(--td);text-align:center;">{d["b"]}</td>
                                    <td style="color:#e67e22;font-weight:600;text-align:right;">{d["d"]:,}</td>
                                    <td style="color:#9b59b6;text-align:right;">{d["dot"]:,}</td>
                                    <td style="color:var(--g);font-weight:700;text-align:right;">{d["t"]:,}</td>
                                    <td style="color:var(--air);text-align:right;">{dpa:,}</td>
                                </tr>'''
                            ui.html(f'''<table class="wk-tbl"><thead><tr>
                                <th>Sort</th><th style="text-align:center;">PA</th><th>Elem</th>
                                <th style="text-align:center;">Base</th><th style="text-align:right;">Crit</th>
                                <th style="text-align:right;">DOT</th><th style="text-align:right;">Total</th>
                                <th style="text-align:right;">DPT/PA</th></tr></thead>
                                <tbody>{rows}</tbody></table>''')

                        # Rotation
                        rot, ap_used = sim_rotation()
                        ui.html('<div class="wk-section">ROTATION OPTIMALE</div>')
                        chips = ''
                        for r in rot:
                            ei = EI.get(r['dm']['e'], EI['Neutre'])
                            c = ei['c']
                            chips += f'''<div class="wk-chip" style="background:rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.08);border:1px solid {c}25;">
                                <div style="font-size:11px;font-weight:600;color:{c};">{r["n"]}</div>
                                <div style="font-size:10px;color:var(--td);">{r["pa"]} PA &rarr; {r["dm"]["t"]:,}</div>
                            </div>'''
                        ui.html(f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px;">{chips}</div>')

                        td = sum(r['dm']['d'] for r in rot)
                        tt = sum(r['dm']['dot'] for r in rot)
                        ui.html(f'''<div class="wk-sum">
                            <div class="wk-sl"><span class="wk-sl-l">PA utilises</span><span class="wk-sl-v" style="color:var(--bl);">{ap_used}/{S["ap"]}</span></div>
                            <div class="wk-sl"><span class="wk-sl-l">Degats directs</span><span class="wk-sl-v" style="color:#e67e22;">{td:,}</span></div>
                            <div class="wk-sl"><span class="wk-sl-l">DOT</span><span class="wk-sl-v" style="color:#9b59b6;">{tt:,}</span></div>
                            <div style="border-top:1px solid var(--bg);margin-top:4px;padding-top:4px;">
                                <div class="wk-sl"><span style="font-family:Cinzel,serif;color:var(--g);letter-spacing:1px;font-size:12px;">TOTAL</span>
                                <span class="wk-big" style="color:var(--g);">{td+tt:,} PV</span></div>
                            </div>
                        </div>''')

                # ===== TAB SORTS =====
                with ui.tab_panel(t_spells).classes('p-0 pt-2'):
                    with ui.element('div').classes('wk-p p-4'):
                        ui.html('<div class="wk-section" style="margin-top:0;">SORTS ACTIFS — DECK</div>')
                        if cs:
                            for n in sorted(cs, key=lambda x: -cs[x].get('base',0)):
                                d = calc_dmg(n, True)
                                dn = calc_dmg(n, False)
                                ei = EI.get(d['e'], EI['Neutre'])
                                ui.html(f'''<div style="display:flex;gap:10px;align-items:center;padding:8px;
                                    background:var(--d3);border-radius:5px;margin-bottom:4px;border-left:3px solid {ei["c"]};">
                                    <div style="width:40px;height:40px;background:var(--d0);border-radius:5px;display:flex;
                                        align-items:center;justify-content:center;border:1px solid {ei["c"]}25;">
                                        <span class="material-icons" style="color:{ei["c"]};font-size:20px;">{ei["ic"]}</span>
                                    </div>
                                    <div style="flex:1;">
                                        <div style="display:flex;justify-content:space-between;align-items:center;">
                                            <span style="font-weight:600;font-size:13px;">{n}</span>
                                            <span class="el el-{d["e"].lower()}">{d["e"]}</span>
                                        </div>
                                        <div style="display:flex;gap:14px;margin-top:3px;font-size:11px;">
                                            <span style="color:var(--td);">PA: <strong style="color:var(--bl);">{d["pa"]}</strong></span>
                                            <span style="color:var(--td);">Base: <strong>{d["b"]}</strong></span>
                                            <span style="color:var(--td);">Crit: <strong style="color:#e67e22;">{d["d"]:,}</strong></span>
                                            <span style="color:var(--td);">Normal: <strong style="color:var(--bl);">{dn["d"]:,}</strong></span>
                                            <span style="color:var(--td);">DOT: <strong style="color:#9b59b6;">{d["dot"]:,}</strong></span>
                                        </div>
                                    </div>
                                    <div style="text-align:right;">
                                        <div class="wk-med" style="color:var(--g);">{d["t"]:,}</div>
                                        <div style="font-size:9px;color:var(--td);">total crit</div>
                                    </div>
                                </div>''')

                # ===== TAB ENCHANTEMENT =====
                with ui.tab_panel(t_enchant).classes('p-0 pt-2'):
                    with ui.element('div').classes('wk-p p-4'):
                        ui.html('''<div class="wk-section" style="margin-top:0;">ENCHANTEMENT & SUBLIMATIONS</div>
                            <div style="font-size:12px;color:var(--td);line-height:1.8;">
                            Cette section sera activee quand les items seront equipes.<br>
                            Le systeme de sockets (rouge/vert/bleu) et de sublimations sera integre
                            avec le meme principe que Wakfuli : grille par slot + recherche de sublimations.<br><br>
                            <strong style="color:var(--g);">Prochaine etape :</strong> Equiper les items depuis l'onglet ITEMS
                            pour debloquer les enchantements.
                            </div>''')

                # ===== TAB COMBAT =====
                with ui.tab_panel(t_combat).classes('p-0 pt-2'):
                    with ui.row().classes('w-full gap-3 no-wrap'):
                        with ui.column().classes('gap-3').style('flex:1;'):
                            with ui.element('div').classes('wk-p p-4'):
                                ui.html('<div class="wk-section" style="margin-top:0;">JOURNAL DE COMBAT</div>')
                                log_box = ui.html('<div style="font-family:monospace;font-size:11px;color:var(--td);padding:8px;background:var(--d0);border-radius:4px;max-height:400px;overflow-y:auto;">En attente...</div>')

                                async def do_refresh():
                                    lp = Path(r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log')
                                    if not lp.exists():
                                        log_box.content = '<div style="color:var(--fire);">Log introuvable</div>'
                                        return
                                    with open(lp, 'r', encoding='utf-8', errors='replace') as f:
                                        lines = f.readlines()
                                    cb = [l for l in lines if 'combat' in l.lower() or 'PV' in l or 'lance le sort' in l]
                                    last = cb[-40:] if cb else lines[-40:]
                                    h = ''
                                    for ln in last:
                                        lt = ln.rstrip()[:140]
                                        if 'Critiques' in lt: h += f'<div style="color:#e67e22;">{lt}</div>'
                                        elif 'PV' in lt and '-' in lt: h += f'<div style="color:var(--fire);">{lt}</div>'
                                        elif '+' in lt and 'PV' in lt: h += f'<div style="color:var(--air);">{lt}</div>'
                                        elif 'lance le sort' in lt: h += f'<div style="color:var(--bl);">{lt}</div>'
                                        else: h += f'<div>{lt}</div>'
                                    log_box.content = f'<div style="font-family:monospace;font-size:11px;color:var(--td);padding:8px;background:var(--d0);border-radius:4px;max-height:400px;overflow-y:auto;">{h}</div>'

                                ui.button('Rafraichir', on_click=do_refresh).classes('wk-btn mt-2').style('font-size:11px;padding:4px 12px;')

                        with ui.column().classes('gap-3').style('width:280px;flex-shrink:0;'):
                            with ui.element('div').classes('wk-p p-4'):
                                ui.html(f'''<div class="wk-section" style="margin-top:0;">VALIDATEUR</div>
                                    <div style="font-size:11px;color:var(--td);margin-bottom:10px;">Compare degats reels vs simulation</div>
                                    <div class="wk-sum"><div style="font-size:10px;color:var(--t);line-height:2;">
                                        <code style="color:var(--bl);font-size:10px;">cd "H:\\Code\\Ankama Dev\\wakfu-optimizer"</code><br>
                                        <code style="color:var(--bl);font-size:10px;">& .\\.venv\\Scripts\\python.exe scripts\\combat_validator.py</code>
                                    </div></div>
                                    <div style="margin-top:10px;">
                                        <div class="wk-sl"><span class="wk-sl-l">Precision</span><span class="wk-sl-v" style="color:var(--air);">&lt; 0.3%</span></div>
                                        <div class="wk-sl"><span class="wk-sl-l">Mult. Crit</span><span class="wk-sl-v" style="color:#e67e22;">x{MC}</span></div>
                                        <div class="wk-sl"><span class="wk-sl-l">Mult. Normal</span><span class="wk-sl-v" style="color:var(--bl);">x{MN}</span></div>
                                    </div>''')

                # ===== TAB CALIBRATION =====
                with ui.tab_panel(t_calib).classes('p-0 pt-2'):
                    with ui.row().classes('w-full gap-3 no-wrap'):
                        with ui.element('div').classes('wk-p p-4').style('flex:1;'):
                            ui.html('<div class="wk-section" style="margin-top:0;">CALIBRATION v2.0</div>')
                            meta = CALIBRATION.get('metadata', {})
                            ui.html(f'''<div class="wk-sum" style="margin-bottom:14px;">
                                <div class="wk-sl"><span class="wk-sl-l">Version</span><span class="wk-sl-v" style="color:var(--g);">{meta.get("version","2.0")}</span></div>
                                <div class="wk-sl"><span class="wk-sl-l">Date</span><span class="wk-sl-v">{meta.get("date","2026-03-14")}</span></div>
                                <div class="wk-sl"><span class="wk-sl-l">Sorts calibres</span><span class="wk-sl-v" style="color:var(--air);">{len(cs)}</span></div>
                                <div class="wk-sl"><span class="wk-sl-l">Precision max</span><span class="wk-sl-v" style="color:var(--air);">&lt; 0.3%</span></div>
                                <div class="wk-sl"><span class="wk-sl-l">Joueur</span><span class="wk-sl-v" style="color:var(--g);">{meta.get("player",S["name"])}</span></div>
                            </div>''')
                            ui.html('''<div class="wk-section">METHODE</div>
                                <div style="font-size:12px;color:var(--td);line-height:1.8;">
                                Reverse-engineering des bases de degats depuis le Mannequin Kanjedo (Sac a Patates, 0 resistance).
                                Chaque sort lance en crit et hors crit, base calculee par division du dommage reel par le multiplicateur.</div>''')

                        with ui.element('div').classes('wk-p p-4').style('flex:1;'):
                            mf = S['mf']+S['mm']+S['mc']
                            mw = S['mw']+S['mm']+S['mc']
                            ui.html(f'''<div class="wk-section" style="margin-top:0;">FORMULE</div>
                                <div style="background:var(--d0);border-radius:5px;padding:12px;font-family:monospace;font-size:11px;color:var(--t);line-height:2.2;">
                                <span style="color:var(--g);">Degats</span> = <span style="color:#e67e22;">Base</span>
                                &times; (1 + <span style="color:var(--bl);">Mastery</span>/100)
                                &times; <span style="color:#e67e22;">CritMult</span>
                                &times; (1 + <span style="color:var(--air);">DI%</span>/100)<br><br>
                                <span style="color:var(--td);">Mastery = Elem + Melee + CritMastery</span><br>
                                <span style="color:var(--fire);">Feu</span>: {S["mf"]} + {S["mm"]} + {S["mc"]} = <strong style="color:var(--g);">{mf}</strong><br>
                                <span style="color:var(--water);">Eau</span>: {S["mw"]} + {S["mm"]} + {S["mc"]} = <strong style="color:var(--g);">{mw}</strong><br>
                                <span style="color:#e67e22;">CritMult</span> = 1.25<br>
                                <span style="color:var(--air);">DI</span> = {S["di"]}%<br><br>
                                <span style="color:var(--td);">Ex: Mise a mort (base 576, Feu, Crit)</span><br>
                                576 &times; {1+mf/100:.2f} &times; 1.25 &times; {1+S["di"]/100:.2f}
                                = <strong style="color:var(--g);">{calc_dmg("Mise a mort",True)["d"]:,} PV</strong></div>''')


# =============================================================================
# LAUNCH
# =============================================================================
log.info('=' * 60)
log.info('  WAKFU OPTIMIZER v3.2 — Pierre Noire x Wakfuli')
log.info('=' * 60)
log.info(f'Joueur: {S["name"]} ({S["class"]} Niv.{S["level"]})')
log.info(f'Calibration: {len(CALIBRATION.get("spells",{}))} sorts | Mult crit: x{MC} | Mult norm: x{MN}')
log.info(f'Items: {len(all_items)} | Spells: {len(all_spells)} | Effects: {len(all_static_effects)}')
log.info(f'NiceGUI: http://localhost:8080')

ui.run(title='Wakfu Optimizer v3.2 — Pierre Noire', port=8080, reload=False, show=True, dark=True,
       favicon='https://www.wakfu.com/favicon.ico')
