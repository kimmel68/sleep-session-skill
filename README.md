# sleep-session-skill

A Claude Code skill that runs a "sleep session" on Claude Code's file-based memory: after a long session it consolidates
what was learned. Repeated judgments of the user become rules, contradictions are resolved, the index is shortened,
open judgments are listed and replaced files are archived (never deleted). A cheaper agent proposes, the main model
checks every proposal against the real files and writes.

The idea is adapted from the SLEEP framework, which alternates a model between a wake phase and a sleep phase
(knowledge seeding, synaptic pruning, curated rehearsal):

- Paper: Ali Behrouz, Farnoosh Hashemi, Adel Javanmard, Vahab Mirrokni. *Language Models Need Sleep: Learning to
  Self-Modify and Consolidate Memories.* 2026. https://arxiv.org/abs/2606.03979
- Article: *The sleep framework: A new way for LLMs to retain knowledge in continual learning.* Google Research,
  27 Oct 2026. https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/

Here there are no weights, only files; `schlaf-sitzung/SKILL.md` maps each part of the framework onto memory files.
This is an independent adaptation, not affiliated with the authors.

## Contents

| File | Purpose |
|---|---|
| `schlaf-sitzung/SKILL.md` | the skill: principles, the five steps (inventory, replay, proposal, check and write, review) |
| `schlaf-sitzung/prompts/vorschlag.md` | the brief for the proposing agent (reads everything, writes one proposal file) |
| `schlaf-sitzung/scripts/gedaechtnis.py` | `inventar` (index, headers, dead links, open judgments) and `archiv` (move to `_archiv/`), standard library only |

The skill text is in German.

## Install

Copy the folder `schlaf-sitzung` into `~/.claude/skills/` (or a project's `.claude/skills/`). It triggers on
"Schlaf", "Sleep", "Gedächtnis aufräumen", "konsolidieren" or when `MEMORY.md` grows too long.

## License

MIT, see [LICENSE](LICENSE).
