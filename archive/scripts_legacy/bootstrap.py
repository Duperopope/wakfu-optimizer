# =============================================================================
# BOOTSTRAP — Cree l'architecture modulaire du projet
# Genere les fichiers: app.py + modules/
# =============================================================================
import os, json
from pathlib import Path

ROOT = Path(r'H:\Code\Ankama Dev\wakfu-optimizer')
MOD = ROOT / 'modules'
MOD.mkdir(exist_ok=True)
STATIC = ROOT / 'static'
STATIC.mkdir(exist_ok=True)

print('=== WAKFU OPTIMIZER — Architecture Modulaire ===')
print(f'Racine: {ROOT}')
print(f'Modules: {MOD}')
print()

# -------------------------------------------------------------------
# 1) modules/__init__.py
# -------------------------------------------------------------------
(MOD / '__init__.py').write_text('', encoding='utf-8')
print('[OK] modules/__init__.py')

# -------------------------------------------------------------------
# 2) modules/data.py — Chargement de toutes les donnees
# -------------------------------------------------------------------
data_py = r'''
import json, logging
from pathlib import Path

log = logging.getLogger('wakfu-optimizer')
DATA_DIR = Path(r'H:\Code\Ankama Dev\wakfu-optimizer\data\extracted')

def load_json(fn):
    fp = DATA_DIR / fn
    if not fp.exists():
        log.warning(f'Introuvable: {fp}')
        return [] if 'map' not in fn else {}
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    log.info(f'{fn}: {len(d) if isinstance(d,(list,dict)) else "?"} entrees')
    return d

# Chargement global
all_items = load_json('all_items.json')
all_spells = load_json('all_spells.json')
all_static_effects = load_json('all_static_effects.json')
all_states = load_json('all_states.json')
breeds_data = load_json('breeds.json')
spell_names_data = load_json('spell_names.json')
ACTION_MAP = load_json('action_map.json')

# Calibration
calibration_path = DATA_DIR / 'sram_calibration.json'
CALIBRATION = {}
if calibration_path.exists():
    with open(calibration_path, 'r', encoding='utf-8') as f:
        CALIBRATION = json.load(f)
    log.info(f'Calibration: {len(CALIBRATION.get("spells", {}))} sorts')

# Index items par type (slot)
# Structure CDN: item.definition.item.baseParameters.itemTypeId
# equipmentItemTypes.json mappe itemTypeId -> positions (slots)
ITEM_TYPE_TO_SLOT = {
    103: 'HEAD', 104: 'BACK', 108: 'CHEST', 110: 'BELT', 119: 'LEGS',
    120: 'NECK', 132: 'LEFT_HAND', 133: 'RIGHT_HAND', 134: 'SHOULDERS',
    136: 'PET', 138: 'MOUNT', 189: 'ACCESSORY',
    # Armes
    101: 'FIRST_WEAPON', 111: 'FIRST_WEAPON', 112: 'FIRST_WEAPON',
    113: 'FIRST_WEAPON', 114: 'FIRST_WEAPON', 115: 'FIRST_WEAPON',
    117: 'FIRST_WEAPON', 223: 'FIRST_WEAPON', 253: 'FIRST_WEAPON',
    254: 'FIRST_WEAPON',
    109: 'SECOND_WEAPON', 112: 'SECOND_WEAPON',
}

RARITY_NAMES = {0:'Common', 1:'Inhabituel', 2:'Rare', 3:'Mythique', 4:'Legendaire', 5:'Relique', 6:'Souvenir', 7:'Epique'}
RARITY_COLORS = {0:'#95a5a6', 1:'#2ecc71', 2:'#3498db', 3:'#b070dd', 4:'#e8d48b', 5:'#e67e22', 6:'#e74c3c', 7:'#e67e22'}

def get_item_slot(item):
    try:
        tid = item['definition']['item']['baseParameters']['itemTypeId']
        return ITEM_TYPE_TO_SLOT.get(tid)
    except (KeyError, TypeError):
        return None

def get_item_level(item):
    try:
        return item['definition']['item']['level']
    except (KeyError, TypeError):
        return 0

def get_item_rarity(item):
    try:
        return item['definition']['item']['baseParameters']['rarity']
    except (KeyError, TypeError):
        return 0

def get_item_title(item):
    try:
        t = item.get('title', {})
        return t.get('fr', t.get('en', str(item.get('definition',{}).get('item',{}).get('id',''))))
    except:
        return '?'

def get_item_effects(item):
    try:
        return item['definition']['item']['equipEffects']
    except (KeyError, TypeError):
        return []

def filter_items(slot=None, min_level=0, max_level=200, min_rarity=0, search=''):
    results = []
    for it in all_items:
        if slot and get_item_slot(it) != slot:
            continue
        lvl = get_item_level(it)
        if lvl < min_level or lvl > max_level:
            continue
        if get_item_rarity(it) < min_rarity:
            continue
        if search:
            name = get_item_title(it).lower()
            if search.lower() not in name:
                continue
        results.append(it)
    # Trier par niveau desc puis rarete desc
    results.sort(key=lambda x: (-get_item_level(x), -get_item_rarity(x)))
    return results[:100]  # Max 100 resultats pour perf

# Index sorts Sram (breedId 4 ou 245)
SRAM_SPELLS_FULL = []
for sp in all_spells:
    bid = None
    if isinstance(sp, dict):
        d = sp.get('definition', sp)
        bid = d.get('breedId') or d.get('m_breedId')
    if bid in (4, 245):
        SRAM_SPELLS_FULL.append(sp)
log.info(f'Sorts Sram complets: {len(SRAM_SPELLS_FULL)}') if SRAM_SPELLS_FULL else None

# Liste complete des sorts Sram (source: wiki + encyclopedie officielle)
SRAM_SPELL_LIST = {
    'fire': [
        {'name': 'Premier Sang', 'pa': 3, 'desc': 'AoE ligne: Degats, Hemorragie si pas deja, Point Faible +10', 'unlock': 0},
        {'name': 'Tourment', 'pa': 4, 'desc': 'AoE anneau: Degats, Point Faible +20', 'unlock': 2},
        {'name': 'Sang Froid', 'pa': 2, 'desc': 'Degats, Soin base sur Hemorragie, Point Faible +10', 'unlock': 4},
        {'name': 'Saignee mortelle', 'pa': 4, 'desc': 'Degats, Hemorragie +1(25), Point Faible +10', 'unlock': 7},
        {'name': 'Mise a mort', 'pa': 6, 'desc': 'Degats, bonus si Point Faible=100, +10% DI cible <35% PV', 'unlock': 10},
    ],
    'water': [
        {'name': 'Kleptosram', 'pa': 4, 'desc': 'Degats, Point Faible +20, Vol de PM', 'unlock': 0},
        {'name': 'Fourberie', 'pa': 3, 'desc': 'AoE croix: Degats, Point Faible +20, Vol de Degats', 'unlock': 2},
        {'name': 'Attaque perfide', 'pa': 3, 'desc': 'Retire Armure, Degats, Point Faible +15', 'unlock': 4},
        {'name': 'Arnaque', 'pa': 4, 'desc': 'Degats, Point Faible +10, Vol Esquive et Tacle', 'unlock': 7},
        {'name': 'Coup de Ripou', 'pa': 2, 'desc': 'Degats, bonus+soin+PW si Point Faible>=50', 'unlock': 10},
    ],
    'air': [
        {'name': 'Coup penetrant', 'pa': 4, 'desc': 'AoE ligne: Degats, Point Faible +20', 'unlock': 0},
        {'name': 'Effroi', 'pa': 4, 'desc': 'Repousse, si invisible: Degats, Point Faible +5', 'unlock': 2},
        {'name': 'Fourberie (Air)', 'pa': 3, 'desc': 'Teleport, si invisible: Degats, Point Faible +15', 'unlock': 4},
        {'name': 'Coup fourbe', 'pa': 3, 'desc': 'Eloigne, si invisible: Degats, Point Faible +15', 'unlock': 7},
        {'name': 'Trauma', 'pa': 4, 'desc': 'Degats, bonus+PW si Point Faible>=50, +DI% dos', 'unlock': 10},
    ],
    'support': [
        {'name': 'Invisibilite', 'pa': 2, 'desc': 'Rend invisible 2 tours, Transparent', 'unlock': 1},
        {'name': 'Double', 'pa': 6, 'desc': 'Invoque un double controlable', 'unlock': 4},
        {'name': 'Galopade', 'pa': 3, 'desc': '+PM, si invisible: ne peut plus etre bloque', 'unlock': 3},
        {'name': 'Piege', 'pa': 4, 'desc': 'Place un piege (Repulsion/Teleportation/Silence)', 'unlock': 5},
        {'name': 'Ouvrir les veines', 'pa': 3, 'desc': '+DI% en critique ou dos', 'unlock': 6},
    ],
    'passives': [
        {'name': 'Maitre des Ombres', 'desc': '+Degats Dos%, +DI 2e tour invisibilite', 'unlock': 1},
        {'name': 'Sramystique', 'desc': '+Initiative, +generation Point Faible', 'unlock': 3},
        {'name': 'Sramuleux', 'desc': '+Tacle, +DI% cible <35% PV', 'unlock': 4},
        {'name': 'Reflexe Sram', 'desc': '+Esquive, +Controle, reduit cout PA', 'unlock': 5},
        {'name': 'Sram jusqu a l os', 'desc': '+Crit% base sur Tacle et Esquive', 'unlock': 6},
    ]
}
'''
(MOD / 'data.py').write_text(data_py, encoding='utf-8')
print('[OK] modules/data.py')

