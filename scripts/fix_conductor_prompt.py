import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\conductor.py')
c = f.read_text('utf-8')

# Ameliorer le prompt pour forcer des vraies commandes
old = "'escalate=probleme critique pour humain, done=tache terminee. Sois concis.'"
new = ("'escalate=probleme critique pour humain, done=tache terminee. '\n"
       "    'IMPORTANT: fix_command DOIT etre une vraie commande PowerShell executable, '\n"
       "    'PAS du texte en francais. Exemple: python -c \"print(2+2)\" ou Write-Host \"test\". '\n"
       "    'Si tu ne sais pas comment corriger, utilise action=escalate pour demander a Claude Opus. '\n"
       "    'Sois concis.'")

c = c.replace(old, new)
f.write_text(c, 'utf-8')
print('Conductor prompt ameliore:', f.stat().st_size, 'octets')
