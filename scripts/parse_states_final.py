"""
Parse all States from file 67 using aOB structure.
Key discoveries:
  - bGG() = readShort (2 bytes), NOT readByte
  - aTf() = readByte (1 byte, raw/unsigned)
  - bGI() = readInt, bGL() = readString, bGM() = readIntArray, bxv() = readBool
"""
import os
import sys
import struct
import zipfile
import json
import logging
from datetime import datetime

# === Config ===
BDATA_DIR = os.path.join("H:", os.sep, "Games", "Wakfu", "contents", "bdata")
SCRIPTS_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\scripts"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
LOG_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'parse_states.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# === Load BinaryReader ===
reader_path = os.path.join(SCRIPTS_DIR, "bdata_reader_final.py")
spec = {}
with open(reader_path, 'r', encoding='utf-8') as f:
    exec(f.read(), spec)

BinaryReader = spec['BinaryReader']
read_header = spec['read_header']

print("=" * 70)
print(f"Wakfu States Parser (file 67) - {datetime.now()}")
print("=" * 70)

# === Extract file 67 ===
jar_path = os.path.join(BDATA_DIR, "67.jar")
with zipfile.ZipFile(jar_path) as zf:
    bin_name = [n for n in zf.namelist() if n.endswith('.bin')][0]
    raw = zf.read(bin_name)

rows, buf, file_size = read_header(raw, 67)
log.info(f"File 67: {len(rows)} rows, buf={len(buf):,}, file_size={file_size}")

# === State reader: aOB structure ===
# Field mapping from decompiled aOB.java:
#  [1]  o    = bGI()  -> readInt       = id
#  [2]  aWK  = bGG()  -> readShort     = type/category
#  [3]  esI  = bGM()  -> readIntArray  = ?
#  [4]  aNh  = bGM()  -> readIntArray  = duration params [maxLevel, durationMs]
#  [5]  esJ  = bGM()  -> readIntArray  = ? [value, durationMs]
#  [6]  esK  = bxv()  -> readBool
#  [7]  esL  = bxv()  -> readBool
#  [8]  esM  = bxv()  -> readBool
#  [9]  esN  = bxv()  -> readBool
# [10]  esO  = bGL()  -> readString    = gfx/condition string
# [11]  esP  = bGL()  -> readString    = gfx/condition string
# [12]  esQ  = bxv()  -> readBool
# [13]  bfZ  = bxv()  -> readBool
# [14]  esR  = bxv()  -> readBool
# [15]  egL  = bGM()  -> readIntArray  = effectIds (same name as EffectGroup!)
# [16]  esS  = bGM()  -> readIntArray  = ?
# [17]  esT  = bxv()  -> readBool
# [18]  esU  = bxv()  -> readBool
# [19]  esV  = aTf()  -> readByte      = raw byte
# [20]  esW  = aTf()  -> readByte      = raw byte
# [21]  esX  = bxv()  -> readBool
# [22]  esY  = bxv()  -> readBool
# [23]  bds  = bGL()  -> readString    = description/condition
# [24]  esZ  = bxv()  -> readBool
# [25]  atb  = bGG()  -> readShort

def read_state(rd, row):
    """Read one state using aOB structure."""
    rd.set_pos(row['off'])
    rd.cRa = row['seed']
    
    state = {}
    state['id']          = rd.ri()       # [1]  o    = bGI
    state['stateType']   = rd.rs()       # [2]  aWK  = bGG -> readShort!
    state['esI']         = rd.ria()      # [3]  esI  = bGM
    state['durationParams'] = rd.ria()   # [4]  aNh  = bGM
    state['esJ']         = rd.ria()      # [5]  esJ  = bGM
    state['esK']         = rd.rbool()    # [6]
    state['esL']         = rd.rbool()    # [7]
    state['esM']         = rd.rbool()    # [8]
    state['esN']         = rd.rbool()    # [9]
    state['gfxString']   = rd.rstr()     # [10] esO  = bGL
    state['condString']  = rd.rstr()     # [11] esP  = bGL
    state['esQ']         = rd.rbool()    # [12]
    state['bfZ']         = rd.rbool()    # [13]
    state['esR']         = rd.rbool()    # [14]
    state['effectIds']   = rd.ria()      # [15] egL  = bGM
    state['esS']         = rd.ria()      # [16] esS  = bGM
    state['esT']         = rd.rbool()    # [17]
    state['esU']         = rd.rbool()    # [18]
    state['esV']         = rd.rb()       # [19] aTf -> readByte
    state['esW']         = rd.rb()       # [20] aTf -> readByte
    state['esX']         = rd.rbool()    # [21]
    state['esY']         = rd.rbool()    # [22]
    state['description'] = rd.rstr()     # [23] bds  = bGL
    state['esZ']         = rd.rbool()    # [24]
    state['atb']         = rd.rs()       # [25] atb  = bGG -> readShort!
    
    return state

