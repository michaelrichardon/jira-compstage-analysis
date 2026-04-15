"""
Debug: Prüft Konsistenz einer spezifischen CompStage
Aufruf: python debug_cs_consistency.py FONTUS-27222
"""
import os, sys, urllib3, requests
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JIRA_BASE_URL      = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
JIRA_PAT           = os.environ.get("JIRA_PAT", "")
FEATURE_TEAM_FIELD = os.environ.get("JIRA_FEATURE_TEAM_FIELD", "customfield_11101")

if not JIRA_PAT or len(sys.argv) < 2:
    print("Aufruf: python debug_cs_consistency.py FONTUS-XXXXX"); sys.exit(1)

cs_key = sys.argv[1]

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {JIRA_PAT}", "Accept": "application/json"})
session.verify = False

STORY_STATUS_MAP = {
    "To Do": 1, "In Specification": 1, "Ready for Estimation": 1,
    "Reopened": 1, "Ready for Development": 1, "In Progress": 1,
    "In Review": 1, "Ready For Deployment": 1,
    "Ready for Test": 2, "In Test": 2,
    "Done": 3, "Closed": 3,
    "Deprecated": 999, "Pending": 0, "Rejected": 0,
}
CS_STATUS_MAP = {
    "To Do": 1, "In Review": 1, "In Specification": 1, "Ready for Design": 1,
    "In Design": 1, "In Test Creation": 1, "Ready for Development": 1, "In Progress": 1,
    "Ready for CompTest": 2, "In CompTest": 2,
    "Ready for INT": 3, "In INT": 3, "INT Tested": 3, "In UAT": 3, "UAT Tested": 3,
    "Closed": 99, "Pending": 999, "Rejected": 999,
}
CS_MIN_STORY_KAT = {1: 1, 2: 2, 3: 3, 99: 3, 999: None}

def get(key, fields):
    r = session.get(f"{JIRA_BASE_URL}/rest/api/2/issue/{key}",
                    params={"fields": ",".join(fields)})
    r.raise_for_status()
    return r.json()

def jql(q, fields):
    r = session.get(f"{JIRA_BASE_URL}/rest/api/2/search",
                    params={"jql": q, "fields": ",".join(fields), "maxResults": 100})
    r.raise_for_status()
    return r.json().get("issues", [])

# CS laden
cs = get(cs_key, ["summary", "status", "issuelinks", "subtasks", "labels"])
cs_status = cs["fields"]["status"]["name"]
cs_ki     = CS_STATUS_MAP.get(cs_status, 999)
min_st_ki = CS_MIN_STORY_KAT.get(cs_ki)
labels    = cs["fields"].get("labels", [])

print(f"\nCS: {cs_key} – {cs['fields']['summary']}")
print(f"    Status={cs_status!r}  Kat-Index={cs_ki}  Min-Story-Kat={min_st_ki}")
print(f"    Labels={labels}")
print(f"    Not-Testable={'Not-Testable' in labels}")

# Stories sammeln
found = {}
for link in cs["fields"].get("issuelinks", []):
    for d in ("outwardIssue", "inwardIssue"):
        li = link.get(d)
        if li:
            it = li.get("fields", {}).get("issuetype", {}).get("name", "")
            if it == "Story":
                found[li["key"]] = li
for sub in cs["fields"].get("subtasks", []):
    if sub.get("fields", {}).get("issuetype", {}).get("name") == "Story":
        found[sub["key"]] = sub
try:
    for ci in jql(f'parent = "{cs_key}" AND issuetype = Story', ["summary","status","labels"]):
        found[ci["key"]] = ci
except Exception as e:
    print(f"  JQL parent skip: {e}")

print(f"\n  {len(found)} Stories gefunden:\n")
bad_keys = []
for key in sorted(found):
    st = get(key, ["summary", "status", "labels"])
    st_status = st["fields"]["status"]["name"]
    st_ki     = STORY_STATUS_MAP.get(st_status, 999)
    st_labels = st["fields"].get("labels", [])
    not_test  = "Not-Testable" in st_labels
    ignored   = not_test or st_ki in (0, 999)
    bad       = (not ignored) and min_st_ki is not None and st_ki < min_st_ki
    if bad:
        bad_keys.append(key)
    marker = "❌ INKONSISTENT" if bad else ("⏭  ignoriert" if ignored else "✓")
    print(f"  {key:20s} Status={st_status!r:25s} Kat={st_ki}  NotTest={not_test}  {marker}")

print(f"\n→ CS inkonsistent: {'JA – X' if bad_keys else 'NEIN'}")
if bad_keys:
    print(f"  Verursacher: {bad_keys}")
