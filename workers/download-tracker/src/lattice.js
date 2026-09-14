/**
 * Hashchain lattice — library pins, possibility hooks, pattern memory.
 * Tips / prev-hash / pin receipts. Not a detached ML store. NO-REWRITE.
 * Author: Aziel Eliab only.
 */
import {
  AXIS_GLYPH,
  CardError,
  GENESIS_PREV,
  PI_EMPTY,
  SCHEMA,
  ZION_CAP,
  axisOf,
  cardReceipt,
  companionCite,
  makeCard,
  verifyCard,
  canonicalJson,
} from "./engine.js";

export const PIN_FRAME_KIND = "4DM-PIN-FRAME";
export const GROWTH = "ON";

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
  author: "Aziel Eliab",
};

export const DISCOVERY = {
  growth: GROWTH,
  skill: true,
  openapi: true,
  mcp: true,
  worker_ui: true,
  reason: "library pin + lattice memory LIVE_OPS",
};

const DATE_RE = /^(\d{4}-\d{2}-\d{2})([T ](\d{2}:\d{2}(:\d{2})?)(Z|[+-]\d{2}:\d{2})?)?$/;
const GAZ_RE = /^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$/;
const POISON_MARKERS = ["poison", "malware", "payload_drop", "__proto__", "constructor.prototype"];

function bytesToHex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function sha256Hex(value) {
  const raw = typeof value === "string" ? value : canonicalJson(value);
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  return bytesToHex(hash);
}

export function clockOf(value) {
  if (value == null || value === "") return null;
  if (typeof value === "object" && !Array.isArray(value)) {
    for (const key of ["clock", "date", "paper_date", "t"]) {
      const inner = clockOf(value[key]);
      if (inner) return inner;
    }
    return null;
  }
  const text = String(value).trim();
  if (!text || !DATE_RE.test(text)) return null;
  if (!text.includes("T") && !text.includes(" ")) return text + "T00:00:00Z";
  return text.replace(" ", "T");
}

export function parseClock(payload) {
  for (const key of ["date", "paper_date", "t", "clock"]) {
    const got = clockOf(payload[key]);
    if (got) return got;
  }
  if (payload.t && typeof payload.t === "object") return clockOf(payload.t);
  return null;
}

function asNum(raw, name) {
  if (raw == null || raw === "") return null;
  if (typeof raw === "boolean") throw new CardError("ANCHOR_REFUSE", name + " must be a finite number, not a boolean");
  const value = Number(raw);
  if (!Number.isFinite(value)) throw new CardError("ANCHOR_REFUSE", name + " is not finite");
  return value;
}

export function validateAnchor(lat, lon, gazetteerId, requirePlace = false) {
  const latN = asNum(lat, "lat");
  const lonN = asNum(lon, "lon");
  if ((latN == null) !== (lonN == null)) throw new CardError("ANCHOR_REFUSE", "lat and lon must be supplied together");
  if (latN != null && (latN < -90 || latN > 90)) throw new CardError("ANCHOR_REFUSE", "lat must be inside [-90, 90]");
  if (lonN != null && (lonN < -180 || lonN > 180)) throw new CardError("ANCHOR_REFUSE", "lon must be inside [-180, 180]");
  let gaz = null;
  if (gazetteerId != null && gazetteerId !== "") {
    gaz = String(gazetteerId).trim();
    if (!GAZ_RE.test(gaz)) throw new CardError("ANCHOR_REFUSE", "gazetteer_id must be an opaque place token, not a DNS/ICANN name");
    const tail = gaz.includes(".") && !gaz.includes(":") ? gaz.split(".").pop() : "";
    if (tail && /^[A-Za-z]+$/.test(tail)) throw new CardError("ANCHOR_REFUSE", "gazetteer_id is not a domain; no fake ICANN");
  }
  if (requirePlace && latN == null && !gaz) {
    throw new CardError("ANCHOR_INCOMPLETE", "library pin needs lat/lon or a gazetteer id (paper place)");
  }
  return { lat: latN, lon: lonN, gazetteer_id: gaz };
}

