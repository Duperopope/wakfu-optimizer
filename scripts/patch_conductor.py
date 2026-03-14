import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\conductor.py')
c = f.read_text('utf-8')

# Mettre a jour le prompt pour inclure fix_command
old_prompt = "    'Regles: continue=OK donne prochaine instruction, fix=erreur explique quoi corriger, '"
new_prompt = (
    "    'Regles: continue=OK donne prochaine instruction, fix=erreur explique quoi corriger '\n"
    "    '(ajoute fix_command avec la commande PowerShell pour corriger si possible), '"
)

c = c.replace(old_prompt, new_prompt)

# Mettre a jour le format JSON dans le prompt
old_json = "    '{{\"action\": \"continue\" ou \"fix\" ou \"escalate\" ou \"done\", '"
new_json = "    '{{\"action\": \"continue\" ou \"fix\" ou \"escalate\" ou \"done\", \"fix_command\": \"commande PowerShell de correction (si fix)\", '"

c = c.replace(old_json, new_json)

# Ajouter enregistrement dans memoire procedurale
old_return = "            decision['tokens_per_sec'] = tok_s"
new_return = """            decision['tokens_per_sec'] = tok_s
            # Enregistrer dans memoire procedurale si fix reussi
            if decision.get('action') == 'fix' and decision.get('fix_command'):
                try:
                    from memory_manager import get_manager
                    mm = get_manager()
                    mm.procedural.register(
                        'auto_fix_' + datetime.now().strftime('%H%M%S'),
                        [decision['fix_command']],
                        ['auto-repair', 'conductor']
                    )
                except: pass"""

c = c.replace(old_return, new_return)

# Forcer reponse en francais
c = c.replace(
    "'Tu es le Conductor, un agent chef de projet IA. '",
    "'Tu es le Conductor, un agent chef de projet IA. Reponds toujours en francais. '"
)

f.write_text(c, 'utf-8')
print('Conductor v1.1 - fix_command + francais + memoire:', f.stat().st_size, 'octets')
