import * as THREE from "/static/vendor/three.module.min.js";

const ERAS = [1914, 1945, 1994, 2010];
const OPENED_KEY = "4dmap-opened-pins";
const Y_AXIS = new THREE.Vector3(0, 1, 0);
const X_AXIS = new THREE.Vector3(1, 0, 0);

const $ = (id) => document.getElementById(id);

const view = { lon: 10, lat: 18, dist: 3.15 };
const layers = { land: true, borders: true, satellite: false, street: false, lidar: false, shadow: false };
let spin = true;
let pins = [];
let places = [];
let land = null;
let borders = {};
let eraYear = 1914;
let satelliteImage = null;
let satelliteNote = "";
let focusId = null;
let areaRing = null;
const opened = new Set(JSON.parse(localStorage.getItem(OPENED_KEY) || "[]"));

const canvas = $("globe");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 40);
const globe = new THREE.Group();
scene.add(globe);
const earth = new THREE.Mesh(
  new THREE.SphereGeometry(1, 72, 48),
  new THREE.MeshPhongMaterial({ color: 0xffffff, shininess: 6 })
);
globe.add(earth);
const atmosphere = new THREE.Mesh(
  new THREE.SphereGeometry(1.07, 48, 32),
  new THREE.MeshBasicMaterial({ color: 0x9ec4d4, transparent: true, opacity: 0.22, side: THREE.BackSide })
);
scene.add(atmosphere);
scene.add(new THREE.AmbientLight(0xffffff, 0.72));
const sun = new THREE.DirectionalLight(0xfff4dd, 1.15);
sun.position.set(4, 2, 5);
scene.add(sun);
const pinGroup = new THREE.Group();
globe.add(pinGroup);
const areaGroup = new THREE.Group();
globe.add(areaGroup);

function dark() {
  return matchMedia("(prefers-color-scheme: dark)").matches;
}

function palette() {
  if (dark()) {
    return { bg: "#12110e", ocean: "#16303a", land: "#3e5248", border: "#e4d7b0", ink: "#f4efe6", grid: "rgba(228,215,176,0.25)" };
  }
  return { bg: "#f4f1ea", ocean: "#8eafbe", land: "#d7e3d2", border: "#243028", ink: "#1c1914", grid: "rgba(36,48,40,0.18)" };
}

