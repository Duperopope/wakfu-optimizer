#!/usr/bin/env python3
"""
sync_wakfuli.py - Extraction complete de l'API Wakfuli
======================================================
Phase 1 du pipeline Wakfu Optimizer.
Source : https://api.wakfuli.com/api/v1/
Version Ankama : recuperee depuis wakfu.cdn.ankama.com/gamedata/config.json

Ce script :
  1. Telecharge les 7 600+ items (pagines par 100)
  2. Telecharge les 68 actions/effets (une seule page)
  3. Telecharge les builds publics (pagines par 50)
  4. Extrait les IDs de sorts uniques depuis les builds
  5. Sauvegarde tout dans data/wakfuli/ avec metadonnees
  6. Genere un rapport de synchronisation dans logs/

Usage :
    python scripts/sync_wakfuli.py

Prerequis :
    pip install requests
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "wakfuli"
LOGS_DIR = PROJECT_ROOT / "logs"

API_BASE = "https://api.wakfuli.com/api/v1"
ANKAMA_CONFIG = "https://wakfu.cdn.ankama.com/gamedata/config.json"

ITEMS_PER_PAGE = 100
BUILDS_PER_PAGE = 50
ACTIONS_PER_PAGE = 100

REQUEST_DELAY = 0.3

# =============================================================================
# LOGGING
# =============================================================================

LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOGS_DIR / f"sync_wakfuli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("sync_wakfuli")

# =============================================================================
# IMPORT REQUESTS
# =============================================================================

try:
    import requests
except ImportError:
    log.error("Le module 'requests' n'est pas installe.")
    log.error("Installe-le avec : pip install requests")
    sys.exit(1)

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================


def fetch_json(url, params=None, retries=3):
    """Effectue un GET et retourne le JSON. Retries avec backoff."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            wait = 2 ** attempt
            log.warning(f"Tentative {attempt}/{retries} echouee pour {url}: {e}")
            if attempt < retries:
                log.info(f"Nouvelle tentative dans {wait}s...")
                time.sleep(wait)
            else:
                log.error(f"Echec definitif pour {url} apres {retries} tentatives.")
                raise
    return None


def paginate_all(endpoint, per_page, label="items"):
    """Recupere toutes les pages d'un endpoint pagine Wakfuli."""
    all_data = []
    page = 1

    log.info(f"[{label}] Requete page 1...")
    result = fetch_json(f"{API_BASE}/{endpoint}", params={
        "page": page,
        "limit": per_page,
    })

    meta = result.get("meta", {})
    total = meta.get("total", 0)
    last_page = meta.get("lastPage", 1)

    log.info(f"[{label}] Total: {total} entrees sur {last_page} pages")

    all_data.extend(result.get("data", []))
    log.info(f"[{label}] Page 1/{last_page} -- {len(all_data)}/{total} recuperes")

    for page in range(2, last_page + 1):
        time.sleep(REQUEST_DELAY)
        log.info(f"[{label}] Requete page {page}/{last_page}...")

        result = fetch_json(f"{API_BASE}/{endpoint}", params={
            "page": page,
            "limit": per_page,
        })

        batch = result.get("data", [])
        all_data.extend(batch)
        log.info(f"[{label}] Page {page}/{last_page} -- {len(all_data)}/{total} recuperes")

    log.info(f"[{label}] Termine : {len(all_data)} entrees recuperees (attendu: {total})")

    return all_data, {
        "total_expected": total,
        "total_received": len(all_data),
        "pages": last_page,
    }


def save_json(data, filename, pretty=True):
    """Sauvegarde un objet en JSON dans data/wakfuli/."""
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False)
    size_mb = filepath.stat().st_size / (1024 * 1024)
    log.info(f"Sauvegarde : {filepath} ({size_mb:.2f} MB)")
    return filepath


# =============================================================================
# EXTRACTION PRINCIPALE
# =============================================================================


def sync_game_version():
    """Recupere la version actuelle du jeu depuis le CDN Ankama."""
    log.info("Recuperation de la version du jeu...")
    config = fetch_json(ANKAMA_CONFIG)
    version = config.get("version", "inconnue")
    log.info(f"Version du jeu : {version}")
    return version


def sync_items():
    """Telecharge tous les items depuis /items."""
    log.info("=" * 60)
    log.info("EXTRACTION DES ITEMS")
    log.info("=" * 60)

    items, meta = paginate_all("items", ITEMS_PER_PAGE, label="Items")
    save_json(items, "all_items.json")
    return items, meta


