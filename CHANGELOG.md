# Changelog

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

- Worker UI (black/gold, everblooming sigil): pin across axes, companion src select, walk/trace/verify, frame status, axis describe, JSON export/import.
- OpenAPI, MCP, skill, `/llms.txt`, `cite.json` updated.
- Counted tarball name: `4dmap-0.2.0.tar.gz`.
- Local `4dmap ui` workbench mirrors the new ops.

### AKM-TRIAD-1.0 fabric pairing (optional)

- `memory_cite` / `memory_observe` build a fabric cite or FragGate observation packet from a 4DM-CARD.
- AKM is LIVE fabric — not a Softwares-tab slug, not a companion software, not a second door.
- Posterior ≠ truth. No history rewrite. Card `h` / `prev` unchanged.
- Agent path for memory writes remains FragGate `memory_*`.

### Framing

- Mesh stays default-off. GET never enables.
- 4DMap remains an inspection frame, not a Softwares door. FragGate is THE single door.

## 0.1.0

Initial dual-surface Worker UI + Python engine (pin/span/join/walk).