function latLonToVector3(lat, lon, radius) {
  const phi = ((lon + 180) * Math.PI) / 180;
  const theta = ((90 - lat) * Math.PI) / 180;
  return new THREE.Vector3(
    -radius * Math.cos(phi) * Math.sin(theta),
    radius * Math.cos(theta),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function applyView() {
  const qLon = new THREE.Quaternion().setFromAxisAngle(Y_AXIS, THREE.MathUtils.degToRad(-(view.lon + 90)));
  const qLat = new THREE.Quaternion().setFromAxisAngle(X_AXIS, THREE.MathUtils.degToRad(view.lat));
  globe.quaternion.copy(qLat).multiply(qLon);
  camera.position.set(0, 0, view.dist);
  camera.lookAt(0, 0, 0);
}

function resize() {
  const w = canvas.clientWidth || innerWidth;
  const h = canvas.clientHeight || innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / Math.max(h, 1);
  camera.updateProjectionMatrix();
}

function nearestEra(year) {
  return ERAS.reduce((best, item) => (Math.abs(item - year) < Math.abs(best - year) ? item : best), ERAS[0]);
}

function eraCopy(year) {
  const bundled = nearestEra(year);
  const source = "Source: aourednik/historical-basemaps, simplified offline subset.";
  if (bundled === year) {
    return `Showing ${year} borders and names. ${source}`;
  }
  return `No bundled borders for ${year}. Showing ${bundled}, the nearest bundled era (${ERAS.join(", ")}). ${source}`;
}

function outerRing(feature) {
  const g = feature.geometry;
  if (!g) return null;
  if (g.type === "Polygon") return g.coordinates[0];
  if (g.type === "MultiPolygon") return g.coordinates[0] && g.coordinates[0][0];
  return null;
}

function traceCollection(ctx, collection, w, h) {
  if (!collection) return;
  for (const feature of collection.features || []) {
    const g = feature.geometry;
    if (!g) continue;
    const polys = g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
    for (const poly of polys) {
      for (const ring of poly) {
        let prev = null;
        for (let i = 0; i < ring.length; i += 1) {
          const lon = ring[i][0];
          const lat = ring[i][1];
          const x = ((lon + 180) / 360) * w;
          const y = ((90 - lat) / 180) * h;
          if (i === 0 || (prev && Math.abs(lon - prev) > 180)) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
          prev = lon;
        }
      }
    }
  }
}

function paintLabels(ctx, collection, colors, w, h) {
  ctx.fillStyle = colors.ink;
  ctx.font = "12px Georgia, serif";
  ctx.textAlign = "center";
  const used = [];
  for (const feature of collection.features || []) {
    const name = feature.properties && feature.properties.NAME;
    const ring = outerRing(feature);
    if (!name || !ring || ring.length < 6) continue;
    let south = 90, north = -90, west = 180, east = -180;
    for (const pair of ring) {
      south = Math.min(south, pair[1]);
      north = Math.max(north, pair[1]);
      west = Math.min(west, pair[0]);
      east = Math.max(east, pair[0]);
    }
    if (east - west > 120 || north - south < 6) continue;
    const lon = (west + east) / 2;
    const lat = (south + north) / 2;
    const x = ((lon + 180) / 360) * w;
    const y = ((90 - lat) / 180) * h;
    if (used.some((item) => Math.hypot(item.x - x, item.y - y) < 42)) continue;
    used.push({ x, y });
    ctx.fillText(name, x, y);
    if (used.length >= 40) break;
  }
}

function paintEarth() {
  const colors = palette();
  const w = 1024;
  const h = 512;
  const plate = document.createElement("canvas");
  plate.width = w;
  plate.height = h;
  const ctx = plate.getContext("2d");
  if (layers.satellite && satelliteImage) {
    ctx.drawImage(satelliteImage, 0, 0, w, h);
  } else {
    ctx.fillStyle = colors.ocean;
    ctx.fillRect(0, 0, w, h);
  }
  ctx.strokeStyle = colors.grid;
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let lon = -180; lon <= 180; lon += 30) {
    const x = ((lon + 180) / 360) * w;
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
  }
  for (let lat = -60; lat <= 60; lat += 30) {
    const y = ((90 - lat) / 180) * h;
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
  }
  ctx.stroke();
  if (layers.land && land && !(layers.satellite && satelliteImage)) {
    ctx.fillStyle = colors.land;
    ctx.beginPath();
    traceCollection(ctx, land, w, h);
    ctx.fill();
  }
  if (layers.borders && borders[nearestEra(eraYear)]) {
    const file = borders[nearestEra(eraYear)];
    ctx.strokeStyle = colors.border;
    ctx.lineWidth = 1.1;
    ctx.beginPath();
    traceCollection(ctx, file, w, h);
    ctx.stroke();
    paintLabels(ctx, file, colors, w, h);
  }
  const texture = new THREE.CanvasTexture(plate);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  earth.material.map = texture;
  earth.material.needsUpdate = true;
  renderer.setClearColor(colors.bg, 1);
  atmosphere.material.color.set(dark() ? "#24424c" : "#9ec4d4");
}

function scoreOf(pin) {
  const value = pin.possibility && typeof pin.possibility.value === "number" ? pin.possibility.value : 0.4;
  return Math.max(0, Math.min(1, value));
}

function rebuildPins() {
  while (pinGroup.children.length) pinGroup.remove(pinGroup.children[0]);
  const list = $("pin-list");
  list.innerHTML = "";
  for (const pin of pins) {
    if (pin.lat == null || pin.lon == null) continue;
    const score = scoreOf(pin);
    const fresh = !opened.has(pin.id);
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.016 + score * 0.02, 16, 12),
      new THREE.MeshBasicMaterial({
        color: fresh ? 0xc9a227 : new THREE.Color().setHSL(0.12, 0.72, 0.34 + score * 0.22),
        depthTest: false,
      })
    );
    mesh.renderOrder = 3;
    mesh.position.copy(latLonToVector3(pin.lat, pin.lon, 1.02));
    mesh.userData.pin = pin;
    pinGroup.add(mesh);
    if (fresh) {
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(0.03, 0.042, 28),
        new THREE.MeshBasicMaterial({ color: 0xc9a227, side: THREE.DoubleSide, transparent: true, opacity: 0.95 })
      );
      ring.position.copy(mesh.position);
      ring.lookAt(mesh.position.clone().multiplyScalar(2));
      ring.userData.pulse = true;
      ring.userData.pin = pin;
      ring.renderOrder = 3;
      pinGroup.add(ring);
    }
    if (pin.bayesian && typeof pin.bayesian.value === "number") {
      const bayes = new THREE.Mesh(
        new THREE.RingGeometry(0.02, 0.026, 24),
        new THREE.MeshBasicMaterial({ color: 0x3d6f8a, side: THREE.DoubleSide })
      );
      bayes.position.copy(mesh.position);
      bayes.lookAt(mesh.position.clone().multiplyScalar(2));
      bayes.userData.pin = pin;
      bayes.renderOrder = 3;
      pinGroup.add(bayes);
    }
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${fresh ? "New · " : ""}${pin.event || pin.id}`;
    if (fresh) button.className = "is-new";
    button.addEventListener("click", () => openPin(pin.id));
    item.append(button);
    list.append(item);
  }
}

function drawArea(ring) {
  while (areaGroup.children.length) areaGroup.remove(areaGroup.children[0]);
  areaRing = null;
  if (!ring || ring.length < 3) return;
  const positions = [];
  const center = latLonToVector3(
    ring.reduce((sum, p) => sum + p.lat, 0) / ring.length,
    ring.reduce((sum, p) => sum + p.lon, 0) / ring.length,
    1.01
  );
  const corners = ring.map((point) => latLonToVector3(point.lat, point.lon, 1.015));
  for (let i = 0; i < corners.length; i += 1) {
    const next = corners[(i + 1) % corners.length];
    positions.push(center.x, center.y, center.z, corners[i].x, corners[i].y, corners[i].z, next.x, next.y, next.z);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  const mesh = new THREE.Mesh(
    geometry,
    new THREE.MeshBasicMaterial({ color: 0xc9a227, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false })
  );
  areaGroup.add(mesh);
  const lineGeo = new THREE.BufferGeometry();
  const linePts = [];
  corners.forEach((corner) => linePts.push(corner.x, corner.y, corner.z));
  linePts.push(corners[0].x, corners[0].y, corners[0].z);
  lineGeo.setAttribute("position", new THREE.Float32BufferAttribute(linePts, 3));
  const outline = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: 0x8a6a10 }));
  outline.renderOrder = 2;
  areaGroup.add(outline);
  areaRing = mesh;
}

async function post(op, payload) {
  const response = await fetch(`/v1/${op}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload: payload || {} }),
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.message || "The request was refused.");
  }
  return data;
}