export async function featureHash(event, clock, lat, lon, gazetteerId) {
  return sha256Hex({
    clock: clock || "",
    event: String(event || "").trim().toLowerCase(),
    gazetteer_id: gazetteerId || "",
    lat: lat == null ? null : Math.round(Number(lat) * 1e5) / 1e5,
    lon: lon == null ? null : Math.round(Number(lon) * 1e5) / 1e5,
  });
}

function surfaceOf(raw) {
  const text = String(raw || "MOCK").trim().toUpperCase();
  if (text === "REAL" || text === "LIVE") return "REAL";
  if (text === "MOCK" || text === "SYNTHETIC" || text === "EXAMPLE") return "MOCK";
  throw new CardError("SURFACE_REFUSE", "surface must be REAL or MOCK");
}

function unwrapIngest(payload) {
  if (payload.ingest && typeof payload.ingest === "object") return { ...payload, ...payload.ingest };
  if (payload.pin_frame && typeof payload.pin_frame === "object") return { ...payload, ...payload.pin_frame };
  if (payload.descriptor && typeof payload.descriptor === "object") return { ...payload, ...payload.descriptor };
  return payload;
}

export function refuseFeatureSet(cards) {
  const out = new Set();
  for (const card of cards || []) {
    const pi = card.pi;
    if (!pi || typeof pi !== "object" || !pi.refuse) continue;
    const feature = String(pi.feature_h || "").trim().toLowerCase();
    if (feature.length === 64 && /^[0-9a-f]+$/.test(feature)) out.add(feature);
  }
  return out;
}

function poisonText(...parts) {
  const blob = parts.map((p) => String(p || "")).join(" ").toLowerCase();
  for (const mark of POISON_MARKERS) {
    if (blob.includes(mark)) throw new CardError("POISON_REFUSE", "poison feature refused (hash/feature only; not stored as payload)");
  }
}

export function labeledScore(label, value, extra = {}) {
  if (value == null || value === "") return null;
  const number = Number(value);
  if (!Number.isFinite(number)) throw new CardError("SCORE_REFUSE", label + " is not finite");
  return {
    label,
    value: Math.min(Math.max(number, 0), 1),
    truth: false,
    courtroom_proof: false,
    ...extra,
  };
}

export function possibilityHooks({ clock, event, lat, lon, gazetteer_id, bayesian, incoming_possibility, collapsed_score }) {
  if (collapsed_score != null && collapsed_score !== "") {
    throw new CardError("SCORE_COLLAPSE", "unlabeled score refused — cite possibility and bayesian separately");
  }
  const clockPart = clock ? 0.4 : 0;
  let geoPart = 0;
  let geoKind = "none";
  if (lat != null && lon != null) {
    geoPart = 0.4;
    geoKind = "latlon";
  } else if (gazetteer_id) {
    geoPart = 0.25;
    geoKind = "gazetteer";
  }
  const eventPart = String(event || "").trim() ? 0.2 : 0;
  const computed = Math.min(clockPart + geoPart + eventPart, 1);
  const hooks = {};
  if (incoming_possibility != null && incoming_possibility !== "") {
    let incoming = incoming_possibility;
    if (typeof incoming_possibility === "object") {
      const lab = String(incoming_possibility.label || "").toLowerCase();
      if (lab && lab !== "possibility" && lab !== "plausibility") {
        throw new CardError("SCORE_COLLAPSE", "incoming possibility must keep label=possibility");
      }
      incoming = incoming_possibility.value;
    }
    hooks.possibility = labeledScore("possibility", computed, { axes: ["T", "geo"], source: "computed" });
    hooks.possibility_cited = labeledScore("possibility", incoming, { axes: ["T", "geo"], source: "cited" });
  } else {
    hooks.possibility = labeledScore("possibility", computed, { axes: ["T", "geo"], source: "computed" });
  }
  if (bayesian && typeof bayesian === "object") {
    const lab = String(bayesian.label || "bayesian").trim().toLowerCase();
    if (!["bayesian", "posterior", "triad"].includes(lab)) {
      throw new CardError("SCORE_COLLAPSE", "bayesian input must keep label=bayesian");
    }
    hooks.bayesian = labeledScore("bayesian", bayesian.value != null ? bayesian.value : bayesian.score, {
      cite: String(bayesian.cite || bayesian.src || "library"),
      triad: bayesian.triad || null,
      posterior_is_truth: false,
    });
  } else if (bayesian != null && bayesian !== "") {
    hooks.bayesian = labeledScore("bayesian", bayesian, { cite: "library", posterior_is_truth: false });
  } else {
    hooks.bayesian = null;
  }
  hooks.collapsed = false;
  hooks.courtroom_proof = false;
  hooks.zion_cap = ZION_CAP;
  hooks.geo_kind = geoKind;
  hooks.note = "possibility = time×geo plausibility. bayesian = cited belief input. They are not one number. Neither is truth or courtroom proof.";
  return hooks;
}

