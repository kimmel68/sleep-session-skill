---
name: schlaf-sitzung
description: Schlaf-Sitzung für das dateibasierte Gedächtnis eines Claude-Code-Assistenten, nach dem SLEEP-Ansatz (Behrouz et al. 2026). Nach einer langen Sitzung oder vielen neuen Urteilen des Nutzers wird das Gedächtnis gefestigt. Wiederholte Urteile werden zu Regeln, Widersprüche werden aufgelöst, der Index wird verkürzt, offene Urteile kommen in eine Liste, Ersetztes ins Archiv. Ein günstigerer Agent schlägt vor, das Hauptmodell prüft gegen die echten Dateien und schreibt. Benutzen, wenn der Nutzer „Schlaf“, „Sleep“, „Gedächtnis aufräumen“, „konsolidieren“, „consolidate memory“ oder „Memory festigen“ sagt, nach sehr langen Sitzungen, oder wenn der Index (MEMORY.md) zu lang wird.
---

# Schlaf-Sitzung: das Gedächtnis festigen

Grundlage ist das Paper „Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories“ (Behrouz, Hashemi,
Javanmard, Mirrokni, 2026, https://arxiv.org/abs/2606.03979), vorgestellt im Artikel „The sleep framework“ (Google
Research, https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/).
Dort wechselt ein Modell zwischen Wachphase (neue Eingaben, Kurzzeitspeicher) und Schlafphase (keine Eingaben). Im Schlaf
geschehen drei Dinge:
- Kurzfristiges Wissen wird in langsame Teile übertragen (Knowledge Seeding).
- Die schnellen Speicher werden geleert (Synaptic Pruning).
- Das Modell übt an ausgewählten eigenen Beispielen (Curated Rehearsal).

Hier gibt es keine Gewichte, sondern Dateien. Die Analogie trägt nur so weit:

| SLEEP | hier |
|---|---|
| Kurzzeitspeicher | Transkript der Sitzung, neue Memory-Dateien mit Fallgeschichten |
| Seeding in langsame Experten | wiederholte Einzelurteile werden zu einer Regel (feedback-Datei, später Projektregeln) |
| Pruning | Index kürzen, Erledigtes ins Archiv, Zwischenstände zu einem Stand verdichten |
| Curated Rehearsal | nur Ereignisse mit Lehre behalten: Urteile, Korrekturen, wiederholte Fehler |
| Prüfung der Leistung | jede Regel gegen echte Dateien und Belege prüfen; der Nutzer sieht die Regeln vor der Übernahme |

## Voraussetzung

Ein Gedächtnisordner im Format von Claude Code: ein Index `MEMORY.md` mit einer Zeile je Datei
(`- [Titel](datei.md) — Kurzbeschreibung`) und je Fakt eine Markdown-Datei mit Frontmatter (`name`, `description`,
`metadata.type`: user, feedback, project oder reference). Verweise zwischen Dateien als `[[name]]`. Wo der Ordner liegt,
steht im Systemprompt der Sitzung (Abschnitt Memory).

## Grundsätze

- **Nichts löschen:** Ersetztes wandert mit `gedaechtnis.py archiv` nach `<memory>/_archiv/`, mit Datum und Grund. Ein
  Fehler beim Verdichten muss umkehrbar bleiben.
- **Der Agent schlägt vor, das Hauptmodell schreibt:**
  - Beim Verdichten verrutschen Zahlen und die Zuordnung von Lob und Kritik am leichtesten.
  - Deshalb prüft das Hauptmodell jede vorgeschlagene Regel an den Dateien, die sie belegen.
- **Die Worte des Nutzers sind die Regel:**
  - Eine Regel nennt die Aussage des Nutzers (kurzes Zitat, Datum) und das *Warum*.
  - Messwerte und Prüfskripte sind Vorfilter, keine Urteile; das Gedächtnis darf aus einer Messung keine Vorliebe machen.
- **Projektregeln nur mit Ja:** Was in die Projektregeln (`CLAUDE.md`, `.claude/rules/`) soll, legt das Hauptmodell dem
  Nutzer als kurzes Diff vor.
- **Keine Arbeit am Projekt:** Die Sitzung schreibt nur ins Gedächtnis. Sie ändert keinen Code und startet keine Prozesse.

## Ablauf

