"""
Debug: Zeigt den genauen Fehler beim Confluence PUT
Aufruf: python debug_confluence.py
"""
import os, sys, json, urllib3, requests
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL   = os.environ.get("CONFLUENCE_BASE_URL", "https://confluence.local.wmgruppe.de").rstrip("/")
PAT        = os.environ.get("CONFLUENCE_PAT", "")
SPACE      = os.environ.get("CONFLUENCE_SPACE", "FONTUS")
PARENT_ID  = os.environ.get("CONFLUENCE_PARENT_PAGE_ID", "328092016")
SSL_VERIFY = os.environ.get("JIRA_SSL_VERIFY", "false").lower() not in ("false","0","no")

if not PAT:
    print("FEHLER: CONFLUENCE_PAT nicht gesetzt"); sys.exit(1)

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {PAT}", "Accept": "application/json",
                  "Content-Type": "application/json"})
s.verify = SSL_VERIFY

title = datetime.now().strftime("%Y-%m-%d") + "-debug"

# 1. Elternseite prüfen
print(f"1. Prüfe Parent-Seite {PARENT_ID} …")
resp = s.get(f"{BASE_URL}/rest/api/content/{PARENT_ID}", params={"expand": "version,space"})
print(f"   Status: {resp.status_code}")
if resp.ok:
    d = resp.json()
    print(f"   Titel : {d.get('title')}")
    print(f"   Space : {d.get('space',{}).get('key')}")
    print(f"   Version: {d.get('version',{}).get('number')}")
else:
    print(f"   FEHLER: {resp.text[:300]}")

# 2. Testseite anlegen
print(f"\n2. Lege Testseite '{title}' an …")
body = {
    "type":      "page",
    "title":     title,
    "space":     {"key": SPACE},
    "ancestors": [{"id": PARENT_ID}],
    "body":      {"storage": {"value": "<p>Test</p>", "representation": "storage"}},
}
resp = s.post(f"{BASE_URL}/rest/api/content", json=body)
print(f"   Status: {resp.status_code}")
if resp.ok:
    page = resp.json()
    page_id = page["id"]
    version = page["version"]["number"]
    print(f"   Page-ID : {page_id}")
    print(f"   Version : {version}")

    # 3. Sofort updaten
    print(f"\n3. Update Seite (version → {version + 1}) …")
    upd = {
        "version": {"number": version + 1},
        "title":   title,
        "type":    "page",
        "body":    {"storage": {"value": "<p>Updated</p>", "representation": "storage"}},
    }
    resp2 = s.put(f"{BASE_URL}/rest/api/content/{page_id}", json=upd)
    print(f"   Status: {resp2.status_code}")
    if not resp2.ok:
        print(f"   FEHLER: {resp2.text[:500]}")
    else:
        print("   Update OK")

    # 4. Testseite löschen
    s.delete(f"{BASE_URL}/rest/api/content/{page_id}")
    print(f"\n4. Testseite gelöscht")
else:
    print(f"   FEHLER: {resp.text[:500]}")
