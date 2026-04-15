"""
Zeigt ALLE Seiten mit dem heutigen Datum-Titel im Space FONTUSIBM
um zu sehen welche Seite gefunden wird und wo sie hängt.
"""
import os, urllib3, requests
from datetime import datetime
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE  = os.environ.get("CONFLUENCE_BASE_URL","https://confluence.local.wmgruppe.de").rstrip("/")
PAT   = os.environ.get("CONFLUENCE_PAT","")
SPACE = os.environ.get("CONFLUENCE_SPACE","FONTUSIBM")
PARENT= os.environ.get("CONFLUENCE_PARENT_PAGE_ID","328092016")

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {PAT}", "Accept": "application/json"})
s.verify = False

title = datetime.now().strftime("%Y-%m-%d")
print(f"Suche nach Titel: '{title}' im Space: {SPACE}\n")

# 1. Suche OHNE ancestors-Filter
resp = s.get(f"{BASE}/rest/api/content", params={
    "spaceKey": SPACE, "title": title,
    "expand": "version,ancestors", "limit": 10,
})
print(f"Ohne ancestors-Filter: {resp.status_code}")
for p in resp.json().get("results", []):
    ancestors = [f"{a['id']} ({a['title']})" for a in p.get("ancestors", [])]
    print(f"  ID={p['id']}  v{p['version']['number']}  ancestors={ancestors}")

# 2. Suche MIT ancestors-Filter (aktueller Code)
resp2 = s.get(f"{BASE}/rest/api/content", params={
    "spaceKey": SPACE, "title": title,
    "ancestors": PARENT, "expand": "version,ancestors", "limit": 10,
})
print(f"\nMit ancestors={PARENT}: {resp2.status_code}")
for p in resp2.json().get("results", []):
    ancestors = [f"{a['id']} ({a['title']})" for a in p.get("ancestors", [])]
    print(f"  ID={p['id']}  v{p['version']['number']}  ancestors={ancestors}")
if not resp2.json().get("results"):
    print("  → Keine Treffer")
