# Contributing to 4DMap

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. pytest is the dev extra. No network.

## Ground rules

1. **Not a truth engine.** Receipts are not truth. Not Lumen. Not GIS 4D. Not certified forensics.
2. **Typed joins only:** T↔Δ, Δ↔Γ, Γ↔Π, T↔Π. Π→T backdate refuses.
3. **Forks are kept.** No winner is chosen.
4. **Π-EMPTY** when the lens is silent. ZionPattern cap 75%.
5. **No legal name / home / county** on cards.
6. **UI binds loopback only** (`127.0.0.1:8844`). Do not listen on `0.0.0.0` from `4dmap ui`. No telemetry. No CDN.
7. **Do not mix the download tracker** with any other product's Worker or KV. Namespace `4DMAP_DOWNLOADS` only.
8. **Public identity is Aziel Eliab only.** Never attach a GodLock-plus-AZ identity label.
9. **Door vs local op.** `/v1/mesh/*` PROXY to aziel-runtime. Local ops are `/v1/{op}` only.
   Suite mesh default OFF; GET never enables; QNM rollup live|locked|isolated;
   QNS-CD-1.0 is a hub cite only; QNS/QNM do not carry 4DMap photons;
   no Node Gate; no auto-heal; not anonymity.
10. Softwares bucket is **Plain** (not Gate, not Lock).
11. New behavior needs a test that fails without the change.
12. 4DMap is an inspection frame (`domains_are_doors:false`). Do not make it a Softwares door. FragGate stays THE single door.
13. Companion softwares (TemporalLock, StaticClock, ChronoLock, TrajectoryLock, SpectralLock) are cite-only inspection inputs. Do not merge products.
14. Do not enable mesh by default. GET `/v1/mesh` never enables.

## Where to change things

- Cards / hash: `fourdmap/card.py` and `workers/download-tracker/src/engine.js`
- Joins: `fourdmap/joins.py`
- Ops: `fourdmap/ops.py`
- CLI / doctor: `fourdmap/cli.py`, `fourdmap/doctor.py`
- Local UI: `fourdmap/server.py`, `fourdmap/static/`
- Skill: `SKILL.md`
- Flutter: `mobile/`
- Isolated counter: `workers/download-tracker/`
- Suite mesh: `workers/download-tracker/src/mesh.js`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.
