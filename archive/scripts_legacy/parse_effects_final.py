"""
Parser StaticEffects (file 68) et EffectGroups (file 29).
Structures from decompiled aOC/fyb and aMd/fvB.
"""
import struct, os, sys, json, zipfile, logging
from datetime import datetime

BDATA_DIR = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\parse_effects_final.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
              logging.StreamHandler(sys.stdout)])
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
        if n < 0 or n > 100000: raise ValueError(f"Bad str len={n} @{self.pos}")
        if n == 0: return ""
        s = self.data[self.pos:self.pos+n]; self.pos += n
        return s.decode('utf-8', errors='replace')

    def ria(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad IA size={n} @{self.pos}")
        return [self.ri() for _ in range(n)]

    def rfa(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad FA size={n} @{self.pos}")
        return [self.rf() for _ in range(n)]

    def rba(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad BA size={n} @{self.pos}")
        return [self.rb() for _ in range(n)]

    def rsa(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad SA size={n} @{self.pos}")
        return [self.rs() for _ in range(n)]

    def rla(self):
        """ReadLongArray - bxz()"""
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad LA size={n} @{self.pos}")
        return [self.rl() for _ in range(n)]

    def rstra(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad StrA size={n} @{self.pos}")
        return [self.rstr() for _ in range(n)]

    def rest(self): return self.data[self.pos:]
    def get_size(self): return self.cRb


def extract_bin(jar):
    with zipfile.ZipFile(jar) as z:
        for n in z.namelist():
            if n.endswith('.bin'): return z.read(n)

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


# === EffectGroup (file 29) - aMd/fvB ===
def read_effect_group(r):
    return {
        'id': r.ri(),
        'effectIds': r.ria(),
    }


# === StaticEffect (file 68) - fyb (shorter) then try aOC (longer) ===
def read_static_effect_fyb(r):
    e = {}
    e['effectId'] = r.ri()       # bfE
    e['actionId'] = r.ri()       # bfF
    e['parentId'] = r.ri()       # egx
    e['areaOrder'] = r.rs()      # eta
    e['areaShape'] = r.ria()     # etb (int[])
    e['areaSize0'] = r.rs()      # etc
    e['areaSize1'] = r.rs()      # etd
    e['areaSize2'] = r.ria()     # ete (int[])
    e['areaSize3'] = r.rs()      # etf
    e['targetMask1'] = r.ria()   # etg
    e['targetMask2'] = r.ria()   # eth
    e['targetMask3'] = r.ria()   # eti
    e['targetMask4'] = r.ria()   # etj
    e['targetMask5'] = r.ria()   # etk
    e['targetMask6'] = r.ria()   # etl
    e['targetMask7'] = r.ria()   # etm
    e['criterion'] = r.rstr()    # etn
    e['triggers'] = r.rla()      # eto (long[])
    e['isAffectedByLoc'] = r.rbool()  # bfY
    e['durationBase'] = r.ri()   # etp
    e['durationIncr'] = r.rf()   # etq
    e['execCount'] = r.rbool()   # esK
    e['isDecursable'] = r.rbool() # etr
    e['triggerTarget'] = r.rs()  # ets
    e['triggersCrit'] = r.rf()   # ett
    e['params'] = r.rfa()        # biv (float[])
    e['f1'] = r.rf()             # etu
    e['f2'] = r.rf()             # etv
    e['b1'] = r.rb()             # etw
    e['b2'] = r.rb()             # etx
    e['b3'] = r.rb()             # ety
    e['targets'] = r.ri()        # bfW
    e['emptyCells'] = r.rbool()  # etz
    e['s1'] = r.rs()             # etA
    e['f3'] = r.rf()             # etB
    e['b4'] = r.rb()             # etC
    e['isPersonal'] = r.rbool()  # etD
    e['str1'] = r.rstr()         # etE
    e['s2'] = r.rs()             # etF
    e['s3'] = r.rs()             # etG
    e['str2'] = r.rstr()         # etH
    e['str3'] = r.rstr()         # etI
    e['str4'] = r.rstr()         # etJ
    e['bfK'] = r.rbool()
    e['etK'] = r.rbool()
    e['etL'] = r.rbool()
    e['etM'] = r.rbool()
    e['etN'] = r.rbool()
    e['etO'] = r.rbool()
    e['dKh'] = r.ri()
    e['bfZ'] = r.rbool()
    e['qZj'] = r.rbool()
    e['qYi'] = r.rbool()
    e['etP'] = r.ria()
    return e


def read_static_effect_aOC(r):
    e = {}
    e['effectId'] = r.ri()
    e['actionId'] = r.ri()
    e['parentId'] = r.ri()
    e['areaOrder'] = r.rs()
    e['areaShape'] = r.ria()
    e['areaSize0'] = r.rs()
    e['areaSize1'] = r.rs()
    e['areaSize2'] = r.ria()
    e['areaSize3'] = r.rs()
    e['targetMask1'] = r.ria()
    e['targetMask2'] = r.ria()
    e['targetMask3'] = r.ria()
    e['targetMask4'] = r.ria()
    e['targetMask5'] = r.ria()
    e['targetMask6'] = r.ria()
    e['targetMask7'] = r.ria()
    e['criterion'] = r.rstr()
    e['triggers'] = r.rla()
    e['isAffectedByLoc'] = r.rbool()
    e['durationBase'] = r.ri()
    e['durationIncr'] = r.rf()
    e['execCount'] = r.rbool()
    e['isDecursable'] = r.rbool()
    e['triggerTarget'] = r.rs()
    e['triggersCrit'] = r.rf()
    e['params'] = r.rfa()
    e['f1'] = r.rf()
    e['f2'] = r.rf()
    e['b1'] = r.rb()
    e['b2'] = r.rb()
    e['b3'] = r.rb()
    e['targets'] = r.ri()
    e['emptyCells'] = r.rbool()
    e['s1'] = r.rs()
    e['f3'] = r.rf()
    e['b4'] = r.rb()
    e['isPersonal'] = r.rbool()
    e['str1'] = r.rstr()
    e['s2'] = r.rs()
    e['s3'] = r.rs()
    e['str2'] = r.rstr()
    e['str3'] = r.rstr()
    e['str4'] = r.rstr()
    e['bfK'] = r.rbool()
    e['etK'] = r.rbool()
    e['etL'] = r.rbool()
    e['etM'] = r.rbool()
    e['etN'] = r.rbool()
    e['etO'] = r.rbool()
    e['dKh'] = r.ri()
    e['bfZ'] = r.rbool()
    e['etP'] = r.ria()
    e['etQ'] = r.rbool()
    e['etR'] = r.rbool()
    e['etS'] = r.rbool()
    e['etT'] = r.rbool()
    e['etU'] = r.rbool()
    return e


def parse_file(fid, reader_fn, name, max_err=20):
    jar = os.path.join(BDATA_DIR, f"{fid}.jar")
    if not os.path.exists(jar):
        log.error(f"Missing {jar}"); return []
    rows, buf, msz = read_header(extract_bin(jar), fid)
    log.info(f"{name} (file {fid}): {len(rows)} rows, buf={len(buf)}")
    rd = BinaryReader(buf, fid, msz)
    results, ok, errs = [], 0, 0
    for row in rows:
        rd.set_pos(row['off']); rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            entry = reader_fn(rd)
            consumed = rd.get_pos() - start
            if consumed == row['sz']:
                ok += 1
            else:
                errs += 1
                if errs <= 5:
                    log.warning(f"  WARN row {row['idx']}: consumed={consumed} expected={row['sz']} delta={consumed-row['sz']}")
            results.append(entry)
        except Exception as e:
            errs += 1
            if errs <= max_err:
                log.error(f"  ERR row {row['idx']} id={row['id']}: {e}")
    log.info(f"  => {ok} OK, {errs} ERR / {len(rows)}")
    return results, ok, len(rows)


def main():
    log.info("=" * 60)
    log.info(f"Wakfu Effects & States Parser - {datetime.now()}")
    log.info("=" * 60)

    # === EffectGroups (file 29) ===
    log.info("\n>>> EffectGroups (file 29) <<<")
    eg_results, eg_ok, eg_total = parse_file(29, read_effect_group, "EffectGroups")

    if eg_ok > 0:
        out = os.path.join(OUTPUT_DIR, 'effect_groups.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(eg_results, f, ensure_ascii=False, default=str)
        log.info(f"  Saved {len(eg_results)} effect groups -> effect_groups.json")

        # Show examples
        for eg in eg_results[:3]:
            log.info(f"  Group {eg['id']}: effects={eg['effectIds']}")

    # === StaticEffects (file 68) - try both versions ===
    log.info("\n>>> StaticEffects (file 68) - trying fyb <<<")
    se_results_fyb, se_ok_fyb, se_total = parse_file(68, read_static_effect_fyb, "StaticEffects(fyb)")

    log.info(f"\n>>> StaticEffects (file 68) - trying aOC <<<")
    se_results_aOC, se_ok_aOC, se_total2 = parse_file(68, read_static_effect_aOC, "StaticEffects(aOC)")

    # Use whichever works better
    if se_ok_fyb >= se_ok_aOC:
        se_results = se_results_fyb
        se_ok = se_ok_fyb
        winner = "fyb"
    else:
        se_results = se_results_aOC
        se_ok = se_ok_aOC
        winner = "aOC"

    log.info(f"\n  Best: {winner} ({se_ok}/{se_total})")

    if se_ok > 0:
        # Too big for full JSON, save only OK entries
        ok_effects = [e for e in se_results if 'effectId' in e]
        out = os.path.join(OUTPUT_DIR, 'static_effects.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(ok_effects, f, ensure_ascii=False, default=str)
        log.info(f"  Saved {len(ok_effects)} static effects -> static_effects.json")

        # Show examples with known IDs
        target_ids = {174266, 174268, 174270, 178427, 178430, 182653}
        for e in ok_effects:
            if e.get('effectId') in target_ids:
                log.info(f"\n  Effect {e['effectId']}:")
                log.info(f"    actionId={e['actionId']}, parentId={e['parentId']}")
                log.info(f"    params={e.get('params', [])}")
                log.info(f"    criterion='{e.get('criterion', '')}'")
                log.info(f"    duration={e.get('durationBase', 0)}")

    log.info("\nDONE")


if __name__ == '__main__':
    main()
