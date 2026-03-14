#!/usr/bin/env python3
"""
Wakfu BData Reader v5.2 - VERIFIED WORKING
===========================================
Sources:
  https://github.com/WakBox/WakfuBDataReader (BinaryReader.h, Spell.h, AvatarBreed.h)

Key findings:
  1. data_start = fileSize - (lastRow.offset + lastRow.size)
  2. Per row: hoo = seed, CalcHoo with positions relative to data buffer
  3. Floats NOT XOR-decoded (ReadFloat: CalcHoo but no subtraction)
  4. Strings: length via ReadInt (XOR), bytes read raw
  5. Spell has 7 booleans before targetFilter (WakBox had 6 - format updated)

Date: 2026-03-13
"""
import struct, zipfile, os, json, logging, urllib.request
from datetime import datetime
from ctypes import c_int8, c_int16, c_int32, c_int64

WAKFU_DIR = r"H:\Games\Wakfu\contents"
BDATA_DIR = os.path.join(WAKFU_DIR, "bdata")
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\logs"
CDN_BASE = "https://wakfu.cdn.ankama.com/gamedata"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "bdata_v5.log"), encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("v5")

FILE_SIZE_MAGIC = 756423

# ============================================================
# BinaryReader - per-row instance
# ============================================================
class RowReader:
    def __init__(self, buf, offset, seed, file_id, m_size):
        self.buf = buf
        self.pos = offset
        self.hoo = c_int8(seed).value
        self.fid = file_id
        self.msz = m_size

    def _ch(self):
        add = c_int8(self.fid * self.pos + self.msz).value
        self.hoo = c_int8(self.hoo + add).value

    def read_int(self):
        self._ch()
        raw = struct.unpack_from('<i', self.buf, self.pos)[0]
        self.pos += 4
        return c_int32(raw - self.hoo).value

    def read_short(self):
        self._ch()
        raw = struct.unpack_from('<h', self.buf, self.pos)[0]
        self.pos += 2
        return c_int16(raw - self.hoo).value

    def read_byte(self):
        self._ch()
        raw = struct.unpack_from('<b', self.buf, self.pos)[0]
        self.pos += 1
        return c_int8(raw - self.hoo).value

    def read_bool(self):
        self._ch()
        raw = struct.unpack_from('<B', self.buf, self.pos)[0]
        self.pos += 1
        return bool((raw - self.hoo) & 0xFF)

    def read_long(self):
        self._ch()
        raw = struct.unpack_from('<q', self.buf, self.pos)[0]
        self.pos += 8
        return c_int64(raw - self.hoo).value

    def read_float(self):
        self._ch()
        raw = struct.unpack_from('<f', self.buf, self.pos)[0]
        self.pos += 4
        return raw

    def read_string(self):
        length = self.read_int()
        if length < 0 or length > 500000:
            raise ValueError(f"str_len={length}")
        if length == 0:
            return ""
        if self.pos + length > len(self.buf):
            raise BufferError(f"str overrun: need {length} at {self.pos}")
        raw = self.buf[self.pos:self.pos + length]
        self.pos += length
        return bytes(raw).decode('utf-8', errors='replace')

    def read_int_array(self):
        sz = self.read_int()
        if sz < 0 or sz > 100000:
            raise ValueError(f"iarr_sz={sz}")
        return [self.read_int() for _ in range(sz)]

    def read_float_array(self):
        sz = self.read_int()
        if sz < 0 or sz > 100000:
            raise ValueError(f"farr_sz={sz}")
        return [self.read_float() for _ in range(sz)]

    def read_byte_array(self):
        sz = self.read_int()
        if sz < 0 or sz > 100000:
            raise ValueError(f"barr_sz={sz}")
        return [self.read_byte() for _ in range(sz)]


# ============================================================
# Header parser (uses accumulated hoo)
# ============================================================
class HeaderReader:
    def __init__(self, data, file_id):
        self.data = data
        self.fid = file_id
        self.pos = 0
        raw_first = struct.unpack_from('<i', data, 0)[0]
        self.pos = 4
        self.msz = raw_first + FILE_SIZE_MAGIC
        self.hoo = c_int8(file_id ^ self.msz).value

    def _ch(self):
        add = c_int8(self.fid * self.pos + self.msz).value
        self.hoo = c_int8(self.hoo + add).value

    def read_int(self):
        self._ch()
        raw = struct.unpack_from('<i', self.data, self.pos)[0]
        self.pos += 4
        return c_int32(raw - self.hoo).value

    def read_long(self):
        self._ch()
        raw = struct.unpack_from('<q', self.data, self.pos)[0]
        self.pos += 8
        return c_int64(raw - self.hoo).value

    def read_byte(self):
        self._ch()
        raw = struct.unpack_from('<b', self.data, self.pos)[0]
        self.pos += 1
        return c_int8(raw - self.hoo).value

    def parse_rows(self):
        rows_count = self.read_int()
        if rows_count < 0 or rows_count > 500000:
            raise ValueError(f"rowsCount={rows_count}")
        rows = []
        for _ in range(rows_count):
            rid = self.read_long()
            roff = self.read_int()
            rsz = self.read_int()
            rseed = self.read_byte()
            rows.append(dict(id=rid, offset=roff, size=rsz, seed=rseed))
        return rows


