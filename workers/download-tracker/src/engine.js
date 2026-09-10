/**
 * 4DMap hosted engine — 4DM-CARD, typed joins, fail-closed SHA-256.
 * Mirrors the Python fourdmap package. Author: Aziel Eliab only.
 */
export const PRODUCT = "4dmap";
export const PRODUCT_NAME = "4DMap";
export const VERSION = "0.1.0";
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
  → Domain Doors (isolated engines)  ←──  4DMap inspection cards sit HERE as
       a read-side coordinate frame over TemporalLock/StaticClock/ChronoLock/
       TrajectoryLock/SpectralLock evidence (not a hop gate)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT`;

export const PIPELINE_NOTE =
  "4DMap is not inserted as another sequential gate. It is a domain-door / inspection frame: engines and operator UI write/read 4DM cards; FragGate grounded claims may cite join types; ChainLock may stamp a walk when the operator seals. QNS/QNM do not carry 4DMap photons.";

export const ALLOWED_JOINS = new Set(["T-DELTA", "DELTA-T", "DELTA-GAMMA", "GAMMA-DELTA", "GAMMA-PI", "PI-GAMMA", "T-PI"]);
export const ILLEGAL_JOINS = new Set(["PI-T"]);

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
  return { ok: true, join: `${leftAxis}-${rightAxis}`, allowed: true, card, left: left.id, right: right.id };
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
  const store = [...cards];
  if (op === "pin") {
    const card = await makeCard({ t: payload.t, src: payload.src || "operator", note: payload.note || "T pin", prev: payload.prev, id: payload.id, pi: PI_EMPTY });
    return { ok: true, op: "pin", axis: "T", card, id: card.id, h: card.h };
  }
  if (op === "span") {
    const left = byId(store, String(payload.from_id || payload.a || ""));
    const right = byId(store, String(payload.to_id || payload.b || ""));
    await verifyCard(left);
    await verifyCard(right);
    const card = await makeCard({
      delta: { from: left.id, to: right.id, from_t: left.t, to_t: right.t },
      src: payload.src || "operator",
      note: payload.note || "Δ span",
      prev: String(right.h || left.h),
      pi: PI_EMPTY,
    });
    return { ok: true, op: "span", axis: "DELTA", card, id: card.id, h: card.h };
  }
  if (op === "stack") {
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
    return { ok: true, op: "stack", axis: "GAMMA", card, id: card.id, h: card.h };
  }
  if (op === "gap") {
    const card = await makeCard({
      delta: { gap: true, from: payload.from_id || payload.t0, to: payload.to_id || payload.t1 },
      src: payload.src || "operator",
      note: payload.note || "Δ gap",
      prev: payload.prev,
      pi: PI_EMPTY,
    });
    return { ok: true, op: "gap", axis: "DELTA", card, id: card.id, h: card.h };
  }
  if (op === "fork") {
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
    return { ok: true, op: "fork", card: sibling, id: sibling.id, h: sibling.h, forks_kept: true, winner: null, forks: findForks(next) };
  }
  if (op === "walk") {
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
    return { ok: true, op: "walk", tip, cards: chain, n: chain.length, forks: findForks(store) };
  }
  if (op === "lens" || op === "absence") {
    const query = String(payload.query || "").trim();
    if (!query) return { ok: true, op, pi: PI_EMPTY, silent: true, note: "lens silent → Π-EMPTY" };
    const hits = [];
    for (const card of store.concat(payload.cards || [])) {
      const blob = ["id", "note", "src", "t", "pi"].map((k) => String(card[k] || "")).join(" ");
      if (blob.toLowerCase().includes(query.toLowerCase())) hits.push(card.id);
    }
    if (!hits.length) return { ok: true, op, pi: PI_EMPTY, silent: true, note: "lens silent → Π-EMPTY" };
    return { ok: true, op, pi: { class: "lens-hit", ids: hits }, silent: false, hits };
  }
  if (op === "class") {
    const label = String(payload.label || "").trim();
    if (!label) return { ok: true, op: "class", pi: PI_EMPTY, silent: true };
    const card = await makeCard({ pi: { class: label }, src: payload.src || "operator", note: payload.note || `Π class ${label}`, prev: payload.prev });
    return { ok: true, op: "class", pi: card.pi, card, id: card.id, h: card.h };
  }
  if (op === "cohort") {
    const ids = (payload.ids || []).map(String);
    if (!ids.length) return { ok: true, op: "cohort", pi: PI_EMPTY, silent: true };
    const card = await makeCard({ pi: { cohort: ids }, src: payload.src || "operator", note: payload.note || "Π cohort", prev: payload.prev });
    return { ok: true, op: "cohort", card, id: card.id, h: card.h };
  }
  if (op === "cap") {
    const score = Number(payload.score ?? payload.confidence ?? 0);
    if (!Number.isFinite(score)) throw new CardError("CAP_REFUSE", "score must be a number");
    const capped = Math.min(Math.max(score, 0), ZION_CAP);
    return { ok: true, op: "cap", score: capped, raw: score, capped: score > ZION_CAP, zion_cap: ZION_CAP, note: "ZionPattern cap 75%" };
  }
  if (op === "join") {
    const left = byId(store, String(payload.left || payload.a || ""));
    const right = byId(store, String(payload.right || payload.b || ""));
    return joinCards(left, right, payload.join_type || payload.type, {
      backdate: Boolean(payload.backdate),
      note: payload.note || "",
      src: payload.src || "4dmap",
    });
  }
  if (op === "list") return { ok: true, op: "list", cards: store, forks: findForks(store) };
  if (op === "example") {
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
  throw new CardError("UNKNOWN_OP", `unknown op ${op}`);
}

export function displayEnvelope(op, result) {
  const fields = [];
  for (const key of ["ok", "code", "id", "h", "join", "pi", "score", "capped", "forks_kept"]) {
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

export const LIVE_OPS = ["health", "skill", "pin", "span", "stack", "gap", "fork", "walk", "lens", "class", "cohort", "absence", "cap", "join", "list", "example"];
