"""
Parser AvatarBreed (86.jar) - Structure exacte de aNn.java + 9 sous-classes
Sources: aNn, aNw, aNs, aNu, aNt, aNv, aNr, aNq, aNp, aNo decompiles
"""
import struct, os, sys, json, zipfile, logging

BDATA_DIR = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_FILE = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\parse_breeds.log"
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

    def rd(self):
        """ReadDouble - bGJ()"""
        self._hoo()
        v = struct.unpack_from('<d', self.data, self.pos)[0]; self.pos += 8
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

    def rsa(self):
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad SA size={n} @{self.pos}")
        return [self.rs() for _ in range(n)]

    def rstra(self):
        """ReadStringArray - bGO()"""
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


# === SOUS-CLASSES ===

def read_aNw(r):
    return {'id': r.ri(), 'eoY': r.ri()}

def read_aNs(r):
    return {
        'id': r.ri(), 'asf': r.rb(), 'name': r.rstr(),
        'eoO': r.rbool(), 'eoP': r.rbool(), 'bMn': r.ri(),
        'eoQ': r.rbool(), 'ehO': r.ri(), 'egP': r.ri()
    }

def read_aNu(r):
    return {
        'id': r.ri(), 'ehc': r.ri(), 'eoS': r.ri(), 'eoT': r.ri(),
        'name': r.rstr(), 'eje': r.rf(), 'eoU': r.ri(),
        'bMn': r.ri(), 'eoV': r.ri(), 'eoW': r.ria(), 'eoX': r.rbool()
    }

def read_aNt(r):
    return {'id': r.ri(), 'bIi': r.ri(), 'egP': r.ri(), 'eoR': r.rbool()}

def read_aNv(r):
    return {'id': r.ri(), 'aHP': r.ri(), 'egP': r.ri()}

def read_aNr(r):
    return {
        'asA': r.ri(), 'eoJ': r.rb(), 'emK': r.rs(), 'emL': r.rs(),
        'eoK': r.rs(), 'emM': r.rbool(), 'eoL': r.rs(),
        'ejs': r.rd(), 'eoM': r.ria(), 'eoN': r.rbool()
    }

def read_aNq(r):
    return {'eoI': r.rstr(), 'beD': r.rstra()}

def read_aNp(r):
    return {'eoH': r.ri(), 'aXS': r.ri()}

def read_aNo(r):
    return {'eoG': r.rb(), 'bdC': r.rstr()}


def read_array(r, reader_fn):
    n = r.ri()
    if n < 0 or n > 10000:
        raise ValueError(f"Bad array size={n} @{r.get_pos()}")
    return [reader_fn(r) for _ in range(n)]


# === BREED READER - exact aNn.java ===
def read_breed(r):
    b = {}
    # Ligne 617-635: scalaires simples
    b['id'] = r.ri()             # o
    b['ena'] = r.ri()
    b['breedId'] = r.rs()        # enb
    b['enc'] = r.rs()
    b['end'] = r.rf()
    b['ene'] = r.rf()
    # ehh-enm: 13 ints
    b['hp'] = r.ri()              # ehh
    b['ap'] = r.ri()              # ehk
    b['mp'] = r.ri()              # ehi
    b['wp'] = r.ri()              # ehj
    b['enf'] = r.ri()
    b['initiative'] = r.ri()      # ehl
    b['eng'] = r.ri()
    b['enh'] = r.ri()
    b['eni'] = r.ri()
    b['enj'] = r.ri()
    b['enk'] = r.ri()
    b['enl'] = r.ri()
    b['enm'] = r.ri()
    # enn-eny: 12 floats
    for i in range(12):
        b[f'float_{i}'] = r.rf()
    # enz-enO: 16 ints
    for i in range(16):
        b[f'int_{i}'] = r.ri()
    # enP-eoc: 14 floats
    for i in range(14):
        b[f'float2_{i}'] = r.rf()
    # eod: 1 bool
    b['eod'] = r.rbool()
    # eoe-eog: 3 shorts
    b['eoe'] = r.rs()
    b['eof'] = r.rs()
    b['eog'] = r.rs()
    # eoh: 1 int
    b['eoh'] = r.ri()
    # eoi, eoj: 2 int arrays
    b['spellIds'] = r.ria()       # eoi
    b['eoj'] = r.ria()
    # ehw: short array (bGN)
    b['ehw'] = r.rsa()
    # aNw array
    b['aNw_array'] = read_array(r, read_aNw)
    # eol: byte
    b['eol'] = r.rb()
    # eom-eop: 4 shorts
    b['eom'] = r.rs()
    b['eon'] = r.rs()
    b['eoo'] = r.rs()
    b['eop'] = r.rs()
    # aNs array
    b['spells_aNs'] = read_array(r, read_aNs)
    # aNu array
    b['passives_aNu'] = read_array(r, read_aNu)
    # aNt array
    b['aNt_array'] = read_array(r, read_aNt)
    # aNv array
    b['aNv_array'] = read_array(r, read_aNv)
    # eou, eov, eow
    b['eou'] = r.ri()
    b['eov'] = r.rs()
    b['eow'] = r.ri()
    # aNr array
    b['characteristics'] = read_array(r, read_aNr)
    # eoy, eoz
    b['eoy'] = r.ri()
    b['eoz'] = r.ri()
    # eoA: int array
    b['eoA'] = r.ria()
    # aNq array
    b['aNq_array'] = read_array(r, read_aNq)
    # aNp array
    b['aNp_array'] = read_array(r, read_aNp)
    # aNo array
    b['aNo_array'] = read_array(r, read_aNo)
    # asz, eoE: 2 ints
    b['asz'] = r.ri()
    b['eoE'] = r.ri()
    # eoF: string (nom de la classe!)
    b['className'] = r.rstr()
    return b


def main():
    jar = os.path.join(BDATA_DIR, "86.jar")
    rows, buf, msz = read_header(extract_bin(jar), 86)
    log.info(f"AvatarBreed: {len(rows)} rows, buf={len(buf)}")

    rd = BinaryReader(buf, 86, msz)
    ok, errs = 0, 0
    breeds = []

    for row in rows:
        rd.set_pos(row['off']); rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            b = read_breed(rd)
            consumed = rd.get_pos() - start
            match = consumed == row['sz']
            if match:
                ok += 1
            else:
                log.warning(f"  WARN breed {b.get('className','?')}: consumed={consumed} expected={row['sz']} delta={consumed-row['sz']}")
            breeds.append(b)
        except Exception as e:
            errs += 1
            log.error(f"  ERR row {row['idx']} id={row['id']}: {e}")

    log.info(f"\nResultat: {ok} OK, {errs} ERR / {len(rows)}")

    # Afficher le mapping
    log.info(f"\n{'='*50}")
    log.info(f"BREED ID -> CLASS NAME")
    log.info(f"{'='*50}")
    for b in breeds:
        name = b.get('className', '?')
        bid = b.get('breedId', '?')
        hp = b.get('hp', '?')
        spells = len(b.get('spellIds', []))
        log.info(f"  breedId={bid:4} -> {name:20s} (HP={hp}, spells={spells})")

    # Sauvegarder
    out = os.path.join(OUTPUT_DIR, 'breeds.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(breeds, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"\nSaved: {out}")


if __name__ == '__main__':
    main()
