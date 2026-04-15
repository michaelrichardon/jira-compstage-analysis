# Jira CompStage & Story Analyse

Analysiert CompStages und zugehörige Stories aus Jira FONTUS, ergänzt sie mit
Release- und Bug-Informationen und exportiert das Ergebnis in Excel, SQLite und Confluence.

---

## Projektstruktur

```
JiraCompStage analysis/
├── jira_compstage_analysis.py   ← Hauptscript
├── requirements.txt              ← Python-Abhängigkeiten
├── .env                          ← Konfiguration (nicht ins Git!)
├── .env.template                 ← Vorlage für .env
├── .gitignore
├── README.md
├── debug_defects.py              ← Debug: Defect-Links einer Story prüfen
├── debug_confluence.py           ← Debug: Confluence Verbindung testen
├── debug_confluence2.py          ← Debug: Confluence Seiten-Suche prüfen
├── debug_confluence3.py          ← Debug: Confluence POST testen
├── debug_env.py                  ← Debug: Umgebungsvariablen prüfen
└── Ergebnisdateien/              ← Excel-Ausgaben (automatisch angelegt)
    └── compstage_story_analysis_YYYYMMDD_HHMMSS.xlsx
```

---

## Einrichtung

```bash
# 1. Virtuelle Umgebung erstellen und aktivieren
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Konfiguration anlegen
copy .env.template .env
# → .env öffnen und Zugangsdaten eintragen
```

---

## Konfiguration (.env)

| Variable | Beschreibung | Default |
|---|---|---|
| `JIRA_BASE_URL` | Jira-Server URL | `https://jira.local.wmgruppe.de` |
| `JIRA_PAT` | Personal Access Token (**Pflicht**) | – |
| `JIRA_PROJECT` | Jira-Projektschlüssel | `FONTUS` |
| `JIRA_FEATURE_TEAM_FIELD` | Custom Field ID Feature Team | `customfield_11101` |
| `JIRA_SSL_VERIFY` | SSL-Zertifikat prüfen | `false` |
| `JIRA_DB_PATH` | Pfad zur SQLite-Datei | `fontus_CS_analysis.db` |
| `OUTPUT_DIR` | Ausgabeverzeichnis für Excel | `C:\Projekte\JiraCompStage analysis\Ergebnisdateien` |
| `OUTPUT_EXCEL` | Vollständiger Excel-Pfad (überschreibt OUTPUT_DIR) | – |
| `CONFLUENCE_BASE_URL` | Confluence-Server URL | `https://confluence.local.wmgruppe.de` |
| `CONFLUENCE_PAT` | Confluence Personal Access Token | – |
| `CONFLUENCE_SPACE` | Confluence Space-Key | `FONTUSIBM` |
| `CONFLUENCE_PARENT_PAGE_ID` | ID der übergeordneten Confluence-Seite | `328092016` |
| `TRACKING_SHEET_URL` | URL des Tracking-Excel auf Confluence | siehe .env.template |

---

## Ausführen

```bash
python jira_compstage_analysis.py
```

### Ablauf

```
1. Tracking-Sheet von Confluence laden (Release-Mapping)
2. CompStages per JQL aus Jira holen (gefiltert nach Feature Teams)
3. Je CompStage: Stories ermitteln (4-Pfad-Strategie)
4. Je Story: Bugs zählen (offen / gesamt)
5. Konsistenzprüfung CS ↔ Stories
6. Excel schreiben → Ergebnisdateien\compstage_story_analysis_YYYYMMDD_HHMMSS.xlsx
7. SQLite aktualisieren (Delta-Modus)
8. Confluence-Seite YYYY-MM-DD anlegen / aktualisieren
```

---

## Excel-Ausgabe

Jede Zeile ist entweder eine **CompStage** (fett, blau) oder eine **Story** (eingerückt, weiß).

| Spalte | Beschreibung | CS | Story |
|---|---|---|---|
| Team Mapping | Aggregierter Teamname | ✓ | – |
| Key | Jira-Key (Hyperlink) | ✓ | ✓ |
| Zusammenfassung | Issue-Titel | ✓ | ✓ |
| Functional Release | `customfield_11313` | ✓ | – |
| Release | Release-Label aus Jira (`R3.x`) | ✓ | ✓ |
| Tracking Release | Release aus R3x_OverallTrackingSheet | ✓ | – |
| Not-Testable | Label `Not-Testable` gesetzt | ✓ | ✓ |
| Bugs offen | Verlinkte Bugs mit Status ≠ Done/Closed/Rejected | – | ✓ |
| Bugs gesamt | Alle verlinkten Bugs | – | ✓ |
| Story Inkonsistent | Done/Closed aber offene Bugs | – | ✓ |
| CS Inkonsistent | CS-Status passt nicht zu Story-Status | ✓ | ✓ |
| Status | Jira-Status | ✓ | ✓ |

