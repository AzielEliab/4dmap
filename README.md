# 4DMap

Place inspection cards on four axes: T Clock, Δ Interval, Γ Trajectory, and Π Pattern.

**Author:** Aziel Eliab
**Date:** 10 September 2026
**License:** [Apache-2.0](LICENSE)
**Version:** 0.3.0
**Spec:** `4DM-WP-1.0`
**Paper:** [docs/4DM-WP-1.0.md](docs/4DM-WP-1.0.md) · [PDF companion note](docs/PDF-COMPANION.md)
**Softwares bucket:** **Plain**

**Forks are welcome and always allowed.**

## Three steps

1. Install: `curl -fsSL https://4dmap-download-tracker.vibelock.workers.dev/install.sh | bash`
2. Run `4dmap ui` and open http://127.0.0.1:8844 (this computer only).
3. Press **Pin**. Run `4dmap doctor` for a self-check.

## Notes

4DMap is an inspection coordinate frame over TemporalLock / StaticClock / ChronoLock / TrajectoryLock / SpectralLock evidence. Cards are 4DM-CARD receipts with fail-closed SHA-256. Forks are kept. The ZionPattern cap is 75%. A silent lens returns Π-EMPTY.

Receipts are not a truth engine, Lumen, GIS 4D, a Node Gate, or certified forensics. Cards do not store a legal name, home, or county, and they do not certify facts, name people, or backdate a clock from a pattern.

Author: **Aziel Eliab**.

## Pipeline placement

4DMap is **not** another sequential gate. It is an **inspection frame** in the Internal Domain Layer (`domains_are_doors:false`):

```
PUBLIC/AGENTS/UI → FragGate → SweepGate → ChainLock-IN → DecisionGATE → AZPIPE
  → Internal Domain Layer (isolated softwares; domains_are_doors:false)  ←──  4DMap
       inspection cards sit HERE as a read-side coordinate frame over
       TemporalLock/StaticClock/ChronoLock/TrajectoryLock/SpectralLock evidence
       (not a hop gate; not a door)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT
```

Engines and operator UI write/read 4DM cards. FragGate grounded claims may cite join types. ChainLock may stamp a walk when the operator seals.

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

