import json, os

PROJECT = r'H:\Code\Ankama Dev\wakfu-optimizer'

with open(os.path.join(PROJECT, 'data', 'extracted', 'all_static_effects.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Type: {type(data).__name__}')

if isinstance(data, list):
    print(f'Longueur: {len(data)}')
    print(f'Type element 0: {type(data[0]).__name__}')
    # Montrer les 3 premiers
    for i in range(min(3, len(data))):
        item = data[i]
        if isinstance(item, dict):
            print(f'  [{i}] keys={list(item.keys())[:10]}')
            print(f'  [{i}] = {str(item)[:200]}')
        elif isinstance(item, list):
            print(f'  [{i}] list len={len(item)}')
            if item:
                print(f'  [{i}][0] = {str(item[0])[:200]}')
        else:
            print(f'  [{i}] = {str(item)[:200]}')

elif isinstance(data, dict):
    keys = list(data.keys())[:10]
    print(f'Cles: {len(data.keys())} total, premieres: {keys}')
    for k in keys[:3]:
        v = data[k]
        print(f'  [{k}] type={type(v).__name__} = {str(v)[:200]}')

# Chercher un effet specifique par ID connu (effet 120859 de spell 4604)
print()
print('=== Recherche effet 120859 ===')
if isinstance(data, dict):
    for k in ['120859', 120859]:
        if k in data:
            print(f'  Trouve par cle {k}: {str(data[k])[:300]}')
if isinstance(data, list):
    for item in data[:100]:
        if isinstance(item, dict):
            if item.get('id') == 120859 or item.get('definitionId') == 120859:
                print(f'  Trouve: {str(item)[:300]}')
                break

# Chercher un effet de sort Attaque perfide (4585) effectIds [411407, 411410, 159366, 159368]
print()
print('=== Recherche effets Attaque perfide ===')
search_ids = [411407, 411410, 159366, 159368]
for sid in search_ids:
    if isinstance(data, dict):
        for k in [str(sid), sid]:
            if k in data:
                print(f'  eff {sid}: {str(data[k])[:300]}')
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                if item.get('id') == sid or item.get('definitionId') == sid:
                    print(f'  eff {sid}: {str(item)[:300]}')
                    break
            elif isinstance(item, (int, str)) and (item == sid or str(item) == str(sid)):
                print(f'  eff {sid}: found as raw value')
