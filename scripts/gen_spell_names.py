import json, sys
sys.path.insert(0, '.')

# Noms des sorts Sram (refonte 1.91 - source: wakfu.com/fr/mmorpg/actualites/maj/1767729)
# Mapping base sur: element (1=feu,2=eau,4=air,9=support) + PA_base + uiPosition

with open('data/extracted/all_spells.json', 'r', encoding='utf-8') as f:
    spells = json.load(f)

with open('data/extracted/breeds.json', 'r', encoding='utf-8') as f:
    breeds = json.load(f)

spell_by_id = {}
for s in spells:
    spell_by_id[s['id']] = s

# Noms connus des sorts Sram (post-refonte 1.91)
# Source: https://www.wakfu.com/fr/mmorpg/actualites/maj/1767729-mise-jour-1-91/details
SRAM_SPELL_NAMES = {
    4604: 'Double',
    4586: 'Mise a mort',
    4585: 'Attaque perfide',
    4595: 'Fourberie',
}

# Elements: 1=Feu, 2=Eau, 4=Air, 8=Terre, 9=Support/Neutre
ELEMENT_NAMES = {
    1: 'Feu', 2: 'Eau', 4: 'Air', 8: 'Terre', 9: 'Support',
    0: 'Neutre', 3: 'Feu+Eau', 5: 'Feu+Air', 6: 'Eau+Air',
    7: 'Feu+Eau+Air', 10: 'Eau+Support', 12: 'Terre+Air',
    15: 'Multi', 16: 'Lumiere', 21: 'Multi',
}

# Generer un fichier spell_names.json pour toutes les classes
spell_names = {}
for breed in breeds:
    bid = breed.get('id', 0)
    spell_ids = breed.get('ehx', [])
    for sid in spell_ids:
        s = spell_by_id.get(sid, {})
        elem = s.get('element', 0)
        pa = s.get('PA_base', 0)
        pw = s.get('PW_base', 0)
        pos = s.get('uiPosition', 0)
        elem_name = ELEMENT_NAMES.get(elem, 'Inconnu(' + str(elem) + ')')
        
        # Utiliser le nom connu si disponible
        if sid in SRAM_SPELL_NAMES:
            name = SRAM_SPELL_NAMES[sid]
        else:
            # Generer un nom descriptif
            breed_names = {
                1:'Feca', 2:'Osamodas', 3:'Enutrof', 4:'Sram', 5:'Xelor',
                6:'Ecaflip', 7:'Eniripsa', 8:'Iop', 9:'Cra', 10:'Sadida',
                11:'Sacrier', 12:'Pandawa', 13:'Roublard', 14:'Zobal',
                15:'Ouginak', 16:'Steamer', 17:'Eliotrope', 18:'Huppermage', 19:'Huppermage'
            }
            bname = breed_names.get(bid, 'Classe' + str(bid))
            cost = ''
            if pa > 0:
                cost = str(int(pa)) + 'PA'
            if pw > 0:
                cost = cost + (' ' if cost else '') + str(int(pw)) + 'PW'
            name = bname + ' ' + elem_name + ' #' + str(pos+1) + ' (' + cost + ')'
        
        spell_names[str(sid)] = {
            'id': sid,
            'name_fr': name,
            'element': elem,
            'element_name': elem_name,
            'pa': pa,
            'pw': pw,
            'breed_id': bid,
            'ui_position': pos,
        }

# Sauvegarder
output_path = 'data/extracted/spell_names.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(spell_names, f, ensure_ascii=False, indent=2)

print('spell_names.json genere: ' + str(len(spell_names)) + ' sorts nommes')
print()
for sid, info in sorted(spell_names.items(), key=lambda x: (x[1]['breed_id'], x[1]['ui_position'])):
    print('  [' + str(info['breed_id']).rjust(2) + '] ' + info['name_fr'].ljust(40) + ' ' + info['element_name'].ljust(10) + ' ' + str(int(info['pa'])) + 'PA ' + str(int(info['pw'])) + 'PW')
