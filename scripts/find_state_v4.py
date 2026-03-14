"""
1. Find java.exe on the system
2. Decompile ewj + top candidates for State reader
3. Identify the State class structure
"""
import os
import sys
import zipfile
import subprocess
import re
import glob

CLIENT_JAR = r"H:\Games\Wakfu\lib\wakfu-client.jar"
CFR_JAR = r"H:\Code\Ankama Dev\wakfu-optimizer\tools\cfr.jar"
STATES_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\decompiled\states"
SCRIPTS_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\scripts"
os.makedirs(STATES_DIR, exist_ok=True)

# ================================================================
# STEP 0: Find java.exe
# ================================================================
print("=" * 70)
print("STEP 0: Locate java.exe")
print("=" * 70)

java_exe = None

# Method 1: Try 'java' directly
try:
    r = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=10)
    if r.returncode == 0 or 'version' in (r.stderr + r.stdout).lower():
        java_exe = 'java'
        print(f"  Found in PATH: java")
        print(f"  Version: {(r.stderr + r.stdout).strip()[:100]}")
except FileNotFoundError:
    print("  'java' not in PATH")

# Method 2: Search common locations
if not java_exe:
    search_patterns = [
        os.path.join("C:", os.sep, "Program Files", "Java", "**", "bin", "java.exe"),
        os.path.join("C:", os.sep, "Program Files", "Eclipse Adoptium", "**", "bin", "java.exe"),
        os.path.join("C:", os.sep, "Program Files", "Microsoft", "**", "bin", "java.exe"),
        os.path.join("C:", os.sep, "Program Files", "OpenJDK", "**", "bin", "java.exe"),
        os.path.join("C:", os.sep, "Program Files", "Zulu", "**", "bin", "java.exe"),
        os.path.join("C:", os.sep, "Program Files", "Amazon Corretto", "**", "bin", "java.exe"),
        os.path.join("H:", os.sep, "Games", "Wakfu", "**", "java.exe"),
    ]
    
    print("\n  Searching for java.exe...")
    for pattern in search_patterns:
        results = glob.glob(pattern, recursive=True)
        for found in results:
            print(f"  Found: {found}")
            if not java_exe:
                java_exe = found

# Method 3: Check JAVA_HOME
if not java_exe:
    jh = os.environ.get('JAVA_HOME', '')
    if jh:
        candidate = os.path.join(jh, 'bin', 'java.exe')
        if os.path.exists(candidate):
            java_exe = candidate
            print(f"  Found via JAVA_HOME: {candidate}")