async function loadPins() {
  const plotted = await post("plot", {});
  pins = (plotted.pins || []).filter((pin) => pin.lat != null && pin.lon != null);
  rebuildPins();
}

function rememberOpened(id) {
  opened.add(id);
  localStorage.setItem(OPENED_KEY, JSON.stringify([...opened]));
}

function fillCard(pin, area) {
  $("card-event").textContent = pin.event || "Pin";
  $("card-date").textContent = pin.clock || "";
  $("card-place").textContent = pin.place || "No place words on this pin.";
  const people = Array.isArray(pin.who) ? pin.who.filter(Boolean) : [];
  $("card-who").textContent = people.length ? people.join(", ") : "No person label on this pin.";
  const possibility = pin.possibility;
  $("card-possibility").textContent = possibility
    ? `possibility ${Number(possibility.value).toFixed(2)} — time × place, not truth`
    : "No possibility value.";
  $("card-bayesian").textContent = pin.bayesian && pin.bayesian.value != null
    ? `bayesian ${Number(pin.bayesian.value).toFixed(2)} — cited belief, not truth`
    : "No Bayesian value was cited.";
  const filled = (possibility ? 1 : 0) + (pin.bayesian && pin.bayesian.value != null ? 1 : 0) + 1;
  $("card-triad").textContent = `AKM-TRIAD-1.0 · E evidence, C possibility, P prior empty, B ${pin.bayesian ? "cited" : "empty"}. ${filled} of 4 filled. 3-of-4 is ${filled >= 3 ? "met" : "not met"}. Posterior ≠ truth.`;
  const uploads = Array.isArray(pin.uploads) ? pin.uploads : [];
  $("card-uploads").textContent = uploads.length ? uploads.join(", ") : "No uploads on this pin.";
  $("card-hash").textContent = pin.h ? `${pin.h} · prev ${pin.prev || ""}` : "";
  $("why").textContent = area && area.why ? area.why : "The shaded region is an estimate, not an exact point.";
  $("pin-card").hidden = false;
  document.body.classList.add("card-open");
}

