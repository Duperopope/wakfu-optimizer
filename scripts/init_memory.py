import json
from pathlib import Path
P = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
M = P / "MANIFEST.json"
m = json.loads(M.read_text("utf-8"))
a = m.get("allowed_files", [])
for e in ["PROJECT_MEMORY.md","scripts/init_memory.py"]:
    if e not in a:
        a.append(e)
m["allowed_files"] = a
M.write_text(json.dumps(m, ensure_ascii=False, indent=2), "utf-8")
print("MANIFEST OK")