# -------------------------------------------------------------------
# 3) modules/engine.py — Moteur de calcul de degats
# -------------------------------------------------------------------
engine_py = r'''
import logging
log = logging.getLogger('wakfu-optimizer')

# Stats reelles L'Immortel (captees in-game 14/03/2026)
PLAYER = {
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

def calc_dmg(spell_name, calibration, crit=True, res=0, stats=None):
    s = stats or PLAYER
    cal = calibration.get('spells', {}).get(spell_name)
    if not cal:
        return {'d':0,'dot':0,'t':0,'e':'?','pa':0,'b':0,'m':0}
    b = cal.get('base', 0)
    pa = cal.get('pa', 0)
    dr = cal.get('dot_ratio', 0)
    e = cal.get('element', 'Feu')
    em = {'Feu':s['mf'],'Eau':s['mw'],'Air':s['ma'],'Terre':s['me']}.get(e, 0)
    tm = em + s['mm'] + (s['mc'] if crit else 0)
    full = (1 + tm/100) * (1.25 if crit else 1.0) * (1 + s['di']/100) * max(0, 1 - res/100)
    d = round(b * full)
    dot = round(b * full * dr)
    return {'d':d, 'dot':dot, 't':d+dot, 'e':e, 'pa':pa, 'b':b, 'm':round(full,2)}

def get_mults(stats=None):
    s = stats or PLAYER
    best = max(s['mf'], s['mw'], s['ma'], s['me'])
    dm = 1 + s['di']/100
    mc = round((1 + (best+s['mm']+s['mc'])/100) * 1.25 * dm, 2)
    mn = round((1 + (best+s['mm'])/100) * 1.0 * dm, 2)
    return mc, mn

def sim_rotation(calibration, res=0, stats=None):
    s = stats or PLAYER
    ap = s['ap']
    cs = calibration.get('spells', {})
    spells = []
    for n, d in cs.items():
        pa = d.get('pa', 0)
        if pa <= 0: continue
        dm = calc_dmg(n, calibration, True, res, s)
        spells.append({'n':n, 'pa':pa, 'dm':dm, 'eff':dm['t']/pa if pa else 0})
    spells.sort(key=lambda x: -x['eff'])
    rot, left = [], ap
    for sp in spells:
        if left >= sp['pa']:
            rot.append(sp)
            left -= sp['pa']
    return rot, ap - left

def res_pct(val, lvl):
    return round(val/(val + 5*lvl)*100) if val > 0 else 0
'''
(MOD / 'engine.py').write_text(engine_py, encoding='utf-8')
print('[OK] modules/engine.py')

