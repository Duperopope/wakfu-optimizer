import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\local_agent.py')
c = f.read_text('utf-8-sig')

# Le probleme: quand le code contient "import" ou "print(", l'heuristique dit NO_EXEC
# Mais "python -c" est une commande executable
# Ajouter une detection: si le bloc commence par "python " ou "$" ou "Write-Host" etc
# c'est une commande, pas du code source

old_heuristic = "def sentinel_heuristic(code_block):"
new_heuristic = """def sentinel_heuristic(code_block):
    code = code_block.strip()
    # Detection prioritaire: commandes executables
    cmd_starts = ['python ', 'python3 ', 'pip ', 'npm ', 'node ', 'git ',
                  'cd ', 'dir ', 'ls ', 'mkdir ', 'Write-Host', 'Get-',
                  'Set-', 'New-', 'Remove-', 'Invoke-', 'Start-', 'Stop-',
                  'Test-Path', '@\\'', '$']
    first_line = code.split(chr(10))[0].strip()
    for cmd in cmd_starts:
        if first_line.startswith(cmd):
            # Verifier danger
            danger_patterns = ['Remove-Item.*-Recurse.*-Force', 'Stop-Process.*-Force',
                               'Format-Volume', 'Clear-Disk', 'rm -rf']
            import re as _re
            for dp in danger_patterns:
                if _re.search(dp, code):
                    return {'verdict': 'EXEC_DANGER', 'reason': 'Destructive command (heuristic)', 'type': 'powershell'}
            return {'verdict': 'EXEC_SAFE', 'reason': 'Command executable (heuristic)', 'type': 'powershell'}
    # Suite de l'heuristique originale pour le code source..."""

# Remplacer seulement la premiere ligne de la fonction
c = c.replace("def sentinel_heuristic(code_block):\n    code = code_block.strip()", new_heuristic)

f.write_text(c, 'utf-8')
print('Heuristique SENTINEL amelioree:', f.stat().st_size, 'octets')
