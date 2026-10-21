"""Shutdown local controller using operator's local token, no third-party access."""
from pathlib import Path
from urllib.request import Request,urlopen
import json
p=Path.home()/'.ripple_antminer_v02'/'api_token.txt'
if not p.is_file():raise SystemExit('No local Ripple controller token file is present')
req=Request('http://127.0.0.1:8877/api/application/shutdown',data=b'',method='POST',
 headers={'Authorization':'Bearer '+p.read_text().strip()})
with urlopen(req,timeout=8) as r:print(json.loads(r.read()))