# Changelog

## 0.3.0 — library pin frames + hashchain lattice memory

Author: Aziel Eliab. Spec: 4DM-WP-1.0. Softwares bucket: Plain. Growth-ON.

### Aziel Digital Library pairing

- Accept/emit **4DM-PIN-FRAME** from library ingest: paper `date` × `event` × `lat`/`lon` or opaque `gazetteer_id`.
- Never uses upload time. Incomplete place+date refuses (`ANCHOR_INCOMPLETE`).
- Malformed / poison anchors refuse. Gazetteer ids are not DNS; no fake ICANN.
- Each pin is **REAL** or **MOCK**. Scores are not courtroom proof. Not GIS.

### Possibility vs Bayesian (labeled)

- `possibility` = time×geo plausibility. `bayesian` = cited belief input.
- Never collapsed into one unlabeled number (`SCORE_COLLAPSE`).
- Hooks write lattice-linked receipts (`prev` = pin hash). NO-REWRITE.

### Adaptive pattern memory = hashchain lattice

- `pattern_recall` walks tips / prev-hash / pin receipts. Not a detached ML store.
- Recurring event patterns are feature hashes only.
- `poison_refuse` appends a refuse-set card (feature hash only).
- `lattice_tip` lists append-only tips. `plot` draws pins + trajectories (inspection, not GIS).
- `neighbor_cite` cites Aziel Digital Library + inspection companions on a declared card.

### Dual surface + discovery

- Worker UI + local `4dmap ui`: library ingest form, REAL/MOCK plot, labeled scores.
- OpenAPI / MCP / skill list the new ops. Growth-ON because Worker discovery changed.
- Counted tarball: `4dmap-0.3.0.tar.gz`.

Demo path: library ingest JSON → `POST /v1/library_pin` → 4DM-PIN-FRAME on T. Cite https://www.azielcorpuslibrary.net/map and `/v1/verify-geo`.

## 0.2.0 — inspection-frame capability pack

Author: Aziel Eliab. Spec: 4DM-WP-1.0. Softwares bucket: Plain.

### Axis frame

- `pin` / `card_pin` write T, Δ, Γ, or Π (default T).
- `span` / `card_span` record from/to axes on the Δ receipt.
- `walk` returns per-step axis traces; `walk_trace` is the explicit receipt walk.
- Every write that produces a card attaches a non-hashed **4DM-CARD** receipt (axis, glyph, src, companion cite). Canonical `h` is unchanged.

### Companion cites

- TemporalLock, StaticClock, ChronoLock, TrajectoryLock, SpectralLock are **inspection inputs only**.
- Typed joins and spans cite `src` companions. Products are not merged. No second door.

### New FragGate-safe ops (LIVE_OPS)

- `card_new`, `card_export`, `card_import` (4DM-CARD-JSON)
- `frame_status` (MASTER-33: `domains_are_doors:false`, inspection after AZPIPE)
- `axis_describe`
- `walk_trace`, `verify_chain`, `verify_hash`
- FragGate aliases: `card_pin`, `card_span`, `card_join`, `card_walk`, `card_list`

Refused: `truth_score`, `lumen_panel`, `invent_mark`, `backdate_class`, `wipe`, `purge`, `delete_all`, `merge_products`, `enable_door`.

### Dual surface

- Worker UI (black/gold): pin across axes, companion src select, walk/trace/verify, frame status, axis describe, JSON export/import.
- OpenAPI, MCP, skill, `/llms.txt`, `cite.json` updated.
- Counted tarball name: `4dmap-0.2.0.tar.gz`.
- Hosted `workers/download-tracker/public/4dmap-0.2.0.tar.gz` as Worker `DEFAULT_ASSET` (rebuild: `tools/pack_counted_tarball.sh`). Nested `*.tar.gz` omitted. Fixes 404 `asset not hosted` when catalog/runtime ask for 0.2.0.
- Local `4dmap ui` workbench mirrors the new ops.

### AKM-TRIAD-1.0 fabric pairing (optional)

- `memory_cite` / `memory_observe` build a fabric cite or FragGate observation packet from a 4DM-CARD.
- AKM is LIVE fabric — not a Softwares-tab slug, not a companion software, not a second door.
- Posterior ≠ truth. No history rewrite. Card `h` / `prev` unchanged.
- Agent path for memory writes remains FragGate `memory_*`.

### Framing

- Mesh stays default-off. GET never enables.
- 4DMap remains an inspection frame, not a Softwares door. FragGate is THE single door.
- Pipeline copy uses Internal Domain Layer (`domains_are_doors:false`). Domain Door wording scrubbed.

## 0.1.0

Initial dual-surface Worker UI + Python engine (pin/span/join/walk).
