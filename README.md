# Jira CompStage & Story Analyse

Holt alle **CompStages** aus Jira (gefiltert nach Feature Teams) und listet die zugehörigen **Stories** darunter auf.  
Ergebnis wird in eine **Excel-Datei** und eine **SQLite-Datenbank** exportiert.

---

## Voraussetzungen

- Python 3.11+
- Zugang zu `https://jira.local.wmgruppe.de` (VPN falls nötig)
- Jira Personal Access Token (PAT)

---

## Einrichtung

```bash
# 1. Virtuelle Umgebung erstellen
python -m venv .venv

# 2. Aktivieren
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Konfiguration anlegen
cp .env.template .env
# → .env öffnen und JIRA_PAT eintragen
```

---

## Konfiguration (`.env`)

| Variable                  | Beschreibung                              | Default                        |
|---------------------------|-------------------------------------------|--------------------------------|
| `JIRA_BASE_URL`           | Jira-Server URL                           | https://jira.local.wmgruppe.de |
| `JIRA_PAT`                | Personal Access Token (**Pflicht**)       | –                              |
| `JIRA_PROJECT`            | Jira-Projektschlüssel                     | `FONTUS`                       |
| `JIRA_FEATURE_TEAM_FIELD` | Custom Field ID für Feature Team          | `customfield_11101`            |
| `JIRA_SSL_VERIFY`         | SSL-Zertifikat prüfen (`true`/`false`)    | `false`                        |
| `JIRA_DB_PATH`            | Pfad zur SQLite-Datei                     | `fontus_CS_analysis.db`        |
| `OUTPUT_EXCEL`            | Pfad zur Excel-Ausgabedatei               | `compstage_story_analysis.xlsx`|

---

## Ausführen

```bash
python jira_compstage_analysis.py
```

**Ausgabe:**
- `compstage_story_analysis.xlsx` – Excel mit CompStages (fett) und Stories (eingerückt)
- `fontus_CS_analysis.db` – SQLite-Datenbank

---

## Story-Verknüpfung (4-Pfad-Strategie)

Da der Linktyp in Jira nicht immer stringent als `is parent` deklariert wird, sucht das Script über vier Wege:

1. `issuelinks` – alle Linktypen, beide Richtungen
2. `subtasks` – klassische Jira-Unteraufgaben
3. JQL `parent = "CS-KEY"` – Next-Gen / hierarchische Projekte
4. JQL `linkedIssues("CS-KEY")` – Rückverlinkungen über beliebige Linktypen

---

## Datenbankschema (SQLite)

```sql
-- CompStages
SELECT * FROM compstages;

-- Stories mit zugehöriger CompStage
SELECT cs.team_mapped, cs.key AS compstage, cs.status AS cs_status,
       s.key AS story, s.summary, s.status
FROM compstages cs
LEFT JOIN stories s ON s.parent_key = cs.key
ORDER BY cs.team_mapped, cs.key, s.key;
```

---

## Feature Teams

| Org-Team        | Aggregierter Name   |
|-----------------|---------------------|
| DL-01 / DL-02 / DL-GenAI / DLH / DLH Source / DL-Output | **DLH** |
| UI&S / User Interfaces | **User Interfaces** |
| T2-Team / Rule Engine  | **Rule Engine**     |
| Rule Validation        | **Rule Validation** |