export function libraryCite() {
  return {
    software: LIBRARY.software,
    slug: LIBRARY.slug,
    role: LIBRARY.role,
    cite_only: true,
    door: false,
    merged: false,
    map: LIBRARY.map,
    verify_geo: LIBRARY.verify_geo,
    note: LIBRARY.note,
  };
}

export function pinFrameOf(card) {
  const t = card && card.t;
  if (t && typeof t === "object" && (t.kind === PIN_FRAME_KIND || t.lat != null || t.gazetteer_id || t.event)) return t;
  return null;
}

export function emitPinFrame(card, hooks) {
  const frame = pinFrameOf(card) || {};
  return {
    kind: PIN_FRAME_KIND,
    schema: SCHEMA,
    id: card.id,
    h: card.h,
    prev: card.prev,
    axis: "T",
    glyph: "T",
    src: card.src,
    event: frame.event,
    clock: frame.clock || clockOf(card.t),
    lat: frame.lat,
    lon: frame.lon,
    gazetteer_id: frame.gazetteer_id,
    doc_id: frame.doc_id,
    surface: frame.surface || (String(card.src || "") === "synthetic" ? "MOCK" : "REAL"),
    feature_h: frame.feature_h,
    library: LIBRARY,
    receipt: cardReceipt(card),
    hooks: hooks || null,
    truth: false,
    courtroom_proof: false,
    gis: false,
  };
}

export function tipsOf(cards) {
  const referenced = new Set();
  for (const card of cards || []) {
    const prev = String(card.prev || "");
    if (prev && prev !== GENESIS_PREV) referenced.add(prev);
  }
  const tips = [];
  for (const card of cards || []) {
    const h = String(card.h || "");
    if (h && !referenced.has(h)) {
      const axis = axisOf(card);
      tips.push({ id: card.id, h, prev: card.prev, axis, glyph: AXIS_GLYPH[axis] });
    }
  }
  return tips;
}

