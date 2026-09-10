# 4dmap download tracker

Isolated Worker `4dmap-download-tracker`. Project `4dmap`.
KV namespace `4DMAP_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV. Hosted never stores a map.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME` /
`https://aziel-runtime.vibelock.workers.dev`). Default OFF.
`GET /v1/mesh` never enables. QNM-BUILD-1.0 live|locked|isolated.
QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh
cross-map only. QNS/QNM do not carry 4DMap photons. No Node Gate.
No public qnsd proxy. No auto-heal. Not anonymity. Human UI Live Nodes
strip polls `GET /v1/mesh`. Softwares bucket **Plain**.

KV namespace `4DMAP_DOWNLOADS` id `e962292069794bcc8cb89e3f559cfa43` (binding `DOWNLOADS`). Already live — do not recreate.

Host: https://4dmap-download-tracker.vibelock.workers.dev

Paper: [docs/4DM-WP-1.0.md](../../docs/4DM-WP-1.0.md)
