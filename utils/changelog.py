"""
Systeme de changelog automatique.
Detecte les fichiers modifies et ecrit dans logs/modifications.jsonl
Sert de memoire persistante entre les sessions LLM.

Usage:
    from utils.changelog import log_modification, scan_changes
    log_modification("engine/damage.py", "create", "Formule officielle de degats")
    scan_changes()  # detecte automatiquement les fichiers modifies
"""

import json
import hashlib
import os
import time
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

MODIFICATIONS_FILE = os.path.join(config.LOGS_DIR, "modifications.jsonl")
HASHES_FILE = os.path.join(config.LOGS_DIR, "file_hashes.json")
REGISTRY_FILE = os.path.join(config.LOGS_DIR, "module_registry.json")


def _ensure_dirs():
    os.makedirs(config.LOGS_DIR, exist_ok=True)


def _file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(filepath, data):
    _ensure_dirs()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_modification(filepath, action, description, dependencies=None):
    _ensure_dirs()
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "file": filepath.replace("\\\\", "/"),
        "action": action,
        "description": description,
        "dependencies": dependencies or [],
        "version": config.VERSION,
    }
    with open(MODIFICATIONS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\\n")

    registry = _load_json(REGISTRY_FILE, {})
    key = filepath.replace("\\\\", "/")
    registry[key] = {
        "role": description,
        "last_modified": time.strftime("%Y-%m-%d"),
        "action": action,
        "version": config.VERSION,
        "depends_on": dependencies or [],
    }
    _save_json(REGISTRY_FILE, registry)


def scan_changes():
    _ensure_dirs()
    old_hashes = _load_json(HASHES_FILE, {})
    new_hashes = {}
    changes = []

    extensions = {".py", ".json", ".md"}
    skip_dirs = {"_archive", ".git", "__pycache__", "output", ".venv"}

    for root, dirs, files in os.walk(config.PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for filename in files:
            if os.path.splitext(filename)[1] not in extensions:
                continue
            filepath = os.path.join(root, filename)
            relative = os.path.relpath(filepath, config.PROJECT_ROOT).replace("\\\\", "/")
            h = _file_hash(filepath)
            new_hashes[relative] = h

            if relative not in old_hashes:
                changes.append((relative, "create"))
            elif old_hashes[relative] != h:
                changes.append((relative, "modify"))

    for relative in old_hashes:
        if relative not in new_hashes:
            changes.append((relative, "delete"))

    _save_json(HASHES_FILE, new_hashes)
    return changes


def print_registry():
    registry = _load_json(REGISTRY_FILE, {})
    if not registry:
        print("Aucun module enregistre.")
        return
    print(f"\\n{'='*60}")
    print(f"  MODULE REGISTRY ({len(registry)} fichiers)")
    print(f"{'='*60}")
    for path, info in sorted(registry.items()):
        print(f"  {path}")
        print(f"    Role: {info.get('role', '?')}")
        print(f"    Modifie: {info.get('last_modified', '?')} | V{info.get('version', '?')}")
        if info.get("depends_on"):
            print(f"    Depends: {', '.join(info['depends_on'])}")
        print()


if __name__ == "__main__":
    changes = scan_changes()
    if changes:
        print(f"{len(changes)} changement(s) detecte(s):")
        for filepath, action in changes:
            print(f"  [{action.upper()}] {filepath}")
    else:
        print("Aucun changement detecte.")
    print_registry()
