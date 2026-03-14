import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

# Ajouter import conductor apres import memory_manager
old_import = 'HAS_MEMORY = True'
new_import = """HAS_MEMORY = True
try:
    from conductor import ask_conductor, format_message
    HAS_CONDUCTOR = True
except Exception as e:
    print('Conductor non disponible:', e)
    HAS_CONDUCTOR = False"""

c = c.replace(old_import, new_import, 1)

# Ajouter route /conductor avant /ollama
old_route = '        elif path == "/ollama":'
new_route = """        elif path == "/conductor":
            cmd = body.get("command", "")
            output = body.get("output", "")
            returncode = body.get("returncode", 0)
            task = body.get("task_context", "")
            if HAS_CONDUCTOR:
                try:
                    decision = ask_conductor(cmd, output, returncode, task)
                    message = format_message(decision)
                    decision["formatted_message"] = message
                    self._json(decision)
                except Exception as e:
                    log("CONDUCTOR", "Erreur: " + str(e))
                    self._json({"action": "continue", "formatted_message": "Continue avec la prochaine etape.", "error": str(e)})
            else:
                self._json({"action": "continue", "formatted_message": "Conductor non disponible. Continue.", "error": "not loaded"})
        elif path == "/ollama":"""

c = c.replace(old_route, new_route)

# Ajouter /conductor dans le banner
c = c.replace('/build-memory /session-end /ollama /restart', '/conductor /build-memory /session-end /ollama /restart')

f.write_text(c, 'utf-8')
print('Route /conductor ajoutee - dev_server.py:', f.stat().st_size, 'octets')
