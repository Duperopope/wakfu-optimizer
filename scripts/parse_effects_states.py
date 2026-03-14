"""
Parser les Effects (static effects) et States avec le reader corrige.
Etape 1: identifier les file_ids et classes pour effects + states.
Etape 2: parser avec le BinaryReader exact.
"""
import struct, os, sys, json, zipfile, logging

BDATA_DIR = r"H:\Games\Wakfu\contents\bdata"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
WAKFU_JAR = r"H:\Games\Wakfu\lib\wakfu-client.jar"
LOG_FILE = r"H:\Code\Ankama Dev\wakfu-optimizer\logs\parse_effects.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
              logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)


# === BINARY READER (exact copy from bdata_reader_final.py) ===
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


# === STEP 1: Find the file_ids for effects and states ===
log.info("=" * 60)
log.info("STEP 1: Identifier les file_ids pour Effects et States")
log.info("=" * 60)

# From ewj.java we know the enum. Key file_ids from WakBox:
# 66 = Spell (confirmed)
# 86 = AvatarBreed (confirmed)  
# 67 = ? (EffectGroup in old WakBox)
# 29 = ? (State in old WakBox?)
# Let's check what ozD=66(spell), ozE=67, ozX=86(breed)
# and find which classes map to states and effects

# Search for classes returning specific ewj values
log.info("\nSearching for effect/state classes in wakfu-client.jar...")

# Known effect IDs from spells: 174266, 174268, etc.
# These should be in a file where rows have these IDs

# Let's scan several bdata files to find which contains our known effect IDs
target_effects = {174266, 174268, 174270, 178427, 178430, 182653}
log.info(f"Looking for effect IDs: {target_effects}")

bdata_files = sorted([f for f in os.listdir(BDATA_DIR) if f.endswith('.jar')])
log.info(f"Scanning {len(bdata_files)} bdata files...")

found_files = {}
for jar_name in bdata_files:
    fid = int(jar_name.replace('.jar', ''))
    jar_path = os.path.join(BDATA_DIR, jar_name)
    try:
        raw = extract_bin(jar_path)
        rows, buf, msz = read_header(raw, fid)
        row_ids = {r['id'] for r in rows}
        
        matches = target_effects & row_ids
        if matches:
            log.info(f"  FILE {fid}: {len(rows)} rows, MATCHES: {matches}")
            found_files[fid] = {'rows': len(rows), 'matches': matches, 'sample_ids': sorted(row_ids)[:10]}
        
        # Also check for large files that might be effects
        if len(rows) > 10000:
            log.info(f"  FILE {fid}: {len(rows)} rows (large file)")
            
    except Exception as e:
        pass  # Skip files that fail to parse

log.info(f"\nFiles containing target effect IDs: {list(found_files.keys())}")

# === STEP 2: Find the class for effects file ===
log.info(f"\n{'='*60}")
log.info("STEP 2: Find classes for effect files")
log.info("=" * 60)

for fid in found_files:
    # Convert fid to ewj enum name
    # ewj enum starts at oza=36, ozb=37, ...
    # 66 = ozD, 67 = ozE, 86 = ozX
    # Pattern: oz[a-z] = 36-61, oz[A-Z] = 62-87
    if fid >= 36 and fid <= 61:
        enum_name = f"oz{chr(ord('a') + fid - 36)}"
    elif fid >= 62 and fid <= 87:
        enum_name = f"oz{chr(ord('A') + fid - 62)}"
    elif fid >= 88:
        # Would need to check ewj.java for higher values
        enum_name = f"??(id={fid})"
    else:
        enum_name = f"??(id={fid})"
    
    log.info(f"\n  File {fid} -> ewj.{enum_name}")
    
    # Search for classes with this enum reference
    target_bytes = enum_name.encode('utf-8')
    with zipfile.ZipFile(WAKFU_JAR, 'r') as zf:
        for entry in zf.namelist():
            if not entry.endswith('.class') or '$' in entry:
                continue
            data = zf.read(entry)
            if target_bytes in data and b'aqz' in data:
                log.info(f"    Class: {entry} ({len(data)} bytes)")

log.info("\nDONE - check output above for file IDs and classes")