def sync_actions():
    """Telecharge toutes les actions depuis /actions."""
    log.info("=" * 60)
    log.info("EXTRACTION DES ACTIONS")
    log.info("=" * 60)

    actions, meta = paginate_all("actions", ACTIONS_PER_PAGE, label="Actions")
    save_json(actions, "all_actions.json")
    return actions, meta


def sync_builds():
    """Telecharge tous les builds publics depuis /builds."""
    log.info("=" * 60)
    log.info("EXTRACTION DES BUILDS PUBLICS")
    log.info("=" * 60)

    builds, meta = paginate_all("builds", BUILDS_PER_PAGE, label="Builds")

    all_spell_ids = set()
    all_passive_ids = set()
    classes_found = set()
    builds_without_spells = 0

    for build in builds:
        char_class = build.get("characterClass")
        if char_class:
            classes_found.add(char_class)

        spells = build.get("spells")

        # Certains builds ont spells = null ou un format inattendu
        if not isinstance(spells, dict):
            builds_without_spells += 1
            continue

        for spell_id in spells.get("ea", []):
            if isinstance(spell_id, int):
                all_spell_ids.add(spell_id)

        for spell_id in spells.get("passive", []):
            if isinstance(spell_id, int):
                all_passive_ids.add(spell_id)

    log.info(f"Classes trouvees dans les builds : {sorted(classes_found)}")
    log.info(f"Sorts actifs uniques : {len(all_spell_ids)}")
    log.info(f"Sorts passifs uniques : {len(all_passive_ids)}")
    log.info(f"Builds sans sorts (spells=null) : {builds_without_spells}")

    save_json(builds, "all_builds.json")

    spell_index = {
        "active_spell_ids": sorted(all_spell_ids),
        "passive_spell_ids": sorted(all_passive_ids),
        "all_spell_ids": sorted(all_spell_ids | all_passive_ids),
        "classes": sorted(classes_found),
        "total_builds_analyzed": len(builds),
        "builds_without_spells": builds_without_spells,
    }
    save_json(spell_index, "spell_index_from_builds.json")

    return builds, meta, spell_index


def generate_sync_report(version, items_meta, actions_meta, builds_meta, spell_index, duration):
    """Genere le rapport de synchronisation."""
    report = {
        "sync_date": datetime.now(timezone.utc).isoformat(),
        "game_version": version,
        "api_base": API_BASE,
        "duration_seconds": round(duration, 1),
        "datasets": {
            "items": items_meta,
            "actions": actions_meta,
            "builds": builds_meta,
        },
        "spell_extraction": {
            "active_spells": len(spell_index["active_spell_ids"]),
            "passive_spells": len(spell_index["passive_spell_ids"]),
            "total_unique_spells": len(spell_index["all_spell_ids"]),
            "classes_covered": spell_index["classes"],
        },
        "files_generated": [
            "data/wakfuli/all_items.json",
            "data/wakfuli/all_actions.json",
            "data/wakfuli/all_builds.json",
            "data/wakfuli/spell_index_from_builds.json",
            "data/wakfuli/sync_report.json",
            "data/wakfuli/version.json",
        ],
    }

    save_json(report, "sync_report.json")
    return report


# =============================================================================
# MAIN
# =============================================================================


def main():
    log.info("=" * 60)
    log.info("WAKFULI SYNC -- Extraction complete")
    log.info(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Projet : {PROJECT_ROOT}")
    log.info(f"Destination : {DATA_DIR}")
    log.info("=" * 60)

    start_time = time.time()

    version = sync_game_version()
    save_json({"game_version": version, "synced_at": datetime.now(timezone.utc).isoformat()}, "version.json")

    items, items_meta = sync_items()
    actions, actions_meta = sync_actions()
    builds, builds_meta, spell_index = sync_builds()

    duration = time.time() - start_time
    report = generate_sync_report(version, items_meta, actions_meta, builds_meta, spell_index, duration)

    log.info("=" * 60)
    log.info("SYNCHRONISATION TERMINEE")
    log.info("=" * 60)
    log.info(f"Version du jeu     : {version}")
    log.info(f"Items              : {items_meta['total_received']}")
    log.info(f"Actions            : {actions_meta['total_received']}")
    log.info(f"Builds publics     : {builds_meta['total_received']}")
    log.info(f"Sorts uniques      : {len(spell_index['all_spell_ids'])}")
    log.info(f"Classes couvertes  : {', '.join(spell_index['classes'])}")
    log.info(f"Duree              : {duration:.1f}s")
    log.info(f"Fichiers dans      : {DATA_DIR}")
    log.info(f"Log complet        : {log_file}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
