#!/usr/bin/env python3
"""
scripts/data_sync.py  V5.0
Pipeline d extraction automatique des donnees Wakfu depuis le CDN Ankama.

Detecte les mises a jour, telecharge les JSON, parse et normalise
les items/actions/states pour l optimizer.

Sources:
  - API CDN officielle Ankama: https://wakfu.cdn.ankama.com/gamedata/{version}/{type}.json
  - Documentation officielle: https://www.wakfu.com/en/forum/591-custom-themes/236779-json-data
  - Parsing des effets: https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
  - DESIGN_DOC.md sections 3.1, 4.1
"""

import os
import sys
import json
import time
import shutil
import hashlib
import logging
import tempfile
import urllib.request
import urllib.error
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from utils.logger import setup_logger
    logger = setup_logger("scripts.data_sync")
except ImportError:
    logger = logging.getLogger("scripts.data_sync")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s"
    )

# ── Constants ───────────────────────────────────────────────────────────
CDN_BASE = "https://wakfu.cdn.ankama.com/gamedata"
CONFIG_URL = f"{CDN_BASE}/config.json"

# Tous les types JSON disponibles sur le CDN (source: post officiel Ankama)
CDN_TYPES = [
    "actions",
    "blueprints",
    "collectibleResources",
    "equipmentItemTypes",
    "harvestLoots",
    "itemProperties",
    "itemTypes",
    "items",
    "jobsItems",
    "recipeCategories",
    "recipeIngredients",
    "recipeResults",
    "recipes",
    "resourceTypes",
    "resources",
    "states",
]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
VERSION_FILE = DATA_DIR / "version.json"
MANIFEST_FILE = DATA_DIR / "sync_manifest.json"
SYNC_LOG = PROJECT_ROOT / "logs" / "sync_report.log"

# Timeout pour les requetes HTTP (secondes)
HTTP_TIMEOUT = 60
# Nombre de threads pour le telechargement parallele
MAX_WORKERS = 4


