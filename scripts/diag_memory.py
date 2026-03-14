import pathlib, json

# 1. Verifier le log memory_manager
ml = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\logs\memory_manager.log')
if ml.exists():
    lines = ml.read_text('utf-8').strip().split('\n')
    print('=== MEMORY LOG (dernieres 15 lignes) ===')
    for l in lines[-15:]:
        print('  ' + l)
else:
    print('Pas de log memory')

print()

# 2. Verifier le log du serveur pour ext-log
sl = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\logs\dev_server.log')
if sl.exists():
    lines = sl.read_text('utf-8').strip().split('\n')
    extlogs = [l for l in lines if 'ext-log' in l.lower() or 'EXT-LOG' in l]
    print('=== EXT-LOG dans server log:', len(extlogs), '===')
    for l in extlogs[-5:]:
        print('  ' + l)
    if not extlogs:
        print('  Aucun ext-log recu par le serveur')

print()

# 3. Verifier les routes du serveur
import urllib.request
try:
    req = urllib.request.Request(
        'http://localhost:8091/ext-log',
        data=json.dumps({"message": "test diagnostic", "type": "diagnostic"}).encode(),
        headers={"Content-Type": "application/json"},
        method='POST'
    )
    resp = urllib.request.urlopen(req, timeout=10)
    print('=== Test ext-log direct:', json.loads(resp.read()), '===')
except Exception as e:
    print('=== Test ext-log ERREUR:', e, '===')
