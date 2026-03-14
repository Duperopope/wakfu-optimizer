"""
decompile_client.py - Decompiler le client Wakfu automatiquement
================================================================
1. Trouver Java (installe avec Wakfu ou systeme)
2. Telecharger CFR (decompilateur Java open-source)
3. Decompiler les classes cles du wakfu-client.jar
4. Sauvegarder le code source Java lisible
"""

import os
import sys
import subprocess
import zipfile
import urllib.request
import shutil

WAKFU_ROOT = r"H:\Games\Wakfu"
CLIENT_JAR = os.path.join(WAKFU_ROOT, "lib", "wakfu-client.jar")
TOOLS_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\tools"
OUTPUT_DIR = r"H:\Code\Ankama Dev\wakfu-optimizer\decompiled"
os.makedirs(TOOLS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Classes cibles (celles qui contiennent hoo, seed, binaryData)
TARGET_CLASSES = [
    "aUA", "aUC", "cCJ", "cCI",  # hoo/seed/binaryData
]

print("=" * 60)
print("ETAPE 1: Trouver Java")
print("=" * 60)

# Chercher java.exe dans plusieurs endroits
java_candidates = []

# 1. Wakfu embarque souvent son propre JRE
for root, dirs, files in os.walk(WAKFU_ROOT):
    for f in files:
        if f == "java.exe":
            java_candidates.append(os.path.join(root, f))
    # Ne pas descendre trop profond
    if root.count(os.sep) - WAKFU_ROOT.count(os.sep) > 4:
        dirs.clear()

# 2. JAVA_HOME
java_home = os.environ.get("JAVA_HOME", "")
if java_home:
    jh = os.path.join(java_home, "bin", "java.exe")
    if os.path.exists(jh):
        java_candidates.append(jh)

# 3. PATH
for p in os.environ.get("PATH", "").split(";"):
    jp = os.path.join(p, "java.exe")
    if os.path.exists(jp):
        java_candidates.append(jp)

# 4. Emplacements classiques Windows
for d in [r"C:\Program Files\Java", r"C:\Program Files (x86)\Java",
          r"C:\Program Files\Eclipse Adoptium", r"C:\Program Files\Zulu"]:
    if os.path.exists(d):
        for sub in os.listdir(d):
            jp = os.path.join(d, sub, "bin", "java.exe")
            if os.path.exists(jp):
                java_candidates.append(jp)

# Deduplicate
java_candidates = list(dict.fromkeys(java_candidates))

print(f"Trouve {len(java_candidates)} java.exe:")
java_exe = None
for jc in java_candidates:
    print(f"  {jc}")
    if java_exe is None:
        java_exe = jc

if not java_exe:
    print("\nJava non trouve! On va utiliser une approche Python pure.")
    print("Installation de pyjadx ou utilisation de krakatau...")
else:
    # Tester la version
    try:
        result = subprocess.run([java_exe, "-version"], capture_output=True, text=True, timeout=10)
        version_output = result.stderr or result.stdout
        print(f"\nJava version: {version_output.strip()}")
    except Exception as e:
        print(f"Erreur test java: {e}")

print("\n" + "=" * 60)
print("ETAPE 2: Obtenir le decompilateur")
print("=" * 60)

cfr_path = os.path.join(TOOLS_DIR, "cfr.jar")

if not os.path.exists(cfr_path):
    # Telecharger CFR depuis GitHub
    cfr_url = "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"
    print(f"Telechargement de CFR depuis {cfr_url}")
    try:
        urllib.request.urlretrieve(cfr_url, cfr_path)
        print(f"CFR telecharge: {cfr_path} ({os.path.getsize(cfr_path)} bytes)")
    except Exception as e:
        print(f"Erreur telechargement: {e}")
        print("Essai URL alternative...")
        try:
            cfr_url2 = "https://github.com/leibnitz27/cfr/releases/latest/download/cfr.jar"
            urllib.request.urlretrieve(cfr_url2, cfr_path)
            print(f"CFR telecharge (alt): {cfr_path} ({os.path.getsize(cfr_path)} bytes)")
        except Exception as e2:
            print(f"Echec telechargement: {e2}")
else:
    print(f"CFR deja present: {cfr_path} ({os.path.getsize(cfr_path)} bytes)")

print("\n" + "=" * 60)
print("ETAPE 3: Extraire les classes cibles du JAR")
print("=" * 60)

extracted_dir = os.path.join(TOOLS_DIR, "extracted_classes")
os.makedirs(extracted_dir, exist_ok=True)

# Extraire les classes cibles + toutes celles qui contiennent hoo/seed
extracted_files = []
with zipfile.ZipFile(CLIENT_JAR, 'r') as zf:
    all_entries = zf.namelist()
    print(f"wakfu-client.jar contient {len(all_entries)} entrees")
    
    # Compter les .class
    class_count = sum(1 for e in all_entries if e.endswith('.class'))
    print(f"Dont {class_count} fichiers .class")
    
    for entry in all_entries:
        if not entry.endswith('.class'):
            continue
        
        short = entry.replace('.class', '').replace('/', '.')
        base = short.split('.')[-1]
        
        # Extraire les classes cibles
        should_extract = False
        for target in TARGET_CLASSES:
            if base == target:
                should_extract = True
                break
        
        if should_extract:
            # Extraire le fichier
            out_path = os.path.join(extracted_dir, entry)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(zf.read(entry))
            extracted_files.append((entry, out_path))
            print(f"  Extrait: {entry}")

    # Aussi extraire les classes liees (inner classes, etc.)
    for entry in all_entries:
        if not entry.endswith('.class'):
            continue
        base = entry.replace('.class', '').split('/')[-1]
        for target in TARGET_CLASSES:
            if base.startswith(target + "$") or base.startswith(target + "."):
                out_path = os.path.join(extracted_dir, entry)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, 'wb') as f:
                    f.write(zf.read(entry))
                extracted_files.append((entry, out_path))
                print(f"  Extrait (inner): {entry}")
                break