| Schritt | wer | Ergebnis |
|---|---|---|
| 1 Inventar | Skript | Befund: lange Indexzeilen, fehlende Köpfe, tote Verweise, offene Urteile |
| 2 Replay | Hauptmodell | Liste der Urteile und Korrekturen dieser Sitzung (aus dem Gespräch, mit Datum, wörtlich kurz) |
| 3 Vorschlag | ein Agent (günstigeres Modell) | `<memory>/_schlaf/<datum>_vorschlag.md` nach `prompts/vorschlag.md` |
| 4 Prüfen und schreiben | Hauptmodell | Index neu, Regeln zusammengeführt, Widersprüche aufgelöst, Liste offener Urteile, Archiv |
| 5 Abnahme | Skript, Nutzer | Inventar erneut (keine toten Verweise, alle Indexzeilen kurz), Bericht, Diff für Projektregeln |

### 1. Inventar

```
python <skill>/scripts/gedaechtnis.py inventar <memory-ordner>
```

Optionen: `--zeile-max 150` (Grenze für Indexzeilen), `--offen "<regex>"` (woran offene Urteile zu erkennen sind;
Standard: deutsche und englische Wendungen wie „Urteil steht aus“, „awaiting feedback“), `--json`.

### 2. Replay

Das Hauptmodell schreibt aus dem Gespräch (und der Zusammenfassung, falls die Sitzung verdichtet wurde) eine Liste. Jeder Eintrag:
Datum, Zitat höchstens 15 Wörter, worauf es sich bezog, was daraus folgte. Dazu eigene Fehler, die der Nutzer bemerkt hat. Die
Liste geht in den Auftrag des Agenten. Routinemeldungen (fertig, läuft, gesendet) gehören nicht hinein.

### 3. Vorschlag

Einen Agenten im Hintergrund starten, mit einem günstigeren Modell als dem Hauptmodell:

```
Agent(description: "Schlaf: Vorschlag", model: "<günstigeres Modell>", subagent_type: "general-purpose",
      run_in_background: true, prompt: <prompts/vorschlag.md mit eingesetztem Ordner, Datum, Inventar und Replay-Liste>)
```

Er liest alle Memory-Dateien und schreibt **nur** die Vorschlagsdatei. Der Aufwand wächst mit der Zahl der Dateien, weil der
Agent jede Datei liest; bei großen Ordnern den Auftrag auf die Dateien eingrenzen, die das Inventar oder das Replay betreffen.

### 4. Prüfen und schreiben

Je Vorschlag:

| Vorschlag | Prüfung | Umsetzung |
|---|---|---|
| Neue oder zusammengeführte Regel | Zitate und Zahlen in den Quelldateien nachlesen | eine feedback-Datei; die Quelldateien verweisen mit `[[name]]` darauf statt die Regel zu wiederholen |
| Widerspruch | beide Stellen lesen, der jüngere Stand gilt, wenn der Nutzer nichts anderes sagte | die ältere Stelle bekommt „ersetzt am <datum> durch [[name]]“ |
| Indexzeile | Datei lesen, Kernlehre und Stand in höchstens 110 Zeichen | `MEMORY.md` neu schreiben, eine Zeile je Datei |
| Offenes Urteil | steht es wirklich noch aus, oder hat der Nutzer es im Replay gegeben? | eine Datei `offene-urteile` mit Liste; Urteile aus dem Replay in die Fachdatei |
| Archiv | ist die Datei ganz ersetzt, nicht nur teilweise? | `gedaechtnis.py archiv ... --grund` |

Nach jeder Datei ein kurzer Blick auf das Ergebnis. Am Ende das Inventar erneut laufen lassen.

### 5. Abnahme und Bericht

Dem Nutzer berichten:
- Zahlen vorher und nachher: Dateien, Indexzeichen, offene Urteile.
- Neue Regeln, je eine Zeile.
- Aufgelöste Widersprüche.
- Archivierte Dateien.
- Den Verbrauch des Agenten.

Vorschläge für die Projektregeln als Diff mit der Frage, ob sie übernommen werden.

## Wann

- Nach einer Sitzung mit vielen Urteilen des Nutzers (Faustregel: ab etwa zehn).
- Wenn der Index so lang wird, dass er einen spürbaren Teil des Kontexts belegt (Faustregel: über etwa 12 000 Zeichen).
- Auf Wunsch des Nutzers.

## Grenzen

- Kein Training, keine Leistungsmessung, die das Ergebnis bestätigt: „wichtig“ entscheidet der Nutzer oder eine Faustregel.
- Der Agent kann beim Verdichten Fehler einführen. Darum prüft das Hauptmodell, und nichts wird gelöscht.
- Das Paper beschreibt Gewichte, nicht Dateien. Zeitpunkt, Häufigkeit und Grenzwerte hier sind Faustregeln, keine Ergebnisse
  des Papers.
