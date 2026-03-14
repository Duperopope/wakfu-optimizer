import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\memory_manager.py')
c = f.read_text('utf-8')

fixes = {
    'lines = [f"# Working Notes - {datetime.now().strftime("%Y-%m-%d %H:%M")}", ""]':
        'lines = ["# Working Notes - " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]',

    'name = f"auto_{datetime.now().strftime("%Y%m%d_%H%M")}"':
        'name = "auto_" + datetime.now().strftime("%Y%m%d_%H%M")',

    'f"Duree: {summary[':
        None,

    'f"Fichiers modifies: {':
        None,
}

# Fix connus
for old, new in fixes.items():
    if new and old in c:
        c = c.replace(old, new)
        print('Fixed: ' + old[:60])

# Fix generique: trouver toutes les lignes avec f-string qui contiennent .strftime ou .join dans {}
lines = c.split('\n')
fixed = []
for i, line in enumerate(lines):
    original = line

    # f"...{summary['duration_min']}..." -> concat
    if 'summary[' in line and ('f"' in line or "f'" in line):
        line = line.replace(
            'f"Duree: {summary[\'duration_min\']}min | Commandes: {summary[\'commands_run\']} | Erreurs: {summary[\'errors\']}"',
            '"Duree: " + str(summary[\'duration_min\']) + "min | Commandes: " + str(summary[\'commands_run\']) + " | Erreurs: " + str(summary[\'errors\'])'
        )
        line = line.replace(
            'f"Fichiers modifies: {", ".join(summary[\'files_modified\'][:10])}"',
            '"Fichiers modifies: " + ", ".join(summary[\'files_modified\'][:10])'
        )

    # f"- {f['context']..." -> concat
    if "f['context']" in line and ('f"' in line or "f'" in line):
        line = line.replace(
            'f"- {f[\'context\'][:80]}: {f[\'result\'][:100]}"',
            '"- " + f[\'context\'][:80] + ": " + f[\'result\'][:100]'
        )

    if line != original:
        print(f'Fixed L{i+1}: {original.strip()[:60]}')
    fixed.append(line)

c = '\n'.join(fixed)
f.write_text(c, 'utf-8')
print(f'Done - {f.stat().st_size} octets')