async function coverage(pin) {
  const lines = [];
  if (layers.street) {
    const response = await fetch(`/v1/tiles/street?lat=${encodeURIComponent(pin.lat)}&lon=${encodeURIComponent(pin.lon)}`);
    const data = await response.json();
    lines.push(data.available ? data.message : `Street view: ${data.message || "not available here"}`);
  }
  if (layers.lidar) {
    const response = await fetch(`/v1/tiles/lidar?lat=${encodeURIComponent(pin.lat)}&lon=${encodeURIComponent(pin.lon)}`);
    const data = await response.json();
    lines.push(data.available ? data.message : `LiDAR: ${data.message || "no LiDAR here"}`);
  }
  if (!layers.street && !layers.lidar) {
    lines.push("Street view and LiDAR are off. Turn a layer on to ask. Neither draws a fake image.");
  }
  $("coverage").textContent = lines.join(" ");
}

async function openPin(id) {
  const pin = pins.find((item) => item.id === id);
  if (!pin) return;
  focusId = id;
  rememberOpened(id);
  rebuildPins();
  spin = false;
  view.lon = pin.lon;
  view.lat = Math.max(-70, Math.min(70, pin.lat));
  view.dist = 2.15;
  applyView();
  let area = null;
  try {
    area = await post("area_estimate", {
      event: pin.event,
      date: pin.clock,
      lat: pin.lat,
      lon: pin.lon,
      place: pin.place,
      year: eraYear,
    });
    drawArea(area.ring);
  } catch (err) {
    $("why").textContent = err.message;
  }
  fillCard(pin, area);
  coverage(pin);
}

