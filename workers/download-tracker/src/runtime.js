/**
 * 4DMap hosted runtime. Stateless /v1. Never stores a map. Never increments DOWNLOADS.
 * /v1/mesh/* PROXY handled in index.js before this catch-all.
 * Author: Aziel Eliab only.
 */
import { meshOpenApiPaths, meshPointer } from "./mesh.js";
import {
  AUTHOR,
  BUCKET,
  CATALOG,
  DISCOVERY,
  GUARDRAIL,
  HOST,
  LIMITATION,
  LIVE_OPS,
  MASTER33,
  PIPELINE,
  PIPELINE_NOTE,
  PRODUCT,
  PRODUCT_NAME,
  SPEC,
  VERSION,
  CardError,
  displayEnvelope,
  runOp,
} from "./engine.js";

const PROTOCOL = "2025-03-26";

export const SKILL = `---
name: 4DMap
description: Use this when inspecting time as four axes (T clock, Δ interval, Γ trajectory, Π pattern). Inspection coordinate frame, not a truth engine, not Lumen, not GIS, not a Node Gate. Hosted /v1 via this Worker and aziel-runtime FragGate slug=4dmap. Dual surface: Worker / Flutter / counted download stay complete human software; agents see display envelopes in chat. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. GET /v1/mesh never enables. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 cite only. No Node Gate. Author Aziel Eliab.
---

# 4DMap

Four-axis temporal mapping and pattern mapping (4DM-WP-1.0). Author: **Aziel Eliab**.

**THIS IS:** an inspection coordinate frame (0.3.0). 4DM-CARD receipts (id, t, delta, gamma, pi, prev, src, h, note) plus axis receipts. Ops pin / span / stack / gap / fork / walk / lens / class / cohort / absence / cap / join plus card_new / card_export / card_import / frame_status / axis_describe / walk_trace / verify_chain / verify_hash / memory_cite / memory_observe / library_pin / plot / possibility / pattern_recall / lattice_tip / poison_refuse / neighbor_cite. Library ingest is paper date × event × lat/lon or gazetteer. Possibility and Bayesian stay labeled separately. Adaptive pattern memory walks the hashchain lattice — not a detached ML store. Typed joins T↔Δ, Δ↔Γ, Γ↔Π, T↔Π cite TemporalLock / StaticClock / ChronoLock / TrajectoryLock / SpectralLock as inspection inputs only. Optional AKM-TRIAD-1.0 fabric cite/observe (not a Softwares-tab product; posterior ≠ truth). Fail-closed SHA-256. Forks kept. ZionPattern cap 75%. Π-EMPTY when the lens is silent. Not a Softwares door (\`domains_are_doors:false\`). FragGate is THE single door. Growth-ON.

**THIS IS NOT:** a truth engine; Lumen; GIS 4D; a Node Gate; certified forensics; an identity store. Receipts are not truth. No legal name, home, or county on cards. Π→T backdate, intent, and identity leak refuse.

Always send a normal \`User-Agent\` (for example \`Mozilla/5.0\`). Cloudflare Workers may 403 empty agents.

## When to call it

- Pin a clock, span an interval, join two cards, walk a prev chain, or apply a lens.
- Health / skill / OpenAPI. Never invent a person, a county, or a backdated clock.

Hosted \`/v1/{op}\` is stateless. Cards travel in the JSON body. The Worker does not store a map.

## Endpoints (this Worker)

Host: \`https://4dmap-download-tracker.vibelock.workers.dev\`

| Method | Path | What |
|--------|------|------|
| GET | \`/v1/health\` | Liveness. Does not increment downloads. |
| GET | \`/v1/skill\` | This markdown. Does not increment downloads. |
| GET | \`/v1/mesh\` | PROXY suite mesh status. Default OFF. Never enables. |
| GET | \`/v1/mesh/nodes\` | PROXY Live Nodes roster. |
| POST | \`/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}\` | PROXY. Bearer required to enable. |
| GET | \`/v1/example\` | Synthetic cards. Not a real case. |
| GET | \`/v1/frame_status\` | MASTER-33 inspection-frame status. Not a door. |
| GET | \`/v1/axis_describe\` | T/Δ/Γ/Π + companion cites. |
| GET | \`/llms.txt\` | Agent-oriented skill text. |
| POST | \`/v1/{pin,span,stack,gap,fork,walk,lens,class,cohort,absence,cap,join}\` | Stateless card ops. |
| POST | \`/v1/{card_new,card_pin,card_span,card_join,card_walk,card_list,verify_hash}\` | FragGate aliases. |
| POST | \`/v1/{card_export,card_import,frame_status,axis_describe,walk_trace,verify_chain}\` | 0.2.0 read/write ops. |
| POST | \`/v1/{memory_cite,memory_observe}\` | Optional AKM-TRIAD-1.0 fabric cite/observe. Not a Softwares slug. |
| POST | \`/v1/{library_pin,plot,possibility,pattern_recall,lattice_tip,poison_refuse,neighbor_cite}\` | Library pin frames + lattice memory. Growth-ON. |

OpenAPI: \`https://4dmap-download-tracker.vibelock.workers.dev/openapi.json\`

Catalog OpenAPI: \`https://aziel-runtime.vibelock.workers.dev/openapi.json\`

MCP: \`POST https://4dmap-download-tracker.vibelock.workers.dev/mcp\`
also \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`

