"""Download the seven required SFX from their original provider; never redistribute them."""
from pathlib import Path
import hashlib, json, urllib.request
ROOT = Path(__file__).resolve().parents[1]
for item in json.loads((ROOT / 'assets-manifest.json').read_text(encoding='utf-8')):
    dest = ROOT / item['path']
    if dest.exists():
        if hashlib.sha256(dest.read_bytes()).hexdigest() != item['sha256']:
            raise SystemExit(f'Existing asset differs; preserve it and inspect manually: {dest}')
        print('OK', item['path'])
        continue
    request = urllib.request.Request(item['url'], headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit(f'Provider asset changed: {item["path"]}; no file written')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as target:
        target.write(data)
    print('Downloaded', item['path'])