export async function parseIngest(payload, cards) {
  const raw = unwrapIngest(payload || {});
  if (raw.poison || raw.poison_feature) throw new CardError("POISON_REFUSE", "poison feature refused (hash/feature only)");
  if (raw.upload_time && !(raw.date || raw.paper_date || raw.t)) {
    throw new CardError("CLOCK_REFUSE", "library pins use paper date, never upload time");
  }
  const event = String(raw.event || raw.title || "").trim();
  const clock = parseClock(raw);
  if (!clock) throw new CardError("CLOCK_REFUSE", "library pin needs a paper date (event date), never upload time");
  if (!event) throw new CardError("EVENT_REFUSE", "library pin needs an event descriptor");
  poisonText(event, raw.note, raw.gazetteer_id);
  const nestedT = raw.t && typeof raw.t === "object" ? raw.t : {};
  const anchor = validateAnchor(
    raw.lat != null ? raw.lat : nestedT.lat,
    raw.lon != null ? raw.lon : nestedT.lon,
    raw.gazetteer_id || raw.gazetteer || nestedT.gazetteer_id,
    true,
  );
  const feature = await featureHash(event, clock, anchor.lat, anchor.lon, anchor.gazetteer_id);
  if (refuseFeatureSet(cards || []).has(feature)) {
    throw new CardError("POISON_REFUSE", "feature hash is on the lattice refuse set");
  }
  const surface = surfaceOf(raw.surface || raw.reality || payload.surface);
  let src = String(raw.src || payload.src || "aziel-corpus").trim().toLowerCase();
  if (["library", "aziel-digital-library", "azielcorpus"].includes(src)) src = "aziel-corpus";
  let docId = raw.doc_id || raw.document_id || raw.cursor || null;
  if (docId) docId = String(docId).trim();
  const unlabeled = raw.possibility == null && raw.bayesian == null && raw.possibility_score == null ? raw.score : null;
  const hooks = possibilityHooks({
    clock,
    event,
    lat: anchor.lat,
    lon: anchor.lon,
    gazetteer_id: anchor.gazetteer_id,
    bayesian: raw.bayesian || payload.bayesian,
    incoming_possibility: raw.possibility || raw.possibility_score || payload.possibility,
    collapsed_score: unlabeled,
  });
  return {
    t: {
      kind: PIN_FRAME_KIND,
      clock,
      event,
      lat: anchor.lat,
      lon: anchor.lon,
      gazetteer_id: anchor.gazetteer_id,
      doc_id: docId,
      surface,
      feature_h: feature,
    },
    event,
    clock,
    lat: anchor.lat,
    lon: anchor.lon,
    gazetteer_id: anchor.gazetteer_id,
    doc_id: docId,
    surface,
    src,
    feature_h: feature,
    hooks,
    note: String(raw.note || payload.note || surface + " library pin " + event),
    prev: raw.prev || payload.prev,
    id: raw.id || payload.id,
  };
}

export function wantsLibraryPin(payload) {
  if (!payload || typeof payload !== "object") return false;
  if (payload.ingest || payload.pin_frame || payload.descriptor) return true;
  if (payload.event || payload.gazetteer_id || payload.gazetteer) return true;
  if (payload.lat != null || payload.lon != null) return true;
  if (payload.date || payload.paper_date || payload.doc_id) return true;
  return false;
}

export async function runLibraryPin(payload, cards) {
  const parsed = await parseIngest(payload, cards);
  let prev = parsed.prev;
  if (!prev) {
    const tips = tipsOf(cards);
    prev = tips.length ? tips[tips.length - 1].h : GENESIS_PREV;
  }
  const card = await makeCard({
    id: parsed.id,
    t: parsed.t,
    src: parsed.src,
    note: parsed.note,
    prev,
    pi: PI_EMPTY,
  });
  const frame = emitPinFrame(card, parsed.hooks);
  return {
    ok: true,
    op: "library_pin",
    axis: "T",
    glyph: "T",
    card,
    id: card.id,
    h: card.h,
    prev: card.prev,
    feature_h: parsed.feature_h,
    surface: parsed.surface,
    pin_frame: frame,
    hooks: parsed.hooks,
    possibility: parsed.hooks.possibility,
    bayesian: parsed.hooks.bayesian,
    collapsed: false,
    library: libraryCite(),
    lattice: true,
    ml_store: false,
    rewrite: false,
    truth: false,
    courtroom_proof: false,
    companion: parsed.src === "aziel-corpus" ? libraryCite() : null,
    receipt: cardReceipt(card),
  };
}

