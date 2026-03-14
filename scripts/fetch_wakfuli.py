import urllib.request, re

url = "https://wakfuli.com/builder/public"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

out = r"H:\Code\Ankama Dev\wakfu-optimizer\reference_wakfuli.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"HTML sauvegarde: {len(html)} caracteres")

scripts = re.findall(r'src="([^"]*\.js[^"]*)"', html)
styles = re.findall(r'href="([^"]*\.css[^"]*)"', html)
print(f"\nScripts JS: {len(scripts)}")
for s in scripts[:10]:
    print(f"  {s}")
print(f"\nStyles CSS: {len(styles)}")
for s in styles[:10]:
    print(f"  {s}")

print(f"\nTitre: {re.findall(r'<title>(.*?)</title>', html)}")
print(f"Meta: {re.findall(r'<meta[^>]*content=[^>]*>', html)[:5]}")
print(f"\nDiv/Section IDs: {re.findall(r'id=\"([^\"]+)\"', html)[:20]}")
print(f"Classes principales: {re.findall(r'class=\"([^\"]{10,60})\"', html)[:20]}")
