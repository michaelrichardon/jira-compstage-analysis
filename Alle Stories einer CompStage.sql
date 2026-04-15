-- Alle Stories einer CompStage
SELECT s.* FROM stories s
JOIN compstage_stories cs ON cs.story_key = s.key
WHERE cs.compstage_key = 'FONTUS-123';

-- Alle CompStages einer Story (zeigt geteilte Stories)
SELECT c.* FROM compstages c
JOIN compstage_stories cs ON cs.compstage_key = c.key
WHERE cs.story_key = 'FONTUS-456';

-- Stories die an mehreren CompStages hängen
SELECT story_key, COUNT(*) as anzahl FROM compstage_stories
GROUP BY story_key HAVING anzahl > 1;