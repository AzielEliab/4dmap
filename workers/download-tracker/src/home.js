/**
 * 4DMap Worker homepage — complete human software surface.
 * Four-axis board + card list + pin/span/join forms.
 * Author: Aziel Eliab only. Apache-2.0.
 */
import { GUARDRAIL, LIMITATION, PIPELINE, PIPELINE_NOTE } from "./engine.js";

export const HOST = "https://4dmap-download-tracker.vibelock.workers.dev";
export const GITHUB_REPO = "https://github.com/AzielEliab/4dmap";
export const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
export const PAGE_TITLE = "4DMap — Aziel Eliab";
export const SEO_DESCRIPTION =
  "4DMap by Aziel Eliab: four-axis inspection coordinate frame (T clock, Δ interval, Γ trajectory, Π pattern). Not a truth engine, not Lumen, not GIS, not a Node Gate.";
export const INSTALL_LINE = "curl -fsSL https://4dmap-download-tracker.vibelock.workers.dev/install.sh | bash";
export const DEFAULT_ASSET = "4dmap-0.3.0.tar.gz";

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function jsonLdDocument() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "4DMap",
    softwareVersion: "0.3.0",
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Cloudflare Workers",
    author: { "@type": "Person", name: "Aziel Eliab", url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    downloadUrl: HOST + "/download",
    license: "https://www.apache.org/licenses/LICENSE-2.0",
    url: HOST + "/",
    description: SEO_DESCRIPTION,
  };
}

function breakdownList(breakdown) {
  if (!Array.isArray(breakdown) || !breakdown.length) return "<li>none yet</li>";
  return breakdown
    .map((b) => {
      return `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${escapeHtml(b.count)}</li>`;
    })
    .join("");
}

