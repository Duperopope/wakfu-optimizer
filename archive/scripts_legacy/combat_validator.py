import re, time, os, sys, json, logging
from datetime import datetime
from collections import defaultdict

LOG_PATH = r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log'
PROJECT_ROOT = r'H:\Code\Ankama Dev\wakfu-optimizer'
PLAYER_NAME = "L'Immortel"
VALIDATION_LOG = os.path.join(PROJECT_ROOT, 'logs', f'validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

os.makedirs(os.path.join(PROJECT_ROOT, 'logs'), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(VALIDATION_LOG, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('validator')

sys.path.insert(0, PROJECT_ROOT)
log.info('Chargement du moteur...')

try:
    from engine.fighter import Fighter
    from engine.effect_bridge import SpellExecutor
    log.info('Engine OK')
except ImportError as e:
    log.error(f'Import error: {e}')
    sys.exit(1)

def load_json(name):
    p = os.path.join(PROJECT_ROOT, 'data', 'extracted', name)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

all_spells = load_json('all_spells.json') or []
breeds_data = load_json('breeds.json') or []
spell_names_data = load_json('spell_names.json') or {}

SPELL_BY_ID = {s['id']: s for s in all_spells}

sram_spell_ids = []
for b in breeds_data:
    if isinstance(b, dict) and b.get('id') == 4:
        sram_spell_ids = b.get('ehx', [])
        break
log.info(f'Sorts Sram (ehx): {sram_spell_ids}')

SPELL_NAME_TO_ID = {
    'Double': 4604,
    'Mise a mort': 4586,
    'Attaque perfide': 4585,
    'Fourberie': 4595,
}
for sid_str, info in spell_names_data.items():
    if isinstance(info, dict) and 'name_fr' in info:
        SPELL_NAME_TO_ID[info['name_fr']] = int(sid_str)
log.info(f'Mapping: {len(SPELL_NAME_TO_ID)} sorts')

executor = SpellExecutor()

PLAYER_PROFILE = {
    'hp': 7400, 'ap': 12, 'mp': 4, 'wp': 8, 'level': 179,
    'critical_hit': 27, 'block': 37, 'dodge': 200, 'lock': 175,
    'mastery_fire': 847, 'mastery_water': 847,
    'mastery_earth': 847, 'mastery_air': 847,
    'mastery_melee': 420, 'mastery_berserk': 90,
    'res_fire': 260, 'res_water': 188,
    'res_earth': 188, 'res_air': 260,
    'damage_inflicted': 0,
}

COMBAT_LINE_RE = re.compile(
    r"(\d{2}:\d{2}:\d{2}),(\d+) - \[Information \(combat\)\] (.+)"
)

def simulate_spell(spell_name, is_crit, target_res=0):
    spell_id = SPELL_NAME_TO_ID.get(spell_name)
    if not spell_id or spell_id not in SPELL_BY_ID:
        return None, 'Sort inconnu'
    try:
        profile = PLAYER_PROFILE.copy()
        caster = Fighter(PLAYER_NAME, 'ally', 'player', 179, 'sram', profile)
        tp = {'hp': 10000, 'ap': 6, 'mp': 3, 'wp': 6, 'level': 179,
              'res_fire': target_res, 'res_water': target_res,
              'res_earth': target_res, 'res_air': target_res}
        target = Fighter('Mannequin', 'enemy', 'monster', 179, 'dummy', tp)
        hp_before = 10000
        result = executor.cast(caster, spell_id, target, {})
        hp_after = target.stats.get('hp', target.hp)
        dmg = hp_before - hp_after
        cast_dmg = 0
        if isinstance(result, list):
            cast_dmg = sum(r.get('final_damage', 0) for r in result)
        return max(dmg, cast_dmg), 'OK'
    except Exception as e:
        return None, str(e)

class CombatSession:
    def __init__(self):
        self.current_spell = None
        self.current_crit = False
        self.spell_data = defaultdict(lambda: {
            'casts': 0, 'crits': 0,
            'direct': [], 'dot': [], 'armor': [],
            'elements': set()
        })
        self.buffs = {}

    def on_cast(self, spell, is_crit):
        self.current_spell = spell
        self.current_crit = is_crit
        self.spell_data[spell]['casts'] += 1
        if is_crit:
            self.spell_data[spell]['crits'] += 1
        sim, status = simulate_spell(spell, is_crit)
        log.info(f'CAST: {spell} {"[CRIT]" if is_crit else ""} | Simu: {sim} ({status})')

    def on_damage(self, target, dmg, elem, is_dot, is_parade):
        if not self.current_spell:
            return
        self.spell_data[self.current_spell]['elements'].add(elem)
        if is_dot:
            self.spell_data[self.current_spell]['dot'].append(dmg)
        else:
            self.spell_data[self.current_spell]['direct'].append({
                'dmg': dmg, 'elem': elem, 'parade': is_parade, 'crit': self.current_crit
            })
        tag = 'DOT' if is_dot else ('PARADE' if is_parade else 'HIT')
        log.info(f'  {tag}: {target} -{dmg} PV ({elem})')

    def on_buff(self, val, name, source):
        self.buffs[name] = {'val': val, 'source': source}
        log.info(f'BUFF: {name} = {val}% ({source})')

    def on_end(self):
        log.info('')
        log.info('=' * 75)
        log.info('  RAPPORT DE VALIDATION - FIN DE COMBAT')
        log.info('=' * 75)
        if self.buffs:
            log.info(f'  Buffs: {self.buffs}')
        log.info('')
        log.info(f'  {"Sort":25s} | {"Cast":4s} | {"Crit":5s} | {"Elem":6s} | {"Moy":>7s} | {"Min":>6s} | {"Max":>6s} | {"Simu":>7s} | {"Ecart":>7s}')
        log.info('  ' + '-' * 75)

        for spell, data in sorted(self.spell_data.items(), key=lambda x: -x[1]['casts']):
            d = data['direct']
            elems = '/'.join(data['elements']) if data['elements'] else '?'
            crit_str = f"{data['crits']}/{data['casts']}"

            if d:
                vals = [h['dmg'] for h in d]
                avg_r = sum(vals) / len(vals)
                min_r = min(vals)
                max_r = max(vals)
                sim, _ = simulate_spell(spell, data['crits'] > 0)
                sim_str = str(sim) if sim else '?'
                if sim and sim > 0:
                    ecart = ((avg_r - sim) / sim) * 100
                    ecart_str = f'{ecart:+.1f}%'
                else:
                    ecart_str = 'N/A'
                log.info(f'  {spell:25s} | {data["casts"]:4d} | {crit_str:5s} | {elems:6s} | {avg_r:7.0f} | {min_r:6d} | {max_r:6d} | {sim_str:>7s} | {ecart_str:>7s}')
            else:
                log.info(f'  {spell:25s} | {data["casts"]:4d} | {crit_str:5s} | {elems:6s} |     N/A |    N/A |    N/A |     N/A |     N/A')

            if data['dot']:
                avg_dot = sum(data['dot']) / len(data['dot'])
                log.info(f'    {"(DOT)":23s} |      |       |        | {avg_dot:7.0f} | {min(data["dot"]):6d} | {max(data["dot"]):6d} |         |')

        log.info('=' * 75)
        log.info('')
        self.spell_data.clear()
        self.current_spell = None
        self.buffs.clear()

def tail_log(filepath):
    log.info(f'Surveillance: {filepath}')
    log.info(f'Joueur: {PLAYER_NAME}')
    log.info('Ctrl+C pour arreter')
    log.info('')

    session = CombatSession()

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        f.seek(0, 2)
        log.info(f'Position: fin ({f.tell()} octets)')
        log.info('En attente... Lance un combat !')
        log.info('')

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            line = line.rstrip()
            if not line:
                continue

            m = COMBAT_LINE_RE.match(line)
            if not m:
                continue

            ts = m.group(1)
            content = m.group(3)

            # Cast de sort par le joueur
            if PLAYER_NAME + ' lance le sort ' in content:
                spell_match = re.search(r'lance le sort (.+?)(?:\s*\(Critiques?\))?\s*$', content)
                if spell_match:
                    spell = spell_match.group(1).strip()
                    is_crit = '(Critiques)' in content or '(Critique)' in content
                    session.on_cast(spell, is_crit)
                continue

            # Degats infliges a une cible (pas au joueur)
            dmg_match = re.search(r'^(.+?): -([\d ]+) PV\s+\(([^)]+)\)', content)
            if dmg_match:
                target = dmg_match.group(1).strip()
                if PLAYER_NAME in target:
                    continue
                dmg = int(dmg_match.group(2).replace(' ', ''))
                elem = dmg_match.group(3)
                is_dot = 'morragie' in line or 'Rupture' in line or 'Conducteur' in line
                is_parade = 'Parade' in line
                session.on_damage(target, dmg, elem, is_dot, is_parade)
                continue

            # Buff du joueur
            buff_match = re.search(re.escape(PLAYER_NAME) + r': (\d+) % (.+?) \((.+?)\)', content)
            if buff_match:
                val = int(buff_match.group(1))
                name = buff_match.group(2)
                source = buff_match.group(3)
                session.on_buff(val, name, source)
                continue

            # Fin de combat
            if 'Combat termin' in content:
                session.on_end()
                continue

if __name__ == '__main__':
    log.info('=' * 60)
    log.info('  WAKFU COMBAT VALIDATOR v1.1')
    log.info('=' * 60)
    log.info('')

    if not os.path.exists(LOG_PATH):
        log.error(f'Log introuvable: {LOG_PATH}')
        sys.exit(1)

    log.info(f'Log: {LOG_PATH} ({os.path.getsize(LOG_PATH):,} octets)')
    log.info(f'Validation: {VALIDATION_LOG}')
    log.info('')

    try:
        tail_log(LOG_PATH)
    except KeyboardInterrupt:
        log.info('')
        log.info('Arret (Ctrl+C)')
        log.info(f'Log: {VALIDATION_LOG}')
