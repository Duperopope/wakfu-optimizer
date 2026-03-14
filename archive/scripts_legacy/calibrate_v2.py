import json, os

PROJECT = r'H:\Code\Ankama Dev\wakfu-optimizer'

# ============================================================
# STATS REELLES DE L'IMMORTEL (captures in-game)
# ============================================================
REAL_STATS = {
    'hp': 8928, 'ap': 13, 'mp': 5, 'wp': 8, 'level': 179,
    'mastery_fire': 808, 'mastery_water': 808,
    'mastery_earth': 190, 'mastery_air': 425,
    'mastery_melee': 1030,
    'mastery_distance': 0,
    'mastery_critical': 456,
    'mastery_rear': 585,
    'mastery_berserk': -90,
    'mastery_healing': 0,
    'mastery_single_target': 0,
    'mastery_area': 0,
    'critical_hit': 72,
    'damage_inflicted': 18,
    'block': 0, 'dodge': 502, 'lock': 252,
    'initiative': 142, 'wisdom': 40, 'prospecting': 40,
    'res_fire': 564, 'res_water': 452,
    'res_earth': 335, 'res_air': 546,
    'res_fire_pct': 71, 'res_water_pct': 63,
    'res_earth_pct': 52, 'res_air_pct': 70,
    'res_critical': 0, 'res_rear': 25,
}

# DEGATS REELS au mannequin (0 resistance)
# Sort                | PA | Elem | Crit | Direct | DOT
REAL_SPELLS = [
    ('Mise a mort',      6, 'Feu',  True,  20325, 0),
    ('Premier Sang',     3, 'Feu',  True,  3503,  751),
    ('Attaque perfide',  3, 'Eau',  True,  7365,  1859),
    ('Saignee mortelle', 4, 'Feu',  True,  5255,  5571),
    ('Kleptosram',       4, 'Eau',  True,  3753,  1005),
    ('Replique Saignee', 0, 'Feu',  False, 3908,  1524),
    ('Arnaque',          4, 'Eau',  True,  6238,  2297),
    ('Fourberie',        3, 'Air',  False, 2239,  1116),
    ('Effroi',           4, 'Air',  True,  5616,  2236),
    ('Ouvrir les veines',3, 'Feu',  True,  3753,  1502),
]

# ============================================================
# RECALIBRATION AVEC STATS REELLES
# ============================================================
# Formule: Degats = Base * (1 + TotalMastery/100) * CritMult * (1 + DI/100)
# 
# CritMult = 1.25 + CritMastery/100
#   Avec CritMastery = 456: CritMult = 1.25 + 4.56 = 5.81 ??? Non, trop.
#   En fait CritMastery fonctionne comme mastery: multiplie la base en crit.
#
# Wakfu formule exacte:
#   Non-crit: Base * (1 + Mastery/100) * (1 + DI/100) * (1 - TargetRes/(TargetRes+100))
#   Crit:     Base * (1 + (Mastery + CritMastery)/100) * 1.25 * (1 + DI/100) * (1 - Res)
#
# Mastery en crit = ElemMastery + MeleeMastery + CritMastery
# Mastery non-crit = ElemMastery + MeleeMastery

print('=' * 90)
print('  RECALIBRATION AVEC STATS REELLES')
print('=' * 90)
print()

# Pour chaque sort, calculer la mastery effective et reverse-engineer la base
print(f'{"Sort":25s} | {"Elem":4s} | {"Cr":2s} | {"ElemM":>5s} | {"Melee":>5s} | {"CritM":>5s} | {"TotM":>5s} | {"Mult":>6s} | {"Reel":>7s} | {"Base":>5s}')
print('-' * 95)

ELEM_MAP = {
    'Feu': 'mastery_fire',
    'Eau': 'mastery_water',
    'Air': 'mastery_air',
    'Terre': 'mastery_earth',
}

DI_PCT = REAL_STATS['damage_inflicted']  # 18%
CRIT_MASTERY = REAL_STATS['mastery_critical']  # 456
MELEE = REAL_STATS['mastery_melee']  # 1030

# Mais attention: le buff Temerite ajoute +12% DI en combat
# Le DI de base est 18%, Temerite ajoute 12% -> 30% en combat ?
# Non: le 18% dans la fiche INCLUT Temerite (c'est un passif permanent)
# Donc en combat, le DI de la fiche EST le DI de base
# MAIS le log montre "12 % Dommages infliges (Temerite)" et "24 % Dommages infliges (Temerite)"
# Cela signifie que Temerite est un buff qui STACK en combat, au-dela du 18% de base