FragGate is LIVE on aziel-runtime: \`fraggate_list\` → \`fraggate_describe slug=4dmap\` → \`fraggate_call\` (\`card_new\` / \`card_pin\` / \`card_span\` / \`card_join\` / \`card_walk\` / \`card_list\` / \`verify_hash\` plus \`card_export\` / \`card_import\` / \`frame_status\` / \`axis_describe\` / \`walk_trace\` / \`verify_chain\` / \`memory_cite\` / \`memory_observe\` / \`library_pin\` / \`plot\` / \`possibility\` / \`pattern_recall\` / \`lattice_tip\` / \`poison_refuse\` / \`neighbor_cite\`). Softwares bucket **Plain**. Hubs list 4DMap. Agent path remains FragGate only. 4DMap is not an extra door. AKM-TRIAD-1.0 is LIVE fabric (not a Softwares-tab product): optional card cite/observe only; posterior ≠ truth; no history rewrite. Pattern recollection stays on the hashchain lattice.

Demo path (library upload → 4DMap pin): ingest \`{event, date, lat, lon|gazetteer_id, surface:REAL|MOCK}\` → \`POST /v1/library_pin\` → 4DM-PIN-FRAME on T. Cite https://www.azielcorpuslibrary.net/map and \`/v1/verify-geo\`. Scores are not courtroom proof.

## How to call (Mozilla/5.0)

\`\`\`bash
curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://4dmap-download-tracker.vibelock.workers.dev/v1/mesh
curl -s -A 'Mozilla/5.0' -X POST https://4dmap-download-tracker.vibelock.workers.dev/v1/pin \\
  -H 'content-type: application/json' \\
  -d '{"t":"2026-09-10T00:00:00Z","src":"synthetic","note":"synthetic T pin"}'
\`\`\`

## Use with AI clients

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Import the catalog OpenAPI as a custom tool, GPT Action, or HTTP tool. Connect MCP remotes in Cursor, Glama, and other MCP clients.

## Honest banner

Receipts are not truth. Not Lumen. Not certified forensics. Not GIS 4D. Not a Node Gate.

Paper: 4DM-WP-1.0

Forks are welcome and always allowed.

Worker homepage Live Nodes strip polls \`GET /v1/mesh\` (default OFF). GET never enables. QNS-CD-1.0 is a hub cite / Worker mesh cross-map only.
`;

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, Authorization, X-Aziel-Runtime-Token, User-Agent",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function openapiSpec(origin) {
  const opDoc = (name, summary) => ({
    post: {
      operationId: "fourdmap_" + name,
      summary,
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "4DMap envelope" }, "400": { description: "refused" } },
    },
  });
  return {
    openapi: "3.1.0",
    info: {
      title: "4DMap runtime",
      version: VERSION,
      summary: "Inspection coordinate frame. Not a truth engine.",
      description: LIMITATION + " Suite mesh /v1/mesh/* PROXY to aziel-runtime. GET never enables. Softwares bucket Plain. Aziel Eliab only.",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: AUTHOR, url: "https://github.com/AzielEliab/4dmap" },
    },
    servers: [{ url: origin }],
    paths: {
      "/v1/health": { get: { operationId: "fourdmap_health", summary: "Liveness. Does not increment download KV.", responses: { "200": { description: "ok" } } } },
      "/v1/skill": { get: { operationId: "fourdmap_skill", summary: "Return 4DMap skill markdown.", responses: { "200": { description: "text/markdown" } } } },
      "/v1/example": { get: { operationId: "fourdmap_example", summary: "Synthetic cards. Not a real case.", responses: { "200": { description: "example" } } } },
      "/v1/pin": opDoc("pin", "Pin a T clock card"),
      "/v1/span": opDoc("span", "Span a Δ interval"),
      "/v1/stack": opDoc("stack", "Stack a Γ trajectory"),
      "/v1/gap": opDoc("gap", "Mark a Δ gap"),
      "/v1/fork": opDoc("fork", "Fork a card; both branches kept"),
      "/v1/walk": opDoc("walk", "Walk prev hashes from a tip"),
      "/v1/lens": opDoc("lens", "Apply a lens; silent → Π-EMPTY"),
      "/v1/class": opDoc("class", "Π class (not identity)"),
      "/v1/cohort": opDoc("cohort", "Π cohort"),
      "/v1/absence": opDoc("absence", "Absence / silent lens → Π-EMPTY"),
      "/v1/cap": opDoc("cap", "ZionPattern cap 75%"),
      "/v1/join": opDoc("join", "Typed join; Π→T backdate refuses"),
      "/v1/list": opDoc("list", "List cards + forks"),
      "/v1/card_new": opDoc("card_new", "Create a 4DM-CARD on any axis"),
      "/v1/card_pin": opDoc("card_pin", "FragGate alias of pin"),
      "/v1/card_span": opDoc("card_span", "FragGate alias of span"),
      "/v1/card_join": opDoc("card_join", "FragGate alias of join"),
      "/v1/card_walk": opDoc("card_walk", "FragGate alias of walk"),
      "/v1/card_list": opDoc("card_list", "FragGate alias of list"),
      "/v1/verify_hash": opDoc("verify_hash", "Verify one 4DM-CARD hash"),
      "/v1/card_export": opDoc("card_export", "Export 4DM-CARD JSON"),
      "/v1/card_import": opDoc("card_import", "Import 4DM-CARD JSON (fail-closed)"),
      "/v1/frame_status": {
        get: { operationId: "fourdmap_frame_status_get", summary: "MASTER-33 inspection-frame status. Not a door.", responses: { "200": { description: "frame" } } },
        post: opDoc("frame_status", "MASTER-33 inspection-frame status. Not a door.").post,
      },
      "/v1/axis_describe": {
        get: { operationId: "fourdmap_axis_describe_get", summary: "Describe T/Δ/Γ/Π + companion cites.", responses: { "200": { description: "axes" } } },
        post: opDoc("axis_describe", "Describe T/Δ/Γ/Π + companion cites.").post,
      },
      "/v1/walk_trace": opDoc("walk_trace", "Walk prev chain with axis receipts"),
      "/v1/verify_chain": opDoc("verify_chain", "Verify a prev-hash chain fail-closed"),
      "/v1/memory_cite": opDoc("memory_cite", "Optional AKM-TRIAD-1.0 fabric cite. Not a Softwares slug. Card unchanged."),
      "/v1/memory_observe": opDoc("memory_observe", "Build a FragGate memory_observe packet from a 4DM-CARD. Posterior ≠ truth."),
      "/v1/library_pin": opDoc("library_pin", "Pin a library ingest (paper date × event × lat/lon or gazetteer). REAL vs MOCK labeled."),
      "/v1/plot": opDoc("plot", "Plot lattice pins and trajectories. Not GIS."),
      "/v1/possibility": opDoc("possibility", "Labeled possibility + Bayesian hooks. Never collapsed. Lattice-linked receipt."),
      "/v1/pattern_recall": opDoc("pattern_recall", "Recall recurring patterns from the hashchain lattice. Not a detached ML store."),
      "/v1/lattice_tip": opDoc("lattice_tip", "List append-only lattice tips (prev-hash)."),
      "/v1/poison_refuse": opDoc("poison_refuse", "Append a poison feature hash to the refuse set. Hash only. NO-REWRITE."),
      "/v1/neighbor_cite": opDoc("neighbor_cite", "Cite Aziel Digital Library + inspection companions on a declared card."),
      "/llms.txt": { get: { operationId: "fourdmap_llms", summary: "Agent-oriented skill text.", responses: { "200": { description: "text" } } } },
      ...meshOpenApiPaths(),
    },
  };
}

