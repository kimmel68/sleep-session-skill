# Auftrag: Schlaf-Sitzung, Vorschlag (nur lesen, eine Datei schreiben)

Du bist Teil einer Schlaf-Sitzung für das dateibasierte Gedächtnis eines Claude-Code-Assistenten. Du **änderst keine** Memory-Datei.
Du schreibst genau eine Datei: `{ORDNER}/_schlaf/{DATUM}_vorschlag.md`. Den Ordner `_schlaf` legst du an, falls er fehlt.

**Eingaben:**
- Gedächtnisordner: `{ORDNER}`. Darin liegen der Index `MEMORY.md` und je eine Datei pro Fakt (Frontmatter name, description,
  metadata.type: user, feedback, project oder reference).
- Inventar des Skripts: siehe unten.
- Replay der letzten Sitzung, also die Urteile und Korrekturen des Nutzers: siehe unten.

**Lesen:** `MEMORY.md` und **alle** Dateien des Ordners (nicht `_archiv/`, nicht `_schlaf/`).

**Schreiben**, in der Sprache der Memory-Dateien, in diesen Abschnitten. Zu jedem Punkt die Quelldateien nennen, Zitate des Nutzers höchstens 15 Wörter.

## A Regeln (Festigen)
Gemeint sind Lehren, die in mehreren Dateien oder Urteilen vorkommen. Je Regel:
- **Text:** Name (Kebab-Slug) und die Regel in 1–2 Sätzen, dazu **Why:** und **How to apply:**.
- **Belege:** Quelldateien und Zitate.
- **Ziel:** eine feedback-Datei oder ein Kandidat für die Projektregeln. Kandidaten nur bei Regeln, die für jede künftige
  Arbeit am Projekt gelten.

Nur Regeln, die die Belege wirklich tragen. Eine Messung ist kein Urteil des Nutzers.

## B Widersprüche
Je Fall:
- beide Stellen, Datei und Satz;
- welcher Stand jünger ist;
- Vorschlag, wie es aufgelöst wird.

## C Index neu
Ein vollständiger neuer `MEMORY.md`:
- je Datei eine Zeile `- [Titel](datei.md) — Kernlehre; Stand`, **höchstens 110 Zeichen**;
- keine Fallgeschichten und Zahlenreihen, die stehen in der Datei;
- Reihenfolge nach Themen gruppiert, je Gruppe eine Überschrift `## …`.

## D Offene Urteile
Eine Tabelle: Datei, was auf das Urteil des Nutzers wartet (Entwurf, Probe, Funktion, Entscheidung), seit wann. Steht das Urteil im Replay,
schreibe es dazu und markiere den Punkt als erledigt.

## E Verdichten und Archiv
- Dateien, deren Inhalt ganz in einer anderen steht oder ganz überholt ist (mit Grund): Archiv-Kandidaten.
- Dateien, die in kleinen Zwischenständen gewachsen sind: Vorschlag für einen verdichteten Stand. Was stehen bleibt, was als
  „ersetzt am …“ markiert wird.

## F Fehlende Erinnerungen
Was aus dem Replay noch in keiner Datei steht und bleiben sollte.

Zum Schluss eine Zeile mit den Zahlen: Dateien, vorgeschlagene Regeln, Widersprüche, offene Urteile, Archiv-Kandidaten.
Deine Antwort an den Auftraggeber ist nur diese Zeile und der Pfad der Datei.

---
Inventar:
{INVENTAR}

Replay der Sitzung:
{REPLAY}