export function renderHomepage({ views, downloads, breakdown, github, asset }) {
  const v = Number(views || 0).toLocaleString("en-US");
  const n = Number(downloads || 0).toLocaleString("en-US");
  const gh = github || {};
  const ld = JSON.stringify(jsonLdDocument());
  const rows = breakdownList(breakdown);
  const assetName = escapeHtml(asset || DEFAULT_ASSET);

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${PAGE_TITLE}</title>
<meta name="description" content="${escapeHtml(SEO_DESCRIPTION)}">
<meta name="author" content="Aziel Eliab">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="icon" href="/sigil.png" type="image/png">
<link rel="sitemap" type="application/xml" href="${HOST}/sitemap.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="${PAGE_TITLE}">
<meta property="og:description" content="${escapeHtml(SEO_DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root { color-scheme: dark; --bg:#0b0b0b; --surface:#141414; --ink:#e8e0d0; --muted:#9a917f; --gold:#c9a227; --line:#3d3420; --ok:#7dcf9a; --err:#d27a7a; }
  * { box-sizing: border-box; }
  body { margin: 0 auto; max-width: 56rem; padding: 1.6rem 1.1rem 4rem; background: var(--bg); color: var(--ink); font: 16px/1.45 system-ui, sans-serif; }
  .brandrow { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 1rem; }
  .brandmark { width:40px; height:40px; border-radius:10px; box-shadow:0 0 0 1px #d4af3733; }
  .stamp { margin:0; color:var(--gold); font-size:.88rem; }
  .tag { margin:.15rem 0 0; color:var(--muted); font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }
  h1 { font-size:2rem; margin:0 0 .15rem; color:var(--gold); }
  .byline { margin:0 0 .4rem; color:var(--gold); }
  .motto { color:var(--muted); margin:0 0 1rem; }
  .banner { border:1px solid var(--gold); background:#241c0d; color:#f0d78c; padding:.85rem 1rem; border-radius:8px; margin:0 0 1rem; font-size:.92rem; }
  .pipe { white-space:pre-wrap; font:12px/1.45 ui-monospace, Menlo, Consolas, monospace; color:var(--muted); border:1px dashed var(--line); padding:.75rem .9rem; border-radius:8px; margin:0 0 1rem; background:#100e0a; }
  #meshStrip { border:1px solid var(--gold); border-radius:12px; padding:.85rem 1rem; background:var(--surface); margin:0 0 1.2rem; display:flex; flex-wrap:wrap; align-items:center; gap:.7rem 1rem; font-size:.88rem; color:var(--muted); }
  #meshStrip .live b, #meshStrip .rollup b { color:var(--gold); }
  #meshStrip button { font:700 .78rem/1 ui-monospace,monospace; height:2rem; padding:0 .75rem; border-radius:8px; background:#101010; color:var(--ink); border:1px solid var(--gold); cursor:pointer; }
  #meshStrip input { width:10rem; padding:.4rem .55rem; border:1px solid var(--gold); border-radius:8px; background:#0e0e0e; color:var(--ink); font:inherit; }
  .card { border:1px solid var(--line); border-radius:12px; padding:1.15rem 1.25rem; background:var(--surface); margin:0 0 1.1rem; }
  .nums { display:grid; grid-template-columns:1fr 1fr; gap:.8rem; }
  .count { font-size:2.1rem; font-variant-numeric:tabular-nums; font-weight:700; margin:0; }
  .count span { display:block; font-size:.95rem; font-weight:500; color:var(--muted); }
  .btns { display:grid; grid-template-columns:1fr 1fr; gap:.75rem; margin:.8rem 0; }
  @media (max-width:620px) { .btns, .axes { grid-template-columns:1fr 1fr !important; } }
  a.btn, button.btn { display:block; width:100%; text-align:center; font:inherit; font-size:1.1rem; font-weight:750; padding:1rem; border-radius:10px; border:0; cursor:pointer; text-decoration:none; }
  a.btn.primary { background:var(--ink); color:var(--bg); }
  button.btn.install, button.gold { background:var(--gold); color:#14110a; }
  .meta, .iso, .kid, .note { color:var(--muted); font-size:.92rem; }
  .meta a { color:#e6d08a; }
  .axes { display:grid; grid-template-columns:repeat(4,1fr); gap:.55rem; }
  .axis { border:1px solid var(--line); border-radius:10px; padding:.65rem; min-height:8rem; background:#100e0a; }
  .axis h2 { margin:0 0 .45rem; color:var(--gold); font-size:.95rem; }
  .tick { border:1px solid var(--line); border-radius:8px; padding:.4rem .45rem; margin:.3rem 0; font-size:.78rem; }
  .tick code { color:var(--gold); }
  label { display:block; color:var(--muted); font-size:.85rem; margin:.35rem 0 .15rem; }
  input, select { width:100%; padding:.45rem .55rem; border:1px solid var(--gold); border-radius:8px; background:#0e0e0e; color:var(--ink); font:inherit; }
  .inline { display:grid; grid-template-columns:1fr 1fr auto; gap:.45rem; align-items:end; }
  .inline4 { display:grid; grid-template-columns:1fr 1fr 1fr auto; gap:.45rem; align-items:end; }
  @media (max-width:720px) { .inline, .inline4 { grid-template-columns:1fr; } }
  textarea { width:100%; min-height:6rem; padding:.55rem; border:1px solid var(--gold); border-radius:8px; background:#0e0e0e; color:var(--ink); font:12px/1.4 ui-monospace, Menlo, Consolas, monospace; }
  .receipt { border:1px solid var(--line); border-radius:8px; padding:.45rem .55rem; margin:.35rem 0; font-size:.78rem; }
  .receipt b { color:var(--gold); }
  pre { background:#0e0e0e; padding:.7rem .85rem; overflow:auto; border-radius:8px; font-size:.8rem; }
  .plot { width:100%; height:220px; border:1px solid var(--line); border-radius:10px; background:#100e0a; }
  .scores { display:grid; grid-template-columns:1fr 1fr; gap:.55rem; margin:.6rem 0; }
  .scorebox { border:1px solid var(--line); border-radius:8px; padding:.55rem .65rem; font-size:.82rem; }
  .scorebox b { color:var(--gold); }
  .mock { color:#9a917f; }
  .real { color:var(--ok); }
  footer { color:var(--muted); font-size:.88rem; margin-top:1.5rem; }
</style>
</head>
<body>
  <header class="brandrow">
    <img class="brandmark" src="/sigil.png" width="40" height="40" alt="">
    <div>
      <p class="stamp">Aziel Eliab</p>
      <p class="tag">v0.3.0 · 4DM-WP-1.0 · Plain · Apache-2.0 · inspection frame · Growth-ON</p>
    </div>
  </header>
  <h1>4DMap</h1>
      <p class="byline">Aziel Eliab only</p>
  <p class="motto">Lamb Lens: Service → Clarity → Peace.</p>
  <p class="motto">Four-axis inspection coordinate frame. T Clock · Δ Interval · Γ Trajectory · Π Pattern. Not a truth engine.</p>
  <p class="banner" role="note">${escapeHtml(LIMITATION)}</p>
  <p class="note">Pipeline strip — 4DMap sits in the Internal Domain Layer as a read-side inspection frame (domains_are_doors:false), not a hop gate.</p>
  <pre class="pipe" id="pipeline">${escapeHtml(PIPELINE)}

${escapeHtml(PIPELINE_NOTE)}</pre>

  <div id="meshStrip" aria-label="Suite Live Nodes">
    <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
    <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.</div>
    <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
    <div>No Node Gate · GET never enables · QNS-CD-1.0 cite · Plain (not Gate/Lock) · Aziel Eliab only</div>
    <div>
      <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
      <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
      <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
      <button id="meshJoin" type="button" title="Join as 4dmap. Refused while mesh is OFF.">Join</button>
      <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
    </div>
    <p id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cross-map · not AnonBroadcast · not a Node Gate · no public qnsd proxy · 4DMap photons are not on QNS/QNM</p>
  </div>

  <section class="card" id="install">
    <div class="nums">
      <p class="count">${v}<span>Views</span></p>
      <p class="count">${n}<span>Downloads</span></p>
    </div>
    <p class="kid"><strong>Counted download.</strong> Download saves the gzip (the Downloads number goes up). One-click install copies a Terminal command. After it finishes: <code>4dmap ui</code> then open http://127.0.0.1:8844.</p>
    <div class="btns">
      <a class="btn primary" href="/download?asset=${assetName}">Download</a>
      <button type="button" class="btn install" id="install-btn">One-click install</button>
    </div>
    <pre id="install-cmd">${INSTALL_LINE}</pre>
    <p class="iso">Isolated counter: Worker <code>4dmap-download-tracker</code>, project <code>4dmap</code>, KV <code>4DMAP_DOWNLOADS</code>. <code>/v1</code> does not increment. Hosted never stores a map.</p>
    <p class="meta">GitHub: stars ${escapeHtml(gh.stars || 0)} · forks ${escapeHtml(gh.forks || 0)} · watchers ${escapeHtml(gh.watchers || 0)} · release assets ${escapeHtml(gh.release_download_count || 0)}</p>
    <p class="meta"><a href="${GITHUB_REPO}">GitHub</a> · <a href="/stats">JSON stats</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/ai">AI runtime</a> · <a href="${CATALOG}">Catalog</a></p>
    <h2>Per repo / branch / fork</h2>
    <ul>${rows}</ul>
  </section>

  <section class="card" id="board">
    <h2>Four-axis board</h2>
    <p class="note">Cards live in this browser. Hosted API is stateless. Fail-closed hashes. Forks kept. Π-EMPTY when the lens is silent. Companion src values cite TemporalLock / StaticClock / ChronoLock / TrajectoryLock / SpectralLock as inspection inputs only — products are not merged. Library pins use paper date × event × geo. Pattern memory is the hashchain lattice (tips / prev-hash), not a detached ML store.</p>
    <div class="axes">
      <div class="axis" id="col-T"><h2>T Clock</h2></div>
      <div class="axis" id="col-DELTA"><h2>Δ Interval</h2></div>
      <div class="axis" id="col-GAMMA"><h2>Γ Trajectory</h2></div>
      <div class="axis" id="col-PI"><h2>Π Pattern</h2></div>
    </div>

    <form id="pin-form" autocomplete="off">
      <label for="pin-t">Pin — T time / Δ change / Γ geometry / Π path</label>
      <div class="inline4">
        <input id="pin-t" placeholder="2026-09-10T00:00:00Z or value">
        <select id="pin-axis" aria-label="pin axis">
          <option value="T">T Clock</option>
          <option value="DELTA">Δ Interval</option>
          <option value="GAMMA">Γ Trajectory</option>
          <option value="PI">Π Pattern</option>
        </select>
        <select id="pin-src" aria-label="pin src cite">
          <option value="operator">operator</option>
          <option value="temporallock">TemporalLock (cite)</option>
          <option value="staticclock">StaticClock (cite)</option>
          <option value="chronolock">ChronoLock (cite)</option>
          <option value="trajectorylock">TrajectoryLock (cite)</option>
          <option value="spectrallock">SpectralLock (cite)</option>
          <option value="synthetic">synthetic</option>
          <option value="aziel-corpus">Aziel Digital Library (cite)</option>
        </select>
        <button class="btn gold" type="submit">Pin</button>
      </div>
    </form>
    <form id="library-form" autocomplete="off">
      <label>Library upload → 4DMap pin — paper date × event × lat/lon or gazetteer. Never upload time. REAL vs MOCK labeled.</label>
      <div class="inline4">
        <input id="lib-event" placeholder="event (paper)">
        <input id="lib-date" placeholder="1912-04-15 paper date">
        <select id="lib-surface" aria-label="REAL or MOCK">
          <option value="MOCK">MOCK</option>
          <option value="REAL">REAL</option>
        </select>
        <button class="btn gold" type="submit">Library pin</button>
      </div>
      <div class="inline4">
        <input id="lib-lat" placeholder="lat">
        <input id="lib-lon" placeholder="lon">
        <input id="lib-gaz" placeholder="gazetteer id (opaque)">
        <input id="lib-doc" placeholder="doc id (optional)">
      </div>
      <p class="note">Sister path: Aziel Digital Library Temporal Map <a href="https://www.azielcorpuslibrary.net/map">/map</a> · <a href="https://www.azielcorpuslibrary.net/v1/verify-geo">/v1/verify-geo</a>. Not GIS. Scores are not courtroom proof.</p>
    </form>
    <div class="scores">
      <div class="scorebox" id="score-possibility"><b>possibility</b> (time×geo) — no score yet</div>
      <div class="scorebox" id="score-bayesian"><b>bayesian</b> (cited) — none</div>
    </div>
    <svg class="plot" id="pin-plot" viewBox="0 0 560 220" role="img" aria-label="Inspection pin plot, not GIS"></svg>
    <p class="note" id="plot-note">Inspection plot. Not GIS 4D. Pins labeled REAL or MOCK.</p>
    <form id="span-form" autocomplete="off">
      <label>Span Δ — from card id → to card id (any axis pair)</label>
      <div class="inline">
        <input id="span-from" placeholder="from id">
        <input id="span-to" placeholder="to id">
        <button class="btn gold" type="submit">Span</button>
      </div>
    </form>
    <form id="join-form" autocomplete="off">
      <label>Typed join — T↔Δ, Δ↔Γ, Γ↔Π, T↔Π. Π→T backdate refuses. Companions cited, not merged.</label>
      <div class="inline">
        <input id="join-left" placeholder="left id">
        <input id="join-right" placeholder="right id">
        <select id="join-type">
          <option value="T-DELTA">T↔Δ</option>
          <option value="DELTA-GAMMA">Δ↔Γ</option>
          <option value="GAMMA-PI">Γ↔Π</option>
          <option value="T-PI">T↔Π</option>
          <option value="PI-T">Π→T (refused)</option>
        </select>
      </div>
      <p><button class="btn gold" type="submit">Join</button>
      <button class="btn gold" type="button" id="fork-btn">Fork last</button>
      <button class="btn gold" type="button" id="lens-btn">Silent lens</button>
      <button class="btn gold" type="button" id="example-btn">Load example</button></p>
    </form>
    <form id="walk-form" autocomplete="off">
      <label>Walk / trace / verify chain — tip card id</label>
      <div class="inline4">
        <input id="walk-tip" placeholder="tip id">
        <button class="btn gold" type="submit">Walk</button>
        <button class="btn gold" type="button" id="trace-btn">Walk trace</button>
        <button class="btn gold" type="button" id="chain-btn">Verify chain</button>
      </div>
    </form>
    <p>
      <button class="btn gold" type="button" id="frame-btn">Frame status</button>
      <button class="btn gold" type="button" id="axis-btn">Axis describe</button>
      <button class="btn gold" type="button" id="export-btn">Export JSON</button>
      <button class="btn gold" type="button" id="memory-cite-btn" title="Optional AKM-TRIAD-1.0 fabric cite. Not a Softwares slug.">Cite memory</button>
      <button class="btn gold" type="button" id="memory-observe-btn" title="Build FragGate memory_observe packet. Posterior ≠ truth.">Observe card</button>
      <button class="btn gold" type="button" id="plot-btn">Plot</button>
      <button class="btn gold" type="button" id="possibility-btn">Possibility hooks</button>
      <button class="btn gold" type="button" id="recall-btn">Pattern recall</button>
      <button class="btn gold" type="button" id="tip-btn">Lattice tip</button>
      <button class="btn gold" type="button" id="poison-btn">Poison refuse</button>
      <button class="btn gold" type="button" id="neighbor-btn">Neighbor cite</button>
      <button class="btn gold" type="button" id="lib-demo-btn">MOCK library demo</button>
    </p>
    <p class="note">AKM-TRIAD-1.0 is LIVE fabric behind FragGate — not a Softwares-tab product, not a second door. Cite/observe leaves the 4DM-CARD unchanged. Posterior ≠ truth. No history rewrite.</p>
    <form id="import-form" autocomplete="off">
      <label for="import-json">Import 4DM-CARD JSON (fail-closed hashes)</label>
      <textarea id="import-json" placeholder='{"cards":[...]}'></textarea>
      <p><button class="btn gold" type="submit">Import</button></p>
    </form>
    <h3>Card list · 4DM-CARD receipts</h3>
    <ol id="card-list"></ol>
    <div id="receipt-box" class="receipt" hidden></div>
    <p class="note" id="last-op">No op yet.</p>
    <pre id="last-json" hidden></pre>
    <p class="note">${escapeHtml(GUARDRAIL)}</p>
  </section>

  <section class="cite" id="cite">
    <h2>How to cite</h2>
    <p>Aziel Eliab. 4DMap. ${GITHUB_REPO}. ${HOST}.</p>
    <p>Apache-2.0. Spec 4DM-WP-1.0. Do not invent a Zenodo identifier.</p>
    <p><a href="${CATALOG}">Catalog</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${HOST}/download">Download</a> · <a href="${HOST}/cite.json">cite.json</a></p>
  </section>
  <footer>
    <p><strong>Receipts are not truth.</strong> Inspection frame only.</p>
    <p>Apache-2.0 · Aziel Eliab only · 2026 · Forks welcome and always allowed.</p>
  </footer>
  <script>
    (function () {
      var cmd = ${JSON.stringify(INSTALL_LINE)};
      var btn = document.getElementById("install-btn");
      var pre = document.getElementById("install-cmd");
      if (btn) btn.addEventListener("click", function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(cmd).then(function () { btn.textContent = "Copied! Paste in Terminal, then run 4dmap ui"; }).catch(function () {});
        } else if (pre && window.getSelection) {
          var r = document.createRange(); r.selectNodeContents(pre); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
        }
      });
    })();
    (function () {
      function $(id) { return document.getElementById(id); }
      function meshNum() {
        for (var i = 0; i < arguments.length; i++) {
          var raw = arguments[i];
          if (raw == null || raw === "") continue;
          var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
          if (Number.isFinite(n) && n >= 0) return Math.floor(n);
        }
        return 0;
      }
      function unwrapMesh(j) {
        if (!j || typeof j !== "object") return {};
        if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
        if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
        return j;
      }
      function paintMesh(raw) {
        var j = unwrapMesh(raw);
        var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
        var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
        var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
        var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
        var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
        $("meshLiveCount").textContent = String(live);
        $("qnmLive").textContent = String(live);
        $("qnmLocked").textContent = String(locked);
        $("qnmIsolated").textContent = String(isolated);
        var line = $("meshLine");
        if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.";
        else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
        else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. GET never enables.";
      }
      async function meshGet(path) {
        var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
        return r.json();
      }
      async function meshPost(path, payload) {
        var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
        return r.json();
      }
      async function refreshMesh() {
        try {
          var status = await meshGet("/v1/mesh");
          var merged = status;
          var inner = unwrapMesh(status);
          if (inner.enabled === true) {
            try { merged = Object.assign({}, inner, unwrapMesh(await meshGet("/v1/mesh/nodes"))); } catch (e) {}
          }
          paintMesh(merged);
          var nodeId = sessionStorage.getItem("fourdmap_mesh_node");
          if (inner.enabled === true && nodeId) {
            try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) {}
          }
        } catch (e) {
          paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
        }
      }
      $("meshEnable").onclick = async function () {
        var bearer = ($("meshBearer").value || "").trim();
        paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
        refreshMesh();
      };
      $("meshDisable").onclick = async function () {
        sessionStorage.removeItem("fourdmap_mesh_node");
        paintMesh(await meshPost("/v1/mesh/disable", {}));
        refreshMesh();
      };
      $("meshJoin").onclick = async function () {
        var j = await meshPost("/v1/mesh/join", { product: "4dmap", label: "4DMap Worker" });
        var inner = unwrapMesh(j);
        var id = inner.node_id || inner.id;
        if (id) sessionStorage.setItem("fourdmap_mesh_node", String(id));
        paintMesh(j);
        refreshMesh();
      };
      $("meshLeave").onclick = async function () {
        var id = sessionStorage.getItem("fourdmap_mesh_node");
        if (id) await meshPost("/v1/mesh/leave", { node_id: id });
        sessionStorage.removeItem("fourdmap_mesh_node");
        refreshMesh();
      };
      refreshMesh();
      setInterval(refreshMesh, 30000);
    })();
    (function () {
      var cards = [];
      function $(id) { return document.getElementById(id); }
      function axisOf(c) {
        if (c.delta) return "DELTA";
        if (c.gamma) return "GAMMA";
        if (c.pi && c.pi !== "Π-EMPTY") return "PI";
        return "T";
      }
      function paint() {
        ["T","DELTA","GAMMA","PI"].forEach(function (a) {
          var titles = { T:"T Clock", DELTA:"Δ Interval", GAMMA:"Γ Trajectory", PI:"Π Pattern" };
          $( "col-"+a ).innerHTML = "<h2>"+titles[a]+"</h2>";
        });
        var list = $("card-list");
        list.innerHTML = "";
        var pinIds = [];
        cards.forEach(function (c) {
          var col = $("col-"+axisOf(c));
          var d = document.createElement("div");
          d.className = "tick";
          d.innerHTML = "<code>"+(c.id||"")+"</code><br>"+String(c.src||"")+" · "+String(c.h||"").slice(0,16);
          col.appendChild(d);
          var li = document.createElement("li");
          li.textContent = (c.id||"") + " · " + axisOf(c) + " · " + (c.src||"") + " · " + String(c.h||"").slice(0,16);
          list.appendChild(li);
          if (axisOf(c) === "T") pinIds.push(c.id);
        });
        if (pinIds.length >= 2) {
          if (!$("span-from").value) $("span-from").value = pinIds[pinIds.length - 2];
          if (!$("span-to").value) $("span-to").value = pinIds[pinIds.length - 1];
        }
        if (cards.length && !$("walk-tip").value) $("walk-tip").value = cards[cards.length - 1].id;
      }
      function paintScores(inner) {
        var hooks = (inner && inner.hooks) || {};
        var pos = hooks.possibility || (inner && inner.possibility);
        var bay = hooks.bayesian || (inner && inner.bayesian);
        var pbox = $("score-possibility");
        var bbox = $("score-bayesian");
        if (pbox) {
          pbox.innerHTML = pos
            ? "<b>possibility</b> (time×geo) = " + pos.value + " · label " + pos.label + " · truth " + String(pos.truth)
            : "<b>possibility</b> (time×geo) — no score yet";
        }
        if (bbox) {
          bbox.innerHTML = bay
            ? "<b>bayesian</b> (cited) = " + bay.value + " · label " + bay.label + " · cite " + (bay.cite || "—") + " · truth false"
            : "<b>bayesian</b> (cited) — none. Not collapsed into possibility.";
        }
      }
      function paintPlot(pins, trajectories) {
        var svg = $("pin-plot");
        if (!svg) return;
        while (svg.firstChild) svg.removeChild(svg.firstChild);
        var list = pins || [];
        var geo = list.filter(function (p) { return p.lat != null && p.lon != null; });
        if (!geo.length) {
          var empty = document.createElementNS("http://www.w3.org/2000/svg", "text");
          empty.setAttribute("x", "16"); empty.setAttribute("y", "28"); empty.setAttribute("fill", "#9a917f");
          empty.textContent = "No lat/lon pins yet. Library pin or MOCK demo.";
          svg.appendChild(empty);
          return;
        }
        geo.forEach(function (p) {
          var x = 20 + ((Number(p.lon) + 180) / 360) * 520;
          var y = 20 + ((90 - Number(p.lat)) / 180) * 180;
          var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("cx", String(x)); c.setAttribute("cy", String(y)); c.setAttribute("r", "5");
          c.setAttribute("fill", p.surface === "REAL" ? "#7dcf9a" : "#c9a227");
          svg.appendChild(c);
          var t = document.createElementNS("http://www.w3.org/2000/svg", "text");
          t.setAttribute("x", String(x + 7)); t.setAttribute("y", String(y + 3)); t.setAttribute("fill", "#e8e0d0");
          t.setAttribute("font-size", "10");
          var surface = p.surface === "REAL" || p.surface === "MOCK" ? p.surface : "not labeled";
          t.textContent = surface + " " + String(p.event || p.id || "").slice(0, 22);
          svg.appendChild(t);
        });
        (trajectories || []).forEach(function (traj) {
          if (!traj || !traj.from_xy || !traj.to_xy) return;
          var x0 = 20 + ((Number(traj.from_xy.lon) + 180) / 360) * 520;
          var y0 = 20 + ((90 - Number(traj.from_xy.lat)) / 180) * 180;
          var x1 = 20 + ((Number(traj.to_xy.lon) + 180) / 360) * 520;
          var y1 = 20 + ((90 - Number(traj.to_xy.lat)) / 180) * 180;
          var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
          line.setAttribute("x1", String(x0)); line.setAttribute("y1", String(y0));
          line.setAttribute("x2", String(x1)); line.setAttribute("y2", String(y1));
          line.setAttribute("stroke", "#3d3420");
          svg.appendChild(line);
        });
      }
      function showReceipt(inner) {
        var box = $("receipt-box");
        var rec = inner && inner.receipt;
        if (!rec) { box.hidden = true; return; }
        box.hidden = false;
        box.innerHTML = "<b>4DM-CARD</b> " + (rec.glyph||"") + " " + (rec.name||"") + " · " + (rec.id||"") +
          "<br>h " + String(rec.h||"").slice(0,16) + " · src " + (rec.src||"") +
          (rec.companion ? " · cite " + rec.companion.software + " (inspection input, not a door)" : "") +
          "<br>role " + (rec.role||"inspection") + " · door " + String(rec.door) + " · truth " + String(rec.truth);
      }
      async function call(op, payload) {
        var r = await fetch("/v1/"+op, { method:"POST", headers:{"content-type":"application/json","user-agent":"Mozilla/5.0"}, body: JSON.stringify(Object.assign({}, payload, { cards: cards })) });
        var j = await r.json();
        var inner = j.result || j;
        $("last-op").textContent = op + (inner.refused ? " refused "+(inner.code||"") : " ok");
        $("last-json").hidden = false;
        $("last-json").textContent = JSON.stringify(j, null, 2);
        if (inner.card) cards.push(inner.card);
        if (op === "card_import" && Array.isArray(inner.cards)) {
          inner.cards.forEach(function (c) {
            if (!cards.some(function (x) { return x.h === c.h; })) cards.push(c);
          });
        }
        showReceipt(inner);
        paintScores(inner);
        if (inner && Array.isArray(inner.pins)) paintPlot(inner.pins, inner.trajectories);
        else {
          var frames = cards.map(function (c) { return c.t && typeof c.t === "object" ? Object.assign({ id: c.id, src: c.src }, c.t) : null; }).filter(Boolean);
          paintPlot(frames);
        }
        paint();
        return inner;
      }
      $("library-form").onsubmit = function (e) {
        e.preventDefault();
        var prev = cards.length ? cards[cards.length - 1].h : undefined;
        call("library_pin", {
          event: $("lib-event").value,
          date: $("lib-date").value,
          lat: $("lib-lat").value || undefined,
          lon: $("lib-lon").value || undefined,
          gazetteer_id: $("lib-gaz").value || undefined,
          doc_id: $("lib-doc").value || undefined,
          surface: $("lib-surface").value || "MOCK",
          src: "aziel-corpus",
          prev: prev
        });
      };
      $("pin-form").onsubmit = function (e) {
        e.preventDefault();
        var axis = $("pin-axis").value || "T";
        call("pin", { t: $("pin-t").value || new Date().toISOString(), axis: axis, src: $("pin-src").value || "operator", note: axis + " pin", value: $("pin-t").value });
      };
      $("span-form").onsubmit = function (e) {
        e.preventDefault();
        call("span", { from_id: $("span-from").value, to_id: $("span-to").value });
      };
      $("join-form").onsubmit = function (e) {
        e.preventDefault();
        call("join", { left: $("join-left").value, right: $("join-right").value, join_type: $("join-type").value });
      };
      $("walk-form").onsubmit = function (e) {
        e.preventDefault();
        call("walk", { tip: $("walk-tip").value });
      };
      $("trace-btn").onclick = function () { call("walk_trace", { tip: $("walk-tip").value }); };
      $("chain-btn").onclick = function () { call("verify_chain", { tip: $("walk-tip").value }); };
      $("frame-btn").onclick = function () { call("frame_status", {}); };
      $("axis-btn").onclick = function () { call("axis_describe", {}); };
      $("memory-cite-btn").onclick = function () { call("memory_cite", { id: $("walk-tip").value }); };
      $("memory-observe-btn").onclick = function () { call("memory_observe", { id: $("walk-tip").value }); };
      $("export-btn").onclick = async function () {
        var inner = await call("card_export", {});
        if (inner && inner.bundle) $("import-json").value = JSON.stringify(inner.bundle, null, 2);
      };
      $("import-form").onsubmit = function (e) {
        e.preventDefault();
        var raw = $("import-json").value || "{}";
        try { call("card_import", { bundle: JSON.parse(raw) }); }
        catch (err) { $("last-op").textContent = "import refused (JSON)"; }
      };
      $("fork-btn").onclick = function () {
        if (!cards.length) return;
        call("fork", { id: cards[cards.length-1].id });
      };
      $("lens-btn").onclick = function () { call("lens", { query: "" }); };
      $("plot-btn").onclick = function () { call("plot", {}); };
      $("possibility-btn").onclick = function () {
        if (!cards.length) return;
        call("possibility", { id: cards[cards.length - 1].id });
      };
      $("recall-btn").onclick = function () { call("pattern_recall", {}); };
      $("tip-btn").onclick = function () { call("lattice_tip", {}); };
      $("poison-btn").onclick = function () {
        var feat = $("lib-event").value;
        if (!feat && cards.length && cards[cards.length - 1].t && cards[cards.length - 1].t.feature_h) {
          call("poison_refuse", { feature_h: cards[cards.length - 1].t.feature_h });
          return;
        }
        call("poison_refuse", { event: feat || "operator-marked", date: $("lib-date").value || "1970-01-01", lat: $("lib-lat").value || undefined, lon: $("lib-lon").value || undefined, gazetteer_id: $("lib-gaz").value || undefined });
      };
      $("neighbor-btn").onclick = function () {
        if (!cards.length) return;
        call("neighbor_cite", { id: cards[cards.length - 1].id });
      };
      $("lib-demo-btn").onclick = function () {
        $("lib-event").value = "synthetic paper event";
        $("lib-date").value = "1912-04-15";
        $("lib-lat").value = "41.726";
        $("lib-lon").value = "-49.947";
        $("lib-surface").value = "MOCK";
        $("lib-doc").value = "AZDOC-MOCK";
        call("library_pin", {
          event: "synthetic paper event",
          date: "1912-04-15",
          lat: 41.726,
          lon: -49.947,
          surface: "MOCK",
          src: "synthetic",
          note: "MOCK library demo — not a real case",
          prev: cards.length ? cards[cards.length - 1].h : undefined
        });
      };
      $("example-btn").onclick = async function () {
        var r = await fetch("/v1/example", { headers: { "user-agent": "Mozilla/5.0" } });
        var j = await r.json();
        (j.cards || []).forEach(function (c) { cards.push(c); });
        $("last-op").textContent = "example loaded (synthetic)";
        paint();
      };
      paint();
    })();
  </script>
</body>
</html>`;
}