function aiHtml(origin) {
  return `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>4DMap — AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 44rem; margin: 3rem auto; padding: 0 1.25rem; background: #0b0b0b; color: #e8e0d0; }
  a { color: #c9a227; }
  .banner { border: 1px solid #c9a227; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
  pre { background: #141414; padding: .85rem 1rem; overflow: auto; border-radius: 8px; }
</style>
<body>
<h1>4DMap runtime</h1>
<p class="banner">${LIMITATION}</p>
<p>Softwares bucket: Plain. Author Aziel Eliab only.</p>
<p>Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>MCP: POST <code>${origin}/mcp</code> · Catalog: <a href="${CATALOG}/">${CATALOG}</a> · FragGate <code>slug=4dmap</code> LIVE</p>
<p>Suite mesh: <code>GET ${origin}/v1/mesh</code> PROXY. Default OFF. GET never enables. No Node Gate.</p>
<pre>curl -A Mozilla/5.0 ${origin}/v1/health
curl -A Mozilla/5.0 -X POST ${origin}/v1/pin -H 'content-type: application/json' \\
  -d '{"t":"2026-09-10T00:00:00Z","src":"synthetic","note":"synthetic T pin"}'</pre>
<p>GET/POST under <code>/v1</code> never increment the download counter. Hosted never stores a map.</p>
<p><a href="/openapi.json">openapi.json</a> · <a href="/v1/health">health</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/">Home</a></p>
</body></html>`;
}

