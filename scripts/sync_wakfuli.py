import json, time, logging
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"
LOGS = PROJECT / "logs"
DATA.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

API_BASE = "https://api.wakfuli.com/api/v1"
CDN_CONFIG = "https://wakfu.cdn.ankama.com/gamedata/config.json"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOGS / f"sync_wakfuli_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("sync")


def get_version():
    try:
        r = requests.get(CDN_CONFIG, timeout=15)
        r.raise_for_status()
        v = r.json().get("version", "inconnue")
        log.info(f"Version : {v}")
        return v
    except Exception as e:
        log.warning(f"Version error : {e}")
        return "inconnue"


def sync_paged(name, endpoint, limit=100):
    log.info(f"--- {name} ---")
    result = []
    page = 1
    while True:
        url = f"{API_BASE}/{endpoint}?page={page}&limit={limit}"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            log.error(f"{name} p{page}: {e}")
            break
        meta = d.get("meta", {})
        rows = d.get("data", [])
        result.extend(rows)
        lp = meta.get("lastPage", page)
        log.info(f"  p{page}/{lp}: +{len(rows)} = {len(result)}")
        if page >= lp:
            break
        page += 1
        time.sleep(0.3)
    return result


def sync_builds():
    log.info("--- BUILDS ---")
    builds = []
    sp_a = set()
    sp_p = set()
    cls = set()
    page = 1
    while True:
        url = f"{API_BASE}/builds?page={page}&limit=50"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            log.error(f"Builds p{page}: {e}")
            break
        meta = d.get("meta", {})
        rows = d.get("data", [])
        for b in rows:
            builds.append(b)
            cc = b.get("characterClass", "")
            if cc:
                cls.add(cc.lower())
            sp = b.get("spells")
            if isinstance(sp, dict):
                for s in sp.get("activeSpells", []):
                    if s is not None:
                        sp_a.add(s)
                for s in sp.get("passiveSpells", []):
                    if s is not None:
                        sp_p.add(s)
        lp = meta.get("lastPage", page)
        log.info(f"  Builds p{page}/{lp}: +{len(rows)} = {len(builds)}")
        if page >= lp:
            break
        page += 1
        time.sleep(0.3)
    idx = {
        "active_spell_ids": sorted(sp_a),
        "passive_spell_ids": sorted(sp_p),
        "total_active": len(sp_a),
        "total_passive": len(sp_p),
        "total_unique": len(sp_a | sp_p),
        "classes_found": sorted(cls),
    }
    return builds, idx


def save(data, name):
    p = DATA / name
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    mb = p.stat().st_size / (1024 * 1024)
    log.info(f"  -> {name} ({mb:.2f} MB, {len(data)} entrees)")


def main():
    log.info("=" * 50)
    log.info("SYNC WAKFULI")
    log.info("=" * 50)
    t0 = time.time()

    ver = get_version()
    ver_data = {"version": ver, "date": datetime.now().isoformat()}
    (DATA / "version.json").write_text(
        json.dumps(ver_data, indent=2), "utf-8"
    )

    items = sync_paged("ITEMS", "items", 100)
    save(items, "all_items.json")

    actions = sync_paged("ACTIONS", "actions", 100)
    save(actions, "all_actions.json")

    builds, idx = sync_builds()
    save(builds, "all_builds.json")
    (DATA / "spell_index_from_builds.json").write_text(
        json.dumps(idx, ensure_ascii=False, indent=2), "utf-8"
    )

    dt = time.time() - t0
    rpt = {
        "version": ver,
        "date": datetime.now().isoformat(),
        "duration_seconds": round(dt, 1),
        "items_received": len(items),
        "actions_received": len(actions),
        "builds_received": len(builds),
        "unique_spells": idx["total_unique"],
        "classes_covered": idx["classes_found"],
    }
    (DATA / "sync_report.json").write_text(
        json.dumps(rpt, ensure_ascii=False, indent=2), "utf-8"
    )

    log.info("=" * 50)
    log.info("SYNCHRONISATION TERMINEE")
    log.info(f"  Duree   : {dt:.1f}s")
    log.info(f"  Version : {ver}")
    log.info(f"  Items   : {len(items)}")
    log.info(f"  Actions : {len(actions)}")
    log.info(f"  Builds  : {len(builds)}")
    log.info(f"  Sorts   : {idx['total_unique']} uniques")
    log.info(f"  Classes : {len(idx['classes_found'])}")
    log.info(f"  Log     : {log_file}")
    log.info("=" * 50)


if __name__ == "__main__":
    main()