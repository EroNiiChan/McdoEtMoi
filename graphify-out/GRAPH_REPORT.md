# Graph Report - McdoEtMoi  (2026-10-27)

## Corpus Check
- 5 files · ~3,723 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .bat 2, .zip 1)

## Summary
- 54 nodes · 79 edges · 9 communities (3 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `362b5bb9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- time
- random
- script.py
- Bot Hello McDo Automatique (Medallia)
- lanceur.sh script
- purger_anciens_screenshots
- renouveler_ip
- charger_config_locale

## God Nodes (most connected - your core abstractions)
1. `pause_humaine()` - 6 edges
2. `remplir_champ()` - 5 edges
3. `Bot Hello McDo Automatique (Medallia)` - 5 edges
4. `purger_anciens_screenshots()` - 4 edges
5. `cliquer_element()` - 4 edges
6. `nettoyer_processus_fantomes()` - 4 edges
7. `generer_commentaire()` - 3 edges
8. `calculer_nombre_passages()` - 3 edges
9. `notifier_discord()` - 3 edges
10. `renouveler_ip()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `purger_anciens_screenshots()` --calls--> `time`  [EXTRACTED]
  script.py →   _Bridges community 6 → community 0_
- `pause_humaine()` --calls--> `random`  [EXTRACTED]
  script.py →   _Bridges community 0 → community 1_

## Import Cycles
- None detected.

## Communities (9 total, 6 thin omitted)

### Community 0 - "time"
Cohesion: 0.32
Nodes (4): explorer_chemin(), cliquer_element(), pause_humaine(), remplir_champ()

### Community 1 - "random"
Cohesion: 0.25
Nodes (4): generer_commentaire(), calculer_nombre_passages(), generer_horaire_ticket(), generer_options_furtives()

### Community 4 - "Bot Hello McDo Automatique (Medallia)"
Cohesion: 0.33
Nodes (5): Bot Hello McDo Automatique (Medallia), 🚀 Caractéristiques Principales, ⚙️ Configuration (`script.py`), 🐧 Utilisation sur Debian / Linux, 💻 Utilisation sur Windows

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `pause_humaine()` connect `time` to `random`, `script.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `purger_anciens_screenshots()` connect `purger_anciens_screenshots` to `time`, `script.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `remplir_champ()` connect `time` to `random`, `script.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._