function mcpTools() {
  return LIVE_OPS.filter((op) => op !== "health" && op !== "skill").map((op) => ({
    name: "fourdmap_" + op,
    description: "4DMap " + op + ". Inspection frame. Not a truth engine. Author Aziel Eliab.",
    inputSchema: { type: "object", additionalProperties: true },
  })).concat([
    { name: "fourdmap_health", description: "Liveness. Does not increment download KV.", inputSchema: { type: "object" } },
    { name: "fourdmap_skill", description: "Return 4DMap skill markdown.", inputSchema: { type: "object" } },
  ]);
}

async function handleMcp(request) {
  if (request.method === "GET") {
    return json({
      ok: true,
      transport: "JSON-RPC MCP-over-HTTP",
      endpoint: "POST /mcp",
      methods: ["initialize", "tools/list", "tools/call", "ping"],
      auth: "none (public)",
      limitation: LIMITATION,
    });
  }
  if (request.method !== "POST") return json({ error: "POST JSON-RPC to /mcp" }, 405);
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
  }
  const id = body && body.id !== undefined ? body.id : null;
  const method = body && body.method;
  const params = (body && body.params) || {};
  const result = (value) => json({ jsonrpc: "2.0", id, result: value });
  if (method === "initialize") {
    return result({
      protocolVersion: PROTOCOL,
      capabilities: { tools: { listChanged: false } },
      serverInfo: { name: PRODUCT, version: VERSION },
      instructions: LIMITATION,
    });
  }
  if (method === "notifications/initialized" || method === "initialized") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (method === "ping") return result({});
  if (method === "tools/list") return result({ tools: mcpTools() });
  if (method === "tools/call") {
    const name = params.name;
    const args = params.arguments || params.input || {};
    let payload;
    try {
      if (name === "fourdmap_health") {
        payload = { ok: true, product: PRODUCT, version: VERSION, kv_increment: false, stored: false, bucket: BUCKET, limitation: LIMITATION };
      } else if (name === "fourdmap_skill") {
        payload = { markdown: SKILL, kv_increment: false, limitation: LIMITATION };
      } else if (typeof name === "string" && name.startsWith("fourdmap_")) {
        const op = name.slice("fourdmap_".length);
        const raw = await runOp(op, args, args.cards || []);
        payload = displayEnvelope(op, raw);
      } else {
        payload = { error: "unknown tool", name };
      }
    } catch (err) {
      payload = err instanceof CardError ? err.asDict() : { error: String(err && err.message ? err.message : err), limitation: LIMITATION };
    }
    return result({ content: [{ type: "text", text: JSON.stringify(payload) }], isError: Boolean(payload.error || payload.refused) });
  }
  return json({ jsonrpc: "2.0", id, error: { code: -32601, message: "Method not found: " + String(method) } });
}