print(f"\nTotal extrait: {len(extracted_files)} classes")

print("\n" + "=" * 60)
print("ETAPE 4: Decompiler")
print("=" * 60)

if java_exe and os.path.exists(cfr_path):
    # Decompiler avec CFR
    for entry, class_path in extracted_files:
        base_name = entry.replace('.class', '').replace('/', '_')
        output_file = os.path.join(OUTPUT_DIR, base_name + ".java")
        
        cmd = [java_exe, "-jar", cfr_path, class_path, "--outputdir", OUTPUT_DIR]
        print(f"Decompilation: {entry}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"  OK -> {OUTPUT_DIR}")
            else:
                print(f"  Erreur: {result.stderr[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Lister les fichiers decompiles
    print(f"\nFichiers decompiles dans {OUTPUT_DIR}:")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            if f.endswith('.java'):
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                print(f"  {os.path.relpath(full, OUTPUT_DIR)} ({size} bytes)")
else:
    print("Java ou CFR non disponible.")
    print("ALTERNATIVE: Decompilation Python pure avec bytecode parsing")
    print("")
    
    # Approche alternative: lire le bytecode directement avec Python
    # On peut extraire les constantes et la structure sans decompilateur externe
    print("Extraction des constantes et structure depuis le bytecode...")
    
    for entry, class_path in extracted_files:
        print(f"\n{'='*40}")
        print(f"CLASS: {entry}")
        print(f"{'='*40}")
        
        with open(class_path, 'rb') as f:
            data = f.read()
        
        print(f"Taille: {len(data)} bytes")
        
        # Magic number verification
        if data[:4] != b'\xCA\xFE\xBA\xBE':
            print("  Pas un fichier .class valide!")
            continue
        
        import struct
        minor = struct.unpack('>H', data[4:6])[0]
        major = struct.unpack('>H', data[6:8])[0]
        print(f"Version: {major}.{minor} (Java {major - 44})")
        
        # Constant pool count
        cp_count = struct.unpack('>H', data[8:10])[0]
        print(f"Constant pool: {cp_count} entries")
        
        # Extraire les strings UTF8 du constant pool
        # (contient les noms de methodes, champs, strings literales)
        pos = 10
        strings_found = []
        for idx in range(1, cp_count):
            if pos >= len(data):
                break
            tag = data[pos]
            pos += 1
            
            if tag == 1:  # CONSTANT_Utf8
                slen = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2
                try:
                    s = data[pos:pos+slen].decode('utf-8', errors='replace')
                    strings_found.append(s)
                except:
                    pass
                pos += slen
            elif tag == 3:  # CONSTANT_Integer
                pos += 4
            elif tag == 4:  # CONSTANT_Float
                pos += 4
            elif tag == 5:  # CONSTANT_Long
                pos += 8
                idx += 1  # longs prennent 2 slots
            elif tag == 6:  # CONSTANT_Double
                pos += 8
                idx += 1
            elif tag == 7:  # CONSTANT_Class
                pos += 2
            elif tag == 8:  # CONSTANT_String
                pos += 2
            elif tag == 9:  # CONSTANT_Fieldref
                pos += 4
            elif tag == 10:  # CONSTANT_Methodref
                pos += 4
            elif tag == 11:  # CONSTANT_InterfaceMethodref
                pos += 4
            elif tag == 12:  # CONSTANT_NameAndType
                pos += 4
            elif tag == 15:  # CONSTANT_MethodHandle
                pos += 3
            elif tag == 16:  # CONSTANT_MethodType
                pos += 2
            elif tag == 17:  # CONSTANT_Dynamic
                pos += 4
            elif tag == 18:  # CONSTANT_InvokeDynamic
                pos += 4
            elif tag == 19:  # CONSTANT_Module
                pos += 2
            elif tag == 20:  # CONSTANT_Package
                pos += 2
            else:
                print(f"  Tag inconnu: {tag} a pos={pos-1}")
                break
        
        # Filtrer les strings interessantes
        keywords = ['hoo', 'seed', 'offset', 'size', 'binary', 'spell', 'breed',
                    'effect', 'property', 'read', 'write', 'buffer', 'position',
                    'storage', 'data', 'array', 'string', 'int', 'float', 'byte',
                    'short', 'long', 'bool', 'passive', 'cast', 'target', 'range',
                    'criteria', 'level', 'element', 'gfx', 'script']
        
        print(f"\nStrings pertinentes ({len(strings_found)} total):")
        relevant = []
        for s in strings_found:
            s_lower = s.lower()
            for kw in keywords:
                if kw in s_lower and len(s) < 200:
                    relevant.append(s)
                    break
        
        # Aussi garder les noms de methodes/champs courts
        for s in strings_found:
            if len(s) < 50 and s not in relevant:
                if any(c.isupper() for c in s) and any(c.islower() for c in s):
                    relevant.append(s)
        
        for s in sorted(set(relevant)):
            print(f"  '{s}'")

print("\n" + "=" * 60)
print("ETAPE 5: Afficher le code decompile des classes cles")
print("=" * 60)

# Chercher et afficher les fichiers .java generes
java_files = []
for root, dirs, files in os.walk(OUTPUT_DIR):
    for f in files:
        if f.endswith('.java'):
            java_files.append(os.path.join(root, f))

if java_files:
    for jf in java_files:
        print(f"\n{'#'*60}")
        print(f"# {os.path.basename(jf)}")
        print(f"{'#'*60}")
        with open(jf, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        print(content[:5000])  # Premiers 5000 chars
        if len(content) > 5000:
            print(f"\n... [tronque, {len(content)} chars total]")
else:
    print("Pas de fichiers .java generes.")
    print("Les constantes extraites ci-dessus donnent deja des indices precieux.")

print("\n" + "=" * 60)
print("TERMINE")
print("=" * 60)
