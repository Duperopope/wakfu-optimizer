"""
Diagnostic v3 - Utilise le code EXACT de bdata_reader_final.py
pour analyser les 395 rows en echec (warn + err).
"""
import struct, os, sys, json, zipfile, logging

BDATA_DIR = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\diagnose_v3.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
              logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)


# === EXACT COPY of BinaryReader from bdata_reader_final.py ===
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


# === EXACT COPY of read_header ===
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


# === SPELL with field-by-field tracking ===
def read_spell_tracked(r):
    s = {}
    trace = []

    def t(name, func):
        p = r.get_pos()
        h = r.cRa
        v = func()
        s[name] = v
        trace.append({'f': name, 'p': p, 'h': h, 'v': repr(v) if isinstance(v, str) else v})
        return v

    t('id', r.ri)
    t('scriptId', r.ri)
    t('gfxId', r.ri)
    t('breedId', r.rs)
    t('maxLevel', r.rs)
    t('castMaxPerTarget', r.rs)
    t('castMaxPerTurn', r.rf)
    t('castMaxPerTurnIncr', r.rf)
    t('castMinInterval', r.rs)
    t('testLOS', r.rbool)
    t('castOnlyLine', r.rbool)
    t('castOnlyDiag', r.rbool)
    t('testFreeCell', r.rbool)
    t('testNotBorder', r.rbool)
    t('testDirectPath', r.rbool)
    t('testLOS2', r.rbool)
    t('targetFilter', r.ri)
    t('castCriterion', r.rstr)
    t('rangeElement', r.rs)
    t('PA_base', r.rf)
    t('PA_inc', r.rf)
    t('PM_base', r.rf)
    t('PM_inc', r.rf)
    t('PW_base', r.rf)
    t('PW_inc', r.rf)
    t('rangeMaxBase', r.rf)
    t('rangeMaxInc', r.rf)
    t('rangeMinBase', r.rf)
    t('rangeMinInc', r.rf)
    t('maxEffectCap', r.rs)
    t('element', r.rs)
    t('xpGainPct', r.rs)
    t('spellType', r.rs)
    t('uiPosition', r.rs)
    t('learnCriteria', r.rstr)
    t('altString', r.rstr)
    t('passive', r.rb)
    t('useAutoDesc', r.rbool)
    t('castRangeDyn', r.rbool)
    t('breakInvis', r.rbool)
    t('actionCritMiss', r.rb)
    t('spellRangeDyn', r.rbool)
    t('castBreakInvis2', r.rbool)
    t('castOnRandom', r.rbool)
    t('tunnelable', r.rbool)
    t('canCastOnSelf', r.rbool)
    t('assocItemUse', r.rbool)
    t('properties', r.ria)
    t('effectIds', r.ria)

    bc = t('baseCastCount', r.ri)
    bcp = {}
    for i in range(bc):
        k = r.rb(); a = r.ri(); b = r.rf()
        bcp[str(k)] = {'a': a, 'b': b}
    s['baseCastParams'] = bcp

    ac = t('altCastCount', r.ri)
    acp = {}
    for i in range(ac):
        k = r.rs(); a = r.ri(); b = r.rf()
        acp[str(k)] = {'a': a, 'b': b}
    s['altCastParams'] = acp

    mc = t('stringCastCount', r.ri)
    scp = {}
    for i in range(mc):
        k = r.rstr(); a = r.ri(); b = r.rf()
        scp[k] = {'a': a, 'b': b}
    s['stringCasts'] = scp

    return s, trace


def main():
    jar = os.path.join(BDATA_DIR, "66.jar")
    rows, buf, msz = read_header(extract_bin(jar), 66)
    log.info(f"Rows: {len(rows)}, buf: {len(buf)}")

    # Verify first 3 rows
    for i in range(min(3, len(rows))):
        r = rows[i]
        log.info(f"  Row {i}: id={r['id']}, off={r['off']}, sz={r['sz']}, seed={r['seed']}")

    rd = BinaryReader(buf, 66, msz)
    ok_count = 0
    warn_list = []
    err_list = []

    for row in rows:
        rd.set_pos(row['off']); rd.set_hoo(row['seed'])
        start = rd.get_pos()
        verbose = (row['idx'] < 3 or row['idx'] in [42, 70, 80, 97, 174, 189, 191, 192, 205, 254])
        try:
            fields, trace = read_spell_tracked(rd)
            consumed = rd.get_pos() - start

            if consumed == row['sz']:
                ok_count += 1
            else:
                delta = consumed - row['sz']
                entry = {
                    'row': row['idx'], 'id': row['id'], 'spell_id': fields.get('id', 0),
                    'name': fields.get('castCriterion', ''),
                    'consumed': consumed, 'expected': row['sz'], 'delta': delta,
                    'effectIds': fields.get('effectIds', []),
                    'baseCastCount': fields.get('baseCastCount', 0),
                    'altCastCount': fields.get('altCastCount', 0),
                    'stringCastCount': fields.get('stringCastCount', 0),
                }
                if verbose:
                    entry['last_fields'] = trace[-10:]
                warn_list.append(entry)

        except Exception as e:
            entry = {'row': row['idx'], 'id': row['id'], 'error': str(e)}
            if verbose and 'trace' in dir() and trace:
                entry['last_fields'] = trace[-5:]
            err_list.append(entry)

    log.info(f"\n{'='*60}")
    log.info(f"RESULTATS: {ok_count} OK, {len(warn_list)} WARN, {len(err_list)} ERR / {len(rows)}")
    log.info(f"{'='*60}")

    if warn_list:
        deltas = [w['delta'] for w in warn_list]
        unique_d = sorted(set(deltas))
        log.info(f"\nWARN deltas ({len(warn_list)} rows):")
        for d in unique_d[:20]:
            c = deltas.count(d)
            examples = [w for w in warn_list if w['delta'] == d][:2]
            log.info(f"  delta={d:+4d}: {c:4d} rows | ex: {[e['id'] for e in examples]}")
            if d != 0:
                for ex in examples:
                    lf = ex.get('last_fields', [])
                    if lf:
                        log.info(f"    last fields: {[f['f'] for f in lf[-5:]]}")
                        log.info(f"    last values: {[f['v'] for f in lf[-5:]]}")

    if err_list:
        log.info(f"\nERR ({len(err_list)} rows), 15 premieres:")
        for e in err_list[:15]:
            log.info(f"  Row {e['row']} id={e['id']}: {e['error']}")
            if 'last_fields' in e:
                log.info(f"    parsed before error: {[f['f'] for f in e['last_fields']]}")

    # Save diagnostic
    diag = {
        'summary': {'ok': ok_count, 'warn': len(warn_list), 'err': len(err_list), 'total': len(rows)},
        'warnings': warn_list[:100],
        'errors': err_list[:100],
    }
    out_path = os.path.join(OUTPUT_DIR, 'diagnostic_v3.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(diag, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"\nSaved: {out_path}")

if __name__ == '__main__':
    main()