export async function handleRuntimeApi(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/mcp") return handleMcp(request);
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true,
      product: PRODUCT,
      name: PRODUCT_NAME,
      version: VERSION,
      spec: SPEC,
      bucket: BUCKET,
      runtime: true,
      kv_increment: false,
      stored: false,
      truth_engine: false,
      lumen: false,
      gis: false,
      node_gate: false,
      certified_forensics: false,
      domains_are_doors: false,
      sequential_gate: false,
      software_door: false,
      role: "inspection",
      master: "MASTER-33",
      limitation: LIMITATION,
      guardrail: GUARDRAIL,
      pipeline: PIPELINE,
      pipeline_note: PIPELINE_NOTE,
      catalog: CATALOG,
      author: AUTHOR,
      mesh: meshPointer(),
      ops: LIVE_OPS,
      frame: MASTER33,
      growth: DISCOVERY.growth,
      discovery: DISCOVERY,
    });
  }
  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "private, no-store",
        "X-KV-Increment": "false",
        ...corsHeaders(),
      },
    });
  }
  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(originOf(request)));
  }
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return html(aiHtml(originOf(request)));
  }
  if (path === "/v1/mesh" || path.startsWith("/v1/mesh/")) return null;
  if ((path === "/llms.txt" || path === "/llms") && request.method === "GET") {
    return new Response(SKILL, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "private, no-store",
        ...corsHeaders(),
      },
    });
  }
  if (path === "/v1/frame_status" && request.method === "GET") {
    try {
      return json(displayEnvelope("frame_status", await runOp("frame_status", {}, [])));
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 400);
    }
  }
  if (path === "/v1/axis_describe" && request.method === "GET") {
    try {
      const axis = url.searchParams.get("axis") || "";
      return json(displayEnvelope("axis_describe", await runOp("axis_describe", axis ? { axis } : {}, [])));
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 400);
    }
  }
  if (path === "/v1/example" && request.method === "GET") {
    try {
      return json(await runOp("example", {}, []));
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err) }, 400);
    }
  }
  if (path.startsWith("/v1/") && request.method === "POST") {
    const op = path.slice("/v1/".length);
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "JSON body required", limitation: LIMITATION, stored: false }, 400);
    }
    try {
      const raw = await runOp(op, body.payload || body, body.cards || []);
      return json(displayEnvelope(op, raw));
    } catch (err) {
      if (err instanceof CardError) return json({ ...err.asDict(), limitation: LIMITATION }, 400);
      return json({ error: String(err && err.message ? err.message : err), stored: false, limitation: LIMITATION }, 400);
    }
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health  GET /v1/skill  GET /v1/example  GET /v1/frame_status  GET /v1/axis_describe  POST /v1/pin|/span|/join|/walk_trace|/card_export|/verify_chain  GET /v1/mesh", limitation: LIMITATION, stored: false }, 404);
  }
  return null;
}
