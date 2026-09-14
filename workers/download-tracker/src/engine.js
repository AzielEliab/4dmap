/**
 * 4DMap hosted engine — 4DM-CARD, typed joins, fail-closed SHA-256.
 * Mirrors the Python fourdmap package. Author: Aziel Eliab only.
 */
export const PRODUCT = "4dmap";
export const PRODUCT_NAME = "4DMap";
export const VERSION = "0.3.0";
export const SPEC = "4DM-WP-1.0";
export const SCHEMA = "4DM-CARD";
export const AUTHOR = "Aziel Eliab";
export const BUCKET = "Plain";
export const HOST = "https://4dmap-download-tracker.vibelock.workers.dev";
export const CATALOG = "https://aziel-runtime.vibelock.workers.dev";
export const GITHUB = "https://github.com/AzielEliab/4dmap";
export const JSON_CAP = 32 * 1024;
export const ZION_CAP = 0.75;
export const PI_EMPTY = "Π-EMPTY";
export const GENESIS_PREV = "0".repeat(64);

export const LIMITATION =
  "THIS IS: an inspection coordinate frame (4DM-WP-1.0) over TemporalLock / StaticClock / ChronoLock / TrajectoryLock / SpectralLock evidence. Cards are 4DM-CARD receipts with fail-closed SHA-256. Forks are kept. ZionPattern confidence is capped at 75%. A silent lens returns Π-EMPTY. THIS IS NOT: a truth engine; Lumen; GIS 4D; a Node Gate; certified forensics; an identity store. Receipts are not truth. No legal name, home, or county on cards. QNS/QNM do not carry 4DMap photons. Author: Aziel Eliab only.";

export const GUARDRAIL =
  "4DMap stamps inspection coordinates. It does not certify facts, solve cases, name people, infer intent, or backdate a clock from a pattern. P(pattern | cards) is capped at 0.75 and is not P(the world is true). Synthetic examples must never be presented as real-case findings.";

export const PIPELINE = `PUBLIC/AGENTS/UI → FragGate → SweepGate → ChainLock-IN → DecisionGATE → AZPIPE
  → Internal Domain Layer (isolated softwares; domains_are_doors:false)  ←──  4DMap
       inspection cards sit HERE as a read-side coordinate frame over
       TemporalLock/StaticClock/ChronoLock/TrajectoryLock/SpectralLock evidence
       (not a hop gate; not a door)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT`;

export const PIPELINE_NOTE =
  "4DMap is not inserted as another sequential gate. It is an inspection frame in the Internal Domain Layer after AZPIPE (domains_are_doors:false): engines and operator UI write/read 4DM cards; FragGate grounded claims may cite join types; ChainLock may stamp a walk when the operator seals. QNS/QNM do not carry 4DMap photons. FragGate is THE single door.";

export const ALLOWED_JOINS = new Set(["T-DELTA", "DELTA-T", "DELTA-GAMMA", "GAMMA-DELTA", "GAMMA-PI", "PI-GAMMA", "T-PI"]);
export const ILLEGAL_JOINS = new Set(["PI-T"]);
export const TARBALL = "4dmap-0.3.0.tar.gz";
export const PIN_FRAME_KIND = "4DM-PIN-FRAME";
export const GROWTH = "ON";

export const COMPANIONS = {
  temporallock: { software: "TemporalLock", slug: "temporallock", axes: ["T", "DELTA"], role: "inspection_input", cite_only: true, door: false, merged: false },
  staticclock: { software: "StaticClock", slug: "staticclock", axes: ["T"], role: "inspection_input", cite_only: true, door: false, merged: false },
  chronolock: { software: "ChronoLock", slug: "chronolock", axes: ["T", "DELTA"], role: "inspection_input", cite_only: true, door: false, merged: false },
  trajectorylock: { software: "TrajectoryLock", slug: "trajectorylock", axes: ["GAMMA"], role: "inspection_input", cite_only: true, door: false, merged: false },
  spectrallock: { software: "SpectralLock", slug: "spectrallock", axes: ["PI"], role: "inspection_input", cite_only: true, door: false, merged: false },
};

export const AXIS_FRAME = {
  T: { glyph: "T", name: "Clock", meaning: "time / when a pin sits", companions: ["temporallock", "staticclock", "chronolock"], ops: ["pin", "card_pin", "library_pin", "span", "card_span", "walk", "walk_trace", "plot"] },
  DELTA: { glyph: "Δ", name: "Interval", meaning: "delta / change / span or gap between pins", companions: ["temporallock", "chronolock"], ops: ["span", "card_span", "gap", "walk", "walk_trace"] },
  GAMMA: { glyph: "Γ", name: "Trajectory", meaning: "pattern / geometry / stacked or walked motion of pins", companions: ["trajectorylock"], ops: ["stack", "walk", "walk_trace", "pin", "card_pin", "plot"] },
  PI: { glyph: "Π", name: "Pattern", meaning: "provenance / path / class / cohort / absence / silence", companions: ["spectrallock"], ops: ["lens", "class", "cohort", "absence", "pin", "card_pin", "pattern_recall", "poison_refuse", "possibility"] },
};