# -------------------------------------------------------------------
# 4) modules/css.py — Feuille de style Pierre Noire x Wakfuli
# -------------------------------------------------------------------
css_py = '''
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
:root{--d0:#0d0d1a;--d1:#1a1a2e;--d2:#1e1e35;--d3:#252545;--d4:#2d2d55;--d5:#1c1c36;--g:#c9a84c;--gl:#e8d48b;--gd:#8b6914;--bl:#3a7bd5;--b:#2a4d6e;--t:#e8e6e3;--td:#8a8a9a;--tw:#fff;--fire:#e74c3c;--water:#3498db;--air:#2ecc71;--earth:#8b4513;--light:#f1c40f;--brd:#3a3a5c;--bg:rgba(201,168,76,0.25);--sh:rgba(0,0,0,0.5)}
body,.q-page{background:var(--d0)!important;color:var(--t)!important;font-family:'Inter',sans-serif!important}
.q-header{background:var(--d1)!important;border-bottom:1px solid var(--brd)!important;min-height:42px!important}
.q-card{background:var(--d2)!important;color:var(--t)!important}
.q-tab{color:var(--td)!important;font-family:'Cinzel',serif!important;text-transform:uppercase!important;letter-spacing:1px!important;font-size:11px!important}
.q-tab--active{color:var(--g)!important}.q-tab-indicator{background:var(--g)!important}.q-tab-panels{background:transparent!important}
.q-field__control{background:var(--d3)!important;color:var(--t)!important}
.wk-sidebar{background:var(--d1);border-right:1px solid var(--brd);width:300px;overflow-y:auto;padding:12px;flex-shrink:0}
.wk-sidebar::-webkit-scrollbar{width:5px}.wk-sidebar::-webkit-scrollbar-thumb{background:var(--brd);border-radius:3px}
.wk-section{font-family:'Cinzel',serif;color:var(--g);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;margin:12px 0 6px;padding-bottom:4px;border-bottom:1px solid rgba(201,168,76,0.15)}.wk-section:first-child{margin-top:0}
.wk-sl{display:flex;justify-content:space-between;align-items:center;padding:2px 0;font-size:12px}
.wk-sl-l{color:var(--td);display:flex;align-items:center;gap:5px}.wk-sl-l .material-icons{font-size:14px}
.wk-sl-v{font-weight:600}
.wk-mr{display:flex;align-items:center;gap:4px;font-size:12px;padding:1px 0}
.wk-p{background:linear-gradient(145deg,var(--d2),var(--d1));border:1px solid var(--brd);border-radius:8px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.04),0 4px 16px var(--sh);position:relative;overflow:hidden}
.wk-p::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.35}
.wk-eqbar{display:flex;gap:4px;flex-wrap:wrap;padding:8px;background:var(--d1);border-radius:6px;border:1px solid var(--brd)}
.wk-eq{width:42px;height:42px;border-radius:5px;background:var(--d5);border:1px solid var(--brd);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all 0.15s}
.wk-eq:hover{border-color:var(--g);box-shadow:0 0 8px rgba(201,168,76,0.2)}.wk-eq .material-icons{font-size:18px;color:var(--td)}.wk-eq:hover .material-icons{color:var(--g)}
.wk-eq-active{border-color:var(--g)!important;box-shadow:0 0 10px rgba(201,168,76,0.3)!important}.wk-eq-active .material-icons{color:var(--g)!important}
.wk-item{background:var(--d3);border:1px solid var(--brd);border-radius:6px;padding:10px;margin-bottom:4px;cursor:pointer;transition:all 0.15s}
.wk-item:hover{border-color:var(--g);background:var(--d4)}
.wk-tbl{width:100%;border-collapse:separate;border-spacing:0 2px}
.wk-tbl th{background:var(--d1);color:var(--g);font-family:'Cinzel',serif;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:7px 8px;text-align:left}
.wk-tbl td{padding:6px 8px;background:var(--d3);font-size:12px}.wk-tbl tr:hover td{background:var(--d4)}
.wk-tbl td:first-child{border-radius:4px 0 0 4px}.wk-tbl td:last-child{border-radius:0 4px 4px 0}
.el{display:inline-flex;align-items:center;gap:3px;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.el-feu{background:rgba(231,76,60,0.12);color:var(--fire)}.el-eau{background:rgba(52,152,219,0.12);color:var(--water)}
.el-air{background:rgba(46,204,113,0.12);color:var(--air)}.el-terre{background:rgba(139,69,19,0.12);color:var(--earth)}
.el-lumiere{background:rgba(241,196,15,0.12);color:var(--light)}
.wk-sum{background:var(--d3);border-radius:5px;padding:10px 12px;border-left:3px solid var(--g)}
.wk-chip{border-radius:4px;padding:5px 8px;text-align:center}
.wk-big{font-size:20px;font-weight:700}.wk-med{font-size:15px;font-weight:600}
.wk-btn{background:linear-gradient(180deg,var(--g),var(--gd))!important;color:var(--d0)!important;font-family:'Cinzel',serif!important;font-weight:600!important;border:none!important;border-radius:4px!important;text-transform:uppercase!important;letter-spacing:1px!important}
.wk-pct{background:rgba(46,204,113,0.15);color:var(--air);padding:1px 5px;border-radius:3px;font-size:11px;font-weight:600}
.wk-pct-fire{background:rgba(231,76,60,0.15);color:var(--fire)}.wk-pct-water{background:rgba(52,152,219,0.15);color:var(--water)}
.wk-pct-air{background:rgba(46,204,113,0.15);color:var(--air)}.wk-pct-earth{background:rgba(139,69,19,0.15);color:var(--earth)}
.wk-rarity-0{color:#95a5a6}.wk-rarity-1{color:#2ecc71}.wk-rarity-2{color:#3498db}
.wk-rarity-3{color:#b070dd;border:1px solid rgba(176,112,221,0.3);background:rgba(176,112,221,0.06);padding:1px 6px;border-radius:3px;font-size:10px}
.wk-rarity-4{color:#e8d48b;border:1px solid rgba(232,212,139,0.3);background:rgba(232,212,139,0.06);padding:1px 6px;border-radius:3px;font-size:10px}
.wk-rarity-5{color:#e67e22;border:1px solid rgba(230,126,34,0.3);background:rgba(230,126,34,0.06);padding:1px 6px;border-radius:3px;font-size:10px}
.wk-rarity-7{color:#e67e22;border:1px solid rgba(230,126,34,0.3);background:rgba(230,126,34,0.06);padding:1px 6px;border-radius:3px;font-size:10px}
.wk-spell-card{background:var(--d3);border-radius:6px;padding:10px;margin-bottom:4px;border-left:3px solid var(--brd);transition:all 0.15s}
.wk-spell-card:hover{background:var(--d4);border-left-color:var(--g)}
.wk-apt{border-radius:6px;padding:12px;border:1px solid}
.wk-apt-int{background:rgba(46,204,113,0.05);border-color:rgba(46,204,113,0.2)}.wk-apt-int .wk-section{color:#2ecc71}
.wk-apt-force{background:rgba(230,126,34,0.05);border-color:rgba(230,126,34,0.2)}.wk-apt-force .wk-section{color:#e67e22}
.wk-apt-agi{background:rgba(241,196,15,0.05);border-color:rgba(241,196,15,0.2)}.wk-apt-agi .wk-section{color:#f1c40f}
.wk-apt-chance{background:rgba(176,112,221,0.05);border-color:rgba(176,112,221,0.2)}.wk-apt-chance .wk-section{color:#b070dd}
.wk-apt-maj{background:rgba(58,123,213,0.05);border-color:rgba(58,123,213,0.2)}.wk-apt-maj .wk-section{color:#3a7bd5}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--d0)}::-webkit-scrollbar-thumb{background:var(--brd);border-radius:3px}::-webkit-scrollbar-thumb:hover{background:var(--gd)}
"""
'''
(MOD / 'css.py').write_text(css_py, encoding='utf-8')
print('[OK] modules/css.py')