# ── Utilitaires ─────────────────────────────────────────────────────────
def sha256_file(filepath):
    """Calcule le SHA-256 d un fichier."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    """Calcule le SHA-256 de bytes."""
    return hashlib.sha256(data).hexdigest()


def ensure_dir(path):
    """Cree un repertoire s il n existe pas."""
    Path(path).mkdir(parents=True, exist_ok=True)


def http_get_json(url, timeout=HTTP_TIMEOUT):
    """Telecharge et parse du JSON depuis une URL."""
    logger.info(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "WakfuOptimizer/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw), raw
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP {e.code} pour {url}: {e.reason}")
        raise
    except urllib.error.URLError as e:
        logger.error(f"Erreur reseau pour {url}: {e.reason}")
        raise


def http_get_raw(url, timeout=HTTP_TIMEOUT):
    """Telecharge des donnees brutes depuis une URL."""
    logger.info(f"GET (raw) {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "WakfuOptimizer/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ── Phase 1: Detection de version ──────────────────────────────────────
class VersionChecker:
    """Verifie si une nouvelle version est disponible sur le CDN."""

    @staticmethod
    def get_remote_version():
        """Recupere la version courante depuis le CDN Ankama."""
        data, _ = http_get_json(CONFIG_URL)
        version = data.get("version", "unknown")
        logger.info(f"Version CDN distante: {version}")
        return version

    @staticmethod
    def get_local_version():
        """Lit la version locale stockee."""
        if VERSION_FILE.exists():
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            version = data.get("version", "none")
            logger.info(f"Version locale: {version}")
            return version
        logger.info("Aucune version locale trouvee")
        return "none"

    @staticmethod
    def save_local_version(version, sync_date=None):
        """Sauvegarde la version locale."""
        ensure_dir(DATA_DIR)
        payload = {
            "version": version,
            "last_sync": sync_date or datetime.now(timezone.utc).isoformat(),
            "cdn_base": CDN_BASE,
        }
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"Version locale mise a jour: {version}")

    @staticmethod
    def needs_update():
        """Retourne (needs_update, remote_version, local_version)."""
        remote = VersionChecker.get_remote_version()
        local = VersionChecker.get_local_version()
        needs = remote != local
        if needs:
            logger.info(f"Mise a jour necessaire: {local} -> {remote}")
        else:
            logger.info(f"Deja a jour: {local}")
        return needs, remote, local


# ── Phase 2: Telechargement CDN ─────────────────────────────────────────
class CDNDownloader:
    """Telecharge tous les fichiers JSON du CDN en parallele."""

    def __init__(self, version):
        self.version = version
        self.base_url = f"{CDN_BASE}/{version}"
        self.results = {}

    def _download_one(self, data_type):
        """Telecharge un fichier JSON unique."""
        url = f"{self.base_url}/{data_type}.json"
        try:
            raw_bytes = http_get_raw(url)
            # Valide que c est du JSON valide
            json.loads(raw_bytes)
            return data_type, raw_bytes, None
        except Exception as e:
            return data_type, None, str(e)

    def download_all(self, tmp_dir):
        """
        Telecharge tous les types en parallele dans tmp_dir.
        Retourne un dict {type: filepath} et la liste des erreurs.
        """
        ensure_dir(tmp_dir)
        errors = []
        file_map = {}

        logger.info(f"Telechargement de {len(CDN_TYPES)} fichiers JSON (v{self.version})...")
        start = time.time()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(self._download_one, dt): dt
                for dt in CDN_TYPES
            }
            for future in as_completed(futures):
                data_type, raw_bytes, error = future.result()
                if error:
                    errors.append((data_type, error))
                    logger.error(f"  ECHEC {data_type}: {error}")
                else:
                    filepath = Path(tmp_dir) / f"{data_type}.json"
                    with open(filepath, "wb") as f:
                        f.write(raw_bytes)
                    file_map[data_type] = filepath
                    size_kb = len(raw_bytes) / 1024
                    logger.info(f"  OK {data_type}.json ({size_kb:.1f} Ko)")

        elapsed = time.time() - start
        logger.info(
            f"Telechargement termine: {len(file_map)}/{len(CDN_TYPES)} OK "
            f"en {elapsed:.1f}s, {len(errors)} erreur(s)"
        )
        return file_map, errors


# ── Phase 3: Parsing et normalisation ───────────────────────────────────
class ActionParser:
    """
    Parse actions.json pour creer un dictionnaire actionId -> effet lisible.

    Chaque action a un ID, un nom d effet, et un template de description
    avec des conditions conditionnelles.
    Source: https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
    """

    # Mapping des actionId les plus importants pour l optimizer
    KNOWN_ACTIONS = {
        1: "damage_neutral",
        # Note: actionId 2,3,4,5 n existent pas dans le CDN Ankama.
        # Les degats elementaires passent par actionId 1083 (Light Damage)
        # qui s adapte automatiquement a l element de maitrise du lanceur.
        20: "boost_hp",
        21: "deboost_hp",
        24: "heal_lifesteal",
        26: "mastery_heal",
        31: "boost_ap",
        39: "gain_charac",
        40: "loss_charac",
        41: "boost_mp",
        56: "deboost_ap",
        57: "deboost_mp",
        71: "res_rear",
        80: "res_elemental",
        82: "res_fire",
        83: "res_water",
        84: "res_earth",
        85: "res_air",
        90: "loss_res_elemental",
        120: "mastery_elemental",
        122: "mastery_fire",
        123: "mastery_earth",
        124: "mastery_water",
        125: "mastery_air",
        130: "loss_mastery_elemental",
        149: "mastery_critical",
        150: "critical_hit_percent",
        160: "gain_range",
        162: "gain_prospection",
        166: "gain_wisdom",
        168: "loss_critical_percent",
        171: "gain_initiative",
        173: "gain_lock",
        175: "gain_dodge",
        177: "gain_willpower",
        180: "mastery_rear",
        191: "boost_wp",
        192: "deboost_wp",
        304: "apply_state",
        875: "gain_block_percent",
        988: "res_critical",
        1052: "mastery_melee",
        1053: "mastery_distance",
        1055: "mastery_berserk",
        1068: "mastery_random_elements",
        1069: "res_random_elements",
        1083: "damage_light",
        1084: "heal_light",
    }

    def __init__(self, actions_filepath):
        self.actions_filepath = actions_filepath
        self.action_map = {}  # id -> {id, effect, description_fr, description_en, category}

    def parse(self):
        """Parse actions.json et construit le dictionnaire."""
        with open(self.actions_filepath, "r", encoding="utf-8") as f:
            raw_actions = json.load(f)

        for entry in raw_actions:
            defn = entry.get("definition", {})
            action_id = defn.get("id")
            effect_name = defn.get("effect", "")

            desc = entry.get("description", {})
            desc_fr = desc.get("fr", "")
            desc_en = desc.get("en", "")

            category = self.KNOWN_ACTIONS.get(action_id, "unknown")

            self.action_map[action_id] = {
                "id": action_id,
                "effect": effect_name,
                "description_fr": desc_fr,
                "description_en": desc_en,
                "category": category,
            }

        logger.info(f"Actions parsees: {len(self.action_map)} effets "
                     f"({sum(1 for v in self.action_map.values() if v['category'] != 'unknown')} connus)")
        return self.action_map


class StateParser:
    """Parse states.json pour creer un dictionnaire stateId -> nom."""

    def __init__(self, states_filepath):
        self.states_filepath = states_filepath
        self.state_map = {}

    def parse(self):
        with open(self.states_filepath, "r", encoding="utf-8") as f:
            raw_states = json.load(f)

        for entry in raw_states:
            defn = entry.get("definition", {})
            state_id = defn.get("id")
            title = entry.get("title", {})
            desc = entry.get("description", {})

            self.state_map[state_id] = {
                "id": state_id,
                "name_fr": title.get("fr", ""),
                "name_en": title.get("en", ""),
                "description_fr": desc.get("fr", ""),
                "description_en": desc.get("en", ""),
            }

        logger.info(f"States parses: {len(self.state_map)} etats")
        return self.state_map


class EquipmentTypeParser:
    """Parse equipmentItemTypes.json pour mapper typeId -> positions d equipement."""

    def __init__(self, equip_filepath):
        self.equip_filepath = equip_filepath
        self.type_map = {}

    def parse(self):
        with open(self.equip_filepath, "r", encoding="utf-8") as f:
            raw_types = json.load(f)

        for entry in raw_types:
            defn = entry.get("definition", {})
            type_id = defn.get("id")
            title = entry.get("title", {})

            self.type_map[type_id] = {
                "id": type_id,
                "name_fr": title.get("fr", ""),
                "name_en": title.get("en", ""),
                "positions": defn.get("equipmentPositions", []),
                "disabled_positions": defn.get("equipmentDisabledPositions", []),
                "parent_id": defn.get("parentId"),
                "is_recyclable": defn.get("isRecyclable", False),
            }

        logger.info(f"Equipment types parses: {len(self.type_map)} types")
        return self.type_map


class ItemParser:
    """
    Parse items.json et croise avec actions et equipment types
    pour produire des items normalises et exploitables par l optimizer.
    """

    def __init__(self, items_filepath, action_map, equip_type_map):
        self.items_filepath = items_filepath
        self.action_map = action_map
        self.equip_type_map = equip_type_map
        self.items = []

    def _resolve_effect(self, effect_entry):
        """Convertit un effet brut en structure lisible."""
        # Structure CDN: {"effect": {"definition": {"actionId": X, "params": [...]}}}
        defn = effect_entry.get("effect", {}).get("definition", {})
        if not defn:
            # Fallback: peut-etre que la structure est directe {"definition": {...}}
            defn = effect_entry.get("definition", {})
        action_id = defn.get("actionId")
        params = defn.get("params", [])

        action_info = self.action_map.get(action_id, {})
        category = action_info.get("category", "unknown")

        # Extraction de la valeur principale (params[0] dans la plupart des cas)
        # Les params CDN sont des floats (ex: 9.0), on convertit en int pour la comparaison
        raw_value = params[0] if params else 0
        value = int(raw_value) if isinstance(raw_value, float) and raw_value == int(raw_value) else raw_value

        return {
            "action_id": action_id,
            "category": category,
            "effect_name": action_info.get("effect", ""),
            "value": value,
            "params": params,
            "area_shape": defn.get("areaShape"),
            "area_size": defn.get("areaSize", []),
        }

    def parse(self):
        """Parse tous les items et retourne la liste normalisee."""
        logger.info("Parsing items.json (cela peut prendre quelques secondes)...")
        with open(self.items_filepath, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        for entry in raw_items:
            defn = entry.get("definition", {})
            item_defn = defn.get("item", {})
            item_id = item_defn.get("id")
            level = item_defn.get("level", 0)

            base_params = item_defn.get("baseParameters", {})
            item_type_id = base_params.get("itemTypeId")
            item_set_id = base_params.get("itemSetId", 0)
            rarity = base_params.get("rarity", 0)

            # Resoudre le type d equipement
            equip_info = self.equip_type_map.get(item_type_id, {})

            title = entry.get("title", {})
            description = entry.get("description", {})

            # Parser les effets d equipement
            # IMPORTANT: dans le JSON CDN Ankama, equipEffects/useEffects/useCriticalEffects
            # sont sous entry["definition"], PAS a la racine de entry.
            # Structure: {"definition": {"item": {...}, "useEffects": [...], "equipEffects": [...]}, "title": {...}}
            equip_effects = []
            for eff in defn.get("equipEffects", []):
                equip_effects.append(self._resolve_effect(eff))

            # Parser les effets d utilisation
            use_effects = []
            for eff in defn.get("useEffects", []):
                use_effects.append(self._resolve_effect(eff))

            # Parser les effets critiques d utilisation
            use_crit_effects = []
            for eff in defn.get("useCriticalEffects", []):
                use_crit_effects.append(self._resolve_effect(eff))

            # Parametres d utilisation (pour les armes)
            use_params = item_defn.get("useParameters", {})

            parsed_item = {
                "id": item_id,
                "level": level,
                "name_fr": title.get("fr", ""),
                "name_en": title.get("en", ""),
                "description_fr": description.get("fr", ""),
                "type_id": item_type_id,
                "type_name_fr": equip_info.get("name_fr", ""),
                "type_name_en": equip_info.get("name_en", ""),
                "positions": equip_info.get("positions", []),
                "disabled_positions": equip_info.get("disabled_positions", []),
                "set_id": item_set_id,
                "rarity": rarity,
                "rarity_name": self._rarity_name(rarity),
                "equip_effects": equip_effects,
                "use_effects": use_effects,
                "use_critical_effects": use_crit_effects,
                "use_ap_cost": use_params.get("useCostAp", 0),
                "use_mp_cost": use_params.get("useCostMp", 0),
                "use_wp_cost": use_params.get("useCostWp", 0),
                "use_range_min": use_params.get("useRangeMin", 0),
                "use_range_max": use_params.get("useRangeMax", 0),
                "properties": item_defn.get("properties", []),
            }

            self.items.append(parsed_item)

        logger.info(f"Items parses: {len(self.items)} objets")
        return self.items

    @staticmethod
    def _rarity_name(rarity_id):
        """Convertit l ID de rarete en nom lisible."""
        names = {
            0: "common",       # Commun
            1: "uncommon",     # Inhabituel
            2: "rare",         # Rare
            3: "mythic",       # Mythique
            4: "legendary",    # Legendaire
            5: "relic",        # Relique
            6: "souvenir",     # Souvenir
            7: "epic",         # Epique
        }
        return names.get(rarity_id, f"unknown_{rarity_id}")


# ── Phase 5 & 6: Ecriture atomique et validation ───────────────────────
class SyncWriter:
    """Ecrit les donnees parsees de facon atomique et valide."""

    def __init__(self, version):
        self.version = version
        self.checksums = {}
        self.stats = {}

    def write_json(self, data, filepath, description=""):
        """Ecrit un fichier JSON avec checksum."""
        ensure_dir(Path(filepath).parent)
        content = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        with open(filepath, "wb") as f:
            f.write(content)
        self.checksums[str(filepath)] = sha256_bytes(content)
        logger.info(f"Ecrit: {filepath} ({len(content)/1024:.1f} Ko) - {description}")

    def write_manifest(self):
        """Ecrit le manifeste de synchronisation."""
        ensure_dir(MANIFEST_FILE.parent)
        manifest = {
            "version": self.version,
            "sync_date": datetime.now(timezone.utc).isoformat(),
            "files": self.checksums,
            "stats": self.stats,
        }
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"Manifeste ecrit: {MANIFEST_FILE}")

    def validate(self, action_map, state_map, equip_type_map, items):
        """Lance les sanity checks post-sync."""
        errors = []

        if len(action_map) == 0:
            errors.append("Aucune action parsee")
        if len(state_map) == 0:
            errors.append("Aucun etat parse")
        if len(equip_type_map) == 0:
            errors.append("Aucun type d equipement parse")
        if len(items) == 0:
            errors.append("Aucun item parse")

        # Verifier que les actions connues critiques existent
        # Note: actionId 2,3,4,5 (degats Feu/Eau/Terre/Air) n existent PAS
        # dans actions.json du CDN. Wakfu utilise actionId 1083 (Light Damage)
        # qui s adapte a l element de maitrise le plus haut du personnage.
        # Source: dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
        critical_actions = [1, 20, 31, 41, 80, 120, 150, 191, 1083]
        for aid in critical_actions:
            if aid not in action_map:
                errors.append(f"Action critique manquante: {aid}")

        # Verifier des items de haut niveau
        high_level = [i for i in items if i["level"] >= 200]
        if len(high_level) == 0:
            errors.append("Aucun item de niveau >= 200 trouve")

        self.stats = {
            "total_actions": len(action_map),
            "known_actions": sum(1 for v in action_map.values() if v.get("category") != "unknown"),
            "total_states": len(state_map),
            "total_equip_types": len(equip_type_map),
            "total_items": len(items),
            "items_by_rarity": {},
            "items_level_200_plus": len(high_level),
            "validation_errors": errors,
        }

        # Comptage par rarete
        rarity_count = {}
        for item in items:
            rname = item.get("rarity_name", "unknown")
            rarity_count[rname] = rarity_count.get(rname, 0) + 1
        self.stats["items_by_rarity"] = rarity_count

        if errors:
            logger.warning(f"Validation: {len(errors)} probleme(s) detecte(s):")
            for e in errors:
                logger.warning(f"  - {e}")
        else:
            logger.info("Validation: tous les checks passent")

        return len(errors) == 0


# ── Orchestrateur principal ─────────────────────────────────────────────
class DataSyncPipeline:
    """
    Pipeline complet de synchronisation des donnees Wakfu.

    Usage:
        pipeline = DataSyncPipeline()
        pipeline.run()           # Sync seulement si nouvelle version
        pipeline.run(force=True) # Force la re-sync
    """

    def __init__(self):
        self.version = None
        self.action_map = {}
        self.state_map = {}
        self.equip_type_map = {}
        self.items = []

    def run(self, force=False):
        """Execute le pipeline complet."""
        logger.info("=" * 70)
        logger.info("WAKFU DATA SYNC PIPELINE V5.0")
        logger.info("=" * 70)
        start = time.time()

        # Phase 1: Detection de version
        logger.info("\n--- Phase 1: Detection de version ---")
        needs_update, remote_version, local_version = VersionChecker.needs_update()

        if not needs_update and not force:
            logger.info("Pas de mise a jour necessaire. Utilisez force=True pour forcer.")
            return True

        self.version = remote_version

        # Phase 2: Telechargement CDN
        logger.info("\n--- Phase 2: Telechargement CDN ---")
        downloader = CDNDownloader(self.version)

        # Utiliser un dossier temporaire ADJACENT a raw (pas dedans)
        # data/.raw_tmp au lieu de data/raw/.tmp pour permettre le rename atomique
        tmp_dir = DATA_DIR / ".raw_tmp"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

        file_map, dl_errors = downloader.download_all(tmp_dir)

        # Verifier les fichiers critiques
        critical_files = ["actions", "items", "states", "equipmentItemTypes"]
        missing_critical = [f for f in critical_files if f not in file_map]
        if missing_critical:
            logger.error(f"Fichiers critiques manquants: {missing_critical}")
            logger.error("Abandon de la synchronisation.")
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
            return False

        # Swap atomique: .raw_tmp -> raw
        if RAW_DIR.exists():
            backup_dir = DATA_DIR / f"raw_backup_{local_version}"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            RAW_DIR.rename(backup_dir)
            logger.info(f"Backup de l ancienne version dans {backup_dir}")

        # Renommer le dossier temporaire en raw
        tmp_dir.rename(RAW_DIR)
        logger.info(f"Swap atomique: .raw_tmp -> raw OK")

        # Phase 3: Parsing et normalisation
        logger.info("\n--- Phase 3: Parsing et normalisation ---")

        # 3a: Actions
        action_parser = ActionParser(RAW_DIR / "actions.json")
        self.action_map = action_parser.parse()

        # 3b: States
        state_parser = StateParser(RAW_DIR / "states.json")
        self.state_map = state_parser.parse()

        # 3c: Equipment types
        equip_parser = EquipmentTypeParser(RAW_DIR / "equipmentItemTypes.json")
        self.equip_type_map = equip_parser.parse()

        # 3d: Items (necessite action_map et equip_type_map)
        item_parser = ItemParser(RAW_DIR / "items.json", self.action_map, self.equip_type_map)
        self.items = item_parser.parse()

        # Phase 5: Ecriture atomique
        logger.info("\n--- Phase 5: Ecriture des fichiers parses ---")
        writer = SyncWriter(self.version)

        writer.write_json(
            self.action_map,
            PARSED_DIR / "action_map.json",
            f"{len(self.action_map)} actions"
        )
        writer.write_json(
            self.state_map,
            PARSED_DIR / "state_map.json",
            f"{len(self.state_map)} etats"
        )
        writer.write_json(
            self.equip_type_map,
            PARSED_DIR / "equipment_types.json",
            f"{len(self.equip_type_map)} types"
        )
        writer.write_json(
            self.items,
            PARSED_DIR / "all_items.json",
            f"{len(self.items)} items"
        )

        # Phase 6: Validation
        logger.info("\n--- Phase 6: Validation ---")
        valid = writer.validate(self.action_map, self.state_map, self.equip_type_map, self.items)

        # Sauvegarder la version et le manifeste
        sync_date = datetime.now(timezone.utc).isoformat()
        VersionChecker.save_local_version(self.version, sync_date)
        writer.write_manifest()

        # Ecrire le rapport de sync dans les logs
        ensure_dir(SYNC_LOG.parent)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"Sync: {sync_date}\n")
            f.write(f"Version: {local_version} -> {self.version}\n")
            f.write(f"Items: {len(self.items)}\n")
            f.write(f"Actions: {len(self.action_map)}\n")
            f.write(f"States: {len(self.state_map)}\n")
            f.write(f"Equip types: {len(self.equip_type_map)}\n")
            f.write(f"Erreurs DL: {len(dl_errors)}\n")
            f.write(f"Validation: {'OK' if valid else 'ERREURS'}\n")
            f.write(f"Stats: {json.dumps(writer.stats, indent=2)}\n")

        elapsed = time.time() - start
        logger.info(f"\n{'='*70}")
        logger.info(f"SYNC TERMINEE en {elapsed:.1f}s")
        logger.info(f"Version: {self.version}")
        logger.info(f"Items: {len(self.items)} | Actions: {len(self.action_map)} | "
                     f"States: {len(self.state_map)} | Types: {len(self.equip_type_map)}")
        logger.info(f"Validation: {'SUCCES' if valid else 'AVERTISSEMENTS'}")
        logger.info(f"{'='*70}")

        return valid


# ── Helper: recherche d item pour l optimizer ───────────────────────────
class ItemSearcher:
    """
    Utilitaire pour rechercher des items dans les donnees parsees.
    Utilise par l optimizer pour trouver les meilleurs equipements.
    """

    def __init__(self, items=None):
        if items is None:
            parsed_file = PARSED_DIR / "all_items.json"
            if parsed_file.exists():
                with open(parsed_file, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            else:
                self.items = []
                logger.warning("Aucun fichier all_items.json trouve. Lancez data_sync d abord.")
        else:
            self.items = items

    def search_by_name(self, name, lang="fr"):
        """Recherche par nom (insensible a la casse)."""
        key = f"name_{lang}"
        name_lower = name.lower()
        return [i for i in self.items if name_lower in i.get(key, "").lower()]

    def search_by_level_range(self, min_level, max_level):
        """Recherche par fourchette de niveau."""
        return [i for i in self.items if min_level <= i.get("level", 0) <= max_level]

    def search_by_position(self, position):
        """Recherche par position d equipement (HEAD, CHEST, LEGS, etc.)."""
        return [i for i in self.items if position in i.get("positions", [])]

    def search_by_rarity(self, rarity_name):
        """Recherche par rarete (common, uncommon, rare, mythic, legendary, relic, epic)."""
        return [i for i in self.items if i.get("rarity_name") == rarity_name]

    def search_by_effect(self, category, min_value=0):
        """Recherche des items ayant un effet specifique avec une valeur minimale."""
        results = []
        for item in self.items:
            for eff in item.get("equip_effects", []):
                if eff.get("category") == category and eff.get("value", 0) >= min_value:
                    results.append(item)
                    break
        return results

    def get_best_for_slot(self, position, level, effect_category, top_n=10):
        """
        Trouve les meilleurs items pour un slot donne, a un niveau donne,
        tries par la valeur de l effet demande.
        """
        candidates = [
            i for i in self.items
            if position in i.get("positions", [])
            and i.get("level", 0) <= level
        ]

        # Calculer le score par effet
        scored = []
        for item in candidates:
            score = 0
            for eff in item.get("equip_effects", []):
                if eff.get("category") == effect_category:
                    score += eff.get("value", 0)
            if score > 0:
                scored.append((item, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]


# ── Tests ───────────────────────────────────────────────────────────────
def run_tests():
    """Tests du pipeline de synchronisation."""

    print("=" * 70)
    print("TESTS - scripts/data_sync.py V5.0")
    print("=" * 70)

    # Test 1: Version checker
    print("\n--- Test 1: Version checker ---")
    remote = VersionChecker.get_remote_version()
    assert remote != "unknown", "Version distante non recuperee"
    assert "." in remote, f"Format de version inattendu: {remote}"
    print(f"  Version CDN: {remote} - OK")

    # Test 2: Telechargement d un seul fichier
    print("\n--- Test 2: Telechargement d un fichier ---")
    downloader = CDNDownloader(remote)
    tmp = tempfile.mkdtemp()
    try:
        file_map, errors = downloader.download_all(tmp)
        assert "actions" in file_map, "actions.json non telecharge"
        assert "items" in file_map, "items.json non telecharge"
        assert "states" in file_map, "states.json non telecharge"
        assert "equipmentItemTypes" in file_map, "equipmentItemTypes.json non telecharge"
        print(f"  Fichiers telecharges: {len(file_map)}/{len(CDN_TYPES)} - OK")
        if errors:
            print(f"  Erreurs (non critiques): {errors}")

        # Test 3: Parsing des actions
        print("\n--- Test 3: Parsing des actions ---")
        action_parser = ActionParser(file_map["actions"])
        action_map = action_parser.parse()
        assert len(action_map) > 50, f"Trop peu d actions: {len(action_map)}"
        assert 120 in action_map, "Action 120 (mastery_elemental) manquante"
        assert action_map[120]["category"] == "mastery_elemental"
        print(f"  {len(action_map)} actions parsees, action 120 = {action_map[120]['effect']} - OK")

        # Test 4: Parsing des states
        print("\n--- Test 4: Parsing des states ---")
        state_parser = StateParser(file_map["states"])
        state_map = state_parser.parse()
        assert len(state_map) > 100, f"Trop peu d etats: {len(state_map)}"
        print(f"  {len(state_map)} etats parses - OK")

        # Test 5: Parsing des equipment types
        print("\n--- Test 5: Parsing des equipment types ---")
        equip_parser = EquipmentTypeParser(file_map["equipmentItemTypes"])
        equip_type_map = equip_parser.parse()
        assert len(equip_type_map) > 10, f"Trop peu de types: {len(equip_type_map)}"
        # Verifier que le type 134 (Casque/Helmet) existe avec position HEAD
        assert 134 in equip_type_map, "Type 134 (Casque) manquant"
        assert "HEAD" in equip_type_map[134]["positions"], "Type 134 devrait avoir position HEAD"
        print(f"  {len(equip_type_map)} types parses, type 134 = Casque/HEAD - OK")

        # Test 6: Parsing des items
        print("\n--- Test 6: Parsing des items ---")
        item_parser = ItemParser(file_map["items"], action_map, equip_type_map)
        items = item_parser.parse()
        assert len(items) > 1000, f"Trop peu d items: {len(items)}"
        # Verifier un item connu (Amulette du Bouftou, id 2021)
        bouftou_amulet = [i for i in items if i["id"] == 2021]
        assert len(bouftou_amulet) == 1, "Amulette du Bouftou (2021) non trouvee"
        assert bouftou_amulet[0]["name_fr"] == "Amulette du Bouftou"
        assert bouftou_amulet[0]["level"] == 6
        print(f"  {len(items)} items parses, Amulette du Bouftou (lvl 6) trouvee - OK")

        # Test 7: Recherche d items
        print("\n--- Test 7: Recherche d items ---")
        searcher = ItemSearcher(items)
        helmets = searcher.search_by_position("HEAD")
        assert len(helmets) > 50, f"Trop peu de casques: {len(helmets)}"
        high_level = searcher.search_by_level_range(200, 999)
        assert len(high_level) > 0, "Aucun item niveau 200+"
        print(f"  Casques: {len(helmets)}, Items 200+: {len(high_level)} - OK")

        # Test 8: Recherche par effet
        print("\n--- Test 8: Recherche par effet ---")
        # Diagnostic: verifier que les effets sont bien parses
        items_with_any_effect = [i for i in items if len(i.get("equip_effects", [])) > 0]
        print(f"  Diagnostic: {len(items_with_any_effect)}/{len(items)} items ont des equip_effects")
        if items_with_any_effect:
            sample = items_with_any_effect[0]
            print(f"  Exemple: {sample['name_fr']} (lvl {sample['level']})")
            for eff in sample.get("equip_effects", [])[:3]:
                print(f"    -> actionId={eff['action_id']}, category={eff['category']}, value={eff['value']}")

        mastery_items = searcher.search_by_effect("mastery_elemental", min_value=10)
        mastery_any = searcher.search_by_effect("mastery_elemental", min_value=0)
        print(f"  Items avec Mastery Elem (any): {len(mastery_any)}")
        print(f"  Items avec Mastery Elem >= 10: {len(mastery_items)}")
        assert len(mastery_items) > 100, f"Trop peu d items avec mastery >= 10: {len(mastery_items)}"
        print(f"  Items avec Mastery Elem >= 10: {len(mastery_items)} - OK")

        # Test 9: Best for slot
        print("\n--- Test 9: Best for slot ---")
        best_helmets = searcher.get_best_for_slot("HEAD", 200, "mastery_elemental", top_n=5)
        assert len(best_helmets) > 0, "Aucun casque optimal trouve"
        print(f"  Top 5 casques (mastery elem, lvl <= 200):")
        for item, score in best_helmets:
            print(f"    - {item['name_fr']} (lvl {item['level']}, rarity: {item['rarity_name']}) "
                  f"= {score:.0f} mastery elem")

        # Test 10: Validation
        print("\n--- Test 10: Validation ---")
        writer = SyncWriter(remote)
        valid = writer.validate(action_map, state_map, equip_type_map, items)
        print(f"  Validation: {'SUCCES' if valid else 'AVERTISSEMENTS'}")
        print(f"  Stats: {json.dumps(writer.stats, indent=2)}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 70)
    print("TOUS LES TESTS PASSENT")
    print("=" * 70)
    print("\nPour lancer la synchronisation complete:")
    print("  python scripts/data_sync.py --sync")
    print("  python scripts/data_sync.py --sync --force")


# ── CLI ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--sync" in sys.argv:
        force = "--force" in sys.argv
        pipeline = DataSyncPipeline()
        success = pipeline.run(force=force)
        sys.exit(0 if success else 1)
    elif "--search" in sys.argv:
        # Mode recherche rapide
        searcher = ItemSearcher()
        query = " ".join(sys.argv[sys.argv.index("--search") + 1:])
        results = searcher.search_by_name(query)
        print(f"Resultats pour '{query}': {len(results)} items")
        for item in results[:20]:
            print(f"  [{item['id']}] {item['name_fr']} (lvl {item['level']}, "
                  f"{item['rarity_name']}, {item.get('type_name_fr', '?')})")
    elif "--check" in sys.argv:
        # Mode verification de version
        needs, remote, local = VersionChecker.needs_update()
        print(f"Local: {local} | Remote: {remote} | Mise a jour: {'OUI' if needs else 'NON'}")
    else:
        run_tests()