export const LIBRARY = {
  software: "Aziel Digital Library",
  slug: "aziel-corpus",
  role: "inspection_input",
  cite_only: true,
  door: false,
  merged: false,
  map: "https://www.azielcorpuslibrary.net/map",
  verify_geo: "https://www.azielcorpuslibrary.net/v1/verify-geo",
  note: "Library Temporal Map pins are paper date × event × geolocation. Never upload time. Docs without resolvable place+date stay unpinned. 4DMap accepts/emits 4DM-PIN-FRAME receipts on the hashchain lattice.",
  author: AUTHOR,
};

export const DISCOVERY = {
  growth: GROWTH,
  skill: true,
  openapi: true,
  mcp: true,
  worker_ui: true,
  reason: "library pin + lattice memory LIVE_OPS",
};

export const AXIS_GLYPH = { T: "T", DELTA: "Δ", GAMMA: "Γ", PI: "Π" };

export const MASTER33 = {
  master: "MASTER-33",
  door: "fraggate",
  fraggate_single_door: true,
  domains_are_doors: false,
  sequential_gate: false,
  role: "inspection",
  layer: "Internal Domain Layer",
  after: "AZPIPE",
  software_door: false,
  fabric: false,
  software_tab: true,
  domain: "Research",
  domain_id: "06",
  note: "4DMap is a Research-domain inspection frame T/Δ/Γ/Π inside Internal Domain Layer after AZPIPE. Isolated software, not an additional door. Not a sequential gate. Not LIVE fabric. FragGate is THE single door.",
};

export const AKM = {
  spec: "AKM-TRIAD-1.0",
  name: "Adaptive Knowledge Memory",
  fabric: true,
  software_tab: false,
  door: false,
  slug: null,
  softwares_product: false,
  pairing: "optional cite/observe",
  posterior_is_truth: false,
  belief_is_not_truth: true,
  authorizes_action: false,
  history_rewrite: false,
  triad: ["E", "C", "P", "B"],
  triad_rule: "3-of-4",
  mcp: ["memory_observe", "memory_resolve", "memory_calibrate", "memory_recall", "memory_get"],
  http: ["POST /v1/memory/observe", "POST /v1/memory/resolve", "POST /v1/memory/calibrate", "POST /v1/memory/recall"],
  learn: "ChainLock learn",
  note: "LIVE fabric on aziel-runtime. Not a Softwares-tab product. Behind FragGate. Optional 4DMap inspection-card cite/observe only. Bayesian 3-of-4 triad E/C/P/B. Posterior ≠ truth. No history rewrite. Author: Aziel Eliab only.",
  author: AUTHOR,
};

export const OP_ALIASES = {
  card_pin: "pin",
  card_span: "span",
  card_join: "join",
  card_walk: "walk",
  card_list: "list",
  ingest_pin: "library_pin",
  plot_pins: "plot",
  score_hooks: "possibility",
  possibility_cite: "possibility",
  lattice_tips: "lattice_tip",
  neighbor: "neighbor_cite",
};

export const REFUSE_OPS = {
  truth_score: { code: "STUB_REFUSE", message: "truth_score is stub — 4DMap is not a truth engine" },
  lumen_panel: { code: "STUB_REFUSE", message: "lumen_panel is stub — 4DMap is not Lumen" },
  invent_mark: { code: "STUB_REFUSE", message: "invent_mark is stub — 4DMap does not invent marks" },
  backdate_class: { code: "STUB_REFUSE", message: "backdate_class is stub — Π cannot rewrite T" },
  wipe: { code: "FANTASY_OP", message: "destructive wipe is refused" },
  purge: { code: "FANTASY_OP", message: "destructive purge is refused" },
  delete_all: { code: "FANTASY_OP", message: "destructive delete_all is refused" },
  merge_products: { code: "FANTASY_OP", message: "companion softwares are cite-only; products are not merged" },
  enable_door: { code: "FANTASY_OP", message: "4DMap is not a Softwares door; FragGate remains THE single door" },
  akm: { code: "AKM_SOFTWARE", message: "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug" },
  akm_triad: { code: "AKM_SOFTWARE", message: "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug" },
  memory_rewrite: { code: "AKM_REWRITE", message: "AKM-TRIAD-1.0 does not rewrite history" },
  posterior_truth: { code: "AKM_TRUTH", message: "posterior ≠ truth; 4DMap receipts are not truth" },
  ml_store: { code: "LATTICE_ONLY", message: "adaptive pattern memory is the hashchain lattice, not a detached ML store" },
  detach_memory: { code: "LATTICE_ONLY", message: "recollection stays on tips/prev-hash/pin receipts" },
};

const FORBIDDEN_KEYS = new Set([
  "legal_name",
  "legalname",
  "full_name",
  "fullname",
  "home",
  "home_address",
  "county",
  "ssn",
  "address",
  "street",
  "residence",
  "dob",
  "date_of_birth",
]);