### Farbkodierung

| Farbe | Bedeutung |
|---|---|
| Blau (Zeile) | CompStage |
| Weiß (Zeile) | Story |
| Rot (Zelle) | Inkonsistenz / Not-Testable |
| Orange (Zelle) | Offene Bugs / Story verursacht CS-Inkonsistenz |
| Rot (Tracking Release) | Abweichung zwischen Release-Label und Tracking-Sheet |

---

## Konsistenzprüfung CS ↔ Stories

Eine CompStage gilt als **inkonsistent** wenn ihr Kat-Index höher ist als der
minimale Kat-Index der zugehörigen Stories.

| CS Kategorie | CS Kat-Index | Mindest-Story-Kat |
|---|---|---|
| DEV | 1 | 1 (DEV oder höher) |
| K-Test | 2 | 2 (TEST oder höher) |
| INT / UAT | 3 | 3 (CLOSED) |
| CLOSED | 99 | 3 (CLOSED) |
| Ignore (Rejected, Pending) | 999 | nicht geprüft |

**Ignoriert:** Stories mit Label `Not-Testable`, Stories mit Status `Pending`, `Rejected` oder `Deprecated`.

Die **verursachenden Stories** werden in der Spalte `CS Inkonsistent` mit einem kleinen `x` (orange) markiert.

---

## Feature Teams & Mapping

| Org-Team | Aggregierter Name |
|---|---|
| DL-01, DL-02, DL-GenAI, DLH, DLH Source, DL-Output | **DLH** |
| UI&S, User Interfaces | **User Interfaces** |
| T2-Team, Rule Engine | **Rule Engine** |
| Rule Validation | **Rule Validation** |

---

## Story-Suche (3-Pfad-Strategie)

Da der Linktyp zwischen CompStage und Story nicht immer stringent als `is parent` deklariert wird:

1. `issuelinks` — alle Linktypen, beide Richtungen
2. `subtasks` — klassische Jira-Unteraufgaben
3. JQL `parent = "CS-KEY"` — Next-Gen / hierarchische Projekte

---

## SQLite-Datenbank

Datei: `fontus_CS_analysis.db`

### Tabellen

```sql
-- CompStages
SELECT * FROM compstages;

-- Stories
SELECT * FROM stories;

-- n:m Verknüpfung
SELECT * FROM compstage_stories;

-- Änderungshistorie
SELECT * FROM delta_log ORDER BY run_at DESC;
```

### Nützliche Abfragen

```sql
-- Alle inkonsistenten CompStages
SELECT key, team_mapped, status FROM compstages WHERE cs_inconsistent = 'X';

-- Stories mit offenen Bugs die bereits closed sind
SELECT key, summary, status, defects_open FROM stories WHERE inconsistent = 'X';

-- Stories einer CompStage
SELECT s.key, s.summary, s.status
FROM stories s
JOIN compstage_stories cs ON cs.story_key = s.key
WHERE cs.compstage_key = 'FONTUS-123';

-- Stories die an mehreren CompStages hängen
SELECT story_key, COUNT(*) AS anzahl
FROM compstage_stories
GROUP BY story_key HAVING anzahl > 1;

-- Was hat sich beim letzten Run geändert?
SELECT issue_key, field, old_value, new_value
FROM delta_log
WHERE run_at = (SELECT MAX(run_at) FROM delta_log)
ORDER BY issue_key;
```

---

## Confluence

Pro Tag wird eine Seite `YYYY-MM-DD` unter der konfigurierten Parent-Seite angelegt.
Mehrfache Läufe am gleichen Tag überschreiben die Seite.

**Inhalt:**
- Laufzeitpunkt
- Anzahl CompStages / Stories (gesamt + inkonsistent)
- SQLite Delta-Zusammenfassung
- Link auf die Excel-Ausgabedatei (als Anhang)

---

## Debug-Scripts

| Script | Zweck | Aufruf |
|---|---|---|
| `debug_defects.py` | Zeigt issuelinks einer Story | `python debug_defects.py FONTUS-XXXXX` |
| `debug_env.py` | Prüft ob .env korrekt geladen wird | `python debug_env.py` |
| `debug_confluence.py` | Testet Confluence-Verbindung und POST | `python debug_confluence.py` |
| `debug_confluence2.py` | Zeigt Seiten-Suchergebnisse | `python debug_confluence2.py` |
| `debug_confluence3.py` | Minimaler POST-Test | `python debug_confluence3.py` |