# → [https://4dmap-download-tracker.vibelock.workers.dev/](https://4dmap-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted):
[4dmap-0.3.0.tar.gz](https://4dmap-download-tracker.vibelock.workers.dev/download?asset=4dmap-0.3.0.tar.gz)

- Live count JSON: [https://4dmap-download-tracker.vibelock.workers.dev/stats](https://4dmap-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://4dmap-download-tracker.vibelock.workers.dev/openapi.json](https://4dmap-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://4dmap-download-tracker.vibelock.workers.dev/v1/skill](https://4dmap-download-tracker.vibelock.workers.dev/v1/skill)
- Suite mesh proxy: [https://4dmap-download-tracker.vibelock.workers.dev/v1/mesh](https://4dmap-download-tracker.vibelock.workers.dev/v1/mesh) — default OFF; GET never enables; QNM live / locked / isolated; QNS-CD-1.0 cite only
- GitHub: [https://github.com/AzielEliab/4dmap](https://github.com/AzielEliab/4dmap)

Isolated counter: Worker `4dmap-download-tracker`, KV `4DMAP_DOWNLOADS`. Not mixed with any other product. `/v1` does not increment downloads. Hosted `/v1` never stores a map.

Or tap **Download** / **One-click install** on the Worker homepage:
https://4dmap-download-tracker.vibelock.workers.dev/

## From source

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
4dmap doctor
4dmap ui
python -m pytest -q
```

Open http://127.0.0.1:8844. No CDN, no telemetry.

## CLI

```bash
4dmap
4dmap ui
4dmap pin --t 2026-09-10T00:00:00Z --src synthetic
4dmap pin --json --t 2026-09-10T00:00:00Z --src synthetic
4dmap doctor
```

A person gets a short summary. `--json` prints the machine object. `-o` still writes that object to a file. Advanced commands stay available; `4dmap --help` lists them after the common ones.

## Local UI

`4dmap ui` prints `Open http://127.0.0.1:8844/` and serves the workbench on this computer only.

The first screen is **Pin**. Span, join, walk, library pins, import, and the other board actions sit under **Advanced**. **Notes** holds the inspection scope. The page follows the system light or dark theme.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id
`com.azieeliab.fourdmap`. Offline. No analytics. Dark matte / gold.
Not a store listing. Not a separate repo. Not store IPAs.

```bash
cd mobile
flutter create --org com.azieeliab --project-name fourdmap .
flutter pub get
flutter run
```

## Hosted `/v1`

The Worker hosts a **stateless** JSON API. It does not increment DOWNLOADS. It never stores a map.

- `GET /v1/health`
- `GET /v1/skill` — this repo's [SKILL.md](SKILL.md)
- `GET /v1/mesh` — PROXY suite mesh status. Default OFF. Never enables.
- `GET /v1/mesh/nodes` — PROXY Live Nodes roster
- `POST /v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` — PROXY. Bearer required to enable.
- `GET /v1/example` — synthetic cards
- `GET /v1/frame_status` — MASTER-33 inspection-frame status (`domains_are_doors:false`)
- `GET /v1/axis_describe` — T/Δ/Γ/Π + companion cites
- `GET /llms.txt` — agent skill text
- `POST /v1/{pin,span,stack,gap,fork,walk,lens,class,cohort,absence,cap,join}`
- `POST /v1/{card_new,card_pin,card_span,card_join,card_walk,card_list,verify_hash}`
- `POST /v1/{card_export,card_import,frame_status,axis_describe,walk_trace,verify_chain}`
- `POST /v1/{memory_cite,memory_observe}` — optional AKM-TRIAD-1.0 fabric cite/observe (not a Softwares slug; posterior ≠ truth; no history rewrite)
- `POST /v1/{library_pin,plot,possibility,pattern_recall,lattice_tip,poison_refuse,neighbor_cite}` — library pin frames + hashchain lattice memory (Growth-ON)
- OpenAPI: `/openapi.json`
- MCP: this Worker `/mcp` and catalog `https://aziel-runtime.vibelock.workers.dev/mcp`

FragGate is LIVE on aziel-runtime: `fraggate_list` → `fraggate_describe slug=4dmap` → `fraggate_call` (`card_new` / `card_pin` / `card_span` / `card_join` / `card_walk` / `card_list` / `verify_hash` plus `card_export` / `card_import` / `frame_status` / `axis_describe` / `walk_trace` / `verify_chain` / `memory_cite` / `memory_observe` / `library_pin` / `plot` / `possibility` / `pattern_recall` / `lattice_tip` / `poison_refuse` / `neighbor_cite`). Softwares bucket **Plain**. Hubs list 4DMap. Agent path remains FragGate only. 4DMap is an inspection frame after AZPIPE, not an extra door (`domains_are_doors:false`). AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab product. Pattern recollection is the hashchain lattice (tips / prev-hash / pin receipts), not a detached ML store.

Library demo: ingest `{event, date, lat, lon, surface:MOCK|REAL}` → `POST /v1/library_pin`. Cite [Temporal Map](https://www.azielcorpuslibrary.net/map) and [`/v1/verify-geo`](https://www.azielcorpuslibrary.net/v1/verify-geo). Possibility and Bayesian stay labeled separately. Not courtroom proof. Not GIS.

Always send `User-Agent: Mozilla/5.0`. Empty agents can 403.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

OpenAPI import (GPT Actions, custom tools, HTTP tools):
`https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP remote: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

Example:

```bash
curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/mesh
curl -s -A 'Mozilla/5.0' -X POST https://4dmap-download-tracker.vibelock.workers.dev/v1/pin \
  -H 'content-type: application/json' \
  -d '{"t":"2026-09-10T00:00:00Z","src":"synthetic","note":"synthetic T pin"}'
```

## Papers

- Paper (markdown): [docs/4DM-WP-1.0.md](docs/4DM-WP-1.0.md)
- PDF companion note: [docs/PDF-COMPANION.md](docs/PDF-COMPANION.md)
- License: Apache-2.0. Creator: Eliab, Aziel. No invented DOI.

## Tests

```bash
python -m pytest -q
```

Card hash, illegal join refuse, fork keep, Π-EMPTY, export/import / walk_trace / verify_chain, library pin / possibility / lattice recall, and MASTER-33 inspection-frame (not door) framing are covered.

## Use with AI clients

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://4dmap-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://4dmap-download-tracker.vibelock.workers.dev/openapi.json
Suite mesh `/v1/mesh/*` PROXY via `AZIEL_RUNTIME` (default OFF; GET never enables; QNM-BUILD-1.0 live|locked|isolated; QNS-CD-1.0 cite only; no Node Gate; no public qnsd proxy). Local qnsd is [qnm-node](https://github.com/AzielEliab/qnm-node). Runtime cites live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime).

Import the catalog or Worker OpenAPI as a custom tool, GPT Action, or HTTP tool. Connect MCP remotes in Cursor, Glama, and other MCP clients. Always send `User-Agent: Mozilla/5.0`.

## Cite this

Aziel Eliab. 4DMap. https://github.com/AzielEliab/4dmap. https://4dmap-download-tracker.vibelock.workers.dev.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://4dmap-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://4dmap-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/4dmap
- Citation JSON: https://4dmap-download-tracker.vibelock.workers.dev/cite.json