const IDENTITY_PHRASES = [/\blegal\s+name\b/i, /\bhome\s+address\b/i, /\bcounty\s+of\b/i, /\b[A-Za-z][A-Za-z .'-]{1,40}\s+County\b/];
const INTENT_PHRASES = [/\bintent\b/i, /\bmotive\b/i, /\bguilt\b/i, /\bmeant to\b/i];

export class CardError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
    this.refused = true;
  }
  asDict() {
    return { ok: false, refused: true, code: this.code, message: this.message };
  }
}

function normAxisValue(value) {
  if (value == null) return null;
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) return value.map(normAxisValue);
  if (typeof value === "object") {
    const out = {};
    for (const k of Object.keys(value).sort()) out[k] = normAxisValue(value[k]);
    return out;
  }
  return String(value);
}

export function canonicalPayload(card) {
  return {
    delta: normAxisValue(card.delta ?? null),
    gamma: normAxisValue(card.gamma ?? null),
    id: String(card.id || ""),
    note: String(card.note || ""),
    pi: normAxisValue(card.pi ?? null),
    prev: String(card.prev || GENESIS_PREV),
    src: String(card.src || ""),
    t: normAxisValue(card.t ?? null),
  };
}

export function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(",") + "]";
  const keys = Object.keys(value).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",") + "}";
}

function bytesToHex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function digest(card) {
  const raw = canonicalJson(canonicalPayload(card));
  const data = new TextEncoder().encode(raw);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return bytesToHex(hash);
}

export function scanIdentity(value, path = "") {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    for (const [key, inner] of Object.entries(value)) {
      const low = String(key).toLowerCase().replace(/-/g, "_");
      if (FORBIDDEN_KEYS.has(low)) {
        throw new CardError("IDENTITY_LEAK", `card field ${path}${key} is a forbidden identity key (no legal name/home/county)`);
      }
      scanIdentity(inner, `${path}${key}.`);
    }
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((inner, i) => scanIdentity(inner, `${path}${i}.`));
    return;
  }
  if (typeof value === "string") {
    for (const pat of IDENTITY_PHRASES) {
      if (pat.test(value)) throw new CardError("IDENTITY_LEAK", "card text names a legal name, home, or county — refused");
    }
  }
}

export function scanIntent(value) {
  if (value && typeof value === "object") {
    const vals = Array.isArray(value) ? value : Object.values(value);
    vals.forEach(scanIntent);
    return;
  }
  if (typeof value === "string") {
    for (const pat of INTENT_PHRASES) {
      if (pat.test(value)) throw new CardError("INTENT_REFUSE", "4DMap does not infer or record intent, motive, or guilt");
    }
  }
}

export function newId() {
  const n = crypto.getRandomValues(new Uint8Array(6));
  return "4dm-" + bytesToHex(n);
}

export async function makeCard(input = {}) {
  const card = {
    schema: SCHEMA,
    id: input.id || newId(),
    t: input.t ?? null,
    delta: input.delta ?? null,
    gamma: input.gamma ?? null,
    pi: input.pi == null ? PI_EMPTY : input.pi,
    prev: input.prev || GENESIS_PREV,
    src: input.src || "operator",
    note: input.note || "",
  };
  scanIdentity(card);
  scanIntent(card);
  const h = await digest(card);
  if (input.expected_h && input.expected_h !== h) {
    throw new CardError("HASH_FAIL", "fail-closed: supplied h does not match canonical SHA-256");
  }
  card.h = h;
  return card;
}

export async function verifyCard(card) {
  if (!card || typeof card !== "object") throw new CardError("HASH_FAIL", "fail-closed: card is not an object");
  scanIdentity(card);
  scanIntent(card);
  const expected = await digest(card);
  if (String(card.h || "") !== expected) throw new CardError("HASH_FAIL", "fail-closed: card hash mismatch");
  return { ok: true, id: card.id, h: expected };
}

export function axisOf(card) {
  if (card.t != null && card.t !== "" && (card.delta == null || card.delta === "") && (card.gamma == null || card.gamma === "")) {
    if (card.pi == null || card.pi === "" || card.pi === PI_EMPTY) return "T";
  }
  if (card.delta != null && card.delta !== "") return "DELTA";
  if (card.gamma != null && card.gamma !== "") return "GAMMA";
  if (card.pi != null && card.pi !== "" && card.pi !== PI_EMPTY) return "PI";
  if (card.t != null && card.t !== "") return "T";
  return "T";
}

export function normalizeAxis(raw) {
  let text = String(raw || "T").trim().toUpperCase().replace(/\s+/g, "");
  text = text.replace(/Δ/g, "DELTA").replace(/Γ/g, "GAMMA").replace(/Π/g, "PI");
  const aliases = {
    T: "T",
    CLOCK: "T",
    TIME: "T",
    D: "DELTA",
    DELTA: "DELTA",
    INTERVAL: "DELTA",
    CHANGE: "DELTA",
    G: "GAMMA",
    GAMMA: "GAMMA",
    TRAJECTORY: "GAMMA",
    GEOMETRY: "GAMMA",
    PATTERN: "PI",
    P: "PI",
    PI: "PI",
    PROVENANCE: "PI",
    PATH: "PI",
  };
  const axis = aliases[text];
  if (!axis) throw new CardError("AXIS_REFUSE", `unknown axis ${raw}; use T, Δ, Γ, or Π`);
  return axis;
}

