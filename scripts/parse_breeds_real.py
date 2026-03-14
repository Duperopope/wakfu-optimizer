"""
Parser AvatarBreed (86.jar) avec les VRAIES classes fuI et aLh.
Teste les deux et garde celle qui marche.
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

    def rba(self):
        """ReadByteArray - bxB()"""
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad BA size={n} @{self.pos}")
        return [self.rb() for _ in range(n)]

    def rfa(self):
        """ReadFloatArray - bxA()"""
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad FA size={n} @{self.pos}")
        return [self.rf() for _ in range(n)]

    def rsa(self):
        """ReadShortArray - bGN()"""
        n = self.ri()
        if n < 0 or n > 100000: raise ValueError(f"Bad SA size={n} @{self.pos}")
        return [self.rs() for _ in range(n)]

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


# === fuI structure (simpler, 17 ints + 3 arrays) ===
def read_fuI(r):
    b = {}
    b['id'] = r.ri()
    b['name'] = r.rstr()
    b['tyH'] = r.ri()
    b['tyI'] = r.ri()
    b['tyJ'] = r.ri()
    b['tyK'] = r.ri()
    b['ehh'] = r.ri()
    b['ehi'] = r.ri()
    b['ehj'] = r.ri()
    b['ehk'] = r.ri()
    b['ehl'] = r.ri()
    b['ehm'] = r.ri()
    b['ehn'] = r.ri()
    b['eho'] = r.ri()
    b['ehp'] = r.ri()
    b['ehq'] = r.ri()
    b['ehr'] = r.ri()
    b['ehs'] = r.ri()
    b['eht'] = r.ri()
    b['ehu'] = r.rba()   # byte[]
    b['ehv'] = r.rfa()   # float[]
    b['ehw'] = r.rsa()   # short[]
    return b


# === aLh structure (17 ints + 5 arrays + 1 short) ===
def read_aLh(r):
    b = {}
    b['id'] = r.ri()
    b['name'] = r.rstr()
    b['ehg'] = r.ri()
    b['ehh'] = r.ri()
    b['ehi'] = r.ri()
    b['ehj'] = r.ri()
    b['ehk'] = r.ri()
    b['ehl'] = r.ri()
    b['ehm'] = r.ri()
    b['ehn'] = r.ri()
    b['eho'] = r.ri()
    b['ehp'] = r.ri()
    b['ehq'] = r.ri()
    b['ehr'] = r.ri()
    b['ehs'] = r.ri()
    b['eht'] = r.ri()
    b['ehu'] = r.rba()   # byte[]
    b['ehv'] = r.rfa()   # float[]
    b['ehw'] = r.rsa()   # short[]
    b['ehx'] = r.ria()   # int[]
    b['ehy'] = r.rsa()   # short[]
    b['ehz'] = r.rs()    # short
    return b


def test_reader(name, reader_fn, rows, buf, msz):
    log.info(f"\n=== Test {name} ===")
    rd = BinaryReader(buf, 86, msz)
    ok, errs = 0, 0
    breeds = []
    for row in rows:
        rd.set_pos(row['off']); rd.set_hoo(row['seed'])
        start = rd.get_pos()
        try:
            b = reader_fn(rd)
            consumed = rd.get_pos() - start
            match = consumed == row['sz']
            if match:
                ok += 1
            else:
                if errs < 3:
                    log.warning(f"  WARN {b.get('name','?')}: consumed={consumed} expected={row['sz']} delta={consumed-row['sz']}")
                errs += 1
            breeds.append(b)
        except Exception as e:
            errs += 1
            if errs <= 3:
                log.error(f"  ERR row {row['idx']} id={row['id']}: {e}")
    log.info(f"  Result: {ok} OK, {errs} ERR / {len(rows)}")
    return ok, breeds


def main():
    jar = os.path.join(BDATA_DIR, "86.jar")
    rows, buf, msz = read_header(extract_bin(jar), 86)
    log.info(f"AvatarBreed: {len(rows)} rows, buf={len(buf)}")

    ok_fuI, breeds_fuI = test_reader("fuI", read_fuI, rows, buf, msz)
    ok_aLh, breeds_aLh = test_reader("aLh", read_aLh, rows, buf, msz)

    # Use whichever works better
    if ok_fuI >= ok_aLh:
        breeds = breeds_fuI
        log.info(f"\nUsing fuI ({ok_fuI} OK)")
    else:
        breeds = breeds_aLh
        log.info(f"\nUsing aLh ({ok_aLh} OK)")

    log.info(f"\n{'='*50}")
    log.info(f"BREED MAPPING")
    log.info(f"{'='*50}")
    for b in breeds:
        log.info(f"  id={b.get('id',0):3d} -> {b.get('name','???')}")

    out = os.path.join(OUTPUT_DIR, 'breeds.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(breeds, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"\nSaved: {out}")


if __name__ == '__main__':
    main()