# ============================================================
# Compute data_start
# ============================================================
def get_data_buffer(raw_data, rows):
    last = rows[-1]
    last_end = last['offset'] + last['size']
    data_start = len(raw_data) - last_end
    return raw_data[data_start:], data_start


# ============================================================
# AvatarBreed reader (exact WakBox)
# ============================================================
def read_breed(r):
    return dict(
        m_id=r.read_int(),
        m_name=r.read_string(),
        m_backgroundAps=r.read_int(),
        m_baseHp=r.read_int(),
        m_baseAp=r.read_int(),
        m_baseMp=r.read_int(),
        m_baseWp=r.read_int(),
        m_baseInit=r.read_int(),
        m_baseFerocity=r.read_int(),
        m_baseFumble=r.read_int(),
        m_baseWisdom=r.read_int(),
        m_baseTackle=r.read_int(),
        m_baseDodge=r.read_int(),
        m_baseProspection=r.read_int(),
        m_timerCountBeforeDeath=r.read_int(),
        m_preferedArea=r.read_int(),
        m_spellElements=r.read_byte_array(),
        m_characRatios=r.read_float_array(),
    )


# ============================================================
# Spell reader (WakBox + extra bool fix)
# ============================================================
def read_spell(r):
    obj = dict(
        m_id=r.read_int(),
        m_scriptId=r.read_int(),
        m_gfxId=r.read_int(),
        m_maxLevel=r.read_short(),
        m_breedId=r.read_short(),
        m_castMaxPerTarget=r.read_short(),
        m_castMaxPerTurn=r.read_float(),
        m_castMaxPerTurnIncr=r.read_float(),
        m_castMinInterval=r.read_short(),
        m_testLineOfSight=r.read_bool(),
        m_castOnlyLine=r.read_bool(),
        m_castOnlyInDiag=r.read_bool(),
        m_testFreeCell=r.read_bool(),
        m_testNotBorderCell=r.read_bool(),
        m_testDirectPath=r.read_bool(),
        m_extraBool=r.read_bool(),  # NEW: added since WakBox
        m_targetFilter=r.read_int(),
        m_castCriterion=r.read_string(),
        m_PA_base=r.read_float(),
        m_PA_inc=r.read_float(),
        m_PM_base=r.read_float(),
        m_PM_inc=r.read_float(),
        m_PW_base=r.read_float(),
        m_PW_inc=r.read_float(),
        m_rangeMaxBase=r.read_float(),
        m_rangeMaxInc=r.read_float(),
        m_rangeMinBase=r.read_float(),
        m_rangeMinLevelIncrement=r.read_float(),
        m_maxEffectCap=r.read_short(),
        m_element=r.read_short(),
        m_xpGainPercentage=r.read_short(),
        m_spellType=r.read_short(),
        m_uiPosition=r.read_short(),
        m_learnCriteria=r.read_string(),
        m_passive=r.read_byte(),
        m_useAutomaticDescription=r.read_bool(),
        m_showInTimeline=r.read_bool(),
        m_canCastWhenCarrying=r.read_bool(),
        m_actionOnCriticalMiss=r.read_byte(),
        m_spellCastRangeIsDynamic=r.read_bool(),
        m_castSpellWillBreakInvisibility=r.read_bool(),
        m_castOnRandomCell=r.read_bool(),
        m_tunnelable=r.read_bool(),
        m_canCastOnCasterCell=r.read_bool(),
        m_associatedWithItemUse=r.read_bool(),
    )
    obj['m_properties'] = r.read_int_array()
    obj['m_effectIds'] = r.read_int_array()

    bcp_count = r.read_int()
    if bcp_count < 0 or bcp_count > 1000:
        raise ValueError(f"bcp={bcp_count}")
    bcp = {}
    for _ in range(bcp_count):
        k = r.read_byte()
        b = r.read_int()
        inc = r.read_float()
        bcp[str(k)] = dict(base=b, increment=inc)
    obj['m_baseCastParameters'] = bcp

    alt_count = r.read_int()
    if alt_count < 0 or alt_count > 1000:
        raise ValueError(f"alt={alt_count}")
    alts = {}
    for _ in range(alt_count):
        akey = r.read_string()
        cc = r.read_int()
        if cc < 0 or cc > 1000:
            raise ValueError(f"cc={cc}")
        costs = {}
        for _ in range(cc):
            ck = r.read_byte()
            cb = r.read_int()
            ci = r.read_float()
            costs[str(ck)] = dict(base=cb, increment=ci)
        cp = dict(
            m_costs=costs, m_cost=r.read_int(),
            m_PA_base=r.read_float(), m_PA_inc=r.read_float(),
            m_PM_base=r.read_float(), m_PM_inc=r.read_float(),
            m_PW_base=r.read_float(), m_PW_inc=r.read_float(),
            m_rangeMinBase=r.read_float(), m_rangeMinInc=r.read_float(),
            m_rangeMaxBase=r.read_float(), m_rangeMaxInc=r.read_float(),
            m_isLosAware=r.read_bool(), m_onlyInLine=r.read_bool(),
            m_rangeIsDynamic=r.read_bool(),
        )
        alts[akey] = cp
    obj['m_alternativeCasts'] = alts
    return obj


