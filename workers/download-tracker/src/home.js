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
    <style>
      html { overflow-x: clip; }
      #board {
        color-scheme: dark;
        --app-bg: #141414;
        --app-ink: #f4efe4;
        --app-muted: #d4cbb8;
        --app-line: #8a8172;
        --app-gold: #e0b53a;
        --app-ok: #b7ebc8;
        --app-err: #ffc9c9;
        --app-surface: #1c1c1c;
        --app-input: #101010;
        --app-on-gold: #1a1408;
      }
      @media (prefers-color-scheme: light) {
        #board {
          color-scheme: light;
          --app-bg: #fffcf7;
          --app-ink: #1c1914;
          --app-muted: #3f3a32;
          --app-line: #5c564c;
          --app-gold: #6d5200;
          --app-ok: #0d6b32;
          --app-err: #8f1d1d;
          --app-surface: #f6f3ec;
          --app-input: #ffffff;
          --app-on-gold: #fffdf8;
          background: var(--app-bg);
          color: var(--app-ink);
        }
      }
      #board :focus-visible {
        outline: 2px solid var(--app-gold);
        outline-offset: 2px;
      }
      #board #pin-form button[type="submit"]:focus-visible {
        outline: 2px solid #fffdf8;
        outline-offset: 2px;
        box-shadow: 0 0 0 4px var(--app-gold);
      }
      @media (prefers-color-scheme: light) {
        :root { color-scheme: light; }
        body { background: #f6f3ec; color: #1c1914; }
        .card, #meshStrip { background: #fffcf7; color: #1c1914; }
        .stamp, .byline, h1 { color: #6d5200; }
        .note, .meta, .iso, .kid, .motto, .tag, footer, .pipe, #meshStrip { color: #3f3a32; }
        .banner { background: #fff6df; color: #1c1914; border-color: #6d5200; }
        input, select, textarea, pre, .pipe, #meshStrip input { background: #ffffff; color: #1c1914; border-color: #5c564c; }
        a.btn.primary { background: #1c1914; color: #f6f3ec; }
        button.btn.install, button.gold { background: #6d5200; color: #fffdf8; }
        .count, #meshStrip .live b, #meshStrip .rollup b { color: #1c1914; }
        #meshStrip .live b, #meshStrip .rollup b { color: #6d5200; }
      }
      #board h2, #board h3 { color: var(--app-gold); }
      #board .note, #board .empty, #board .axis .empty { color: var(--app-muted); }
      #board .axes { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .55rem; }
      #board .axis { min-width: 0; background: var(--app-surface); color: var(--app-ink); overflow-wrap: anywhere; }
      #board .primary-pin {
        border: 1px solid var(--app-gold);
        border-radius: 12px;
        padding: .9rem 1rem 1rem;
        margin: .9rem 0 1rem;
        background: var(--app-surface);
      }
      #board .primary-pin h3 { margin: 0 0 .35rem; font-size: 1.15rem; }
      #board label { color: var(--app-muted); }
      #board input, #board select, #board textarea {
        background: var(--app-input);
        color: var(--app-ink);
        border: 1px solid var(--app-line);
        min-height: 44px;
        max-width: 100%;
      }
      #board textarea { min-height: 6rem; }
      #board .stack > * { min-width: 0; }
      #board button.btn.gold, #board button.quiet {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: auto;
        max-width: 100%;
        min-height: 44px;
        margin: 0;
        padding: .5rem .85rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 650;
        background: transparent;
        color: var(--app-ink);
        border: 1px solid var(--app-line);
        cursor: pointer;
      }
      #board #pin-form button[type="submit"] {
        display: flex;
        width: 100%;
        min-height: 48px;
        margin-top: .75rem;
        background: var(--app-gold);
        color: var(--app-on-gold);
        border: 1px solid transparent;
        font-size: 1.15rem;
        font-weight: 750;
      }
      #board button.quiet {
        border: 0;
        text-decoration: underline;
        padding-left: 0;
        padding-right: 0;
        margin-top: .35rem;
      }
      #board .toolrow { display: flex; flex-wrap: wrap; gap: .45rem; margin: .55rem 0 0; }
      #board details.fold {
        border: 1px solid var(--app-line);
        border-radius: 10px;
        padding: .2rem .85rem .75rem;
        margin: .55rem 0;
        background: var(--app-surface);
        min-width: 0;
      }
      #board details.fold > summary {
        cursor: pointer;
        min-height: 44px;
        display: flex;
        align-items: center;
        font-weight: 650;
        color: var(--app-ink);
      }
      #board .inline, #board .inline4 { display: grid; grid-template-columns: 1fr !important; gap: .45rem; }
      #board .inline > *, #board .inline4 > * { min-width: 0; }
      @media (min-width: 720px) {
        #board .inline { grid-template-columns: 1fr 1fr auto !important; }
        #board .scores { grid-template-columns: 1fr 1fr; }
      }
      @media (max-width: 720px) {
        #board .axes { grid-template-columns: 1fr 1fr !important; }
        #board .scores { grid-template-columns: 1fr; }
      }
      #board .scores { display: grid; gap: .55rem; }
      #board .scorebox { border: 1px solid var(--app-line); border-radius: 8px; padding: .55rem .65rem; color: var(--app-ink); overflow-wrap: anywhere; }
      #board .plot { width: 100%; height: auto; max-width: 100%; background: var(--app-input); display: block; }
      #board .status { color: var(--app-ink); font-size: 1rem; margin: .8rem 0 .35rem; }
      #board .status.ok { color: var(--app-ok); }
      #board .status.err { color: var(--app-err); }
      #board .receipt { color: var(--app-ink); overflow-wrap: anywhere; }
      #board pre { max-width: 100%; overflow: auto; white-space: pre-wrap; word-break: break-word; background: var(--app-input); color: var(--app-ink); }
      #board ol { padding-left: 1.2rem; overflow-wrap: anywhere; }
    </style>
    <h2>Four-axis board</h2>
    <p class="note">Cards stay in this browser for this visit. The hosted API keeps no map. Hashes fail closed. Forks are kept. A silent lens returns Π-EMPTY. Companion sources cite TemporalLock, StaticClock, ChronoLock, TrajectoryLock, and SpectralLock as inspection inputs. Library pins use a paper date, an event, and a place. Pattern memory is the hashchain lattice (tips and the previous hash).</p>
    <div class="axes">
      <div class="axis" id="col-T"><h3>T Clock</h3><p class="empty">Nothing here yet.</p></div>
      <div class="axis" id="col-DELTA"><h3>Δ Interval</h3><p class="empty">Nothing here yet.</p></div>
      <div class="axis" id="col-GAMMA"><h3>Γ Trajectory</h3><p class="empty">Nothing here yet.</p></div>
      <div class="axis" id="col-PI"><h3>Π Pattern</h3><p class="empty">Nothing here yet.</p></div>
    </div>
    <p class="empty" id="board-empty">No cards on this visit.</p>

    <form id="pin-form" class="primary-pin" autocomplete="off">
      <h3>Pin a card</h3>
      <p class="note">One step. Choose an axis, enter a value, then pin. An empty value uses the current UTC time, and the field shows that time.</p>
      <label for="pin-axis">Axis</label>
      <select id="pin-axis">
        <option value="T">T Clock</option>
        <option value="DELTA">Δ Interval</option>
        <option value="GAMMA">Γ Trajectory</option>
        <option value="PI">Π Pattern</option>
      </select>
      <label for="pin-t">Value</label>
      <input id="pin-t" placeholder="2026-09-10T00:00:00Z">
      <label for="pin-src">Source</label>
      <select id="pin-src" aria-label="pin src cite">
        <option value="operator">Operator</option>
        <option value="temporallock">TemporalLock (cite)</option>
        <option value="staticclock">StaticClock (cite)</option>
        <option value="chronolock">ChronoLock (cite)</option>
        <option value="trajectorylock">TrajectoryLock (cite)</option>
        <option value="spectrallock">SpectralLock (cite)</option>
        <option value="synthetic">Synthetic</option>
        <option value="aziel-corpus">Aziel Digital Library (cite)</option>
      </select>
      <button class="btn gold" type="submit">Pin</button>
      <button class="quiet" type="button" id="load-example">Load synthetic example</button>
    </form>

    <details class="fold" id="library-fold">
      <summary>Library upload → 4DMap pin</summary>
      <form id="library-form" autocomplete="off">
        <p class="note">Paper date, event, and place. REAL and MOCK stay labeled. Upload time is not a field.</p>
        <label for="lib-event">Event</label>
        <input id="lib-event" placeholder="event on the paper">
        <label for="lib-date">Paper date</label>
        <input id="lib-date" placeholder="1912-04-15">
        <label for="lib-surface">Label</label>
        <select id="lib-surface" aria-label="REAL or MOCK">
          <option value="MOCK">MOCK</option>
          <option value="REAL">REAL</option>
        </select>
        <label for="lib-lat">Latitude</label>
        <input id="lib-lat" placeholder="lat" inputmode="decimal">
        <label for="lib-lon">Longitude</label>
        <input id="lib-lon" placeholder="lon" inputmode="decimal">
        <label for="lib-gaz">Gazetteer id</label>
        <input id="lib-gaz" placeholder="opaque id">
        <label for="lib-doc">Document id</label>
        <input id="lib-doc" placeholder="optional">
        <p class="note">Sister pages: Aziel Digital Library Temporal Map <a href="https://www.azielcorpuslibrary.net/map">/map</a> and <a href="https://www.azielcorpuslibrary.net/v1/verify-geo">/v1/verify-geo</a>. Possibility and bayesian stay separate labels.</p>
        <div class="toolrow"><button class="btn gold" type="submit">Library pin</button></div>
      </form>
      <div class="scores">
        <div class="scorebox" id="score-possibility">possibility (time × place) — none yet</div>
        <div class="scorebox" id="score-bayesian">bayesian (cited) — none yet</div>
      </div>
      <svg class="plot" id="pin-plot" viewBox="0 0 560 220" role="img" aria-label="Inspection pin plot"></svg>
      <p class="note" id="plot-note">Inspection plot. Each pin is labeled REAL or MOCK.</p>
    </details>

    <details class="fold" id="relate-fold">
      <summary>Span and join</summary>
      <form id="span-form" autocomplete="off">
        <p class="note">Span records the interval between two cards already on this page.</p>
        <label for="span-from">From card</label>
        <input id="span-from" placeholder="from id">
        <label for="span-to">To card</label>
        <input id="span-to" placeholder="to id">
        <div class="toolrow"><button class="btn gold" type="submit">Span</button></div>
      </form>
      <form id="join-form" autocomplete="off">
        <p class="note">Join two cards. Pattern to clock (Π→T) is refused, because a pattern cannot rewrite the clock.</p>
        <label for="join-left">Left card</label>
        <input id="join-left" placeholder="left id">
        <label for="join-right">Right card</label>
        <input id="join-right" placeholder="right id">
        <label for="join-type">Join</label>
        <select id="join-type">
          <option value="T-DELTA">T↔Δ Clock and interval</option>
          <option value="DELTA-GAMMA">Δ↔Γ Interval and trajectory</option>
          <option value="GAMMA-PI">Γ↔Π Trajectory and pattern</option>
          <option value="T-PI">T↔Π Clock and pattern</option>
          <option value="PI-T">Π→T Pattern to clock (refused)</option>
        </select>
      <div class="toolrow"><button class="btn gold" type="submit">Join</button>
      <button class="btn gold" type="button" id="fork-btn">Fork last</button>
      <button class="btn gold" type="button" id="lens-btn">Silent lens</button>
      <button class="btn gold" type="button" id="example-btn">Load example</button></div>
      </form>
    </details>

    <details class="fold">
      <summary>Walk and check</summary>
      <form id="walk-form" autocomplete="off">
        <label for="walk-tip">Tip card</label>
        <input id="walk-tip" placeholder="tip id">
        <div class="toolrow">
          <button class="btn gold" type="submit">Walk</button>
          <button class="btn gold" type="button" id="trace-btn">Walk trace</button>
          <button class="btn gold" type="button" id="chain-btn">Verify chain</button>
        </div>
      </form>
    </details>

    <details class="fold">
      <summary>Frame, memory, and lattice</summary>
      <p class="note">These read the cards on this page. Cite and observe leave the 4DM-CARD unchanged. AKM-TRIAD-1.0 is fabric behind FragGate. A posterior is a belief. The hashchain lattice keeps tips and the previous hash.</p>
    <div class="toolrow">
      <button class="btn gold" type="button" id="frame-btn">Frame status</button>
      <button class="btn gold" type="button" id="axis-btn">Axis describe</button>
      <button class="btn gold" type="button" id="export-btn">Export JSON</button>
      <button class="btn gold" type="button" id="memory-cite-btn" title="AKM-TRIAD-1.0 fabric cite. The 4DM-CARD stays unchanged.">Cite memory</button>
      <button class="btn gold" type="button" id="memory-observe-btn" title="FragGate memory_observe packet. A posterior is a belief.">Observe card</button>
      <button class="btn gold" type="button" id="plot-btn">Plot</button>
      <button class="btn gold" type="button" id="possibility-btn">Possibility hooks</button>
      <button class="btn gold" type="button" id="recall-btn">Pattern recall</button>
      <button class="btn gold" type="button" id="tip-btn">Lattice tip</button>
      <button class="btn gold" type="button" id="poison-btn">Poison refuse</button>
      <button class="btn gold" type="button" id="neighbor-btn">Neighbor cite</button>
      <button class="btn gold" type="button" id="lib-demo-btn">MOCK library demo</button>
    </div>
    </details>

    <details class="fold" id="import-fold">
      <summary>Import cards</summary>
      <form id="import-form" autocomplete="off">
        <label for="import-json">4DM-CARD JSON</label>
        <textarea id="import-json" placeholder='{"cards":[...]}'></textarea>
        <p class="note">Hashes fail closed. A card that does not hash is refused.</p>
        <div class="toolrow"><button class="btn gold" type="submit">Import</button></div>
      </form>
    </details>

    <h3>Cards on this visit</h3>
    <p class="empty" id="list-empty">No cards yet.</p>
    <ol id="card-list"></ol>
    <div id="receipt-box" class="receipt" hidden></div>
    <p class="status" id="last-op" role="status" aria-live="polite">No action yet.</p>
    <details class="fold" id="record-fold">
      <summary>Response record</summary>
      <pre id="last-json">No response yet.</pre>
    </details>
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
      function cssVar(name, fallback) {
        var board = $("board");
        if (!board) return fallback;
        var v = getComputedStyle(board).getPropertyValue(name).trim();
        return v || fallback;
      }
      function setStatus(text, kind) {
        var el = $("last-op");
        if (!el) return;
        el.textContent = text;
        el.className = kind ? "status " + kind : "status";
      }
      function paint() {
        var titles = { T:"T Clock", DELTA:"Δ Interval", GAMMA:"Γ Trajectory", PI:"Π Pattern" };
        ["T","DELTA","GAMMA","PI"].forEach(function (a) {
          var col = $("col-"+a);
          col.textContent = "";
          var h = document.createElement("h3");
          h.textContent = titles[a];
          col.appendChild(h);
        });
        var list = $("card-list");
        list.textContent = "";
        var pinIds = [];
        var counts = { T:0, DELTA:0, GAMMA:0, PI:0 };
        cards.forEach(function (c) {
          var axis = axisOf(c);
          counts[axis] = (counts[axis] || 0) + 1;
          var col = $("col-"+axis);
          var d = document.createElement("div");
          d.className = "tick";
          var code = document.createElement("code");
          code.textContent = c.id || "";
          d.appendChild(code);
          d.appendChild(document.createElement("br"));
          d.appendChild(document.createTextNode(String(c.src || "") + " · " + String(c.h || "").slice(0, 16)));
          col.appendChild(d);
          var li = document.createElement("li");
          li.textContent = (c.id || "") + " · " + axis + " · " + (c.src || "") + " · " + String(c.h || "").slice(0, 16);
          list.appendChild(li);
          if (axis === "T") pinIds.push(c.id);
        });
        ["T","DELTA","GAMMA","PI"].forEach(function (a) {
          if (!counts[a]) {
            var empty = document.createElement("p");
            empty.className = "empty";
            empty.textContent = "Nothing here yet.";
            $("col-"+a).appendChild(empty);
          }
        });
        var boardEmpty = $("board-empty");
        if (boardEmpty) boardEmpty.hidden = cards.length > 0;
        var listEmpty = $("list-empty");
        if (listEmpty) listEmpty.hidden = cards.length > 0;
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
          pbox.textContent = pos
            ? "possibility (time × place) " + pos.value + " · label " + (pos.label || "possibility")
            : "possibility (time × place) — none yet";
        }
        if (bbox) {
          bbox.textContent = bay
            ? "bayesian (cited) " + bay.value + " · label " + (bay.label || "bayesian") + (bay.cite ? " · cite " + bay.cite : "")
            : "bayesian (cited) — none yet. Kept separate from possibility.";
        }
      }
      function paintPlot(pins) {
        var svg = $("pin-plot");
        if (!svg) return;
        while (svg.firstChild) svg.removeChild(svg.firstChild);
        var list = pins || [];
        var geo = list.filter(function (p) { return p.lat != null && p.lon != null; });
        var muted = cssVar("--app-muted", "#d4cbb8");
        var ink = cssVar("--app-ink", "#f4efe4");
        var gold = cssVar("--app-gold", "#e0b53a");
        var ok = cssVar("--app-ok", "#b7ebc8");
        var lineColor = cssVar("--app-line", "#8a8172");
        if (!geo.length) {
          var empty = document.createElementNS("http://www.w3.org/2000/svg", "text");
          empty.setAttribute("x", "16"); empty.setAttribute("y", "28"); empty.setAttribute("fill", muted);
          empty.textContent = "No place pins yet. Use a library pin or the MOCK library demo.";
          svg.appendChild(empty);
          return;
        }
        geo.forEach(function (p, i) {
          var x = 20 + ((Number(p.lon) + 180) / 360) * 520;
          var y = 20 + ((90 - Number(p.lat)) / 180) * 180;
          var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("cx", String(x)); c.setAttribute("cy", String(y)); c.setAttribute("r", "5");
          c.setAttribute("fill", p.surface === "REAL" ? ok : gold);
          svg.appendChild(c);
          var t = document.createElementNS("http://www.w3.org/2000/svg", "text");
          t.setAttribute("x", String(x + 7)); t.setAttribute("y", String(y + 3)); t.setAttribute("fill", ink);
          t.setAttribute("font-size", "10");
          t.textContent = (p.surface || "MOCK") + " " + String(p.event || p.id || "").slice(0, 22);
          svg.appendChild(t);
          if (i > 0) {
            var prev = geo[i - 1];
            var x0 = 20 + ((Number(prev.lon) + 180) / 360) * 520;
            var y0 = 20 + ((90 - Number(prev.lat)) / 180) * 180;
            var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", String(x0)); line.setAttribute("y1", String(y0));
            line.setAttribute("x2", String(x)); line.setAttribute("y2", String(y));
            line.setAttribute("stroke", lineColor);
            svg.appendChild(line);
          }
        });
      }
      function showReceipt(inner) {
        var box = $("receipt-box");
        if (!box) return;
        var rec = inner && inner.receipt;
        if (!rec) { box.hidden = true; box.textContent = ""; return; }
        box.hidden = false;
        box.textContent = "";
        var title = document.createElement("strong");
        title.textContent = "4DM-CARD " + (rec.glyph || "") + " " + (rec.id || "");
        box.appendChild(title);
        var bits = ["source " + (rec.src || ""), "hash " + String(rec.h || "").slice(0, 16), "role " + (rec.role || "inspection")];
        if (rec.companion && rec.companion.software) bits.push("cites " + rec.companion.software);
        box.appendChild(document.createElement("br"));
        box.appendChild(document.createTextNode(bits.join(" · ")));
      }
      function plainStatus(op, j, inner) {
        inner = inner || {};
        var display = (j && j.display) || {};
        var message = String(inner.message || inner.note || display.summary || "");
        var refused = inner.refused === true || inner.ok === false;
        if (refused) {
          var why = message && message !== "refused" && message !== "ok" ? message : "The operation was refused.";
          return "Refused" + (inner.code ? " (" + inner.code + ")" : "") + ". " + why;
        }
        if (message && message !== "ok") return message;
        if (inner.verified === true) return "Chain verified.";
        if (inner.verified === false) return "Chain did not verify.";
        if (inner.id) return "Recorded " + inner.id + " on this page.";
        if (op === "card_export") return "Export is in the import box. Open Import cards to copy it.";
        if (op === "card_import") return "Import finished.";
        if (op === "frame_status") return "Frame status is in the response record.";
        if (op === "axis_describe") return "Axis description is in the response record.";
        if (op === "walk" || op === "walk_trace") return "Walk finished.";
        if (op === "plot") return "Plot updated from the cards on this page.";
        if (op === "possibility") return "Possibility and bayesian are labeled separately.";
        if (op === "pattern_recall") return "Pattern recall finished on the hashchain lattice.";
        if (op === "lattice_tip") return "Lattice tip is ready.";
        if (op === "memory_cite" || op === "memory_observe") return "Packet ready. The card on this page was not rewritten.";
        if (op === "neighbor_cite") return "Neighbor cite is ready.";
        if (op === "poison_refuse") return "Poison mark refused.";
        return "Done.";
      }
      function writeRecord(j) {
        var pre = $("last-json");
        if (!pre) return;
        pre.hidden = false;
        try { pre.textContent = JSON.stringify(j, null, 2); }
        catch (err) { pre.textContent = "The response could not be shown."; }
      }
      async function call(op, payload) {
        var r;
        var j;
        try {
          r = await fetch("/v1/" + op, { method:"POST", headers:{"content-type":"application/json","user-agent":"Mozilla/5.0"}, body: JSON.stringify(Object.assign({}, payload, { cards: cards })) });
          j = await r.json();
        } catch (err) {
          setStatus("The request did not complete. The cards on this page were not changed.", "err");
          return null;
        }
        var inner = (j && j.result) || j || {};
        var refused = inner.refused === true || inner.ok === false || !r.ok;
        setStatus(plainStatus(op, j, inner), refused ? "err" : "ok");
        writeRecord(j);
        if (!refused && inner.card) cards.push(inner.card);
        if (!refused && op === "card_import" && Array.isArray(inner.cards)) {
          inner.cards.forEach(function (c) {
            if (!cards.some(function (x) { return x.h === c.h; })) cards.push(c);
          });
        }
        showReceipt(inner);
        paintScores(inner);
        if (inner && Array.isArray(inner.pins)) paintPlot(inner.pins);
        else {
          var frames = cards.map(function (c) { return c.t && typeof c.t === "object" ? Object.assign({ id: c.id, src: c.src }, c.t) : null; }).filter(Boolean);
          paintPlot(frames);
        }
        paint();
        return refused ? inner : inner;
      }
      function needCards(message) {
        if (cards.length) return false;
        setStatus(message, "err");
        return true;
      }
      function loadExample() {
        fetch("/v1/example", { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: "{}" }).then(function (r) {
          return r.json();
        }).then(function (j) {
          var added = j.cards || (j.result && j.result.cards) || [];
          added.forEach(function (c) { cards.push(c); });
          setStatus(added.length ? "Loaded the synthetic example (" + added.length + " cards). These cards are not a case finding." : "The example returned no cards.", added.length ? "ok" : "err");
          writeRecord(j);
          paint();
        }).catch(function () {
          setStatus("The example did not load. The cards on this page were not changed.", "err");
        });
      }
      $("library-form").onsubmit = function (e) {
        e.preventDefault();
        var eventName = ($("lib-event").value || "").trim();
        var date = ($("lib-date").value || "").trim();
        if (!eventName || !date) {
          setStatus("Enter an event and a paper date. Nothing was pinned.", "err");
          return;
        }
        var prev = cards.length ? cards[cards.length - 1].h : undefined;
        call("library_pin", {
          event: eventName,
          date: date,
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
        var value = ($("pin-t").value || "").trim();
        if (!value) {
          value = new Date().toISOString();
          $("pin-t").value = value;
        }
        call("pin", { t: value, axis: axis, src: $("pin-src").value || "operator", note: axis + " pin", value: value });
      };
      $("span-form").onsubmit = function (e) {
        e.preventDefault();
        if (!($("span-from").value || "").trim() || !($("span-to").value || "").trim()) {
          setStatus("Enter a from card and a to card. Nothing was spanned.", "err");
          return;
        }
        call("span", { from_id: $("span-from").value.trim(), to_id: $("span-to").value.trim() });
      };
      $("join-form").onsubmit = function (e) {
        e.preventDefault();
        if (!($("join-left").value || "").trim() || !($("join-right").value || "").trim()) {
          setStatus("Enter a left card and a right card. Nothing was joined.", "err");
          return;
        }
        call("join", { left: $("join-left").value.trim(), right: $("join-right").value.trim(), join_type: $("join-type").value });
      };
      $("walk-form").onsubmit = function (e) {
        e.preventDefault();
        if (!($("walk-tip").value || "").trim()) {
          setStatus("Enter a tip card. Nothing was walked.", "err");
          return;
        }
        call("walk", { tip: $("walk-tip").value.trim() });
      };
      $("trace-btn").onclick = function () {
        if (!($("walk-tip").value || "").trim()) { setStatus("Enter a tip card. No trace was requested.", "err"); return; }
        call("walk_trace", { tip: $("walk-tip").value.trim() });
      };
      $("chain-btn").onclick = function () {
        if (!($("walk-tip").value || "").trim()) { setStatus("Enter a tip card. The chain was not checked.", "err"); return; }
        call("verify_chain", { tip: $("walk-tip").value.trim() });
      };
      $("frame-btn").onclick = function () { call("frame_status", {}); };
      $("axis-btn").onclick = function () { call("axis_describe", {}); };
      $("memory-cite-btn").onclick = function () { call("memory_cite", { id: $("walk-tip").value }); };
      $("memory-observe-btn").onclick = function () { call("memory_observe", { id: $("walk-tip").value }); };
      $("export-btn").onclick = async function () {
        var inner = await call("card_export", {});
        if (inner && inner.bundle) {
          $("import-json").value = JSON.stringify(inner.bundle, null, 2);
          var fold = $("import-fold");
          if (fold) fold.open = true;
          setStatus("Export is in the import box.", "ok");
        }
      };
      $("import-form").onsubmit = function (e) {
        e.preventDefault();
        var raw = $("import-json").value || "";
        if (!raw.trim()) {
          setStatus("Paste 4DM-CARD JSON. Nothing was imported.", "err");
          return;
        }
        try { call("card_import", { bundle: JSON.parse(raw) }); }
        catch (err) { setStatus("That text is not JSON. Nothing was imported.", "err"); }
      };
      $("fork-btn").onclick = function () {
        if (needCards("Pin a card before forking. Nothing was forked.")) return;
        call("fork", { id: cards[cards.length - 1].id });
      };
      $("lens-btn").onclick = function () { call("lens", { query: "" }); };
      $("plot-btn").onclick = function () { call("plot", {}); };
      $("possibility-btn").onclick = function () {
        if (needCards("Pin a card before possibility hooks.")) return;
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
        if (needCards("Pin a card before a neighbor cite.")) return;
        call("neighbor_cite", { id: cards[cards.length - 1].id });
      };
      $("lib-demo-btn").onclick = function () {
        var fold = $("library-fold");
        if (fold) fold.open = true;
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
      $("example-btn").onclick = loadExample;
      if ($("load-example")) $("load-example").onclick = loadExample;
      paint();
      paintPlot([]);
    })();
  </script>
</body>
</html>`;
}
