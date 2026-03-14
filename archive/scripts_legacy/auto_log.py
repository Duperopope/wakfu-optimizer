"""
Script de pre-lancement automatique.
A appeler avant chaque simulation ou manuellement.
Detecte les fichiers modifies, met a jour le registre,
et ecrit dans logs/modifications.jsonl.

Usage:
    python scripts/auto_log.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.changelog import scan_changes, log_modification, print_registry


def auto_log():
    changes = scan_changes()
    if not changes:
        print("Aucun changement depuis le dernier scan.")
    else:
        print(f"{len(changes)} changement(s) detecte(s):")
        for filepath, action in changes:
            print(f"  [{action.upper()}] {filepath}")
            log_modification(filepath, action, f"Auto-detecte par scan ({action})")

    print_registry()


if __name__ == "__main__":
    auto_log()
