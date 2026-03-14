"""
session_end.py - Script de fin de session
Met a jour CHANGELOG.md, cree SESSION_HANDOFF.md, relance build_memory.py.
Usage : python scripts/session_end.py
  ou   python scripts/session_end.py "Titre de la session"
"""

import sys, json, subprocess
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
DATE = datetime.now().strftime("%Y-%m-%d")

def ask(prompt, default=""):
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default

def main():
    print("=" * 50)
    print("  SESSION END - wakfu-optimizer")
    print(f"  {NOW}")
    print("=" * 50)
    print()

    # Titre
    if len(sys.argv) > 1:
        title = " ".join(sys.argv[1:])
    else:
        title = ask("Titre de la session", "Session de travail")

    # Ce qui a ete fait
    print("Ce qui a ete fait (une ligne par item, ligne vide pour finir) :")
    work_done = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        work_done.append(line)

    # Fichiers modifies
    print("Fichiers modifies (une ligne par item, ligne vide pour finir) :")
    files_modified = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        files_modified.append(line)

    # Problemes
    print("Problemes non resolus (une ligne par item, ligne vide pour finir) :")
    issues = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        issues.append(line)

    # 1. SESSION_HANDOFF.md
    handoff = [
        "# SESSION HANDOFF - wakfu-optimizer",
        f"> Derniere session : {NOW}",
        f"> Titre : {title}",
        "",
        "## CE QUI A ETE FAIT",
    ]
    for w in work_done:
        handoff.append(f"- {w}")
    handoff.append("")
    handoff.append("## FICHIERS MODIFIES")
    for f in files_modified:
        handoff.append(f"- {f}")
    handoff.append("")
    handoff.append("## PROBLEMES NON RESOLUS")
    for i in issues:
        handoff.append(f"- {i}")
    handoff.append("")
    handoff.append("## PROCHAINE ETAPE")
    handoff.append("- Lire BRIEFING.md en debut de prochaine session")
    handoff.append("")

    handoff_path = PROJECT / "SESSION_HANDOFF.md"
    handoff_path.write_text("\n".join(handoff), "utf-8")
    print(f"\nSESSION_HANDOFF.md ecrit ({len(handoff)} lignes)")

    # 2. CHANGELOG.md
    changelog_path = PROJECT / "CHANGELOG.md"
    entry = [
        "",
        f"## [{DATE}] {title}",
        f"> Mise a jour : {NOW}",
        "> Commits : https://github.com/Duperopope/wakfu-optimizer/commits/main",
        "",
        "### Ce qui a ete fait",
    ]
    for w in work_done:
        entry.append(f"- {w}")
    entry.append("")
    entry.append("### Fichiers modifies")
    for f in files_modified:
        entry.append(f"- {f}")
    entry.append("")
    if issues:
        entry.append("### Problemes non resolus")
        for i in issues:
            entry.append(f"- {i}")
        entry.append("")

    if changelog_path.exists():
        existing = changelog_path.read_text("utf-8")
        if "---" in existing:
            parts = existing.split("---", 1)
            new_content = parts[0] + "---" + "\n".join(entry) + "\n" + parts[1]
        else:
            new_content = existing + "\n".join(entry)
        changelog_path.write_text(new_content, "utf-8")
    else:
        header = "# CHANGELOG - wakfu-optimizer\n> Archive des sessions\n\n---\n"
        changelog_path.write_text(header + "\n".join(entry), "utf-8")
    print("CHANGELOG.md mis a jour")

    # 3. Regenerer memoire
    print("\nRegeneration de la memoire...")
    r = subprocess.run(
        [sys.executable, "scripts/build_memory.py"],
        capture_output=True, text=True, cwd=str(PROJECT)
    )
    print(r.stdout)
    if r.returncode != 0:
        print(f"ERREUR build_memory: {r.stderr}")

    print("\n=== SESSION TERMINEE ===")
    print("autopush.py va pousser les changements.")
