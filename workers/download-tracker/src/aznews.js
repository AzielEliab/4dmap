/**
 * AZNews beside 4DMap on the hosted /v1 surface.
 * Standalone ingest stores a story with no pin. news_pin and news_open are the join.
 * This file does not fetch a feed and does not keep isolate memory: the caller
 * sends records and receives them back. A fixture never flips a live flag.
 * The join is marked live only after one complete fetched item was stored off
 * the map and read back from a pin. 4DMap itself is not marked live.
 * Author: Aziel Eliab only.
 */
import { AUTHOR, CardError, GENESIS_PREV, LIBRARY, PI_EMPTY, PIN_FRAME_KIND, makeCard, scanIdentity, scanIntent } from "./engine.js";

export const ABSENT_CODE = "AZNEWS-SOURCE-ABSENT";
export const LIBRARY_CODE = "AZNEWS-NOT-LIBRARY";
export const ABSENT_MODULE = "workers/download-tracker/src/aznews.js";
export const ABSENT_SOURCE = "public Aziel news feed";
export const JOIN = "aznews-4dmap";
const LIBRARY_MAP = LIBRARY.map;
const DATE_RE = /^(\d{4}-\d{2}-\d{2})([T ](\d{2}:\d{2}(:\d{2})?)(Z|[+-]\d{2}:\d{2})?)?$/;
const HASH_RE = /^[a-f0-9]{64}$/;
const USER_RE = /^[a-zA-Z0-9._-]{1,80}$/;

function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(",") + "]";
  const keys = Object.keys(value).sort();
  return "{" + keys.map((key) => JSON.stringify(key) + ":" + canonicalJson(value[key])).join(",") + "}";
}