export function companionCite(src, axis) {
  const key = String(src || "").trim().toLowerCase();
  const info = COMPANIONS[key];
  if (!info) return null;
  const cite = {
    software: info.software,
    slug: info.slug,
    axes: info.axes.slice(),
    role: "inspection_input",
    cite_only: true,
    door: false,
    merged: false,
  };
  if (axis) cite.axis = axis;
  return cite;
}

export function cardReceipt(card) {
  const axis = axisOf(card);
  const src = String(card.src || "");
  const frame = AXIS_FRAME[axis];
  return {
    schema: SCHEMA,
    kind: "4DM-CARD",
    id: card.id,
    h: card.h,
    axis,
    glyph: AXIS_GLYPH[axis],
    name: frame.name,
    meaning: frame.meaning,
    src,
    companion: companionCite(src, axis),
    role: "inspection",
    door: false,
    truth: false,
  };
}

function withReceipt(result) {
  if (result && result.card && typeof result.card === "object") {
    result.receipt = result.receipt || cardReceipt(result.card);
    if (result.axis == null) result.axis = result.receipt.axis;
    if (result.glyph == null) result.glyph = result.receipt.glyph;
  }
  return result;
}

function refuseAkmAbuse(payload) {
  const p = payload || {};
  if (p.rewrite || p.history_rewrite || p.backdate) {
    throw new CardError("AKM_REWRITE", "AKM-TRIAD-1.0 does not rewrite history; 4DM-CARD prev chain is fail-closed");
  }
  if (p.truth || p.posterior_is_truth === true) {
    throw new CardError("AKM_TRUTH", "posterior ≠ truth; 4DMap receipts are not truth");
  }
  const slug = String(p.slug || p.software || "").trim().toLowerCase().replace(/_/g, "-");
  if (p.software_tab || ["akm", "akm-triad", "akm-triad-1.0", "memory"].includes(slug)) {
    throw new CardError("AKM_SOFTWARE", "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug or second door");
  }
}

function observationFromCard(card, payload) {
  const p = payload || {};
  const axis = axisOf(card);
  const fact = String(
    p.fact
    || `4DM-CARD ${card.id} axis=${axis} glyph=${AXIS_GLYPH[axis]} h=${card.h} src=${card.src} — inspection receipt, not truth`,
  );
  return {
    kind: "memory_observation",
    spec: AKM.spec,
    subject: String(p.subject || `${PRODUCT}:${card.id}`),
    fact,
    memory_id: p.memory_id || null,
    use_case: String(p.use_case || "4dmap-inspection-cite"),
    card: { schema: SCHEMA, spec: SPEC, id: card.id, h: card.h, axis, glyph: AXIS_GLYPH[axis], src: card.src, prev: card.prev },
    triad: AKM.triad.slice(),
    triad_rule: AKM.triad_rule,
    posterior_is_truth: false,
    belief_is_not_truth: true,
    authorizes_action: false,
    history_rewrite: false,
    software_tab: false,
    door: false,
    fabric: true,
    learn: AKM.learn,
    fraggate: "memory_observe",
    http: "POST /v1/memory/observe",
    note: AKM.note,
    author: AKM.author,
    fourdmap_version: VERSION,
  };
}

function wantsLibraryPin(payload) {
  if (!payload || typeof payload !== "object") return false;
  if (payload.ingest || payload.pin_frame || payload.descriptor) return true;
  if (payload.event || payload.gazetteer_id || payload.gazetteer) return true;
  if (payload.lat != null || payload.lon != null) return true;
  if (payload.date || payload.paper_date || payload.doc_id) return true;
  return false;
}

let latticeMod = null;
async function lattice() {
  if (!latticeMod) latticeMod = await import("./lattice.js");
  return latticeMod;
}

function cardFromPayload(payload, store) {
  if (payload.card && typeof payload.card === "object") return payload.card;
  const id = String(payload.id || payload.tip || "");
  if (id) return byId(store, id);
  throw new CardError("NOT_FOUND", "memory cite/observe needs a card id or card object");
}

function traceSteps(chain) {
  return (chain || []).map((card, i) => {
    const axis = axisOf(card);
    return {
      i,
      id: card.id,
      h: card.h,
      prev: card.prev,
      axis,
      glyph: AXIS_GLYPH[axis],
      src: card.src,
      companion: companionCite(card.src, axis),
      note: card.note,
    };
  });
}

export function normalizeJoinType(raw) {
  let text = String(raw || "").trim().toUpperCase().replace(/\s+/g, "");
  text = text.replace(/Δ/g, "DELTA").replace(/Γ/g, "GAMMA").replace(/Π/g, "PI");
  text = text.replace(/↔/g, "-").replace(/->/g, "-").replace(/→/g, "-").replace(/_/g, "-");
  const aliases = { D: "DELTA", INTERVAL: "DELTA", G: "GAMMA", TRAJECTORY: "GAMMA", P: "PI", PATTERN: "PI", CLOCK: "T" };
  const parts = text.split("-").filter(Boolean);
  if (parts.length !== 2) throw new CardError("JOIN_REFUSE", `join type must be A-B, got ${raw}`);
  return [aliases[parts[0]] || parts[0], aliases[parts[1]] || parts[1]];
}