function flyTo(pin) {
  spin = false;
  const startLon = view.lon;
  let delta = pin.lon - startLon;
  if (delta > 180) delta -= 360;
  if (delta < -180) delta += 360;
  const startLat = view.lat;
  const startDist = view.dist;
  const begun = performance.now();
  function step(now) {
    const t = Math.min(1, (now - begun) / 700);
    const ease = 1 - (1 - t) ** 3;
    view.lon = startLon + delta * ease;
    view.lat = startLat + (Math.max(-70, Math.min(70, pin.lat)) - startLat) * ease;
    view.dist = startDist + (2.15 - startDist) * ease;
    applyView();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

async function search(query) {
  const list = $("search-results");
  list.innerHTML = "";
  const q = query.trim().toLowerCase();
  if (!q) return;
  const hits = pins.filter((pin) => {
    const people = Array.isArray(pin.who) ? pin.who.join(" ") : "";
    return `${pin.event || ""} ${people} ${pin.place || ""}`.toLowerCase().includes(q);
  });
  if (!hits.length) {
    const item = document.createElement("li");
    item.textContent = "No pin matches that event or person label.";
    list.append(item);
    return;
  }
  for (const pin of hits) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    const people = Array.isArray(pin.who) && pin.who.length ? ` · ${pin.who.join(", ")}` : "";
    button.textContent = `${pin.event || pin.id}${people}`;
    button.addEventListener("click", () => {
      list.innerHTML = "";
      $("search").value = "";
      flyTo(pin);
      openPin(pin.id);
    });
    item.append(button);
    list.append(item);
  }
}

function resolvePlace(words) {
  const low = words.toLowerCase();
  let best = null;
  let bestLen = 0;
  for (const place of places) {
    const names = [place.name, ...(place.aliases || [])];
    for (const name of names) {
      const token = String(name).toLowerCase();
      if (token.length >= 3 && new RegExp(`\\b${token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`).test(low) && token.length > bestLen) {
        best = place;
        bestLen = token.length;
      }
    }
  }
  return best;
}

async function onPin(event) {
  event.preventDefault();
  const status = $("status");
  const name = $("event").value.trim();
  const date = $("date").value;
  const place = $("place").value.trim();
  let lat = $("lat").value.trim();
  let lon = $("lon").value.trim();
  if (!name || !date) {
    status.textContent = "Add an event and a paper date, then press Pin.";
    return;
  }
  if (!lat || !lon) {
    const found = resolvePlace(`${place} ${name}`);
    if (!found) {
      status.textContent = "This place is not in the local list. Enter a reported latitude and longitude. 4DMap will not invent a coordinate.";
      return;
    }
    lat = String(found.lat);
    lon = String(found.lon);
    status.textContent = `Using the local name list for ${found.name}. The dot is that name's anchor, not a surveyed point.`;
  }
  const who = $("who").value.trim();
  const uploads = [...document.querySelectorAll("#attach-uploads input:checked")].map((box) => box.value);
  try {
    const result = await post("library_pin", {
      event: name,
      date,
      lat: Number(lat),
      lon: Number(lon),
      place,
      who: who ? who.split(",").map((part) => part.trim()).filter(Boolean) : [],
      uploads,
      surface: $("surface").value,
      src: "operator",
      note: place ? `place words: ${place}` : "globe pin",
    });
    status.textContent = "Pinned. The new pin stays gold until you open it.";
    await loadPins();
    const created = pins.find((pin) => pin.id === result.id);
    if (created) {
      spin = false;
      view.lon = created.lon;
      view.lat = Math.max(-70, Math.min(70, created.lat));
      applyView();
    }
    $("receipt").textContent = result.h ? `hash ${result.h}` : "";
  } catch (err) {
    status.textContent = err.message;
  }
}

async function loadSatellite() {
  satelliteNote = "";
  satelliteImage = null;
  const response = await fetch("/v1/tiles/satellite");
  if (!response.ok) {
    let message = "Satellite imagery did not load from NASA GIBS. No substitute image is drawn.";
    try {
      const data = await response.json();
      if (data.message) message = data.message;
    } catch (_err) {
      /* keep the honest fallback sentence */
    }
    satelliteNote = message;
    $("layer-note").textContent = message;
    return;
  }
  const blob = await response.blob();
  if (!blob.type.startsWith("image/")) {
    satelliteNote = "Satellite imagery did not load from NASA GIBS. No substitute image is drawn.";
    $("layer-note").textContent = satelliteNote;
    return;
  }
  satelliteImage = await createImageBitmap(blob);
  satelliteNote = "NASA GIBS Blue Marble shaded relief. This is a base image, not a photograph from the event date.";
  $("layer-note").textContent = satelliteNote;
}

function syncShadow() {
  $("shadow").hidden = !layers.shadow;
}

async function loadShadow() {
  const response = await fetch("/v1/shadow_links");
  const data = await response.json();
  const list = $("shadow-list");
  list.innerHTML = "";
  const links = data.links || [];
  $("shadow-empty").hidden = links.length > 0;
  for (const link of links) {
    const item = document.createElement("li");
    const when = link.linked_at ? `${link.linked_at} · ` : "";
    const kind = link.kind ? ` · ${link.kind}` : "";
    const label = link.label ? ` · ${link.label}` : "";
    item.textContent = `${when}${link.slug}${label}${kind} · ${link.input_id || link.input_path || ""}`;
    list.append(item);
  }
  const path = data.path ? ` 4DMap only reads ${data.path}.` : "";
  if (!links.length && data.message) {
    $("shadow-empty").textContent = data.message;
  }
  if (path) {
    const note = document.createElement("li");
    note.textContent = path.trim();
    list.append(note);
  }
}

async function loadUploads() {
  const response = await fetch("/v1/uploads");
  const data = await response.json();
  const list = $("upload-list");
  list.innerHTML = "";
  const attach = $("attach-uploads");
  attach.innerHTML = "";
  for (const row of data.uploads || []) {
    const item = document.createElement("li");
    item.textContent = `${row.name} · ${row.bytes} bytes · ${row.sha256}`;
    list.append(item);
    const label = document.createElement("label");
    const box = document.createElement("input");
    box.type = "checkbox";
    box.value = row.sha256;
    label.append(box, document.createTextNode(` ${row.name}`));
    attach.append(label);
  }
}

function showReceipt(data) {
  $("receipt").textContent = JSON.stringify(data, null, 2).slice(0, 4000);
  $("board").classList.add("open");
}

const pointers = new Map();
canvas.addEventListener("pointerdown", (event) => {
  spin = false;
  canvas.setPointerCapture(event.pointerId);
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY, moved: false });
});
canvas.addEventListener("pointermove", (event) => {
  const start = pointers.get(event.pointerId);
  if (!start) return;
  const dx = event.clientX - start.x;
  const dy = event.clientY - start.y;
  if (Math.hypot(dx, dy) > 3) start.moved = true;
  if (pointers.size === 2) {
    const pts = [...pointers.values()];
    const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    if (start.lastPinch) {
      view.dist = Math.min(5.6, Math.max(1.65, view.dist * (start.lastPinch / Math.max(dist, 1))));
    }
    start.lastPinch = dist;
  } else {
    view.lon -= dx * 0.25;
    view.lat = Math.max(-80, Math.min(80, view.lat + dy * 0.2));
  }
  start.x = event.clientX;
  start.y = event.clientY;
  applyView();
});
function endPointer(event) {
  const start = pointers.get(event.pointerId);
  pointers.delete(event.pointerId);
  if (!start || start.moved) return;
  const rect = canvas.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1
  );
  const ray = new THREE.Raycaster();
  ray.setFromCamera(mouse, camera);
  const hits = ray.intersectObjects(pinGroup.children, false);
  if (hits[0] && hits[0].object.userData.pin) openPin(hits[0].object.userData.pin.id);
}
canvas.addEventListener("pointerup", endPointer);
canvas.addEventListener("pointercancel", (event) => pointers.delete(event.pointerId));
canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  spin = false;
  view.dist = Math.min(5.6, Math.max(1.65, view.dist + Math.sign(event.deltaY) * 0.18));
  applyView();
}, { passive: false });