# Test avec DI = 18% (fiche) + 0% combat buff pour le premier sort
# Test avec DI = 18% + 12% Temerite = 30% pour les sorts suivants

results = []

for (name, pa, elem, crit, real_direct, real_dot) in REAL_SPELLS:
    if real_direct == 0:
        continue
    
    elem_mastery = REAL_STATS.get(ELEM_MAP.get(elem, 'mastery_fire'), 0)
    
    # Mastery totale
    if crit:
        total_mastery = elem_mastery + MELEE + CRIT_MASTERY
    else:
        total_mastery = elem_mastery + MELEE
    
    mastery_mult = 1 + total_mastery / 100
    crit_mult = 1.25 if crit else 1.0
    
    # Tester differents DI pour trouver la bonne valeur
    # Mise a mort est le premier sort offensif -> DI = 18% (fiche) ou 18% + buff?
    # Le log montre que Temerite apparait APRES Saignee mortelle (4e sort)
    # Donc les premiers sorts ont DI = 18% base
    
    di_base = 18  # % de la fiche
    # Le premier sort du tour n'a probablement pas encore Temerite stack
    # Mais le 18% inclut peut-etre deja des passifs permanents
    
    di_mult = 1 + di_base / 100
    
    full_mult = mastery_mult * crit_mult * di_mult
    base = real_direct / full_mult
    
    cm = 'C' if crit else ' '
    print(f'{name:25s} | {elem:4s} | {cm:2s} | {elem_mastery:>5d} | {MELEE:>5d} | {CRIT_MASTERY if crit else 0:>5d} | {total_mastery:>5d} | {full_mult:>6.2f} | {real_direct:>7,} | {base:>5.0f}')
    
    results.append({
        'name': name, 'pa': pa, 'elem': elem, 'crit': crit,
        'real_direct': real_direct, 'real_dot': real_dot,
        'base': round(base), 'total_mastery': total_mastery,
        'multiplier': round(full_mult, 3),
    })

# Verification
print()
print('=== VERIFICATION ===')
for r in results:
    name = r['name']
    base = r['base']
    mult = r['multiplier']
    recalc = base * mult
    ecart = ((recalc - r['real_direct']) / r['real_direct']) * 100
    print(f'  {name:25s} | base={base:>4d} * {mult:.2f} = {recalc:>7,.0f} vs {r["real_direct"]:>7,} | {ecart:+.1f}%')

# Les bases sont-elles coherentes? (meme sort = meme base?)
print()
print('=== COHERENCE ===')
print('Kleptosram et Ouvrir les veines ont le meme reel (3753) et meme PA (4 vs 3)')
print('Si meme elem+mastery -> bases differentes = sorts differents (OK)')

# Sauvegarder la calibration corrigee
cal_data = {
    'calibration_date': '2026-03-14',
    'calibration_version': '2.0',
    'player': "L'Immortel",
    'class': 'Sram',
    'level': 179,
    'real_stats': REAL_STATS,
    'formula': {
        'description': 'Degats = Base * (1 + TotalMastery/100) * CritMult * (1 + DI/100) * ResMult',
        'mastery_crit': 'ElemMastery + MeleeMastery + CritMastery',
        'mastery_normal': 'ElemMastery + MeleeMastery',
        'crit_mult': 1.25,
        'di_base': DI_PCT,
    },
    'spells': {},
}

for r in results:
    cal_data['spells'][r['name']] = {
        'base': r['base'],
        'elem': r['elem'],
        'pa': r['pa'],
        'dot_ratio': round(r['real_dot'] / r['real_direct'] * 100) if r['real_direct'] > 0 else 0,
        'armor_ratio': 40 if r['name'] == 'Attaque perfide' else 0,
        'multiplier_crit': r['multiplier'] if r['crit'] else None,
        'multiplier_normal': r['multiplier'] if not r['crit'] else None,
    }

out_path = os.path.join(PROJECT, 'data', 'extracted', 'sram_calibration.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(cal_data, f, indent=2, ensure_ascii=False)
print(f'\nCalibration v2.0 sauvegardee: {out_path}')
