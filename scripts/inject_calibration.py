import json, os, sys

PROJECT = r'H:\Code\Ankama Dev\wakfu-optimizer'
APP_PATH = os.path.join(PROJECT, 'app.py')

# Charger la calibration
cal_path = os.path.join(PROJECT, 'data', 'extracted', 'sram_calibration.json')
with open(cal_path, 'r', encoding='utf-8') as f:
    cal = json.load(f)

print(f'Calibration chargee: {len(cal["spells"])} sorts')

# Lire app.py
with open(APP_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# Trouver et remplacer la fonction run_combat_simulation
# On va injecter un nouveau simulateur base sur la calibration

NEW_SIMULATOR = '''
# ============================================================
# SIMULATEUR CALIBRE v2.0
# Base sur les degats reels du mannequin Kanjedo (0 res)
# Calibration: 2026-03-14, L'Immortel Sram 179
# ============================================================
import json as _json

def load_calibration():
    """Charge les bases de degats calibrees"""
    cal_path = os.path.join(os.path.dirname(__file__), 'data', 'extracted', 'sram_calibration.json')
    if os.path.exists(cal_path):
        with open(cal_path, 'r', encoding='utf-8') as f:
            return _json.load(f)
    return None

CALIBRATION = load_calibration()
if CALIBRATION:
    log.info(f"Calibration chargee: {len(CALIBRATION.get('spells', {}))} sorts, mult crit={CALIBRATION['multipliers']['crit']}, norm={CALIBRATION['multipliers']['normal']}")

def calculate_damage(spell_name, profile, target_res=0, is_crit=True, verbose=False):
    """
    Calcule les degats d'un sort en utilisant la formule Wakfu calibree.
    
    Formule: Base * (1 + Mastery/100) * CritMult * (1 + DI/100) * (1 - TargetRes/100)
    
    Args:
        spell_name: Nom du sort (francais)
        profile: Dict avec les stats du joueur
        target_res: Resistance elementaire de la cible
        is_crit: True si coup critique
        verbose: True pour afficher le detail du calcul
    
    Returns:
        dict avec direct, dot, armor, total, detail
    """
    if not CALIBRATION:
        return {'direct': 0, 'dot': 0, 'armor': 0, 'total': 0, 'detail': 'Pas de calibration'}
    
    spells = CALIBRATION.get('spells', {})
    
    # Chercher le sort (match flexible)
    spell_data = None
    for sname, sdata in spells.items():
        if sname.lower().replace(' ', '') == spell_name.lower().replace(' ', '').replace('\\u00e0', 'a').replace('\\u00e9', 'e'):
            spell_data = sdata
            break
    
    if not spell_data:
        # Essai partiel
        for sname, sdata in spells.items():
            if sname.lower()[:8] in spell_name.lower()[:8]:
                spell_data = sdata
                break
    
    if not spell_data:
        return {'direct': 0, 'dot': 0, 'armor': 0, 'total': 0, 'detail': f'Sort inconnu: {spell_name}'}
    
    base = spell_data['base']
    elem = spell_data['elem']
    
    # Mastery elementaire
    mastery_key = f'mastery_{elem.lower()}'
    elem_mastery = profile.get(mastery_key, profile.get('mastery_fire', 0))
    
    # Mastery secondaire (melee pour Sram)
    melee_mastery = profile.get('mastery_melee', 0)
    
    # Mastery totale
    total_mastery = elem_mastery + melee_mastery
    mastery_mult = 1 + total_mastery / 100
    
    # Crit
    crit_mult = 1.25 if is_crit else 1.0
    crit_mastery = profile.get('mastery_critical', 0)
    if is_crit and crit_mastery > 0:
        crit_mult += crit_mastery / 100
    
    # Dommages infliges (buffs comme Temerite)
    di_pct = profile.get('damage_inflicted', 0) / 100
    di_mult = 1 + di_pct
    
    # Resistance de la cible
    res_mult = 1 - target_res / (target_res + 100) if target_res > 0 else 1.0
    
    # Calcul final
    direct = base * mastery_mult * crit_mult * di_mult * res_mult
    
    # DOT (ratio calibre)
    dot_ratio = spell_data.get('dot_ratio', 0) / 100
    dot = direct * dot_ratio
    
    # Armure (ratio calibre)
    armor_ratio = spell_data.get('armor_ratio', 0) / 100
    armor = direct * armor_ratio
    
    total = direct + dot
    
    detail = (f'Base={base} * Mastery(x{mastery_mult:.2f}) * '
              f'Crit(x{crit_mult:.2f}) * DI(x{di_mult:.2f}) * '
              f'Res(x{res_mult:.2f}) = {direct:.0f}')
    
    if verbose:
        log.info(f'  {spell_name}: {detail}')
        if dot > 0:
            log.info(f'    DOT: {direct:.0f} * {dot_ratio:.0%} = {dot:.0f}')
    
    return {
        'direct': round(direct),
        'dot': round(dot),
        'armor': round(armor),
        'total': round(total),
        'detail': detail,
        'base': base,
        'mastery': total_mastery,
        'crit': is_crit,
    }


def run_combat_simulation(base_profile, equipped_profile, class_name='sram'):
    """
    Simule un tour de combat complet et compare base vs equipe.
    Utilise les bases de degats calibrees du mannequin.
    """
    if not CALIBRATION:
        log.warning('Pas de calibration disponible')
        return 0, 0, 0
    
    spells = CALIBRATION.get('spells', {})
    
    # Rotation typique Sram (1 tour = 12 PA)
    # Mise a mort (6PA) + Attaque perfide (3PA) + Premier Sang (3PA) = 12 PA
    rotation = []
    pa_left = equipped_profile.get('ap', 12)
    
    # Trier les sorts par Base/PA (efficacite)
    sorted_spells = sorted(spells.items(), key=lambda x: x[1]['base'] / x[1]['pa'] if x[1]['pa'] > 0 else 0, reverse=True)
    
    for sname, sdata in sorted_spells:
        if sdata['pa'] <= 0:
            continue
        while pa_left >= sdata['pa']:
            rotation.append(sname)
            pa_left -= sdata['pa']
            break  # 1 fois par sort pour varier
    
    # Si PA restants, ajouter le sort le plus efficace
    for sname, sdata in sorted_spells:
        if sdata['pa'] <= 0:
            continue
        while pa_left >= sdata['pa']:
            rotation.append(sname)
            pa_left -= sdata['pa']
    
    log.info(f'Rotation ({class_name}): {rotation} | PA utilises: {equipped_profile.get("ap", 12) - pa_left}/{equipped_profile.get("ap", 12)}')
    
    # Simuler avec le profil de base (sans equipement)
    base_total = 0
    log.info('--- Degats BASE (sans equipement) ---')
    for spell in rotation:
        result = calculate_damage(spell, base_profile, target_res=0, is_crit=True, verbose=True)
        base_total += result['total']
    
    # Simuler avec le profil equipe
    equipped_total = 0
    log.info('--- Degats EQUIPE ---')
    for spell in rotation:
        result = calculate_damage(spell, equipped_profile, target_res=0, is_crit=True, verbose=True)
        equipped_total += result['total']
    
    ratio = equipped_total / base_total if base_total > 0 else 0
    log.info(f'Resultat: Base={base_total:,} | Equipe={equipped_total:,} | Ratio=x{ratio:.2f} (+{(ratio-1)*100:.0f}%)')
    
    return base_total, equipped_total, ratio
'''

# Trouver l'ancienne fonction run_combat_simulation et la remplacer
import re

# Chercher le debut de la fonction
start_marker = 'def run_combat_simulation('
end_markers = ['\ndef generate_build(', '\ndef create_ui(', '\n# ===', '\nclass ', '\n@ui.']

start_idx = code.find(start_marker)
if start_idx == -1:
    print('ERREUR: run_combat_simulation non trouvee dans app.py')
    sys.exit(1)

# Trouver la fin de la fonction (prochaine definition de fonction/classe au meme niveau)
end_idx = len(code)
for marker in end_markers:
    idx = code.find(marker, start_idx + 100)
    if idx != -1 and idx < end_idx:
        end_idx = idx

old_func = code[start_idx:end_idx]
print(f'Ancienne fonction trouvee: {len(old_func)} caracteres')
print(f'  Debut: {old_func[:80]}...')

# Remplacer
new_code = code[:start_idx] + NEW_SIMULATOR + '\n\n' + code[end_idx:]

# Aussi ajouter le chargement de la calibration apres les imports
# Verifier si CALIBRATION est deja charge
if 'load_calibration' not in code[:start_idx]:
    # Ajouter apres la ligne "log = logging.getLogger"
    log_line = "log = logging.getLogger"
    log_idx = new_code.find(log_line)
    if log_idx != -1:
        end_of_log_line = new_code.find('\n', log_idx) + 1
        # Le NEW_SIMULATOR contient deja load_calibration, pas besoin d'ajouter

# Ecrire le fichier
with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(new_code)

print(f'app.py mis a jour: {len(new_code)} caracteres')
print('Nouveau simulateur calibre v2.0 injecte')
print()
print('Relance avec:')
print('  & .\\.venv\\Scripts\\python.exe app.py')
