---
name: 4DMap
description: Use this when inspecting time as four axes (T clock, Δ interval, Γ trajectory, Π pattern). Inspection coordinate frame, not a truth engine, not Lumen, not GIS, not a Node Gate. Hosted /v1 via this Worker and aziel-runtime FragGate slug=4dmap. Dual surface: Worker / Flutter / counted download stay complete human software; agents see display envelopes in chat. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. GET /v1/mesh never enables. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 cite only. No Node Gate. Author Aziel Eliab.
---

# 4DMap

Four-axis temporal mapping and pattern mapping (4DM-WP-1.0). Author: **Aziel Eliab**.

**THIS IS:** an inspection coordinate frame. 4DM-CARD receipts (id, t, delta, gamma, pi, prev, src, h, note). Ops pin / span / stack / gap / fork / walk / lens / class / cohort / absence / cap / join. Typed joins T↔Δ, Δ↔Γ, Γ↔Π, T↔Π. Fail-closed SHA-256. Forks kept. ZionPattern cap 75%. Π-EMPTY when the lens is silent.

**THIS IS NOT:** a truth engine; Lumen; GIS 4D; a Node Gate; certified forensics; an identity store. Receipts are not truth. No legal name, home, or county on cards. Π→T backdate, intent, and identity leak refuse.

Always send a normal `User-Agent` (for example `Mozilla/5.0`). Cloudflare Workers may 403 empty agents.

## When to call it

- Pin a clock, span an interval, join two cards, walk a prev chain, or apply a lens.
- Health / skill / OpenAPI. Never invent a person, a county, or a backdated clock.

Hosted `/v1/{op}` is stateless. Cards travel in the JSON body. The Worker does not store a map.

## Endpoints (this Worker)

Host: `https://4dmap-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster. |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. |
| GET | `/v1/example` | Synthetic cards. Not a real case. |
| POST | `/v1/{pin,span,stack,gap,fork,walk,lens,class,cohort,absence,cap,join}` | Stateless card ops. |

OpenAPI: `https://4dmap-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP: `POST https://4dmap-download-tracker.vibelock.workers.dev/mcp`
also `POST https://aziel-runtime.vibelock.workers.dev/mcp`

FragGate is LIVE: `fraggate_list` → `fraggate_describe slug=4dmap` → `fraggate_call` (`card_new` / `pin` / `span` / `join` / `walk` / `list` / `verify_hash`). Softwares bucket **Plain**. Hubs list 4DMap.

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/health

curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/mesh

curl -s -A 'Mozilla/5.0' -X POST https://4dmap-download-tracker.vibelock.workers.dev/v1/pin \
  -H 'content-type: application/json' \
  -d '{"t":"2026-09-10T00:00:00Z","src":"synthetic","note":"synthetic T pin"}'
```

## Use with AI clients

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Import the catalog OpenAPI as a custom tool, GPT Action, or HTTP tool. Connect MCP remotes in Cursor, Glama, and other MCP clients.

## Honest banner

Receipts are not truth. Not Lumen. Not certified forensics. Not GIS 4D. Not a Node Gate.

Paper: 4DM-WP-1.0

Forks are welcome and always allowed.

Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). GET never enables. QNS-CD-1.0 is a hub cite / Worker mesh cross-map only.