# === Parse all states ===
print("\n>>> Parsing all states <<<")

rd = BinaryReader(buf, 67, file_size)

ok_count = 0
warn_count = 0
err_count = 0
all_states = []

for i, row in enumerate(rows):
    try:
        state = read_state(rd, row)
        
        consumed = rd.pos - row['off']
        delta = row['sz'] - consumed
        
        if delta == 0:
            ok_count += 1
        elif abs(delta) <= 4:
            warn_count += 1
            if warn_count <= 10:
                log.warning(f"Row {i} id={row['id']}: delta={delta} (consumed {consumed}/{row['sz']})")
        else:
            err_count += 1
            if err_count <= 20:
                log.error(f"Row {i} id={row['id']}: delta={delta} (consumed {consumed}/{row['sz']})")
        
        all_states.append(state)
        
    except Exception as e:
        err_count += 1
        if err_count <= 20:
            consumed = rd.pos - row['off']
            log.error(f"Row {i} id={row['id']}: {e} (at {consumed}/{row['sz']})")

log.info(f"\nParse results: {ok_count} OK, {warn_count} WARN, {err_count} ERR / {len(rows)}")

# === Show sample states ===
print("\n>>> Sample parsed states <<<")
for s in all_states[:5]:
    print(f"\n  State {s['id']} (type={s['stateType']}):")
    print(f"    durationParams = {s['durationParams']}")
    print(f"    effectIds      = {s['effectIds']}")
    print(f"    gfxString      = {s['gfxString'][:80]}{'...' if len(s['gfxString'])>80 else ''}")
    print(f"    condString     = {s['condString'][:80]}{'...' if len(s['condString'])>80 else ''}")
    print(f"    description    = {s['description'][:80]}{'...' if len(s['description'])>80 else ''}")

# === Save if success rate > 90% ===
success = ok_count + warn_count
total = len(rows)
rate = success / total * 100 if total > 0 else 0

if rate > 90:
    out_path = os.path.join(OUTPUT_DIR, "all_states.json")
    
    # Convert bytes/bytearray for JSON
    def jsonify(obj):
        if isinstance(obj, (bytes, bytearray)):
            return list(obj)
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [jsonify(x) for x in obj]
        return obj
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(jsonify(all_states), f, ensure_ascii=False)
    
    sz = os.path.getsize(out_path)
    log.info(f"\nSaved {len(all_states)} states -> {out_path} ({sz/1024/1024:.1f} MB)")
    
    # === Check known Sram states ===
    print("\n>>> Known Sram state IDs <<<")
    sram_ids = [3114, 3129, 3136, 2956, 1579]
    state_map = {s['id']: s for s in all_states}
    
    for sid in sram_ids:
        if sid in state_map:
            s = state_map[sid]
            print(f"\n  State {sid} (type={s['stateType']}):")
            print(f"    effectIds    = {s['effectIds']}")
            print(f"    durationParams = {s['durationParams']}")
            print(f"    gfxString    = {s['gfxString'][:100]}")
            print(f"    condString   = {s['condString'][:100]}")
            print(f"    description  = {s['description'][:100]}")
            print(f"    bools: esK={s['esK']} esL={s['esL']} esM={s['esM']} esN={s['esN']}")
        else:
            print(f"\n  State {sid}: NOT FOUND")
    
    # === Statistics ===
    print("\n>>> State statistics <<<")
    types = {}
    has_effects = 0
    has_gfx = 0
    has_cond = 0
    has_desc = 0
    
    for s in all_states:
        t = s['stateType']
        types[t] = types.get(t, 0) + 1
        if s['effectIds']:
            has_effects += 1
        if s['gfxString']:
            has_gfx += 1
        if s['condString']:
            has_cond += 1
        if s['description']:
            has_desc += 1
    
    print(f"  Total states: {len(all_states)}")
    print(f"  With effectIds: {has_effects}")
    print(f"  With gfxString: {has_gfx}")
    print(f"  With condString: {has_cond}")
    print(f"  With description: {has_desc}")
    print(f"\n  State types distribution (top 10):")
    for t, count in sorted(types.items(), key=lambda x: -x[1])[:10]:
        print(f"    type {t}: {count} states")
else:
    log.error(f"\nSuccess rate too low ({rate:.1f}%). Not saving.")
    log.error(f"Check the first errors above and fix the reader.")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