# ============================================================
# EffectGroup reader
# ============================================================
def read_effect_group(r):
    return dict(m_id=r.read_int(), m_effectIds=r.read_int_array())


# ============================================================
# Load JARs
# ============================================================
def load_jars(bdata_dir):
    loaded = {}
    for fname in os.listdir(bdata_dir):
        if not fname.endswith('.jar'):
            continue
        try:
            fid = int(fname.replace('.jar', ''))
        except ValueError:
            continue
        path = os.path.join(bdata_dir, fname)
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                bin_name = f"{fid}.bin"
                if bin_name in zf.namelist():
                    loaded[fid] = zf.read(bin_name)
        except Exception as e:
            log.warning(f"Failed {fname}: {e}")
    return loaded


# ============================================================
# Process file
# ============================================================
def process_file(raw_data, file_id, reader_func, label):
    hdr = HeaderReader(raw_data, file_id)
    rows = hdr.parse_rows()
    buf, ds = get_data_buffer(raw_data, rows)

    log.info(f"  {label}: {len(rows)} rows, data_start={ds}, buf={len(buf)} bytes")

    results = []
    errors = []
    for idx, row in enumerate(rows):
        r = RowReader(buf, row['offset'], row['seed'], file_id, hdr.msz)
        try:
            obj = reader_func(r)
            consumed = r.pos - row['offset']
            obj['_consumed'] = consumed
            obj['_size'] = row['size']
            results.append(obj)
        except Exception as e:
            errors.append(dict(idx=idx, id=row['id'], error=str(e)))
            if idx < 5:
                log.warning(f"  Row {idx} (id={row['id']}): {e}")

    log.info(f"  {label}: {len(results)}/{len(rows)} OK, {len(errors)} errors")
    return results, errors, len(rows)