export async function runPlot(cards) {
  const pins = [];
  const trajectories = [];
  for (const card of cards || []) {
    await verifyCard(card);
    const frame = pinFrameOf(card);
    if (frame && (frame.lat != null || frame.gazetteer_id)) {
      pins.push({
        id: card.id,
        h: card.h,
        prev: card.prev,
        clock: frame.clock,
        event: frame.event,
        lat: frame.lat,
        lon: frame.lon,
        gazetteer_id: frame.gazetteer_id,
        surface: frame.surface,
        feature_h: frame.feature_h,
        src: card.src,
        axis: "T",
      });
    }
    if (card.gamma && typeof card.gamma === "object" && Array.isArray(card.gamma.stack)) {
      trajectories.push({ kind: "stack", ids: card.gamma.stack.slice(), hs: (card.gamma.hs || []).slice(), card_id: card.id });
    }
    if (card.delta && typeof card.delta === "object" && card.delta.from && card.delta.to) {
      trajectories.push({ kind: "span", from: card.delta.from, to: card.delta.to, card_id: card.id });
    }
  }
  const byId = Object.fromEntries(pins.map((p) => [p.id, p]));
  for (const traj of trajectories) {
    if (traj.kind === "span") {
      const a = byId[traj.from];
      const b = byId[traj.to];
      if (a && b && a.lat != null && b.lat != null) {
        traj.from_xy = { lat: a.lat, lon: a.lon };
        traj.to_xy = { lat: b.lat, lon: b.lon };
      }
    }
  }
  return {
    ok: true,
    op: "plot",
    pins,
    trajectories,
    n: pins.length,
    gis: false,
    truth: false,
    courtroom_proof: false,
    note: "Inspection plot of lattice pins. Not GIS 4D. REAL vs MOCK labeled on each pin.",
  };
}

export async function runPossibility(payload, cards, pushCard) {
  let card = payload.card;
  if (!card && payload.id) card = (cards || []).find((c) => c.id === payload.id);
  let hooks;
  if (!card && (payload.event || payload.date || payload.ingest || payload.pin_frame)) {
    const pinned = await runLibraryPin(payload, cards);
    pushCard(pinned.card);
    card = pinned.card;
    hooks = pinned.hooks;
  } else if (card && typeof card === "object") {
    await verifyCard(card);
    const frame = pinFrameOf(card) || {};
    const unlabeled = payload.possibility == null && payload.bayesian == null ? payload.score : null;
    hooks = possibilityHooks({
      clock: frame.clock || clockOf(card.t),
      event: frame.event,
      lat: frame.lat,
      lon: frame.lon,
      gazetteer_id: frame.gazetteer_id,
      bayesian: payload.bayesian,
      incoming_possibility: payload.possibility || payload.possibility_score,
      collapsed_score: unlabeled,
    });
  } else {
    throw new CardError("NOT_FOUND", "possibility needs a pin card, id, or library ingest");
  }
  const scoreCard = await makeCard({
    pi: {
      scores: { possibility: hooks.possibility, bayesian: hooks.bayesian },
      collapsed: false,
      courtroom_proof: false,
      lattice: true,
      ml_store: false,
      pin_id: card.id,
      pin_h: card.h,
    },
    src: payload.src || card.src || "4dmap",
    note: payload.note || "possibility + bayesian hooks (labeled, not collapsed)",
    prev: String(card.h || GENESIS_PREV),
  });
  pushCard(scoreCard);
  return {
    ok: true,
    op: "possibility",
    id: scoreCard.id,
    h: scoreCard.h,
    prev: scoreCard.prev,
    card: scoreCard,
    pin: { id: card.id, h: card.h },
    hooks,
    possibility: hooks.possibility,
    bayesian: hooks.bayesian,
    collapsed: false,
    courtroom_proof: false,
    lattice: true,
    ml_store: false,
    rewrite: false,
    receipt: cardReceipt(scoreCard),
    note: hooks.note,
  };
}

