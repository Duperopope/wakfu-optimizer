#!/usr/bin/env python3
"""
bdata_reader_final.py - Parser Wakfu DEFINITIF v2
==================================================
Sources decompilees du client Wakfu v1.91 (wakfu-client.jar):
  aqJ.java  - CalcHoo: cRa = byte(long(cRa) + (long(cRc)*pos + long(cRb)))
  aqH.java  - BinaryReader: bGI=ReadInt, bGG=ReadShort, bGH=ReadFloat, etc.
  aqA.java  - File loader: header + slice + row parsing
  aOx.java  - SpellBinaryData (file_id=66)
  aOz.java  - BaseCastParam: int + float
  aOA.java  - AltCastParam: short + int[]
  aOy.java  - StringCastParam: int + HashMap<Int,aOz> + 10f + 4b + 4f + 4b
"""
import struct, os, sys, json, zipfile, logging
from datetime import datetime

BDATA_DIR = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\bdata_final.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
              logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)


class BinaryReader:
    """Exact port of aqJ + aqH from decompiled Wakfu client."""
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

    def rla(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad LA size={n} @{self.pos}")
        return [self.rl() for _ in range(n)]

    def rsa(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad SA size={n} @{self.pos}")
        return [self.rs() for _ in range(n)]

    def rstra(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad StrA size={n} @{self.pos}")
        return [self.rstr() for _ in range(n)]

    def rest(self):
        return self.data[self.pos:]

    def get_size(self):
        return self.cRb


def extract_bin(jar):
    with zipfile.ZipFile(jar) as z:
        for n in z.namelist():
            if n.endswith('.bin'): return z.read(n)
    raise FileNotFoundError(jar)


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


# ================================================================
# aOz: baseCastParam {int esE, float esF}
# ================================================================
def read_aOz(r):
    return {'esE': r.ri(), 'esF': r.rf()}


# ================================================================
# aOA: altCastParam {short esG, int[] esH}
# ================================================================
def read_aOA(r):
    return {'esG': r.rs(), 'esH': r.ria()}


# ================================================================
# aOy: stringCastParam - the big one
# {int emS, HashMap<Integer,aOz> esr,
#  10 floats, 4 bools, 4 floats, 4 bools}
# ================================================================
def read_aOy(r):
    obj = {}
    obj['emS'] = r.ri()
    # HashMap<Integer, aOz>
    n = r.ri()
    sub_map = {}
    for _ in range(n):
        key = r.ri()
        sub_map[str(key)] = read_aOz(r)
    obj['castParamOverrides'] = sub_map
    # 10 floats
    obj['PA_base'] = r.rf()
    obj['PA_inc'] = r.rf()
    obj['PM_base'] = r.rf()
    obj['PM_inc'] = r.rf()
    obj['PW_base'] = r.rf()
    obj['PW_inc'] = r.rf()
    obj['rangeMax'] = r.rf()
    obj['f8'] = r.rf()
    obj['rangeMin'] = r.rf()
    obj['rangeMinInc'] = r.rf()
    # 4 bools
    obj['b1'] = r.rbool()
    obj['b2'] = r.rbool()
    obj['b3'] = r.rbool()
    obj['b4'] = r.rbool()
    # 4 floats
    obj['f11'] = r.rf()
    obj['f12'] = r.rf()
    obj['f13'] = r.rf()
    obj['f14'] = r.rf()
    # 4 bools
    obj['b5'] = r.rbool()
    obj['b6'] = r.rbool()
    obj['b7'] = r.rbool()
    obj['b8'] = r.rbool()
    return obj


# ================================================================
# SPELL reader - exact copy of aOx.java a(aqH)
# ================================================================
def read_spell(r):
    s = {}
    s['id'] = r.ri()
    s['scriptId'] = r.ri()
    s['gfxId'] = r.ri()
    s['breedId'] = r.rs()
    s['maxLevel'] = r.rs()
    s['castMaxPerTarget'] = r.rs()
    s['castMaxPerTurn'] = r.rf()
    s['castMaxPerTurnIncr'] = r.rf()
    s['castMinInterval'] = r.rs()
    s['testLineOfSight'] = r.rbool()
    s['castOnlyLine'] = r.rbool()
    s['castOnlyInDiag'] = r.rbool()
    s['testFreeCell'] = r.rbool()
    s['testNotBorderCell'] = r.rbool()
    s['testDirectPath'] = r.rbool()
    s['testLOS2'] = r.rbool()
    s['targetFilter'] = r.ri()
    s['castCriterion'] = r.rstr()
    s['rangeElement'] = r.rs()
    s['PA_base'] = r.rf()
    s['PA_inc'] = r.rf()
    s['PM_base'] = r.rf()
    s['PM_inc'] = r.rf()
    s['PW_base'] = r.rf()
    s['PW_inc'] = r.rf()
    s['rangeMaxBase'] = r.rf()
    s['rangeMaxInc'] = r.rf()
    s['rangeMinBase'] = r.rf()
    s['rangeMinInc'] = r.rf()
    s['maxEffectCap'] = r.rs()
    s['element'] = r.rs()
    s['xpGainPercentage'] = r.rs()
    s['spellType'] = r.rs()
    s['uiPosition'] = r.rs()
    s['learnCriteria'] = r.rstr()
    s['altString'] = r.rstr()
    s['passive'] = r.rb()
    s['useAutoDesc'] = r.rbool()
    s['castRangeDynamic'] = r.rbool()
    s['breakInvis'] = r.rbool()
    s['actionOnCritMiss'] = r.rb()
    s['spellRangeDynamic'] = r.rbool()
    s['castBreakInvis2'] = r.rbool()
    s['castOnRandom'] = r.rbool()
    s['tunnelable'] = r.rbool()
    s['canCastOnSelf'] = r.rbool()
    s['assocItemUse'] = r.rbool()
    s['properties'] = r.ria()
    s['effectIds'] = r.ria()

    # HashMap<Byte, aOz> eso - baseCastParams
    bc = r.ri()
    s['baseCastParams'] = {}
    for _ in range(bc):
        k = r.rb()
        s['baseCastParams'][str(k)] = read_aOz(r)

    # HashMap<Short, aOA> esp - altCastParams
    ac = r.ri()
    s['altCastParams'] = {}
    for _ in range(ac):
        k = r.rs()
        s['altCastParams'][str(k)] = read_aOA(r)

    # HashMap<String, aOy> esq - stringCasts
    mc = r.ri()
    s['stringCasts'] = {}
    for _ in range(mc):
        k = r.rstr()
        s['stringCasts'][k] = read_aOy(r)

    return s


def parse_file(fid, reader_fn, max_err=20):
    jar = os.path.join(BDATA_DIR, f"{fid}.jar")
    if not os.path.exists(jar):
        log.error(f"Missing {jar}"); return []
    rows, buf, msz = read_header(extract_bin(jar), fid)
    log.info(f"File {fid}: {len(rows)} rows, buf={len(buf)}")
    rd = BinaryReader(buf, fid, msz)
    results, ok, warns, errs = [], 0, 0, 0
    for row in rows:
        rd.set_pos(row['off']); rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            entry = reader_fn(rd)
            consumed = rd.get_pos() - start
            entry['_ok'] = consumed == row['sz']
            entry['_consumed'] = consumed
            entry['_expected'] = row['sz']
            if entry['_ok']:
                ok += 1
            else:
                warns += 1
                delta = consumed - row['sz']
                if warns <= max_err:
                    log.warning(f"  WARN Row {row['idx']} id={row['id']}: consumed={consumed} expected={row['sz']} delta={delta}")
            results.append(entry)
        except Exception as e:
            errs += 1
            if errs <= max_err:
                log.error(f"  ERR Row {row['idx']} id={row['id']}: {e}")
            results.append({'_error': str(e), '_row_id': row['id']})
    log.info(f"  => {ok} OK, {warns} WARN, {errs} ERR / {len(rows)}")
    return results


def main():
    log.info("=" * 60)
    log.info(f"Wakfu BData Reader FINAL v2 - {datetime.now()}")
    log.info("Source: decompiled aOx.java + aOz.java + aOA.java + aOy.java")
    log.info("=" * 60)

    # SPELL (file 66)
    log.info("\n>>> Spell (66) <<<")
    spells = parse_file(66, read_spell)
    ok_spells = [s for s in spells if s.get('_ok')]
    warn_spells = [s for s in spells if '_ok' in s and not s['_ok']]
    err_spells = [s for s in spells if '_error' in s]

    for s in ok_spells[:5]:
        log.info(f"  Spell {s['id']}: breed={s['breedId']} PA={s['PA_base']} effects={s['effectIds']}")

    sram = [s for s in ok_spells if s.get('breedId') == 4]
    log.info(f"  Sram spells: {len(sram)}")

    # Analyser les warns restants
    if warn_spells:
        deltas = [s['_consumed'] - s['_expected'] for s in warn_spells]
        unique_d = sorted(set(deltas))
        log.info(f"\n  WARN analysis ({len(warn_spells)} rows):")
        for d in unique_d[:15]:
            c = deltas.count(d)
            log.info(f"    delta={d:+4d}: {c} rows")

    # Save
    with open(os.path.join(OUTPUT_DIR, 'all_spells.json'), 'w', encoding='utf-8') as f:
        json.dump(ok_spells, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"\nSaved {len(ok_spells)} OK spells -> all_spells.json")

    with open(os.path.join(OUTPUT_DIR, 'sram_spells.json'), 'w', encoding='utf-8') as f:
        json.dump(sram, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"Saved {len(sram)} Sram spells -> sram_spells.json")

    # Save ALL (including warns, they parsed but size mismatch)
    all_parsed = [s for s in spells if '_error' not in s]
    with open(os.path.join(OUTPUT_DIR, 'all_spells_including_warns.json'), 'w', encoding='utf-8') as f:
        json.dump(all_parsed, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"Saved {len(all_parsed)} total parsed spells -> all_spells_including_warns.json")

    if ok_spells:
        s = ok_spells[0]
        log.info(f"\n  Example spell {s['id']}:")
        for k, v in s.items():
            if not k.startswith('_'):
                log.info(f"    {k}: {v}")

    log.info("\nDONE")


if __name__ == '__main__':
    main()
