"""
Minimaler POST-Test mit einem eindeutigen Titel (kein Konflikt möglich)
"""
import os, urllib3, requests, json
from datetime import datetime
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE   = os.environ.get("CONFLUENCE_BASE_URL","").rstrip("/")
PAT    = os.environ.get("CONFLUENCE_PAT","")
SPACE  = os.environ.get("CONFLUENCE_SPACE","")
PARENT = os.environ.get("CONFLUENCE_PARENT_PAGE_ID","")

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {PAT}", "Accept": "application/json",
                  "Content-Type": "application/json"})
s.verify = False

# Eindeutiger Titel – kann unmöglich kollidieren
title = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

print(f"POST nach {BASE}/rest/api/content")
print(f"  Space : {SPACE}")
print(f"  Parent: {PARENT}")
print(f"  Titel : {title}\n")

body = {
    "type":      "page",
    "title":     title,
    "space":     {"key": SPACE},
    "ancestors": [{"id": PARENT}],
    "body":      {"storage": {"value": "<p>Test</p>", "representation": "storage"}},
}
resp = s.post(f"{BASE}/rest/api/content", json=body)
print(f"Status: {resp.status_code}")
print(f"Response:\n{json.dumps(resp.json(), indent=2)[:1500]}")

if resp.ok:
    page_id = resp.json()["id"]
    print(f"\nSeite erstellt: ID={page_id}")
    # aufräumen
    s.delete(f"{BASE}/rest/api/content/{page_id}")
    print("Seite wieder gelöscht.")
