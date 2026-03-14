import sys, json
sys.path.insert(0, r'H:\Code\Ankama Dev\wakfu-optimizer\scripts')
from local_agent import sentinel_classify
r = sentinel_classify('Write-Host "hello test"')
print(json.dumps(r, indent=2))