export async function runPatternRecall(payload, cards, pushCard) {
  for (const card of cards || []) await verifyCard(card);
  const counts = {};
  for (const card of cards || []) {
    const frame = pinFrameOf(card);
    if (!frame || !frame.feature_h) continue;
    const key = String(frame.feature_h);
    if (!counts[key]) counts[key] = { feature_h: key, n: 0, event: frame.event, ids: [], hs: [] };
    counts[key].n += 1;
    counts[key].ids.push(card.id);
    counts[key].hs.push(card.h);
  }
  const recurring = Object.values(counts).filter((r) => r.n >= 2).sort((a, b) => b.n - a.n || a.feature_h.localeCompare(b.feature_h));
  const tips = tipsOf(cards);
  const prev = String(payload.prev || (tips.length ? tips[tips.length - 1].h : GENESIS_PREV));
  const memoryCard = await makeCard({
    pi: {
      lattice: true,
      ml_store: false,
      patterns: recurring.map((r) => ({ feature_h: r.feature_h, n: r.n, event: r.event })),
      store: "hashchain",
      tips: tips.map((t) => t.h),
    },
    src: payload.src || "4dmap",
    note: payload.note || "lattice pattern recall (hash/feature only)",
    prev,
  });
  pushCard(memoryCard);
  return {
    ok: true,
    op: "pattern_recall",
    card: memoryCard,
    id: memoryCard.id,
    h: memoryCard.h,
    prev: memoryCard.prev,
    patterns: recurring,
    n: recurring.length,
    tips,
    lattice: true,
    ml_store: false,
    rewrite: false,
    receipt: cardReceipt(memoryCard),
    note: "Recurring event patterns counted on the hashchain lattice. Not a detached ML store.",
  };
}

export async function runPoisonRefuse(payload, cards, pushCard) {
  const raw = unwrapIngest(payload || {});
  let feature = String(raw.feature_h || raw.feature || "").trim().toLowerCase();
  if (!feature) {
    const event = String(raw.event || "").trim();
    const clock = parseClock(raw);
    const anchor = validateAnchor(raw.lat, raw.lon, raw.gazetteer_id, false);
    if (!event && !clock && anchor.lat == null && !anchor.gazetteer_id) {
      throw new CardError("POISON_REFUSE", "poison refuse needs a feature hash or event/date/geo to hash");
    }
    feature = await featureHash(event, clock, anchor.lat, anchor.lon, anchor.gazetteer_id);
  }
  if (feature.length !== 64 || !/^[0-9a-f]+$/.test(feature)) feature = await sha256Hex(feature);
  const tips = tipsOf(cards);
  const prev = String(payload.prev || (tips.length ? tips[tips.length - 1].h : GENESIS_PREV));
  const card = await makeCard({
    pi: { refuse: true, feature_h: feature, kind: "poison", store: "hashchain", ml_store: false },
    src: payload.src || "4dmap",
    note: payload.note || "poison feature refuse (hash only)",
    prev,
  });
  pushCard(card);
  return {
    ok: true,
    op: "poison_refuse",
    card,
    id: card.id,
    h: card.h,
    prev: card.prev,
    feature_h: feature,
    refused_set: [...refuseFeatureSet([...(cards || []), card])].sort(),
    payload_stored: false,
    lattice: true,
    ml_store: false,
    rewrite: false,
    receipt: cardReceipt(card),
    note: "Refuse set is append-only on the lattice. Feature hash only. No rewrite.",
  };
}

export async function runLatticeTip(cards) {
  for (const card of cards || []) await verifyCard(card);
  const tips = tipsOf(cards);
  return {
    ok: true,
    op: "lattice_tip",
    tips,
    n: tips.length,
    cards: (cards || []).length,
    genesis: GENESIS_PREV,
    rewrite: false,
    ml_store: false,
    lattice: true,
    note: "Tips are cards whose h is not cited as prev. Append-only.",
  };
}

export async function runNeighborCite(payload, cards) {
  let card = payload.card;
  const cardId = String(payload.id || payload.card_id || payload.tip || "");
  if (!card && cardId) card = (cards || []).find((c) => c.id === cardId);
  if (!card || typeof card !== "object") {
    throw new CardError("4DM-MISSING", "Unknown card_id. Cite a neighbor on a declared card.");
  }
  await verifyCard(card);
  const neighbors = [libraryCite()];
  const cited = companionCite(card.src, axisOf(card));
  if (cited) neighbors.push(cited);
  return {
    ok: true,
    op: "neighbor_cite",
    id: card.id,
    h: card.h,
    join_type: "neighbor",
    neighbors,
    library: libraryCite(),
    receipt: cardReceipt(card),
    companions_merged: false,
    second_door: false,
    note: "Research-domain neighbor cite. Aziel Digital Library + inspection companions. Products are not merged.",
  };
}
