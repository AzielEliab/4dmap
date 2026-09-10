# 4DM-WP-1.0

**Four-Axis Temporal Mapping and Pattern Mapping**

Aziel Eliab  
2026  
License: Apache-2.0  
Product: **4DMap** (Softwares bucket: **Plain** — not Gate, not Lock)

> Receipts are not truth. 4DMap is an inspection coordinate frame.

A typeset PDF companion may be generated from this markdown
(`tools/build_whitepaper.py`). This file is the canonical paper.

---

## Abstract

4DMap is an **inspection coordinate frame**. It is not a truth engine,
not Lumen, not GIS, not a Node Gate, and not certified forensics.

It maps evidence already produced by TemporalLock, StaticClock,
ChronoLock, TrajectoryLock, and SpectralLock onto four axes:

| Glyph | Name | Axis |
|-------|------|------|
| **T** | Clock | when a pin sits |
| **Δ** | Interval | span or gap between pins |
| **Γ** | Trajectory | stacked / walked motion of pins |
| **Π** | Pattern | class, cohort, absence, or silence |

Operators and engines write and read **4DM-CARD** receipts. FragGate
grounded claims may cite join types. ChainLock may stamp a walk when
the operator seals. QNS/QNM do not carry 4DMap photons.

Public identity is **Aziel Eliab** only. GodLock is a sibling product
name elsewhere. Never attach a GodLock-plus-AZ identity label.

---

## Pipeline placement

4DMap is **not** inserted as another sequential gate. It sits in the
**Internal Domain Layer** as an **inspection frame** (`domains_are_doors:false`):

```
PUBLIC/AGENTS/UI → FragGate → SweepGate → ChainLock-IN → DecisionGATE → AZPIPE
  → Internal Domain Layer (isolated softwares; domains_are_doors:false)  ←──  4DMap
       inspection cards sit HERE as a read-side coordinate frame over
       TemporalLock/StaticClock/ChronoLock/TrajectoryLock/SpectralLock evidence
       (not a hop gate; not a door)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT
```

Engines and operator UI write/read 4DM cards in the Internal Domain Layer.
FragGate may cite a join type on a grounded claim. ChainLock may stamp
a walk when the operator seals. The public mesh GET never enables.

---

## Card schema (4DM-CARD)

| Field | Meaning |
|-------|---------|
| `id` | stable card id |
| `t` | clock (T) |
| `delta` | interval (Δ) |
| `gamma` | trajectory (Γ) |
| `pi` | pattern (Π); `Π-EMPTY` when the lens is silent |
| `prev` | previous card SHA-256, or 64 zeros at genesis |
| `src` | source cite (`temporallock`, `staticclock`, `chronolock`, `trajectorylock`, `spectrallock`, `operator`, `synthetic`) |
| `h` | SHA-256 of the canonical core (this field is **excluded** from the hash) |
| `note` | short operator note |

Canonical encoding: UTF-8 JSON, **sorted keys**, no extra whitespace.
Algorithm: SHA-256, lowercase hex. Fail-closed: a mismatched `h` refuses.
No legal name, home, or county may appear on a card.

---

## Ops

| Op | Axis / effect |
|----|----------------|
| `pin` / `card_pin` | write a pin on T, Δ, Γ, or Π (default T) |
| `span` / `card_span` | write a Δ between two cards; records from/to axes |
| `stack` | write a Γ stack |
| `gap` | write a Δ absence of span |
| `fork` | sibling with the same `prev`; **both branches kept**; no winner |
| `walk` / `card_walk` | follow `prev` from a tip |
| `walk_trace` | walk with per-step axis / src / companion cite |
| `verify_chain` | fail-closed hash check of a `prev` chain |
| `verify_hash` | fail-closed check of one 4DM-CARD |
| `lens` | inspect Π; silent → `Π-EMPTY` |
| `class` | Π class (not identity) |
| `cohort` | Π grouping |
| `absence` | Π absence; silent → `Π-EMPTY` |
| `cap` | ZionPattern confidence **capped at 75%** |
| `join` / `card_join` | typed join or refuse; companion softwares cited, not merged |
| `card_new` | construct a 4DM-CARD on any axis |
| `card_list` | list cards + receipts |
| `card_export` | export a 4DM-CARD-JSON bundle |
| `card_import` | import JSON; fail-closed hashes |
| `frame_status` | MASTER-33 inspection-frame status (`domains_are_doors:false`) |
| `axis_describe` | describe T/Δ/Γ/Π and cite-only companions |
| `memory_cite` | optional AKM-TRIAD-1.0 fabric cite; card unchanged |
| `memory_observe` | build a FragGate `memory_observe` packet from a 4DM-CARD |

Refused (not LIVE): `truth_score`, `lumen_panel`, `invent_mark`, `backdate_class`, `wipe`, `purge`, `delete_all`, `merge_products`, `enable_door`, `akm`, `akm_triad`, `memory_rewrite`, `posterior_truth`.

Companion cites (inspection inputs only): TemporalLock, StaticClock, ChronoLock, TrajectoryLock, SpectralLock. Functional pairing / cite. Do not merge products. Do not invent a second door. FragGate remains THE single door.

AKM-TRIAD-1.0 (Adaptive Knowledge Memory) is **LIVE fabric** on aziel-runtime — not a Softwares-tab product, not a 4DMap companion slug, not a second door. Optional cite/observe of inspection cards only. Bayesian 3-of-4 triad E/C/P/B. Posterior ≠ truth. No history rewrite. Agent writes stay on FragGate `memory_*` / `POST /v1/memory/observe|resolve|calibrate|recall`.

---

## Typed joins

Allowed inspection joins:

- **T↔Δ**
- **Δ↔Γ**
- **Γ↔Π**
- **T↔Π**

Refused:

- **Π→T backdate** — a pattern cannot rewrite the clock
- **intent** — motive / guilt / “meant to”
- **identity leak** — legal name, home, or county

A refused join is ledgered as a refuse. It does not rewrite cards.

---

## Laws

1. **Fail-closed hashes.** Broken `h` refuses. No auto-repair.
2. **Forks are kept.** Two children of one `prev` are both retained.
   No winner is chosen.
3. **ZionPattern cap 75%.** `cap` never returns more than 0.75.
4. **Π-EMPTY.** A silent lens or empty class/cohort returns `Π-EMPTY`.
5. **No identity on cards.** Legal name / home / county refuse.
6. **Not a hop gate.** 4DMap does not sit in the sequential pipe.
7. **Mesh GET never enables.** Default radios OFF. No Node Gate.
8. **QNS/QNM do not carry 4DMap photons.** Cite only.
9. **Receipts are not truth.** Not Lumen. Not certified forensics. Not GIS 4D.

---

## Dual surface

1. **Human software** — Cloudflare Worker UI (black / gold), Flutter
   stubs under `mobile/`, counted `/download` tarball, local `4dmap ui`.
2. **Agent / MCP** — FragGate `slug=4dmap` is LIVE on aziel-runtime, plus this
   Worker `/v1` OpenAPI / MCP. Agents show `display.title` /
   `display.summary` / `display.fields`. No technical MCP chrome as
   the product.

Compatible clients: ChatGPT, Grok, Venice, Claude, Cursor, Glama,
Perplexity, Copilot / Bing, Gemini / Vertex, Mistral, Meta, Apple,
Amazon Q, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable
peers.

---

## Honesty

4DMap does not certify facts, solve cases, name people, infer intent,
or backdate a clock from a pattern. Synthetic examples must never be
presented as real-case findings. Forks are welcome and always allowed.

Author: **Aziel Eliab**.