async function sha(payload) {
  const raw = canonicalJson(payload);
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function sentence(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function usernameOf(payload) {
  const raw = payload.username;
  const name = raw == null || raw === "" ? "operator" : String(raw).trim();
  if (!USER_RE.test(name)) {
    throw new CardError("AZNEWS-USERNAME-ABSENT", "A news receipt needs a short username handle. A legal name is not stored.");
  }
  scanIdentity(name);
  return name;
}

function clockOf(value) {
  const text = String(value || "").trim();
  if (!text || !DATE_RE.test(text)) return null;
  if (!text.includes("T") && !text.includes(" ")) return `${text}T00:00:00Z`;
  return text.replace(" ", "T");
}

function imageHash(raw) {
  if (raw == null || raw === "") return null;
  const text = typeof raw === "string" ? raw.trim().toLowerCase() : String((raw && (raw.content_hash || raw.sha256)) || "").trim().toLowerCase();
  if (!HASH_RE.test(text)) {
    throw new CardError("AZNEWS-ITEM-INCOMPLETE", "An image hash must be 64 hex characters. This package does not fetch image bytes.");
  }
  return text;
}

function scoreOf(raw) {
  if (raw == null || raw === "") return null;
  if (typeof raw === "boolean" || typeof raw === "object") {
    throw new CardError("AZNEWS-SCORE", "A score must be a finite number. Nothing was written.");
  }
  const number = Number(raw);
  if (!Number.isFinite(number)) throw new CardError("AZNEWS-SCORE", "A score must be a finite number. Nothing was written.");
  return Number.isInteger(number) ? number : number;
}

function placeOf(raw) {
  const place = String(raw.place || raw.geo || "").trim();
  const latMissing = raw.lat == null || raw.lat === "";
  const lonMissing = raw.lon == null || raw.lon === "";
  if (latMissing !== lonMissing) throw new CardError("AZNEWS-ANCHOR", "Latitude and longitude must be supplied together.");
  let lat = null;
  let lon = null;
  if (!latMissing) {
    lat = Number(raw.lat);
    lon = Number(raw.lon);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new CardError("AZNEWS-ANCHOR", "Latitude and longitude must be numbers.");
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      throw new CardError("AZNEWS-ANCHOR", "Latitude must be between -90 and 90, and longitude between -180 and 180.");
    }
  }
  if (!place && lat == null) throw new CardError("AZNEWS-ANCHOR", "A news item needs a place, or a latitude and longitude.");
  return { place, lat, lon };
}

function mentionsLibrary(payload) {
  const src = String((payload && (payload.src || payload.source)) || "").trim().toLowerCase();
  if (["aziel-corpus", "library", "aziel-digital-library", "azielcorpus"].includes(src)) return true;
  const blobs = [payload && payload.map, payload && payload.source_url, payload && payload.url];
  const item = payload && payload.item;
  if (item && typeof item === "object") blobs.push(item.map, item.source_url, item.url, item.src, item.source);
  return blobs.some((blob) => {
    const text = String(blob || "");
    return text.includes(LIBRARY_MAP) || ["aziel-corpus", "library"].includes(text.trim().toLowerCase());
  });
}

async function documentHash(item) {
  return sha({
    date: item.date,
    event: item.event,
    fetched: item.fetched === true,
    fixture: item.fixture === true,
    image_hash: item.image_hash ?? null,
    place: item.place,
    score: item.score ?? null,
    wording: item.wording,
  });
}

async function openHash(documentHashValue, wording) {
  return sha({ document_hash: documentHashValue, op: "news_open", wording });
}

function hasItem(payload) {
  const raw = payload && payload.item && typeof payload.item === "object" ? payload.item : payload;
  if (!raw || typeof raw !== "object") return false;
  return ["event", "wording", "body", "date", "headline", "place", "geo"].some((key) => raw[key] != null && raw[key] !== "");
}

async function itemFrom(payload) {
  const raw = payload.item && typeof payload.item === "object" ? payload.item : payload;
  if (!raw || typeof raw !== "object") throw new CardError("AZNEWS-ITEM-INCOMPLETE", "A news item must be an object.");
  scanIdentity(raw);
  scanIntent(raw);
  const fixture = payload.fixture === true || raw.fixture === true;
  const fetched = (payload.fetched === true || raw.fetched === true) && !fixture;
  let label = "";
  if (fixture) {
    label = String(payload.fixture_label || raw.fixture_label || "").trim();
    if (!/fixture/i.test(label) || label.length > 80) {
      throw new CardError("AZNEWS-FIXTURE-UNLABELED", "A test fixture must carry a short label that says fixture. An unlabeled item is not a news source.");
    }
  }
  const event = String(raw.event || "").trim();
  const wording = String(raw.wording || raw.body || "").trim();
  const headline = String(raw.headline || "").trim() || wording.slice(0, 240);
  const clock = clockOf(raw.date || raw.paper_date);
  if (!clock) throw new CardError("AZNEWS-CLOCK", "A news item needs a paper date. Upload time is not the event date.");
  if (!event) throw new CardError("AZNEWS-EVENT", "A news item needs an event.");
  if (!wording) throw new CardError("AZNEWS-ITEM-INCOMPLETE", "A news item needs wording so it can be opened in plain language.");
  if (event.length > 240 || headline.length > 240 || wording.length > 8000) {
    throw new CardError("AZNEWS-ITEM-INCOMPLETE", "Event, headline, and wording exceed the allowed length.");
  }
  const anchor = placeOf(raw);
  const image = imageHash(raw.image != null ? raw.image : raw.image_hash);
  const score = scoreOf(raw.score != null ? raw.score : payload.score);
  if (fetched && score == null) throw new CardError("AZNEWS-ITEM-INCOMPLETE", "A fetched item needs a score. None was filled in.");
  if (fetched && !image) {
    throw new CardError("AZNEWS-ITEM-INCOMPLETE", "A fetched item needs an image content hash. This package does not fetch image bytes.");
  }
  const item = {
    date: clock,
    event,
    headline,
    wording,
    place: anchor.place,
    lat: anchor.lat,
    lon: anchor.lon,
    image_hash: image,
    image_gap: image == null,
    score,
    fixture,
    fixture_label: label,
    fetched,
    origin: fixture ? "fixture" : fetched ? "fetch" : "supplied",
  };
  let itemId = String(raw.id || raw.item_id || "").trim();
  if (!itemId) itemId = "nw-" + (await documentHash(item)).slice(0, 12);
  if (itemId.length > 80) throw new CardError("AZNEWS-ITEM-INCOMPLETE", "An item id must stay within 80 characters.");
  item.id = itemId;
  return item;
}

async function loadRecords(payload) {
  if (!Object.prototype.hasOwnProperty.call(payload || {}, "records")) return [];
  const raw = payload.records;
  if (!Array.isArray(raw)) throw new CardError("AZNEWS-ITEM-INCOMPLETE", "records must be a list of news receipts.");
  const loaded = [];
  for (const row of raw) {
    if (!row || typeof row !== "object" || !row.item || typeof row.item !== "object") {
      throw new CardError("AZNEWS-ITEM-INCOMPLETE", "A news receipt must contain its item.");
    }
    const item = { ...row.item };
    const digest = await documentHash(item);
    if (String(row.document_hash || "") !== digest) throw new CardError("HASH_FAIL", "news record hash does not match the item");
    let opened = row.opened === true && row.on_map === true;
    let openReceipt = row.open_receipt && typeof row.open_receipt === "object" ? row.open_receipt : null;
    if (opened) {
      const expected = await openHash(digest, String(item.wording || ""));
      if (!openReceipt || openReceipt.open_hash !== expected) {
        opened = false;
        openReceipt = null;
      }
    }
    loaded.push({
      document_hash: digest,
      on_map: row.on_map === true,
      opened,
      item,
      pin_id: row.pin_id || null,
      card: row.card && typeof row.card === "object" ? row.card : null,
      receipt: row.receipt && typeof row.receipt === "object" ? row.receipt : {},
      open_receipt: openReceipt,
      username: row.username || "operator",
    });
  }
  return loaded;
}

function exportRecords(records) {
  return records.map((row) => ({
    document_hash: row.document_hash,
    on_map: row.on_map,
    opened: row.opened,
    item: row.item,
    pin_id: row.pin_id,
    card: row.card,
    receipt: row.receipt,
    open_receipt: row.open_receipt,
    username: row.username,
  }));
}

function fetchedRows(records) {
  return records.filter((row) => row.item.fetched === true && row.item.fixture !== true && row.item.origin === "fetch");
}

function joinReady(records) {
  const flags = new Map();
  for (const row of fetchedRows(records)) {
    const marks = flags.get(row.document_hash) || new Set();
    marks.add(row.on_map ? "map" : "alone");
    if (row.on_map && row.opened) marks.add("opened");
    flags.set(row.document_hash, marks);
  }
  for (const marks of flags.values()) {
    if (marks.has("alone") && marks.has("map") && marks.has("opened")) return true;
  }
  return false;
}

function cross() {
  return {
    azos_updated: false,
    interface_updated: false,
    runtime_claimed: false,
    runtime_done: false,
    note: "This package does not update AZ-OS, the human interface, or aziel-runtime. Those desks keep their own stores.",
  };
}

function flagsOf(records) {
  const ready = joinReady(records);
  const fetched = fetchedRows(records).length > 0;
  if (ready && !fetched) throw new CardError("AZNEWS-LIVE", "join live was set without a fetched item");
  return {
    live: ready,
    join_live: ready,
    joined: ready,
    aznews_live: ready,
    fourdmap_live: false,
    catalog_live: false,
    feed_configured: false,
    fetched_from_network: false,
    merged: false,
    installed: false,
    engine_installed: false,
    software_tab: false,
    mcp_tool: false,
    second_door: false,
    door: "fraggate",
    domains_are_doors: false,
    source_present: fetched,
    fixture_is_source: false,
    library_map_is_aznews: false,
    library_cite_merged: false,
  };
}

export function joinCard(records = []) {
  const flags = flagsOf(records);
  return {
    name: "AZNews",
    spec: JOIN,
    standalone: true,
    fourdmap_standalone: true,
    joined_into: "4dmap",
    software_tab: false,
    mcp_tool: false,
    catalog_slug: null,
    installed: false,
    merged: false,
    live: flags.live,
    join_live: flags.join_live,
    aznews_live: flags.aznews_live,
    fourdmap_live: false,
    catalog_live: false,
    feed_configured: false,
    fetched_from_network: false,
    source_present: flags.source_present,
    library_map: LIBRARY_MAP,
    library_map_is_aznews: false,
    library_cite_merged: false,
    absent_code: flags.source_present ? null : ABSENT_CODE,
    absent_module: ABSENT_MODULE,
    absent_source: ABSENT_SOURCE,
    paths: {
      standalone: { callable: true, op: "news_ingest" },
      joined: { callable: true, ops: ["news_pin", "news_open"] },
      fourdmap_without_news: { callable: true, op: "pin" },
    },
    cross_tether: cross(),
    author: AUTHOR,
  };
}

function seal(record, records) {
  const ready = joinReady(records);
  Object.assign(record, flagsOf(records));
  record.aznews = joinCard(records);
  record.cross_tether = cross();
  record.author = AUTHOR;
  if (record.refused === true || record.ok === false) {
    record.live = false;
    record.join_live = false;
    record.joined = false;
    record.aznews_live = false;
    record.round_trip = false;
    record.aznews = { ...record.aznews, live: false, join_live: false, aznews_live: false };
  }
  if (record.fourdmap_live === true) throw new CardError("AZNEWS-LIVE", "4DMap is marked live");
  if (record.merged === true || record.software_tab === true || record.installed === true) {
    throw new CardError("AZNEWS-LIVE", "AZNews is marked merged, installed, or listed as its own Softwares card");
  }
  if (record.live === true && !ready) {
    throw new CardError("AZNEWS-LIVE", "join live is true before a fetched item is stored both ways and opened");
  }
  if (record.catalog_live === true || record.feed_configured === true || record.fetched_from_network === true) {
    throw new CardError("AZNEWS-LIVE", "a feed was marked live though this package did not fetch one");
  }
  return record;
}

function summaryFor(item, records, onMap) {
  const ready = joinReady(records);
  if (!item) {
    return sentence(
      `No news source is present. AZNews can store a story without a pin (news_ingest). 4DMap can pin without a story. The join (news_pin, news_open) reads a stored story back from a pin. ${ABSENT_MODULE} does not fetch a feed. No ${ABSENT_SOURCE} is configured. The join is not marked live. AZNews is not marked live. 4DMap is not marked live.`,
    );
  }
  if (item.fixture) {
    const where = onMap ? "on a 4DMap pin" : "on the AZNews standalone path";
    return sentence(
      `A labeled fixture was stored ${where}. Date ${item.date}, event ${item.event}. A fixture is not a news source. The join is not marked live. AZNews is not marked live. 4DMap is not marked live.`,
    );
  }
  if (ready) {
    return sentence(
      `A fetched item is stored on AZNews and read back from a 4DMap pin. Date ${item.date}, event ${item.event}. The join is live for that item. This package did not GET a feed. 4DMap is not marked live as a product. AZNews is not a Softwares card and is not merged. AZ-OS and the human interface were not updated.`,
    );
  }
  if (item.fetched && onMap) {
    return sentence(
      `A fetched item is on a 4DMap pin. Date ${item.date}, event ${item.event}. The standalone AZNews copy is not stored yet, or the pin was not opened, so the join is not marked live. AZNews is not marked live. 4DMap is not marked live.`,
    );
  }
  if (item.fetched) {
    return sentence(
      `A fetched item is stored on the AZNews standalone path. Date ${item.date}, event ${item.event}. It is not yet read back from a 4DMap pin, so the join is not marked live. AZNews is not marked live. 4DMap is not marked live.`,
    );
  }
  const where = onMap ? "on a 4DMap pin" : "on the AZNews standalone path, not on a pin";
  return sentence(
    `A supplied item is stored ${where}. Date ${item.date}, event ${item.event}. It was not fetched by this package. The join is not marked live. AZNews is not marked live. 4DMap is not marked live.`,
  );
}

function refuse(op, code, text, records) {
  const summary = sentence(text);
  return seal(
    {
      ok: false,
      refused: true,
      op,
      code,
      absent_module: code === ABSENT_CODE ? ABSENT_MODULE : null,
      absent_source: code === ABSENT_CODE ? ABSENT_SOURCE : null,
      message: summary,
      summary,
      note: summary,
      records: exportRecords(records),
    },
    records,
  );
}

async function receiptFor(item, username, records, onMap) {
  const document_hash = await documentHash(item);
  const prev = records.length && records[records.length - 1].receipt ? records[records.length - 1].receipt.primary : GENESIS_PREV;
  const primary = await sha({ document_hash, prev, on_map: onMap });
  const secondary = await sha({ document_hash, username, on_map: onMap });
  if (records.some((row) => row.receipt && row.receipt.secondary === secondary)) {
    throw new CardError("AZNEWS-DOUBLE", "This document is already stored for that username on this path. It was not written again.");
  }
  return {
    kind: "aznews-receipt",
    document_hash,
    primary,
    primary_prev: prev,
    secondary,
    on_map: onMap,
    username,
    wording: item.wording,
    image_hash: item.image_hash,
    score: item.score,
    author: AUTHOR,
  };
}

async function storeItem(item, payload, records, onMap, card) {
  const username = usernameOf(payload);
  const receipt = await receiptFor(item, username, records, onMap);
  const row = {
    document_hash: receipt.document_hash,
    on_map: onMap,
    opened: false,
    item,
    pin_id: card ? card.id : null,
    card: card || null,
    receipt,
    open_receipt: null,
    username,
  };
  records.push(row);
  return row;
}

function resultOf(op, item, row, records) {
  const summary = summaryFor(item, records, row.on_map === true);
  const body = {
    ok: true,
    refused: false,
    op,
    path: row.on_map ? "joined" : "standalone",
    on_map: row.on_map,
    fixture: item.fixture === true,
    fixture_is_source: false,
    fixture_label: item.fixture_label || null,
    item_id: item.id,
    date: item.date,
    event: item.event,
    headline: item.headline,
    wording: item.wording,
    place: item.place,
    lat: item.lat,
    lon: item.lon,
    image_hash: item.image_hash,
    image_gap: item.image_gap === true,
    score: item.score,
    document_hash: row.document_hash,
    receipt: row.receipt,
    records: exportRecords(records),
    summary,
    note: summary,
    round_trip: joinReady(records),
  };
  if (row.card) {
    body.card = row.card;
    body.id = row.card.id;
    body.h = row.card.h;
    body.pin_frame = {
      kind: PIN_FRAME_KIND,
      date: item.date,
      event: item.event,
      place: item.place,
      lat: item.lat,
      lon: item.lon,
      surface: item.fixture ? "MOCK" : "REAL",
    };
  }
  return seal(body, records);
}

function prevHash(payload, cards) {
  if (payload && payload.prev) return String(payload.prev);
  if (cards && cards.length && cards[cards.length - 1] && cards[cards.length - 1].h) return String(cards[cards.length - 1].h);
  return GENESIS_PREV;
}

async function pinCard(item, prev) {
  const src = item.fixture ? "aznews-fixture" : item.fetched ? "aznews-fetch" : "aznews";
  const note = `${item.fixture ? "Fixture" : "News"} pin ${item.event}`;
  return makeCard({
    t: {
      kind: PIN_FRAME_KIND,
      clock: item.date,
      event: item.event,
      place: item.place,
      lat: item.lat,
      lon: item.lon,
      surface: item.fixture ? "MOCK" : "REAL",
      fixture: item.fixture === true,
      join: "aznews",
      news_id: item.id,
    },
    src,
    note,
    prev,
    pi: PI_EMPTY,
  });
}

function matchRecord(payload, records, onMap) {
  const pool = onMap ? records.filter((row) => row.on_map) : records.slice();
  const raw = payload && payload.item && typeof payload.item === "object" ? payload.item : payload || {};
  let wanted = String((payload && (payload.item_id || payload.pin_id || payload.id)) || "").trim();
  if (!wanted) wanted = String(raw.id || raw.item_id || "").trim();
  if (wanted) return pool.find((row) => row.item.id === wanted || row.pin_id === wanted) || null;
  const clock = clockOf(raw.date || raw.paper_date);
  const event = String(raw.event || "").trim();
  const place = String(raw.place || raw.geo || "").trim();
  if (!clock || !event) return null;
  return pool.find((row) => row.item.date === clock && row.item.event === event && (!place || row.item.place === place)) || null;
}

export async function runAznews(op, payload = {}, cards = []) {
  const records = await loadRecords(payload);
  if (mentionsLibrary(payload)) {
    return refuse(op, LIBRARY_CODE, "The library map is a corpus cite. It is not AZNews. Use library_pin for a corpus card.", records);
  }
  if (op === "news_status") {
    const fetched = fetchedRows(records);
    const ready = joinReady(records);
    const item = ready ? fetched[fetched.length - 1].item : null;
    const summary = summaryFor(item, records, ready);
    return seal(
      {
        ok: true,
        refused: false,
        op: "news_status",
        code: fetched.length ? null : ABSENT_CODE,
        absent_module: ABSENT_MODULE,
        absent_source: ABSENT_SOURCE,
        standalone_items: records.filter((row) => !row.on_map).length,
        pins: records.filter((row) => row.on_map).length,
        paths: joinCard(records).paths,
        summary,
        note: summary,
        records: exportRecords(records),
        round_trip: ready,
      },
      records,
    );
  }
  if (op === "news_ingest") {
    if (!hasItem(payload)) {
      return refuse(op, ABSENT_CODE, `AZNews refused this ingest. No news source is present. ${ABSENT_MODULE} returned no item, and no ${ABSENT_SOURCE} is configured. Nothing was written.`, records);
    }
    const item = await itemFrom(payload);
    const row = await storeItem(item, payload, records, false, null);
    return resultOf(op, item, row, records);
  }
  if (op === "news_pin") {
    let item;
    if (!hasItem(payload)) {
      const found = matchRecord(payload, records, false);
      if (!found) {
        return refuse(op, ABSENT_CODE, `AZNews refused this pin. No news source is present. ${ABSENT_MODULE} returned no item, and no ${ABSENT_SOURCE} is configured. Nothing was written.`, records);
      }
      item = { ...found.item };
    } else {
      item = await itemFrom(payload);
    }
    const card = await pinCard(item, prevHash(payload, cards));
    const row = await storeItem(item, payload, records, true, card);
    return resultOf(op, item, row, records);
  }
  if (op === "news_open") {
    const path = String(payload.path || "joined").trim().toLowerCase();
    const onMap = path !== "standalone" && path !== "aznews";
    if (!records.length) {
      return refuse(op, ABSENT_CODE, `AZNews refused this open. No news source is present. ${ABSENT_MODULE} has no stored item. Nothing was invented.`, records);
    }
    const found = matchRecord(payload, records, onMap);
    if (!found) return refuse(op, "AZNEWS-NO-MATCH", "No stored item matches that id, date, event, and place. Nothing was invented.", records);
    if (onMap && !found.on_map) return refuse(op, "AZNEWS-NO-MATCH", "That story is not pinned. Nothing was invented.", records);
    const item = found.item;
    if (found.on_map && !found.opened) {
      found.opened = true;
      found.open_receipt = { op: "news_open", open_hash: await openHash(found.document_hash, item.wording) };
    }
    const summary = "Opened. " + summaryFor(item, records, found.on_map === true);
    return seal(
      {
        ok: true,
        refused: false,
        op: "news_open",
        path: found.on_map ? "joined" : "standalone",
        on_map: found.on_map,
        fixture: item.fixture === true,
        fixture_is_source: false,
        item_id: item.id,
        id: found.pin_id,
        date: item.date,
        event: item.event,
        headline: item.headline,
        wording: item.wording,
        place: item.place,
        score: item.score,
        image_hash: item.image_hash,
        document_hash: found.document_hash,
        open_receipt: found.open_receipt,
        records: exportRecords(records),
        summary,
        note: summary,
        round_trip: joinReady(records),
      },
      records,
    );
  }
  throw new CardError("UNKNOWN_OP", `unknown op ${op}`);
}
