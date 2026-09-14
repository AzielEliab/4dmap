# Library upload → 4DMap pin

Author: Aziel Eliab. Spec: 4DM-WP-1.0. Scores are not courtroom proof. NO-FAN / NO-LIE.

Aziel Digital Library Temporal Map: https://www.azielcorpuslibrary.net/map  
Library verify-geo: https://www.azielcorpuslibrary.net/v1/verify-geo

4DMap is an inspection frame after AZPIPE. It is not GIS, not a truth engine, not a second door.

## Contract

Library ingest (sister upload→pin) is **paper date × event × geolocation**. Never upload time. Docs without resolvable place+date stay unpinned.

```json
{
  "event": "paper event title",
  "date": "1912-04-15",
  "lat": 41.726,
  "lon": -49.947,
  "gazetteer_id": null,
  "doc_id": "AZDOC-…",
  "surface": "MOCK",
  "src": "aziel-corpus",
  "bayesian": { "label": "bayesian", "value": 0.41, "cite": "library" }
}
```

`surface` is **REAL** or **MOCK**. Gazetteer ids are opaque tokens (`geonames:…`, `wd:Q…`). They are not DNS names. No fake ICANN.

## Demo path (MOCK labeled)

1. Operator (or sister library PR) posts the ingest above.
2. `POST /v1/library_pin` (Worker or `4dmap ui`) with the JSON. Or FragGate `slug=4dmap` `op=library_pin`.
3. 4DMap writes a T pin whose `t` is a **4DM-PIN-FRAME** (clock, event, lat/lon or gazetteer, `feature_h`, surface).
4. `prev` links to the current lattice tip (or genesis). Fail-closed SHA-256. NO-REWRITE.
5. Response includes labeled hooks:

   - `possibility` — time×geo plausibility (`label=possibility`)
   - `bayesian` — cited belief if supplied (`label=bayesian`)

   They are not one number. `collapsed: false`. `courtroom_proof: false`. `gis: false`.

6. `POST /v1/plot` draws pins + trajectories (inspection plot, not GIS).
7. `POST /v1/pattern_recall` walks tips / prev-hash / pin receipts and appends a Π memory card. Not a detached ML store.
8. Poison features: `POST /v1/poison_refuse` with a `feature_h` (or event/date/geo to hash). Hash only. Append-only refuse set.

Worker UI: **MOCK library demo** button on https://4dmap-download-tracker.vibelock.workers.dev/  
Local: `4dmap ui` → Library pin / MOCK demo.

## REAL vs MOCK

| Label | Meaning |
|-------|---------|
| **MOCK** | Synthetic / example / doctor / demo. Never present as a real case. |
| **REAL** | Operator-asserted library ingest. Still an inspection receipt, not truth. |

## Refs

- Paper: [4DM-WP-1.0.md](4DM-WP-1.0.md)
- Skill: [../SKILL.md](../SKILL.md)