addEventListener("keydown", (event) => {
  const tag = (event.target && event.target.tagName) || "";
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
  if (event.key === "ArrowLeft") view.lon -= 8;
  else if (event.key === "ArrowRight") view.lon += 8;
  else if (event.key === "ArrowUp") view.lat = Math.min(80, view.lat + 6);
  else if (event.key === "ArrowDown") view.lat = Math.max(-80, view.lat - 6);
  else if (event.key === "+" || event.key === "=") view.dist = Math.max(1.65, view.dist - 0.2);
  else if (event.key === "-" || event.key === "_") view.dist = Math.min(5.6, view.dist + 0.2);
  else return;
  spin = false;
  applyView();
});

$("pin-form").addEventListener("submit", onPin);
$("search").addEventListener("input", () => search($("search").value));
$("search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const first = $("search-results").querySelector("button");
  if (first) first.click();
});
$("layers-toggle").addEventListener("click", () => {
  const panel = $("layers");
  panel.hidden = !panel.hidden;
  $("layers-toggle").setAttribute("aria-expanded", String(!panel.hidden));
});
$("board-toggle").addEventListener("click", () => {
  $("board").classList.toggle("open");
});
$("card-close").addEventListener("click", () => {
  $("pin-card").hidden = true;
  document.body.classList.remove("card-open");
});
$("era").addEventListener("input", () => {
  eraYear = Number($("era").value);
  $("era-value").textContent = String(eraYear);
  $("era-note").textContent = eraCopy(eraYear);
  paintEarth();
});
for (const [id, key] of [
  ["layer-land", "land"],
  ["layer-borders", "borders"],
  ["layer-satellite", "satellite"],
  ["layer-street", "street"],
  ["layer-lidar", "lidar"],
  ["layer-shadow", "shadow"],
]) {
  $(id).addEventListener("change", async () => {
    layers[key] = $(id).checked;
    if (key === "satellite") {
      if (layers.satellite) await loadSatellite();
      else $("layer-note").textContent = "Satellite is off. No imagery is fetched.";
    }
    if (key === "shadow") syncShadow();
    if ((key === "street" || key === "lidar") && focusId) {
      const pin = pins.find((item) => item.id === focusId);
      if (pin) coverage(pin);
    }
    if (key === "street" && layers.street && !focusId) {
      $("layer-note").textContent = "Street view needs an open pin. Nothing is open, so there is no frame.";
    }
    if (key === "lidar" && layers.lidar && !focusId) {
      $("layer-note").textContent = "LiDAR needs an open pin. Nothing is open, so there is no sample. No LiDAR is invented.";
    }
    paintEarth();
  });
}
$("shadow-refresh").addEventListener("click", loadShadow);
$("upload-file").addEventListener("change", async () => {
  const file = $("upload-file").files && $("upload-file").files[0];
  if (!file) return;
  const bytes = new Uint8Array(await file.arrayBuffer());
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  const response = await fetch("/v1/upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: file.name, content_b64: btoa(binary) }),
  });
  const data = await response.json();
  $("receipt").textContent = data.message || (data.upload ? `logged ${data.upload.sha256}` : "upload refused");
  if (response.ok) await loadUploads();
});