# ============================================================
# CDN
# ============================================================
def get_version():
    try:
        req = urllib.request.Request(f"{CDN_BASE}/config.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())['version']
    except:
        return None

def cdn_fetch(ver, name):
    try:
        req = urllib.request.Request(f"{CDN_BASE}/{ver}/{name}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except:
        return None


# ============================================================
# MAIN
# ============================================================
def main():
    log.info("=" * 70)
    log.info("Wakfu BData Reader v5.2 - VERIFIED")
    log.info(f"Date: {datetime.now().isoformat()}")
    log.info("=" * 70)

    ver = get_version()
    log.info(f"Game version: {ver}")

    cdn_data = {}
    if ver:
        for name in ["actions.json", "states.json"]:
            d = cdn_fetch(ver, name)
            if d:
                cdn_data[name] = d
                p = os.path.join(OUTPUT_DIR, f"cdn_{name}")
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump(d, f, indent=2, ensure_ascii=False)
                log.info(f"  CDN {name}: {len(d)} entries")

    jars = load_jars(BDATA_DIR)
    log.info(f"Loaded {len(jars)} JAR files")

    targets = [
        (86, "AvatarBreed", read_breed),
        (66, "Spell", read_spell),
        (29, "EffectGroup", read_effect_group),
    ]

    all_res = {}
    sram_breed_id = None

    for fid, name, func in targets:
        if fid not in jars:
            log.warning(f"{fid}.jar not found!")
            continue
        log.info(f"\n=== {name} ({fid}.bin) ===")
        results, errors, total = process_file(jars[fid], fid, func, name)
        all_res[name] = dict(results=results, errors=errors, total=total)

    # ---- BREEDS ----
    if 'AvatarBreed' in all_res:
        log.info(f"\n{'='*50}")
        log.info("BREEDS")
        log.info(f"{'='*50}")
        for b in all_res['AvatarBreed']['results']:
            n = b['m_name']
            log.info(f"  {b['m_id']:3d} {n:15s} HP={b['m_baseHp']} AP={b['m_baseAp']} MP={b['m_baseMp']} WP={b['m_baseWp']}")
            if n.upper() == 'SRAM':
                sram_breed_id = b['m_id']

    # ---- SPELLS ----
    if 'Spell' in all_res:
        spells = all_res['Spell']['results']
        total = all_res['Spell']['total']
        errs = all_res['Spell']['errors']
        log.info(f"\n{'='*50}")
        log.info(f"SPELLS: {len(spells)}/{total} OK, {len(errs)} errors ({len(spells)/max(total,1)*100:.1f}%)")
        log.info(f"{'='*50}")

        breeds = {}
        for sp in spells:
            bid = sp['m_breedId']
            breeds[bid] = breeds.get(bid, 0) + 1
        for bid in sorted(breeds):
            log.info(f"  breedId={bid:3d}: {breeds[bid]} spells")

        if sram_breed_id is not None:
            sram = [s for s in spells if s['m_breedId'] == sram_breed_id]
            log.info(f"\n  SRAM (breedId={sram_breed_id}): {len(sram)} spells")
            for sp in sram[:15]:
                eff = len(sp.get('m_effectIds') or [])
                log.info(f"    id={sp['m_id']:6d} PA={sp['m_PA_base']:.0f} el={sp['m_element']:3d} effects={eff} criterion={sp['m_castCriterion'][:50]}")

        log.info(f"\n  First 3 spells:")
        for sp in spells[:3]:
            log.info(f"    --- Spell {sp['m_id']} ---")
            for k, v in sp.items():
                if not k.startswith('_'):
                    log.info(f"      {k} = {str(v)[:100]}")

    # ---- SAVING ----
    log.info(f"\n=== SAVING ===")

    def save(name, data):
        p = os.path.join(OUTPUT_DIR, name)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info(f"  {p}")

    if 'AvatarBreed' in all_res:
        save("breeds.json", all_res['AvatarBreed']['results'])

    if 'Spell' in all_res:
        save("all_spells.json", all_res['Spell']['results'])
        if sram_breed_id is not None:
            sram_data = dict(
                breed_id=sram_breed_id,
                spells=[s for s in all_res['Spell']['results'] if s['m_breedId'] == sram_breed_id]
            )
            save("sram_complete.json", sram_data)

    if 'EffectGroup' in all_res:
        save("all_effect_groups.json", all_res['EffectGroup']['results'])

    summary = dict(version='5.2', date=datetime.now().isoformat(), game_version=ver)
    summary['results'] = {}
    for name, d in all_res.items():
        t = d['total']
        o = len(d['results'])
        summary['results'][name] = dict(total=t, ok=o, errors=len(d['errors']), rate=round(o/max(t,1)*100, 1))
    save("diag_v5_results.json", summary)

    # ---- VALIDATION ----
    log.info(f"\n=== VALIDATION ===")
    tests = []
    bc = len(all_res.get('AvatarBreed', {}).get('results', []))
    tests.append(("Breeds loaded (>=15)", bc >= 15))
    tests.append(("Sram breed found", sram_breed_id is not None))

    hp_ok = False
    if 'AvatarBreed' in all_res:
        hps = [b['m_baseHp'] for b in all_res['AvatarBreed']['results']]
        hp_ok = all(0 < h < 500 for h in hps)
    tests.append(("Breed HP sane", hp_ok))

    sr = 0
    if 'Spell' in all_res:
        sr = len(all_res['Spell']['results']) / max(all_res['Spell']['total'], 1) * 100
    tests.append((f"Spell rate >90% ({sr:.1f}%)", sr > 90))

    sc = 0
    if sram_breed_id and 'Spell' in all_res:
        sc = len([s for s in all_res['Spell']['results'] if s['m_breedId'] == sram_breed_id])
    tests.append((f"Sram spells >20 ({sc})", sc > 20))

    pa_ok = False
    if 'Spell' in all_res and all_res['Spell']['results']:
        pas = [s['m_PA_base'] for s in all_res['Spell']['results'][:200]]
        pa_ok = sum(1 for p in pas if 0 <= p <= 30) > len(pas) * 0.7
    tests.append(("PA values sane", pa_ok))

    eg = len(all_res.get('EffectGroup', {}).get('results', []))
    tests.append((f"EffectGroups ({eg})", eg > 100))

    se = len(all_res.get('Spell', {}).get('errors', []))
    tests.append((f"Spell errors <200 ({se})", se < 200))

    passed = 0
    for desc, ok in tests:
        s = "PASS" if ok else "FAIL"
        m = "" if ok else " <<<<<"
        log.info(f"  [{s}] {desc}{m}")
        if ok: passed += 1

    log.info(f"\n  Overall: {passed}/{len(tests)}")
    log.info(f"\n{'='*70}")
    log.info("DONE")

if __name__ == "__main__":
    main()