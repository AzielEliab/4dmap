/**
 * Hermetic AZNews ↔ 4DMap check for the Worker engine.
 * No network. No isolate memory. Records travel with the call.
 * Author: Aziel Eliab.
 */
import assert from "node:assert/strict";
import { LIVE_OPS, runOp } from "../src/engine.js";
import { ABSENT_CODE, LIBRARY_CODE, runAznews } from "../src/aznews.js";

const IMAGE = "ab".repeat(32);
const FETCHED = {
  id: "nw-harbor",
  date: "2026-03-01",
  event: "Harbor inspection",
  place: "Lisbon",
  wording: "A fetched harbor note with enough words to open again.",
  score: 3,
  image_hash: IMAGE,
  fetched: true,
};

for (const op of ["news_status", "news_ingest", "news_pin", "news_open"]) {
  assert.equal(LIVE_OPS.includes(op), true, op);
}

const frame = await runOp("frame_status", {}, []);
assert.equal(frame.aznews.software_tab, false);
assert.equal(frame.aznews.live, false);
assert.equal(frame.aznews.fourdmap_live, false);
assert.equal(frame.aznews.library_map_is_aznews, false);
assert.equal(frame.aznews.paths.standalone.op, "news_ingest");
assert.deepEqual(frame.aznews.paths.joined.ops, ["news_pin", "news_open"]);
assert.equal(frame.companions.some((row) => row.slug === "aznews"), false);

const empty = await runAznews("news_ingest", { records: [] }, []);
assert.equal(empty.ok, false);
assert.equal(empty.code, ABSENT_CODE);
assert.equal(empty.live, false);
assert.deepEqual(empty.records, []);

const library = await runAznews("news_pin", { records: [], url: frame.aznews.library_map, event: "paper", date: "1912-04-15", place: "Atlantic" }, []);
assert.equal(library.code, LIBRARY_CODE);
assert.equal(library.live, false);

const pinned = await runOp("pin", { t: "2026-09-10T00:00:00Z", src: "synthetic", note: "clock only" }, []);
assert.equal(pinned.ok, true);
assert.equal(pinned.card.src, "synthetic");

const alone = await runAznews("news_ingest", { ...FETCHED, records: [] }, []);
assert.equal(alone.on_map, false);
assert.equal(alone.live, false);
assert.equal(alone.aznews_live, false);

const mapped = await runAznews("news_pin", { id: FETCHED.id, records: alone.records }, []);
assert.equal(mapped.on_map, true);
assert.equal(mapped.card.src, "aznews-fetch");
assert.equal(mapped.live, false);

const opened = await runAznews("news_open", { id: mapped.id, records: mapped.records }, []);
assert.equal(opened.wording, FETCHED.wording);
assert.match(opened.summary, /^Opened\./);
assert.equal(opened.join_live, true);
assert.equal(opened.aznews_live, true);
assert.equal(opened.live, true);
assert.equal(opened.fourdmap_live, false);
assert.equal(opened.catalog_live, false);
assert.equal(opened.fetched_from_network, false);
assert.equal(opened.merged, false);
assert.equal(opened.software_tab, false);
assert.equal(opened.cross_tether.azos_updated, false);
assert.equal(opened.cross_tether.interface_updated, false);
assert.equal(opened.cross_tether.runtime_claimed, false);

const pinOnly = await runAznews("news_pin", { ...FETCHED, records: [] }, []);
const pinOpened = await runAznews("news_open", { id: pinOnly.id, records: pinOnly.records }, []);
assert.equal(pinOpened.wording, FETCHED.wording);
assert.equal(pinOpened.join_live, false);
assert.equal(pinOpened.live, false);

const fixture = await runAznews(
  "news_ingest",
  {
    records: [],
    fixture: true,
    fixture_label: "fixture — not live news",
    date: "2026-01-02",
    event: "fixture drill",
    place: "fixture quay",
    wording: "This fixture story is not a fetched article.",
  },
  [],
);
assert.equal(fixture.live, false);
assert.equal(fixture.aznews_live, false);

console.log("ok aznews-4dmap");