export function refuseJoin(leftAxis, rightAxis, backdate = false) {
  const pair = `${leftAxis}-${rightAxis}`;
  if (ILLEGAL_JOINS.has(pair) || backdate) {
    throw new CardError("PI_T_BACKDATE", "illegal join: Π→T backdate refused (pattern cannot rewrite the clock)");
  }
  if (!ALLOWED_JOINS.has(pair)) {
    throw new CardError("JOIN_REFUSE", `illegal join ${leftAxis}→${rightAxis}; allowed T↔Δ, Δ↔Γ, Γ↔Π, T↔Π`);
  }
}

export async function joinCards(left, right, joinType, { backdate = false, note = "", src = "4dmap" } = {}) {
  scanIdentity(left);
  scanIdentity(right);
  scanIntent(left);
  scanIntent(right);
  scanIntent(note);
  let leftAxis = axisOf(left);
  let rightAxis = axisOf(right);
  if (joinType) [leftAxis, rightAxis] = normalizeJoinType(joinType);
  refuseJoin(leftAxis, rightAxis, backdate);
  const cite = { join: `${leftAxis}-${rightAxis}`, left: left.id, right: right.id };
  const fields = { t: null, delta: null, gamma: null, pi: null };
  if (leftAxis === "T" || rightAxis === "T") fields.t = axisOf(left) === "T" ? left.t : right.t;
  if (leftAxis === "DELTA" || rightAxis === "DELTA") fields.delta = cite;
  if (leftAxis === "GAMMA" || rightAxis === "GAMMA") fields.gamma = cite;
  if (leftAxis === "PI" || rightAxis === "PI") fields.pi = cite;
  const card = await makeCard({
    t: fields.t,
    delta: fields.delta,
    gamma: fields.gamma,
    pi: fields.pi,
    prev: String(left.h || ""),
    src,
    note: note || `typed join ${leftAxis}-${rightAxis}`,
  });
  const cites = [];
  const seen = new Set();
  for (const [citeSrc, citeAxis] of [[left.src, leftAxis], [right.src, rightAxis], [src, null]]) {
    const cite = companionCite(citeSrc, citeAxis);
    if (cite && !seen.has(cite.slug)) {
      seen.add(cite.slug);
      cites.push(cite);
    }
  }
  return withReceipt({
    ok: true,
    join: `${leftAxis}-${rightAxis}`,
    allowed: true,
    card,
    left: left.id,
    right: right.id,
    cites,
    companions_merged: false,
    second_door: false,
    note: "typed join cites companion softwares as inspection inputs only",
  });
}

export function findForks(cards) {
  const children = {};
  for (const card of cards || []) {
    const prev = String(card.prev || GENESIS_PREV);
    children[prev] = children[prev] || [];
    children[prev].push(String(card.h));
  }
  return Object.entries(children)
    .filter(([, hashes]) => hashes.length > 1)
    .map(([prev, hashes]) => ({ prev, child_hashes: hashes, kept: true, winner: null }));
}

function byId(cards, id) {
  const card = (cards || []).find((c) => c.id === id);
  if (!card) throw new CardError("NOT_FOUND", `card ${id} not found`);
  return card;
}

