"""
Wakfu StaticEffects Parser - file 68
Uses EXACT same pattern as bdata_reader_final.py:
  - ONE BinaryReader on the FULL buffer
  - set_pos(absolute_offset) + set_hoo(seed) per row
"""
import struct
import zipfile
import json
import os
import logging
from datetime import datetime
from collections import Counter

BDATA_DIR  = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE   = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\parse_static_effects.log"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ============================================================
# BINARY READER - exact copy from bdata_reader_final.py
# ============================================================
class BinaryReader:
    def __init__(self, data, file_id, file_size=0):
        self.data = data
        self.cRc = file_id
        self.pos = 0
        if file_size == 0:
            self.cRb = struct.unpack_from('<i', data, 0)[0] + 756423
            self.pos = 4
        else:
            self.cRb = file_size
        self.cRa = self._b(self.cRc ^ self.cRb)

    @staticmethod
    def _b(v):
        v = v & 0xFF
        return v - 256 if v >= 128 else v

    def set_pos(self, p): self.pos = p
    def set_hoo(self, s): self.cRa = self._b(s)
    def get_pos(self): return self.pos

    def _hoo(self):
        self.cRa = self._b(self.cRa + (self.cRc * self.pos + self.cRb))

    def ri(self):
        self._hoo()
        v = struct.unpack_from('<i', self.data, self.pos)[0]; self.pos += 4
        r = (v - self.cRa) & 0xFFFFFFFF
        return r - 0x100000000 if r >= 0x80000000 else r

    def rs(self):
        self._hoo()
        v = struct.unpack_from('<h', self.data, self.pos)[0]; self.pos += 2
        r = (v - self.cRa) & 0xFFFF
        return r - 0x10000 if r >= 0x8000 else r

    def rb(self):
        self._hoo()
        v = struct.unpack_from('<b', self.data, self.pos)[0]; self.pos += 1
        return self._b(v - self.cRa)

    def rbool(self):
        self._hoo()
        v = self.data[self.pos]; self.pos += 1
        return ((v - self.cRa) & 0xFF) != 0

    def rf(self):
        self._hoo()
        v = struct.unpack_from('<f', self.data, self.pos)[0]; self.pos += 4
        return v

    def rl(self):
        self._hoo()
        v = struct.unpack_from('<q', self.data, self.pos)[0]; self.pos += 8
        return v - self.cRa

    def rstr(self):
        n = self.ri()
        if n < 0 or n > 1_000_000: raise ValueError(f"Bad str len={n} @{self.pos}")
        if n == 0: return ""
        s = self.data[self.pos:self.pos+n]; self.pos += n
        return s.decode('utf-8', errors='replace')

    def ria(self):
        n = self.ri()
        if n < 0 or n > 1_000_000: raise ValueError(f"Bad IA size={n} @{self.pos}")
        return [self.ri() for _ in range(n)]

    def rfa(self):
        n = self.ri()
        if n < 0 or n > 1_000_000: raise ValueError(f"Bad FA size={n} @{self.pos}")
        return [self.rf() for _ in range(n)]

    def rla(self):
        n = self.ri()
        if n < 0 or n > 1_000_000: raise ValueError(f"Bad LA size={n} @{self.pos}")
        return [self.rl() for _ in range(n)]

    def rsa(self):
        n = self.ri()
        if n < 0 or n > 1_000_000: raise ValueError(f"Bad SA size={n} @{self.pos}")
        return [self.rs() for _ in range(n)]

    def rest(self): return self.data[self.pos:]
    def get_size(self): return self.cRb