# -------------------------------------------------------------------
# 5) modules/constants.py
# -------------------------------------------------------------------
const_py = r'''
from collections import OrderedDict

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

ACTION_EFFECTS = {
    20: {'n': 'PV', 'i': 'favorite', 'c': '#e74c3c'},
    31: {'n': 'PA', 'i': 'star', 'c': '#3a7bd5'},
    41: {'n': 'PM', 'i': 'directions_walk', 'c': '#2ecc71'},
    56: {'n': 'PW', 'i': 'auto_awesome', 'c': '#9b59b6'},
    80: {'n': 'Maitrise Elementaire', 'i': 'whatshot', 'c': '#e67e22'},
    82: {'n': 'Maitrise Feu', 'i': 'local_fire_department', 'c': '#e74c3c'},
    83: {'n': 'Maitrise Eau', 'i': 'water_drop', 'c': '#3498db'},
    84: {'n': 'Maitrise Terre', 'i': 'landscape', 'c': '#8b4513'},
    85: {'n': 'Maitrise Air', 'i': 'air', 'c': '#2ecc71'},
    120: {'n': 'Resistance Elementaire', 'i': 'shield', 'c': '#95a5a6'},
    122: {'n': 'Resistance Feu', 'i': 'shield', 'c': '#e74c3c'},
    123: {'n': 'Resistance Eau', 'i': 'shield', 'c': '#3498db'},
    124: {'n': 'Resistance Terre', 'i': 'shield', 'c': '#8b4513'},
    125: {'n': 'Resistance Air', 'i': 'shield', 'c': '#2ecc71'},
    149: {'n': 'Coup Critique', 'i': 'casino', 'c': '#e67e22'},
    160: {'n': 'Esquive', 'i': 'swap_horiz', 'c': '#3a7bd5'},
    161: {'n': 'Tacle', 'i': 'gps_fixed', 'c': '#e67e22'},
    162: {'n': 'Initiative', 'i': 'speed', 'c': '#95a5a6'},
    166: {'n': 'Sagesse', 'i': 'auto_stories', 'c': '#95a5a6'},
    171: {'n': 'Prospection', 'i': 'search', 'c': '#95a5a6'},
    173: {'n': 'Portee', 'i': 'gps_not_fixed', 'c': '#95a5a6'},
    174: {'n': 'Volonte', 'i': 'psychology', 'c': '#95a5a6'},
    175: {'n': 'Parade', 'i': 'block', 'c': '#3498db'},
    180: {'n': 'Maitrise Dos', 'i': 'visibility', 'c': '#9b59b6'},
    184: {'n': 'Maitrise Melee', 'i': 'sports_martial_arts', 'c': '#c9a84c'},
    191: {'n': 'Maitrise Distance', 'i': 'radar', 'c': '#95a5a6'},
    192: {'n': 'Maitrise Critique', 'i': 'flash_on', 'c': '#e67e22'},
    875: {'n': 'Maitrise Soin', 'i': 'healing', 'c': '#2ecc71'},
    876: {'n': 'Maitrise Berserk', 'i': 'dangerous', 'c': '#e74c3c'},
    979: {'n': 'Resistance Dos', 'i': 'shield', 'c': '#9b59b6'},
    988: {'n': 'Resistance Critique', 'i': 'shield', 'c': '#e67e22'},
    1020: {'n': 'Dommages infliges', 'i': 'bolt', 'c': '#2ecc71'},
    1050: {'n': 'Armure donnee', 'i': 'security', 'c': '#95a5a6'},
    1051: {'n': 'Armure recue', 'i': 'security', 'c': '#95a5a6'},
    1052: {'n': 'Soins realises', 'i': 'favorite', 'c': '#2ecc71'},
    1053: {'n': 'Dommage indirects', 'i': 'blur_on', 'c': '#95a5a6'},
}
'''
(MOD / 'constants.py').write_text(const_py, encoding='utf-8')
print('[OK] modules/constants.py')

print()
print('=== Architecture creee avec succes ===')
print(f'  modules/data.py       — Chargement donnees + filtrage items')
print(f'  modules/engine.py     — Moteur degats calibre')
print(f'  modules/css.py        — Style Pierre Noire x Wakfuli')
print(f'  modules/constants.py  — Constantes (slots, elements, actions)')
print()
print('Prochaine etape: generer app.py modulaire')
print('  & .\\.venv\\Scripts\\python.exe scripts\\bootstrap.py')