export async function runOp(op, payload = {}, cards = []) {
  const resolved = OP_ALIASES[op] || op;
  if (REFUSE_OPS[op] || REFUSE_OPS[resolved]) {
    const refused = REFUSE_OPS[op] || REFUSE_OPS[resolved];
    throw new CardError(refused.code, refused.message);
  }
  const store = [...cards];
  const pushCard = (card) => {
    store.push(card);
  };
  if (resolved === "library_pin" || (resolved === "pin" && wantsLibraryPin(payload) && normalizeAxis(payload.axis || "T") === "T")) {
    const L = await lattice();
    return withReceipt(await L.runLibraryPin(payload, store));
  }
  if (resolved === "plot") {
    const L = await lattice();
    return L.runPlot(store);
  }
  if (resolved === "possibility") {
    const L = await lattice();
    return withReceipt(await L.runPossibility(payload, store, pushCard));
  }
  if (resolved === "pattern_recall") {
    const L = await lattice();
    return withReceipt(await L.runPatternRecall(payload, store, pushCard));
  }
  if (resolved === "lattice_tip") {
    const L = await lattice();
    return L.runLatticeTip(store);
  }
  if (resolved === "poison_refuse") {
    const L = await lattice();
    return withReceipt(await L.runPoisonRefuse(payload, store, pushCard));
  }
  if (resolved === "neighbor_cite") {
    const L = await lattice();
    return L.runNeighborCite(payload, store);
  }
  if (resolved === "pin") {
    const axis = normalizeAxis(payload.axis || "T");
    const src = payload.src || "operator";
    const note = payload.note || `${AXIS_GLYPH[axis]} pin`;
    const fields = { src, note, prev: payload.prev, id: payload.id, pi: PI_EMPTY };
    if (axis === "T") fields.t = payload.t;
    else if (axis === "DELTA") {
      fields.delta = payload.delta || { change: payload.value || payload.t };
      fields.t = payload.t;
    } else if (axis === "GAMMA") {
      fields.gamma = payload.gamma || { geometry: payload.value || payload.t };
      fields.t = payload.t;
    } else {
      fields.pi = payload.pi != null ? payload.pi : payload.value || PI_EMPTY;
      fields.t = payload.t;
    }
    const card = await makeCard(fields);
    return withReceipt({ ok: true, op: "pin", axis, glyph: AXIS_GLYPH[axis], card, id: card.id, h: card.h, companion: companionCite(src, axis) });
  }
  if (resolved === "span") {
    const left = byId(store, String(payload.from_id || payload.a || ""));
    const right = byId(store, String(payload.to_id || payload.b || ""));
    await verifyCard(left);
    await verifyCard(right);
    const fromAxis = axisOf(left);
    const toAxis = axisOf(right);
    const src = payload.src || "operator";
    const card = await makeCard({
      delta: {
        from: left.id,
        to: right.id,
        from_t: left.t,
        to_t: right.t,
        from_axis: fromAxis,
        to_axis: toAxis,
        from_glyph: AXIS_GLYPH[fromAxis],
        to_glyph: AXIS_GLYPH[toAxis],
      },
      src,
      note: payload.note || "Δ span",
      prev: String(right.h || left.h),
      pi: PI_EMPTY,
    });
    const cites = [companionCite(left.src, fromAxis), companionCite(right.src, toAxis), companionCite(src, "DELTA")].filter(Boolean);
    return withReceipt({ ok: true, op: "span", axis: "DELTA", glyph: "Δ", card, id: card.id, h: card.h, cites, companions_merged: false });
  }
  if (resolved === "stack") {
    const ids = payload.ids || [];
    const picked = ids.map((i) => byId(store, String(i)));
    for (const c of picked) await verifyCard(c);
    const card = await makeCard({
      gamma: { stack: picked.map((c) => c.id), hs: picked.map((c) => c.h) },
      src: payload.src || "operator",
      note: payload.note || "Γ stack",
      prev: picked.length ? String(picked[picked.length - 1].h) : undefined,
      pi: PI_EMPTY,
    });
    return withReceipt({ ok: true, op: "stack", axis: "GAMMA", glyph: "Γ", card, id: card.id, h: card.h });
  }
  if (resolved === "gap") {
    const card = await makeCard({
      delta: { gap: true, from: payload.from_id || payload.t0, to: payload.to_id || payload.t1 },
      src: payload.src || "operator",
      note: payload.note || "Δ gap",
      prev: payload.prev,
      pi: PI_EMPTY,
    });
    return withReceipt({ ok: true, op: "gap", axis: "DELTA", glyph: "Δ", card, id: card.id, h: card.h });
  }
  if (resolved === "fork") {
    const source = byId(store, String(payload.id || ""));
    await verifyCard(source);
    const sibling = await makeCard({
      t: source.t,
      delta: source.delta,
      gamma: source.gamma,
      pi: source.pi,
      prev: String(source.prev),
      src: payload.src || source.src || "operator",
      note: payload.note || "fork kept",
    });
    const next = store.concat([sibling]);
    return withReceipt({ ok: true, op: "fork", card: sibling, id: sibling.id, h: sibling.h, forks_kept: true, winner: null, forks: findForks(next) });
  }
  if (resolved === "walk" || resolved === "walk_trace") {
    const tip = String(payload.tip || payload.id || "");
    const seen = new Set();
    const chain = [];
    let card = byId(store, tip);
    while (card) {
      if (seen.has(card.h)) throw new CardError("HASH_FAIL", "fail-closed: walk cycle");
      seen.add(card.h);
      await verifyCard(card);
      chain.push(card);
      const prev = String(card.prev || GENESIS_PREV);
      if (prev === GENESIS_PREV || !prev) break;
      card = store.find((c) => c.h === prev) || null;
    }
    chain.reverse();
    const steps = traceSteps(chain);
    if (resolved === "walk_trace") {
      return {
        ok: true,
        op: "walk_trace",
        tip,
        cards: chain,
        n: chain.length,
        forks: findForks(store),
        steps,
        genesis: Boolean(steps.length) && String(steps[0].prev || "").replace(/0/g, "") === "",
        role: "inspection",
      };
    }
    return { ok: true, op: "walk", tip, cards: chain, n: chain.length, forks: findForks(store), steps };
  }
  if (resolved === "lens" || resolved === "absence") {
    const query = String(payload.query || "").trim();
    if (!query) return { ok: true, op: resolved, pi: PI_EMPTY, silent: true, note: "lens silent → Π-EMPTY" };
    const hits = [];
    for (const card of store.concat(payload.cards || [])) {
      const blob = ["id", "note", "src", "t", "pi"].map((k) => String(card[k] || "")).join(" ");
      if (blob.toLowerCase().includes(query.toLowerCase())) hits.push(card.id);
    }
    if (!hits.length) return { ok: true, op: resolved, pi: PI_EMPTY, silent: true, note: "lens silent → Π-EMPTY" };
    return { ok: true, op: resolved, pi: { class: "lens-hit", ids: hits }, silent: false, hits };
  }
  if (resolved === "class") {
    const label = String(payload.label || "").trim();
    if (!label) return { ok: true, op: "class", pi: PI_EMPTY, silent: true };
    const card = await makeCard({ pi: { class: label }, src: payload.src || "operator", note: payload.note || `Π class ${label}`, prev: payload.prev });
    return withReceipt({ ok: true, op: "class", pi: card.pi, card, id: card.id, h: card.h });
  }
  if (resolved === "cohort") {
    const ids = (payload.ids || []).map(String);
    if (!ids.length) return { ok: true, op: "cohort", pi: PI_EMPTY, silent: true };
    const card = await makeCard({ pi: { cohort: ids }, src: payload.src || "operator", note: payload.note || "Π cohort", prev: payload.prev });
    return withReceipt({ ok: true, op: "cohort", card, id: card.id, h: card.h });
  }
  if (resolved === "cap") {
    const score = Number(payload.score ?? payload.confidence ?? 0);
    if (!Number.isFinite(score)) throw new CardError("CAP_REFUSE", "score must be a number");
    const capped = Math.min(Math.max(score, 0), ZION_CAP);
    return { ok: true, op: "cap", score: capped, raw: score, capped: score > ZION_CAP, zion_cap: ZION_CAP, note: "ZionPattern cap 75%" };
  }
  if (resolved === "join") {
    const left = byId(store, String(payload.left || payload.a || ""));
    const right = byId(store, String(payload.right || payload.b || ""));
    return joinCards(left, right, payload.join_type || payload.type, {
      backdate: Boolean(payload.backdate),
      note: payload.note || "",
      src: payload.src || "4dmap",
    });
  }
  if (resolved === "list") {
    return { ok: true, op: "list", cards: store, forks: findForks(store), receipts: store.map(cardReceipt) };
  }
  if (resolved === "example") {
    const pin = await makeCard({
      id: "4dm-example-pin",
      t: "2026-09-10T00:00:00Z",
      src: "synthetic",
      note: "synthetic T pin — not a real case",
      prev: GENESIS_PREV,
      pi: PI_EMPTY,
    });
    return { ok: true, synthetic: true, cards: [pin], limitation: LIMITATION };
  }
  if (resolved === "card_new") {
    const card = await makeCard({
      id: payload.id,
      t: payload.t,
      delta: payload.delta,
      gamma: payload.gamma,
      pi: payload.pi,
      prev: payload.prev,
      src: payload.src || "operator",
      note: payload.note || "4DM-CARD",
      expected_h: payload.expected_h || payload.h,
    });
    return withReceipt({ ok: true, op: "card_new", card, id: card.id, h: card.h });
  }
  if (resolved === "verify_hash") {
    let card = payload.card;
    if (!card && (payload.id || payload.h)) {
      card = payload.id ? byId(store, String(payload.id)) : store.find((c) => c.h === payload.h);
    }
    const checked = await verifyCard(card);
    return { ok: true, op: "verify_hash", ...checked, receipt: cardReceipt(card) };
  }
  if (resolved === "card_export") {
    for (const card of store) await verifyCard(card);
    const bundle = {
      format: "4DM-CARD-JSON",
      schema: SCHEMA,
      spec: SPEC,
      version: VERSION,
      product: PRODUCT,
      author: AUTHOR,
      role: "inspection",
      domains_are_doors: false,
      cards: store,
      n: store.length,
      forks: findForks(store),
    };
    return { ok: true, op: "card_export", ...bundle, bundle };
  }
  if (resolved === "card_import") {
    let raw = payload.bundle != null ? payload.bundle : payload.json;
    if (raw == null) raw = payload;
    if (typeof raw === "string") raw = JSON.parse(raw);
    let incoming = [];
    if (Array.isArray(raw)) incoming = raw;
    else if (raw && typeof raw === "object") {
      if (Array.isArray(raw.cards)) incoming = raw.cards;
      else if (raw.bundle && Array.isArray(raw.bundle.cards)) incoming = raw.bundle.cards;
      else if (raw.id && raw.h) incoming = [raw];
    } else {
      throw new CardError("IMPORT_REFUSE", "card_import expects a JSON object or card list");
    }
    const imported = [];
    const existing = new Set(store.map((c) => c.h));
    for (const card of incoming) {
      if (!card || typeof card !== "object") throw new CardError("IMPORT_REFUSE", "each imported card must be an object");
      await verifyCard(card);
      if (!existing.has(card.h)) {
        store.push(card);
        existing.add(card.h);
      }
      imported.push(card);
    }
    return { ok: true, op: "card_import", format: "4DM-CARD-JSON", n: imported.length, cards: imported, forks: findForks(store), receipts: imported.map(cardReceipt) };
  }
  if (resolved === "frame_status") {
    const companions = Object.entries(COMPANIONS).map(([slug, info]) => ({
      software: info.software,
      slug,
      axes: info.axes.slice(),
      role: "inspection_input",
      cite_only: true,
      door: false,
      merged: false,
    }));
    return {
      ok: true,
      op: "frame_status",
      product: PRODUCT,
      name: PRODUCT_NAME,
      version: VERSION,
      spec: SPEC,
      schema: SCHEMA,
      bucket: BUCKET,
      author: AUTHOR,
      cards: store.length,
      live_ops: LIVE_OPS.slice(),
      refuse_ops: Object.keys(REFUSE_OPS),
      companions,
      mesh: { default_off: true, get_enables: false, node_gate: false },
      library: LIBRARY,
      growth: DISCOVERY.growth,
      discovery: DISCOVERY,
      akm: AKM,
      limitation: LIMITATION,
      guardrail: GUARDRAIL,
      pipeline: PIPELINE,
      pipeline_note: PIPELINE_NOTE,
      ...MASTER33,
    };
  }
  if (resolved === "axis_describe") {
    const wanted = payload.axis;
    const axes = {};
    for (const [key, frame] of Object.entries(AXIS_FRAME)) {
      if (wanted && normalizeAxis(wanted) !== key) continue;
      axes[key] = {
        ...frame,
        companions: frame.companions.map((slug) => ({
          software: COMPANIONS[slug].software,
          slug,
          role: "inspection_input",
          cite_only: true,
          door: false,
          merged: false,
        })),
        ops: frame.ops.slice(),
      };
    }
    return {
      ok: true,
      op: "axis_describe",
      axis: wanted ? normalizeAxis(wanted) : null,
      axes,
      role: "inspection",
      domains_are_doors: false,
      n: store.length,
    };
  }
  if (resolved === "verify_chain") {
    const tip = String(payload.tip || payload.id || "");
    const walked = await runOp("walk", { tip }, store);
    const hashes = [];
    for (const card of walked.cards) {
      const checked = await verifyCard(card);
      hashes.push(checked.h);
    }
    return {
      ok: true,
      op: "verify_chain",
      tip,
      verified: hashes.length,
      n: hashes.length,
      hashes,
      broken: null,
      steps: walked.steps,
      forks: walked.forks,
    };
  }
  if (resolved === "memory_cite") {
    refuseAkmAbuse(payload);
    const card = cardFromPayload(payload, store);
    await verifyCard(card);
    return {
      ok: true,
      op: "memory_cite",
      id: card.id,
      h: card.h,
      receipt: cardReceipt(card),
      cited: true,
      card_rewritten: false,
      history_rewrite: false,
      posterior_is_truth: false,
      belief_is_not_truth: true,
      authorizes_action: false,
      software_tab: false,
      door: false,
      fabric: true,
      akm: AKM,
      note: "optional AKM-TRIAD-1.0 fabric cite. Inspection card unchanged. Posterior ≠ truth.",
    };
  }
  if (resolved === "memory_observe") {
    refuseAkmAbuse(payload);
    const card = cardFromPayload(payload, store);
    await verifyCard(card);
    return {
      ok: true,
      op: "memory_observe",
      id: card.id,
      h: card.h,
      receipt: cardReceipt(card),
      observation: observationFromCard(card, payload),
      forwarded: false,
      card_rewritten: false,
      history_rewrite: false,
      posterior_is_truth: false,
      belief_is_not_truth: true,
      authorizes_action: false,
      software_tab: false,
      door: false,
      fabric: true,
      akm: AKM,
      fraggate: "memory_observe",
      http: "POST /v1/memory/observe",
      note: "optional observation packet for FragGate memory_observe. 4DMap does not own AKM. Not forwarded unless the operator uses FragGate. Posterior ≠ truth. No history rewrite.",
    };
  }
  throw new CardError("UNKNOWN_OP", `unknown op ${op}`);
}

