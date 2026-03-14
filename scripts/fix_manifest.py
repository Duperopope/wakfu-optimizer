import pathlib, json

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\manifest.json')
m = json.loads(f.read_text('utf-8'))

# Ajouter la permission pour le serveur local
if 'http://127.0.0.1:8091/*' not in m['host_permissions']:
    m['host_permissions'].append('http://127.0.0.1:8091/*')

# Ajouter aussi localhost au cas ou
if 'http://localhost:8091/*' not in m['host_permissions']:
    m['host_permissions'].append('http://localhost:8091/*')

f.write_text(json.dumps(m, indent=2, ensure_ascii=False), 'utf-8')
print('Permissions ajoutees:', m['host_permissions'])