# ============================================================
# HEADER - exact copy from bdata_reader_final.py
# ============================================================
def extract_bin(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        for name in zf.namelist():
            if name.endswith('.bin'):
                return zf.read(name)
    raise FileNotFoundError(f"No .bin in {jar_path}")

def read_header(data, fid):
    r = BinaryReader(data, fid, 0)
    cnt = r.ri()
    rows = []
    for i in range(cnt):
        rows.append({'id': r.rl(), 'off': r.ri(), 'sz': r.ri(), 'seed': r.rb(), 'idx': i})
    ic = r.rb()
    for _ in range(ic):
        u = r.rb(); r.rstr(); c = r.ri()
        for _ in range(c):
            r.rl()
            if u: r.ri()
            else: r.ria()
    return rows, r.rest(), r.get_size()

# ============================================================
# EFFECT READER (aOC structure - 57 fields)
# ============================================================
def read_effect_aOC(rd):
    e = {}
    e['id']              = rd.ri()
    e['actionId']        = rd.ri()
    e['areaId']          = rd.ri()
    e['areaShape']       = rd.rs()
    e['areaSize']        = rd.ria()
    e['areaMinSize']     = rd.rs()
    e['paramsCount']     = rd.rs()
    e['params']          = rd.ria()
    e['execCount']       = rd.rs()
    e['durationBase']    = rd.ria()
    e['durationIncr']    = rd.ria()
    e['delay']           = rd.ria()
    e['group']           = rd.ria()
    e['contId']          = rd.ria()
    e['flags1']          = rd.ria()
    e['flags2']          = rd.ria()
    e['gfxId_str']       = rd.rstr()
    e['targets']         = rd.rla()
    e['triggerTarget']   = rd.rbool()
    e['maxExec']         = rd.ri()
    e['probability']     = rd.rf()
    e['affectsMap']      = rd.rbool()
    e['needLOS']         = rd.rbool()
    e['maxLevel']        = rd.rs()
    e['effectDuration']  = rd.rf()
    e['floatParams']     = rd.rfa()
    e['effectParam1']    = rd.rf()
    e['effectParam2']    = rd.rf()
    e['byte1']           = rd.rb()
    e['byte2']           = rd.rb()
    e['byte3']           = rd.rb()
    e['stateId']         = rd.ri()
    e['isDecursable']    = rd.rbool()
    e['applyCrit']       = rd.rs()
    e['critBonus']       = rd.rf()
    e['displayOrder']    = rd.rb()
    e['isPersonal']      = rd.rbool()
    e['condition']       = rd.rstr()
    e['elemMastery']     = rd.rs()
    e['elemResist']      = rd.rs()
    e['description']     = rd.rstr()
    e['gfxScript']       = rd.rstr()
    e['tooltip']         = rd.rstr()
    e['hideInFight']     = rd.rbool()
    e['hideInTimeline']  = rd.rbool()
    e['hideInTooltip']   = rd.rbool()
    e['isInactive']      = rd.rbool()
    e['isRebound']       = rd.rbool()
    e['useCaster']       = rd.rbool()
    e['effectElement']   = rd.ri()
    e['isStacking']      = rd.rbool()
    e['altEffectIds']    = rd.ria()
    e['bool_Q']          = rd.rbool()
    e['bool_R']          = rd.rbool()
    e['bool_S']          = rd.rbool()
    e['bool_T']          = rd.rbool()
    e['bool_U']          = rd.rbool()
    return e

def read_effect_fyb(rd):
    e = {}
    e['id']              = rd.ri()
    e['actionId']        = rd.ri()
    e['areaId']          = rd.ri()
    e['areaShape']       = rd.rs()
    e['areaSize']        = rd.ria()
    e['areaMinSize']     = rd.rs()
    e['paramsCount']     = rd.rs()
    e['params']          = rd.ria()
    e['execCount']       = rd.rs()
    e['durationBase']    = rd.ria()
    e['durationIncr']    = rd.ria()
    e['delay']           = rd.ria()
    e['group']           = rd.ria()
    e['contId']          = rd.ria()
    e['flags1']          = rd.ria()
    e['flags2']          = rd.ria()
    e['gfxId_str']       = rd.rstr()
    e['targets']         = rd.rla()
    e['triggerTarget']   = rd.rbool()
    e['maxExec']         = rd.ri()
    e['probability']     = rd.rf()
    e['affectsMap']      = rd.rbool()
    e['needLOS']         = rd.rbool()
    e['maxLevel']        = rd.rs()
    e['effectDuration']  = rd.rf()
    e['floatParams']     = rd.rfa()
    e['effectParam1']    = rd.rf()
    e['effectParam2']    = rd.rf()
    e['byte1']           = rd.rb()
    e['byte2']           = rd.rb()
    e['byte3']           = rd.rb()
    e['stateId']         = rd.ri()
    e['isDecursable']    = rd.rbool()
    e['applyCrit']       = rd.rs()
    e['critBonus']       = rd.rf()
    e['displayOrder']    = rd.rb()
    e['isPersonal']      = rd.rbool()
    e['condition']       = rd.rstr()
    e['elemMastery']     = rd.rs()
    e['elemResist']      = rd.rs()
    e['description']     = rd.rstr()
    e['gfxScript']       = rd.rstr()
    e['tooltip']         = rd.rstr()
    e['hideInFight']     = rd.rbool()
    e['hideInTimeline']  = rd.rbool()
    e['hideInTooltip']   = rd.rbool()
    e['isInactive']      = rd.rbool()
    e['isRebound']       = rd.rbool()
    e['useCaster']       = rd.rbool()
    e['effectElement']   = rd.ri()
    e['isStacking']      = rd.rbool()
    e['bool_qZj']       = rd.rbool()
    e['bool_qYi']       = rd.rbool()
    e['altEffectIds']    = rd.ria()
    return e

# ============================================================
# PARSE - exact same pattern as bdata_reader_final.py L286-315
# ONE reader on FULL buffer, set_pos(absolute) per row
# ============================================================
def parse_file(file_id, reader_fn, label, max_err=20):
    jar = os.path.join(BDATA_DIR, f"{file_id}.jar")
    rows, buf, msz = read_header(extract_bin(jar), file_id)
    log.info(f"{label}: {len(rows)} rows, buf={len(buf):,}")

    rd = BinaryReader(buf, file_id, msz)
    results = []
    ok = 0
    warns = 0
    errs = 0

    for row in rows:
        rd.set_pos(row['off'])
        rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            entry = reader_fn(rd)
            consumed = rd.get_pos() - start
            if consumed == row['sz']:
                ok += 1
                results.append(entry)
            else:
                warns += 1
                delta = consumed - row['sz']
                entry['_warn_delta'] = delta
                results.append(entry)
                if warns <= max_err:
                    log.warning(f"  WARN row {row['idx']} id={row['id']}: consumed={consumed} expected={row['sz']} delta={delta}")
        except Exception as e:
            errs += 1
            if errs <= max_err:
                log.error(f"  ERR row {row['idx']} id={row['id']}: {e}")

    log.info(f"  => {ok} OK, {warns} WARN, {errs} ERR / {len(rows)}")
    return results, ok, warns, errs

# ============================================================
# MAIN
# ============================================================
def main():
    log.info("=" * 60)
    log.info(f"Wakfu StaticEffects Parser - {datetime.now()}")
    log.info("=" * 60)

    # Test aOC
    log.info(f"\n>>> aOC (57 fields) <<<")
    aOC_res, aOC_ok, aOC_warn, aOC_err = parse_file(68, read_effect_aOC, "StaticEffects(aOC)")

    # Test fyb
    log.info(f"\n>>> fyb (54 fields) <<<")
    fyb_res, fyb_ok, fyb_warn, fyb_err = parse_file(68, read_effect_fyb, "StaticEffects(fyb)")

    # Pick winner
    log.info(f"\n{'=' * 60}")
    log.info(f"aOC: {aOC_ok} OK + {aOC_warn} WARN, {aOC_err} ERR")
    log.info(f"fyb: {fyb_ok} OK + {fyb_warn} WARN, {fyb_err} ERR")

    if aOC_ok + aOC_warn >= fyb_ok + fyb_warn:
        winner_name = "aOC"
        winner_data = aOC_res
        w_ok, w_warn, w_err = aOC_ok, aOC_warn, aOC_err
    else:
        winner_name = "fyb"
        winner_data = fyb_res
        w_ok, w_warn, w_err = fyb_ok, fyb_warn, fyb_err

    log.info(f"WINNER: {winner_name} ({w_ok} OK + {w_warn} WARN = {w_ok+w_warn} parsed)")

    # Show target effects
    target_ids = {174266, 174268, 174270, 178427, 178430, 182653}
    log.info(f"\n>>> Target effects (Sram spell effectIds) <<<")
    for entry in winner_data:
        if entry.get('id') in target_ids:
            log.info(f"  Effect {entry['id']}:")
            log.info(f"    actionId={entry['actionId']}, params={entry.get('params', [])}")
            log.info(f"    element={entry.get('effectElement', '?')}")
            log.info(f"    stateId={entry.get('stateId', 0)}, duration={entry.get('durationBase', [])}")
            log.info(f"    condition='{entry.get('condition', '')}'")

    # Warn deltas distribution
    deltas = [e.get('_warn_delta') for e in winner_data if '_warn_delta' in e]
    if deltas:
        dc = Counter(deltas)
        log.info(f"\n>>> WARN delta distribution (top 5) <<<")
        for d, c in dc.most_common(5):
            log.info(f"  delta={d}: {c} rows")

    # Save
    def sanitize(obj):
        if isinstance(obj, float):
            if obj != obj or obj == float('inf') or obj == float('-inf'):
                return None
            return round(obj, 6) if abs(obj) > 0.000001 else 0.0
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items() if not k.startswith('_')}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    clean = [sanitize(e) for e in winner_data if '_error' not in str(e.get('id', ''))]
    out_path = os.path.join(OUTPUT_DIR, "static_effects.json")
    log.info(f"\nSaving {len(clean)} effects -> {out_path}")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(clean, f, ensure_ascii=False)
    log.info(f"Size: {os.path.getsize(out_path)/1048576:.1f} MB")
    log.info("DONE")

if __name__ == '__main__':
    main()
