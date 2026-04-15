"""
Debug-Script: Zeigt die rohen issuelinks einer Story
um zu prüfen wie Defects tatsächlich verlinkt sind.
Aufruf: python debug_defects.py FONTUS-12345
"""
import os, sys, json, urllib3, requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "https://jira.local.wmgruppe.de").rstrip("/")
JIRA_PAT      = os.environ.get("JIRA_PAT", "")

if not JIRA_PAT:
    print("FEHLER: JIRA_PAT nicht gesetzt"); sys.exit(1)

if len(sys.argv) < 2:
    print("Aufruf: python debug_defects.py FONTUS-XXXXX"); sys.exit(1)

key = sys.argv[1]

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {JIRA_PAT}", "Accept": "application/json"})
session.verify = False

resp = session.get(f"{JIRA_BASE_URL}/rest/api/2/issue/{key}",
                   params={"fields": "issuelinks,summary,issuetype"})
resp.raise_for_status()
data = resp.json()

links = data.get("fields", {}).get("issuelinks", [])
print(f"\n{key} – {data['fields']['summary']}")
print(f"Anzahl issuelinks: {len(links)}\n")

for i, link in enumerate(links):
    lt = link.get("type", {})
    print(f"Link {i+1}: type='{lt.get('name')}' "
          f"inward='{lt.get('inward')}' outward='{lt.get('outward')}'")
    for direction in ("outwardIssue", "inwardIssue"):
        linked = link.get(direction)
        if linked:
            fields = linked.get("fields", {})
            it     = fields.get("issuetype", {})
            status = fields.get("status", {})
            print(f"  [{direction}] key={linked.get('key')}  "
                  f"issuetype={it.get('name')!r}  "
                  f"status={status.get('name')!r}")
            # Rohe Felder zeigen falls issuetype fehlt
            if not it.get('name'):
                print(f"    RAW fields: {json.dumps(fields, indent=4)}")