export function displayEnvelope(op, result) {
  const fields = [];
  for (const key of ["ok", "code", "id", "h", "join", "pi", "score", "capped", "forks_kept", "axis", "glyph", "n", "verified", "format", "role", "surface", "feature_h", "lattice", "collapsed"]) {
    if (result && result[key] !== undefined) fields.push({ label: key, value: String(result[key]) });
  }
  return {
    display: {
      title: `4DMap ${op}`,
      summary: result.message || result.note || (result.ok === false ? "refused" : "ok"),
      fields,
      next: "Show this 4DMap output, then take the next input.",
    },
    result,
  };
}

export const LIVE_OPS = [
  "health",
  "skill",
  "pin",
  "span",
  "stack",
  "gap",
  "fork",
  "walk",
  "lens",
  "class",
  "cohort",
  "absence",
  "cap",
  "join",
  "list",
  "example",
  "card_new",
  "card_pin",
  "card_span",
  "card_join",
  "card_walk",
  "card_list",
  "verify_hash",
  "card_export",
  "card_import",
  "frame_status",
  "axis_describe",
  "walk_trace",
  "verify_chain",
  "memory_cite",
  "memory_observe",
  "library_pin",
  "plot",
  "possibility",
  "pattern_recall",
  "lattice_tip",
  "poison_refuse",
  "neighbor_cite",
];
