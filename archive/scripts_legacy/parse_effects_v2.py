"""
Wakfu StaticEffects Parser v2 - file 68
CONFIRMED: ONE reader on FULL buffer + absolute positions
Structure: aOC (57 fields) = 173,626/173,626
"""
import struct
import zipfile
import json
import os
import logging
from datetime import datetime

BDATA_DIR  = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE   = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\parse_effects_v2.log"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO, format='%(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

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

    def rest(self): return self.data[self.pos:]
    def get_size(self): return self.cRb

def extract_bin(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        for name in zf.namelist():
            if name.endswith('.bin'):
                return zf.read(name)

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

def read_effect(rd):
    e = {}
    e['id']             = rd.ri()
    e['actionId']       = rd.ri()
    e['areaId']         = rd.ri()
    e['areaShape']      = rd.rs()
    e['areaSize']       = rd.ria()
    e['areaMinSize']    = rd.rs()
    e['paramsCount']    = rd.rs()
    e['params']         = rd.ria()
    e['execCount']      = rd.rs()
    e['durationBase']   = rd.ria()
    e['durationIncr']   = rd.ria()
    e['delay']          = rd.ria()
    e['group']          = rd.ria()
    e['contId']         = rd.ria()
    e['flags1']         = rd.ria()
    e['flags2']         = rd.ria()
    e['gfxId_str']      = rd.rstr()
    e['targets']        = rd.rla()
    e['triggerTarget']  = rd.rbool()
    e['maxExec']        = rd.ri()
    e['probability']    = rd.rf()
    e['affectsMap']     = rd.rbool()
    e['needLOS']        = rd.rbool()
    e['maxLevel']       = rd.rs()
    e['effectDuration'] = rd.rf()
    e['floatParams']    = rd.rfa()
    e['effectParam1']   = rd.rf()
    e['effectParam2']   = rd.rf()
    e['byte1']          = rd.rb()
    e['byte2']          = rd.rb()
    e['byte3']          = rd.rb()
    e['stateId']        = rd.ri()
    e['isDecursable']   = rd.rbool()
    e['applyCrit']      = rd.rs()
    e['critBonus']      = rd.rf()
    e['displayOrder']   = rd.rb()
    e['isPersonal']     = rd.rbool()
    e['condition']      = rd.rstr()
    e['elemMastery']    = rd.rs()
    e['elemResist']     = rd.rs()
    e['description']    = rd.rstr()
    e['gfxScript']      = rd.rstr()
    e['tooltip']        = rd.rstr()
    e['hideInFight']    = rd.rbool()
    e['hideInTimeline'] = rd.rbool()
    e['hideInTooltip']  = rd.rbool()
    e['isInactive']     = rd.rbool()
    e['isRebound']      = rd.rbool()
    e['useCaster']      = rd.rbool()
    e['effectElement']  = rd.ri()
    e['isStacking']     = rd.rbool()
    e['altEffectIds']   = rd.ria()
    e['bool_Q']         = rd.rbool()
    e['bool_R']         = rd.rbool()
    e['bool_S']         = rd.rbool()
    e['bool_T']         = rd.rbool()
    e['bool_U']         = rd.rbool()
    return e

def main():
    log.info("=" * 60)
    log.info(f"Wakfu StaticEffects Parser v2 - {datetime.now()}")
    log.info("=" * 60)

    # Parse file 68
    jar = os.path.join(BDATA_DIR, "68.jar")
    rows, buf, msz = read_header(extract_bin(jar), 68)
    log.info(f"File 68: {len(rows):,} rows, buf={len(buf):,}, file_size={msz}")

    rd = BinaryReader(buf, 68, msz)
    results = []
    ok = 0
    errs = 0
    warns = 0

    for row in rows:
        rd.set_pos(row['off'])
        rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            entry = read_effect(rd)
            consumed = rd.get_pos() - start
            if consumed == row['sz']:
                ok += 1
            else:
                warns += 1
                if warns <= 10:
                    log.warning(f"  WARN row {row['idx']} id={row['id']}: {consumed} != {row['sz']}")
            results.append(entry)
        except Exception as e:
            errs += 1
            if errs <= 10:
                log.error(f"  ERR row {row['idx']} id={row['id']}: {e}")

    log.info(f"  => {ok:,} OK, {warns:,} WARN, {errs:,} ERR / {len(rows):,}")
    log.info(f"  Total parsed: {len(results):,}")

    # Index for lookups
    eff_by_id = {e['id']: e for e in results}
    log.info(f"  Unique IDs: {len(eff_by_id):,}")

    # Target effects
    target_ids = [174266, 174268, 174270, 178427, 178430, 182653,
                  120859, 136510, 410581, 411407]
    log.info(f"\n>>> Sample effects <<<")
    for tid in target_ids:
        e = eff_by_id.get(tid)
        if e:
            log.info(f"  Effect {tid}: action={e['actionId']}, params={e['params']}, "
                     f"element={e['effectElement']}, state={e['stateId']}, "
                     f"cond='{e['condition'][:60]}'")
        else:
            log.info(f"  Effect {tid}: NOT FOUND")

    # Save - compact JSON (no indent for 173K entries)
    def sanitize(obj):
        if isinstance(obj, float):
            if obj != obj or obj == float('inf') or obj == float('-inf'):
                return None
            return obj
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    out_path = os.path.join(OUTPUT_DIR, "static_effects.json")
    log.info(f"\nSaving {len(results):,} effects -> {out_path}")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump([sanitize(e) for e in results], f, ensure_ascii=False)

    fsize = os.path.getsize(out_path)
    log.info(f"  File size: {fsize / 1048576:.1f} MB")

    # Verification: reload and count
    with open(out_path, 'r', encoding='utf-8') as f:
        check = json.load(f)
    log.info(f"  Verification: reloaded {len(check):,} entries")

    log.info("\nDONE")

if __name__ == '__main__':
    main()
