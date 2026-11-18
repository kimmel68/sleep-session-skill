---
name: schlaf-sitzung
description: Schlaf-Sitzung für das dateibasierte Gedächtnis von Claude Code, nach dem SLEEP-Ansatz (Google Research 2026). Nach einer langen Sitzung oder vielen neuen Urteilen des Nutzers wird das Gedächtnis gefestigt. Wiederholte Urteile werden zu Regeln, Widersprüche werden aufgelöst, der Index wird verkürzt, offene Urteile kommen in eine Liste, Ersetztes ins Archiv. Ein günstiger Agent schlägt vor, das Hauptmodell prüft gegen die echten Dateien und schreibt. Benutzen, wenn der Nutzer „Schlaf“, „Sleep“, „Gedächtnis aufräumen“, „konsolidieren“ oder „Memory festigen“ sagt, nach sehr langen Sitzungen, oder wenn der Index (MEMORY.md) zu lang wird.
---

# Schlaf-Sitzung: das Gedächtnis festigen

Grundlage ist das Paper „Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories“ (Behrouz, Hashemi,
Javanmard, Mirrokni, 2026, https://arxiv.org/abs/2606.03979) und der Artikel „The sleep framework“ (Google Research,
27.10.2026, https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/).
Erarbeitet am 8.11.2026. Dort wechselt ein
Modell zwischen Wachphase (neue Eingaben, Kurzzeitspeicher) und Schlafphase (keine Eingaben). Im Schlaf geschehen drei Dinge:
- Kurzfristiges Wissen wird in langsame Teile übertragen (Knowledge Seeding).
- Die schnellen Speicher werden geleert (Synaptic Pruning).
- Das Modell übt an ausgewählten eigenen Beispielen (Curated Rehearsal).

Hier gibt es keine Gewichte, sondern Dateien. Die Analogie trägt nur so weit:

| SLEEP | hier |
|---|---|
| Kurzzeitspeicher | Transkript der Sitzung, neue Memory-Dateien mit Fallgeschichten |
| Seeding in langsame Experten | wiederholte Einzelurteile werden zu einer Regel (feedback-Datei, später `.claude/rules/`) |
| Pruning | Index kürzen, Erledigtes ins Archiv, Zwischenstände zu einem Stand verdichten |
| Curated Rehearsal | nur Ereignisse mit Lehre behalten: Urteile, Korrekturen, wiederholte Fehler |
| Prüfung der Leistung | jede Regel gegen echte Dateien, Skripte und Messwerte prüfen; der Nutzer sieht die Regeln vor der Übernahme |

## Grundsätze

- **Nichts löschen:** Ersetztes wandert mit `gedaechtnis.py archiv` nach `<memory>/_archiv/`, mit Datum und Grund. Ein
  Fehler beim Verdichten muss umkehrbar bleiben.
- **Der Agent schlägt vor, das Hauptmodell schreibt:**
  - Beim Verdichten verrutschen Zahlen und die Zuordnung von Lob am leichtesten.
  - Deshalb prüft das Hauptmodell jede vorgeschlagene Regel an den Dateien, die sie belegen.
- **Seine Worte sind die Regel:**
  - Eine Regel nennt die Aussage des Nutzers (kurzes Zitat, Datum) und das *Warum*.
  - Messlatten sind Vorfilter, keine Urteile; das Gedächtnis darf aus einer Messung keine Vorliebe machen.
- **Projektregeln nur mit Ja:** Was in `.claude/rules/` oder `CLAUDE.md` soll, legt das Hauptmodell dem Nutzer als kurzes Diff vor.
- **Keine Arbeit am Projekt:** Die Sitzung schreibt nur ins Gedächtnis. Keine Renders, keine Eingriffe in laufende Anwendungen.

## Ablauf

| Schritt | wer | Ergebnis |
|---|---|---|
| 1 Inventar | Skript | Befund: lange Indexzeilen, fehlende Köpfe, tote Verweise, offene Urteile |
| 2 Replay | Hauptmodell | Liste der Urteile und Korrekturen dieser Sitzung (aus dem Gespräch, mit Datum, wörtlich kurz) |
| 3 Vorschlag | ein Agent (Sonnet) | `<memory>/_schlaf/<datum>_vorschlag.md` nach `prompts/vorschlag.md` |
| 4 Prüfen und schreiben | Hauptmodell | Index neu, Regeln zusammengeführt, Widersprüche aufgelöst, Liste offener Urteile, Archiv |
| 5 Abnahme | Skript, Nutzer | Inventar erneut (0 tote Verweise, alle Zeilen ≤ 150 Zeichen), Bericht, Diff für Projektregeln |

### 1. Inventar

```
python <skill>/scripts/gedaechtnis.py inventar <memory-ordner>
```

Der Gedächtnisordner steht im Systemprompt der Sitzung (Abschnitt Memory), etwa
`C:\Users\<name>\.claude\projects\<projekt>\memory\`.

### 2. Replay

Das Hauptmodell schreibt aus dem Gespräch (und der Zusammenfassung, falls die Sitzung verdichtet wurde) eine Liste. Jeder Eintrag:
Datum, Zitat höchstens 15 Wörter, worauf es sich bezog, was daraus folgte. Dazu eigene Fehler, die der Nutzer bemerkt hat. Die
Liste geht in den Auftrag des Agenten. Routinemeldungen (fertig, läuft, gesendet) gehören nicht hinein.

### 3. Vorschlag

Einen Agenten im Hintergrund starten (gemessen 8.11.2026: etwa 100 000–150 000 Tokens bei einem schmalen Auftrag, 236 000 Tokens
und knapp 8 Minuten, als er alle 91 Dateien las):

```
Agent(description: "Schlaf: Vorschlag", model: "sonnet", subagent_type: "general-purpose", run_in_background: true,
      prompt: <prompts/vorschlag.md mit eingesetztem Ordner, Datum, Inventar und Replay-Liste>)
```

Er liest alle Memory-Dateien und schreibt **nur** die Vorschlagsdatei.

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
- Die Tokens des Agenten.

Vorschläge für `.claude/rules/` als Diff mit der Frage, ob sie übernommen werden.

## Wann

- Nach einer Sitzung mit vielen Urteilen des Nutzers (ab etwa zehn).
- Wenn der Index über etwa 12 000 Zeichen wächst.
- Auf Wunsch des Nutzers.
- Dauer etwa 15–20 Minuten.

## Grenzen

- Kein Training, keine Leistungsmessung, die das Ergebnis bestätigt: „wichtig“ entscheidet der Nutzer oder eine Faustregel.
- Der Agent kann beim Verdichten Fehler einführen. Darum prüft das Hauptmodell, und nichts wird gelöscht.
- Kosten und Zeitpunkt für Dateien nennt das Paper nicht; die Angaben oben sind Annahmen aus dem ersten Lauf (8.11.2026).