# Method 4: where command
if not java_exe:
    try:
        r = subprocess.run(['where', 'java'], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            java_exe = r.stdout.strip().split('\n')[0].strip()
            print(f"  Found via 'where': {java_exe}")
    except:
        pass

if not java_exe:
    print("\n  *** JAVA NOT FOUND ***")
    print("  Listing H:\\Games\\Wakfu structure:")
    wakfu_root = os.path.join("H:", os.sep, "Games", "Wakfu")
    for dirpath, dirnames, files in os.walk(wakfu_root):
        depth = dirpath.replace(wakfu_root, "").count(os.sep)
        if depth < 3:
            indent = "  " * (depth + 2)
            print(f"{indent}{os.path.basename(dirpath)}/")
            for fn in sorted(files)[:10]:
                sz = os.path.getsize(os.path.join(dirpath, fn))
                print(f"{indent}  {fn} ({sz:,})")
            if len(files) > 10:
                print(f"{indent}  ... +{len(files)-10} more")
    
    print("\n  *** Please install Java JDK 17+ ***")
    print("  Download: https://adoptium.net/")
    sys.exit(1)

print(f"\n  Using: {java_exe}")

# Verify it works with CFR
try:
    r = subprocess.run([java_exe, '-jar', CFR_JAR, '--help'],
                       capture_output=True, text=True, timeout=10)
    cfr_ok = r.returncode == 0 or 'CFR' in r.stdout + r.stderr
    print(f"  CFR test: {'OK' if cfr_ok else 'FAIL'}")
except Exception as e:
    print(f"  CFR test error: {e}")

def decompile(class_name):
    """Extract and decompile a class from wakfu-client.jar"""
    with zipfile.ZipFile(CLIENT_JAR) as zf:
        cf = f"{class_name}.class"
        if cf not in zf.namelist():
            print(f"    {class_name}.class not in JAR")
            return None
        data = zf.read(cf)
        temp = os.path.join(STATES_DIR, cf)
        with open(temp, 'wb') as f:
            f.write(data)
    
    try:
        result = subprocess.run(
            [java_exe, '-jar', CFR_JAR, temp],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and len(result.stdout) > 50:
            out = os.path.join(STATES_DIR, f"{class_name}.java")
            with open(out, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            return result.stdout
        else:
            print(f"    CFR returned {result.returncode}: {result.stderr[:200]}")
    except Exception as e:
        print(f"    Decompile error: {e}")
    return None

# ================================================================
# STEP 1: Decompile ewj (file enum) to find oyT -> class mapping
# ================================================================
print("\n" + "=" * 70)
print("STEP 1: Decompile ewj (file enum)")
print("=" * 70)

ewj_src = decompile('ewj')
if ewj_src:
    print(f"  ewj.java: {len(ewj_src):,} chars")
    
    lines = ewj_src.split('\n')
    print("\n  Lines containing 'oyT':")
    for i, line in enumerate(lines):
        if 'oyT' in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 4)
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"  {marker} L{j+1}: {lines[j]}")
            print()
    
    print("  Lines containing 'ozF' (effects, for reference):")
    for i, line in enumerate(lines):
        if 'ozF' in line:
            print(f"    L{i+1}: {line.rstrip()}")
    
    print("\n  Lines containing 'ozD' (spells, for reference):")
    for i, line in enumerate(lines):
        if 'ozD' in line:
            print(f"    L{i+1}: {line.rstrip()}")
else:
    print("  Failed to decompile ewj")

# ================================================================
# STEP 2: Decompile top candidates
# ================================================================
print("\n" + "=" * 70)
print("STEP 2: Decompile top candidates")
print("=" * 70)

candidates = ['fwH', 'aOx', 'aMa', 'aMU', 'fxW', 'fvy', 'fwm',
              'aOB', 'aMS', 'aOl', 'aOq', 'aMe', 'fya', 'fwk', 'fxJ']

state_reader = None

for name in candidates:
    src = decompile(name)
    if not src:
        continue
    
    ext_match = re.search(r'extends\s+(\w+)', src)
    extends = ext_match.group(1) if ext_match else "none"
    
    bga_match = re.search(r'bGA\(\)\s*\{[^}]*?return\s+([^;]+);', src, re.DOTALL)
    bga_ret = bga_match.group(1).strip() if bga_match else "?"
    
    alines = src.split('\n')
    in_method = False
    depth = 0
    method = []
    for line in alines:
        if 'public void a(aqH' in line:
            in_method = True
            depth = 0
        if in_method:
            method.append(line)
            depth += line.count('{') - line.count('}')
            if depth <= 0 and len(method) > 1:
                break
    
    is_state = 'oyT' in bga_ret
    marker = " *** STATE READER ***" if is_state else ""
    print(f"\n  {name}: extends={extends}, bGA={bga_ret}, a(aqH)={len(method)} lines{marker}")
    
    if is_state:
        state_reader = (name, method, src, extends, bga_ret)
        print(f"\n  Full a(aqH) method:")
        for line in method:
            print(f"    {line}")
        
        print(f"\n  Fields:")
        for line in src.split('\n'):
            s = line.strip()
            if (s.startswith('protected ') or s.startswith('private ')) and '(' not in s:
                print(f"    {s}")
        break

# If not found, show all bGA returns for manual inspection
if not state_reader:
    print("\n  State reader not found. All bGA returns:")
    for fn in sorted(os.listdir(STATES_DIR)):
        if fn.endswith('.java'):
            fp = os.path.join(STATES_DIR, fn)
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            bga_m = re.search(r'bGA\(\)\s*\{[^}]*?return\s+([^;]+);', content, re.DOTALL)
            bga_v = bga_m.group(1).strip() if bga_m else "not found"
            print(f"    {fn}: bGA -> {bga_v}")

# ================================================================
# STEP 3: Map read sequence if found
# ================================================================
if state_reader:
    print("\n" + "=" * 70)
    print("STEP 3: Map State field structure")
    print("=" * 70)
    
    name, method, src, extends, bga_ret = state_reader
    
    read_map = {
        'bGI': 'readInt',
        'bGH': 'readFloat',
        'bGJ': 'readLong',
        'bGK': 'readShort',
        'bGG': 'readByte',
        'bGL': 'readString',
        'bGM': 'readIntArray',
        'bxv': 'readBool',
        'bxA': 'readFloatArray',
        'bxz': 'readLongArray',
        'bxw': 'readByteArray',
        'bxx': 'readShortArray',
    }
    
    print(f"\nRead sequence for {name}:")
    idx = 0
    for line in method:
        for call, desc in read_map.items():
            if call in line:
                idx += 1
                fm = re.search(r'this\.(\w+)\s*=', line)
                fn = fm.group(1) if fm else "?"
                print(f"  [{idx:2d}] {fn:25s} = {call}() -> {desc}")
    print(f"\n  Total: {idx} read operations")
    
    # ================================================================
    # STEP 4: Validate against file 67
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 4: Validate against file 67 data")
    print("=" * 70)
    
    reader_path = os.path.join(SCRIPTS_DIR, "bdata_reader_final.py")
    spec = {}
    with open(reader_path, 'r', encoding='utf-8') as f:
        exec(f.read(), spec)
    
    BinaryReader = spec['BinaryReader']
    read_header_fn = spec['read_header']
    
    jar_path = os.path.join(r"H:\Games\Wakfu\contents\bdata", "67.jar")
    with zipfile.ZipFile(jar_path) as zf:
        bin_name = [n for n in zf.namelist() if n.endswith('.bin')][0]
        raw67 = zf.read(bin_name)
    
    rows, buf, file_size = read_header_fn(raw67, 67)
    print(f"File 67: {len(rows)} rows, buf={len(buf):,}")
    
    br_map = {
        'bGI': 'ri',
        'bGH': 'rf',
        'bGJ': 'rl',
        'bGK': 'rs',
        'bGG': 'rb',
        'bGL': 'rstr',
        'bGM': 'ria',
        'bxv': 'rbool',
        'bxA': 'rfa',
        'bxz': 'rla',
        'bxw': 'rba',
        'bxx': 'rsa',
    }
    
    read_seq = []
    for line in method:
        for call, desc in read_map.items():
            if call in line:
                fm = re.search(r'this\.(\w+)\s*=', line)
                fn = fm.group(1) if fm else "anon"
                read_seq.append((fn, call))
    
    rd = BinaryReader(buf, 67, file_size)
    
    ok = 0
    err = 0
    for ri in range(min(5, len(rows))):
        r = rows[ri]
        print(f"\n  State {ri}: id={r['id']}, off={r['off']}, sz={r['sz']}, seed={r['seed']}")
        rd.set_pos(r['off'])
        rd.cRa = r['seed']
        
        try:
            for fn, java_call in read_seq:
                py_method = br_map.get(java_call)
                if py_method and hasattr(rd, py_method):
                    val = getattr(rd, py_method)()
                    consumed = rd.pos - r['off']
                    display = val
                    if isinstance(val, (list, tuple)) and len(val) > 5:
                        display = f"[{val[0]}, {val[1]}, ... {len(val)} items]"
                    if isinstance(val, str) and len(val) > 50:
                        display = val[:50] + "..."
                    print(f"    {fn:25s} = {display}  ({consumed}/{r['sz']})")
                else:
                    print(f"    {fn:25s} = ??? (missing {py_method})")
                    break
            
            final = rd.pos - r['off']
            delta = r['sz'] - final
            status = "OK" if delta == 0 else f"WARN delta={delta}"
            print(f"    => {final}/{r['sz']} [{status}]")
            if delta == 0:
                ok += 1
        except Exception as e:
            err += 1
            consumed = rd.pos - r['off']
            print(f"    ERROR at {consumed}/{r['sz']}: {e}")
    
    print(f"\n  Validation: {ok} OK, {err} ERR out of {min(5, len(rows))}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