async function advanced(op, payload) {
  try {
    const result = await post(op, payload);
    showReceipt(result);
    if (result.card || op === "card_import") await loadPins();
  } catch (err) {
    $("receipt").textContent = err.message;
  }
}
$("act-span").addEventListener("click", () => advanced("span", { from_id: $("from-id").value, to_id: $("to-id").value }));
$("act-join").addEventListener("click", () => advanced("join", { left: $("from-id").value, right: $("to-id").value, join_type: $("join-type").value }));
$("act-walk").addEventListener("click", () => advanced("walk", { tip: $("from-id").value || $("to-id").value }));
$("act-tip").addEventListener("click", () => advanced("lattice_tip", {}));
$("act-verify").addEventListener("click", () => advanced("verify_chain", { tip: $("from-id").value || $("to-id").value }));
$("act-export").addEventListener("click", () => advanced("card_export", {}));
$("act-import").addEventListener("click", () => {
  const text = $("bundle").value.trim();
  if (!text) {
    $("receipt").textContent = "Paste a card bundle first.";
    return;
  }
  try {
    advanced("card_import", { bundle: JSON.parse(text) });
  } catch (_err) {
    $("receipt").textContent = "That paste is not JSON.";
  }
});
$("axis-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const axis = $("axis").value;
  const value = $("axis-value").value.trim();
  const payload = { axis, src: "operator" };
  if (axis === "T") payload.t = value || new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  else payload.value = value || "note";
  advanced("pin", payload);
});

function frame() {
  if (spin) {
    view.lon += 0.12;
    applyView();
  }
  const t = performance.now() / 1000;
  for (const child of pinGroup.children) {
    if (child.userData.pulse) {
      const scale = 1 + 0.18 * (0.5 + 0.5 * Math.sin(t * 4));
      child.scale.setScalar(scale);
    }
  }
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

async function boot() {
  resize();
  addEventListener("resize", resize);
  applyView();
  try {
    const [landFile, placesFile, ...eraFiles] = await Promise.all([
      fetch("/static/geo/land.geojson").then((response) => response.json()),
      fetch("/static/geo/places.json").then((response) => response.json()),
      ...ERAS.map((year) => fetch(`/static/geo/era-${year}.geojson`).then((response) => response.json())),
    ]);
    land = landFile;
    places = placesFile.places || [];
    ERAS.forEach((year, index) => {
      borders[year] = eraFiles[index];
    });
  } catch (_err) {
    $("status").textContent = "The bundled globe files did not load.";
  }
  $("era-note").textContent = eraCopy(eraYear);
  syncShadow();
  paintEarth();
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", paintEarth);
  try {
    await loadPins();
  } catch (err) {
    $("status").textContent = err.message;
  }
  loadShadow();
  loadUploads();
  if (!renderer.getContext()) $("globe-fallback").hidden = false;
  frame();
}

boot();
