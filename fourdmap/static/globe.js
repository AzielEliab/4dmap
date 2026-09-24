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
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 40);
const globe = new THREE.Group();
scene.add(globe);
const earth = new THREE.Mesh(
  new THREE.SphereGeometry(1, 96, 64),
  new THREE.MeshPhongMaterial({ color: 0xffffff, shininess: 18, specular: new THREE.Color(0xc5d8e0) })
);
globe.add(earth);
const atmosphere = new THREE.Mesh(
  new THREE.SphereGeometry(1.065, 64, 48),
  new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.BackSide,
    blending: THREE.NormalBlending,
    uniforms: {
      glowColor: { value: new THREE.Color(0x8eb8d4) },
      strength: { value: 0.55 },
    },
    vertexShader: `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vNormal;
      uniform vec3 glowColor;
      uniform float strength;
      void main() {
        float rim = pow(0.62 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.6);
        gl_FragColor = vec4(glowColor, clamp(rim, 0.0, 1.0) * strength);
      }
    `,
  })
);
scene.add(atmosphere);
const ambient = new THREE.AmbientLight(0xffffff, 0.74);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xfff6e8, 1.15);
sun.position.set(4.2, 1.6, 5);
scene.add(sun);
const pinGroup = new THREE.Group();
globe.add(pinGroup);
const areaGroup = new THREE.Group();
globe.add(areaGroup);
const lineGroup = new THREE.Group();
globe.add(lineGroup);
const geoCache = new Map();
const labelNodes = [];
let labelCatalog = [];
let starField = null;
let surfaceKey = "";
let lineKey = "";
const PIN_CORE = new THREE.SphereGeometry(0.008, 20, 16);
const PIN_RING = new THREE.RingGeometry(0.0115, 0.015, 48);
const BAYES_RING = new THREE.RingGeometry(0.017, 0.0195, 40);
const AREA_MATERIAL = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  side: THREE.DoubleSide,
  uniforms: { uColor: { value: new THREE.Color(0xc9a227) } },
  vertexShader: `
    attribute float alpha;
    varying float vAlpha;
    void main() {
      vAlpha = alpha;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 uColor;
    varying float vAlpha;
    void main() {
      gl_FragColor = vec4(uColor, vAlpha);
    }
  `,
});
const Z_AXIS = new THREE.Vector3(0, 0, 1);

function dark() {
  return matchMedia("(prefers-color-scheme: dark)").matches;
}

function palette() {
  if (dark()) {
    return {
      bg: "#07090e",
      oceanTop: "#07141c",
      oceanMid: "#12384c",
      oceanEq: "#1a5270",
      land: "#24362e",
      landEdge: "#315246",
      border: "#e4d3a2",
      coast: "#8fb8a4",
      grid: "#8aa4b4",
      glow: "#7eb6d6",
      specular: "#1a3344",
    };
  }
  return {
    bg: "#f4f1ea",
    oceanTop: "#6f97a8",
    oceanMid: "#9ec4d2",
    oceanEq: "#c5dde6",
    land: "#e4efe2",
    landEdge: "#d5e4d4",
    border: "#2a3b34",
    coast: "#3e5c52",
    grid: "#6d8b99",
    glow: "#8eb4cc",
    specular: "#d5e4ea",
  };
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

function eachRing(collection, visit) {
  for (const feature of (collection && collection.features) || []) {
    const g = feature.geometry;
    if (!g) continue;
    if (g.type === "Polygon") {
      for (const ring of g.coordinates) visit(ring);
    } else if (g.type === "MultiPolygon") {
      for (const poly of g.coordinates) {
        for (const ring of poly) visit(ring);
      }
    }
  }
}

function traceCollection(ctx, collection, w, h) {
  if (!collection) return;
  eachRing(collection, (ring) => {
    let prev = null;
    for (let i = 0; i < ring.length; i += 1) {
      const lon = ring[i][0];
      const lat = ring[i][1];
      const x = ((lon + 180) / 360) * w;
      const y = ((90 - lat) / 180) * h;
      if (i === 0 || (prev != null && Math.abs(lon - prev) > 180)) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
      prev = lon;
    }
  });
}

function largestRing(feature) {
  const g = feature.geometry;
  if (!g) return null;
  let best = null;
  let bestArea = 0;
  const consider = (ring) => {
    if (!ring || ring.length < 4) return;
    let south = 90;
    let north = -90;
    let west = 180;
    let east = -180;
    for (const pair of ring) {
      south = Math.min(south, pair[1]);
      north = Math.max(north, pair[1]);
      west = Math.min(west, pair[0]);
      east = Math.max(east, pair[0]);
    }
    const area = Math.max(0, east - west) * Math.max(0, north - south);
    if (area > bestArea) {
      bestArea = area;
      best = { ring, south, north, west, east, area };
    }
  };
  if (g.type === "Polygon") g.coordinates.forEach(consider);
  else if (g.type === "MultiPolygon") {
    for (const poly of g.coordinates) poly.forEach(consider);
  }
  return best;
}

function lineGeometry(key, collection, radius, stride) {
  const id = `${key}:${radius}:${stride}`;
  if (geoCache.has(id)) return geoCache.get(id);
  const positions = [];
  eachRing(collection, (ring) => {
    for (let i = 0; i < ring.length - 1; i += stride) {
      const a = ring[i];
      const b = ring[Math.min(i + stride, ring.length - 1)];
      if (Math.abs(a[0] - b[0]) > 180) continue;
      const va = latLonToVector3(a[1], a[0], radius);
      const vb = latLonToVector3(b[1], b[0], radius);
      positions.push(va.x, va.y, va.z, vb.x, vb.y, vb.z);
    }
  });
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geoCache.set(id, geometry);
  return geometry;
}

function graticuleGeometry(step) {
  const id = `grat:${step}`;
  if (geoCache.has(id)) return geoCache.get(id);
  const positions = [];
  const radius = 1.0015;
  for (let lon = -180; lon < 180; lon += step) {
    for (let lat = -80; lat < 80; lat += 4) {
      const a = latLonToVector3(lat, lon, radius);
      const b = latLonToVector3(lat + 4, lon, radius);
      positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
  }
  for (let lat = -60; lat <= 60; lat += step) {
    for (let lon = -180; lon < 180; lon += 4) {
      const a = latLonToVector3(lat, lon, radius);
      const nextLon = Math.min(180, lon + 4);
      const b = latLonToVector3(lat, nextLon, radius);
      positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geoCache.set(id, geometry);
  return geometry;
}

function addLines(geometry, color, opacity) {
  const material = new THREE.LineBasicMaterial({
    color,
    transparent: true,
    opacity,
    depthWrite: false,
  });
  const lines = new THREE.LineSegments(geometry, material);
  lines.renderOrder = 2;
  lineGroup.add(lines);
}

function rebuildLines() {
  const colors = palette();
  const year = nearestEra(eraYear);
  const close = view.dist < 2.4;
  const key = `${year}|${close}|${dark()}|${layers.land}|${layers.borders}|${Boolean(layers.satellite && satelliteImage)}`;
  if (key === lineKey) return;
  lineKey = key;
  while (lineGroup.children.length) {
    const child = lineGroup.children[0];
    lineGroup.remove(child);
    if (child.material) child.material.dispose();
  }
  addLines(graticuleGeometry(close ? 15 : 30), colors.grid, dark() ? 0.16 : 0.22);
  if (layers.land && land && !(layers.satellite && satelliteImage)) {
    addLines(lineGeometry("coast", land, 1.004, 1), colors.coast, 0.95);
  }
  if (layers.borders && borders[year]) {
    addLines(lineGeometry(`era-${year}`, borders[year], 1.007, 1), colors.border, 0.92);
  }
}

function buildLabelCatalog() {
  labelCatalog = [];
  const file = layers.borders ? borders[nearestEra(eraYear)] : null;
  if (!file) return;
  for (const feature of file.features || []) {
    const name = feature.properties && feature.properties.NAME;
    const box = largestRing(feature);
    if (!name || !box || box.east - box.west > 170 || box.area < 4) continue;
    labelCatalog.push({
      name,
      lon: (box.west + box.east) / 2,
      lat: (box.south + box.north) / 2,
      priority: box.area,
    });
  }
  labelCatalog.sort((a, b) => b.priority - a.priority);
}

function minLabelPriority() {
  if (view.dist > 3.3) return 180;
  if (view.dist > 2.7) return 70;
  if (view.dist > 2.3) return 22;
  return 6;
}

function globeScreenRadius() {
  camera.updateMatrixWorld();
  const distance = camera.position.length();
  const z = 1 / Math.max(distance, 1.01);
  const x = Math.sqrt(Math.max(0, 1 - z * z));
  const origin = new THREE.Vector3(0, 0, 0).project(camera);
  const limb = new THREE.Vector3(x, 0, z).project(camera);
  return Math.abs((limb.x - origin.x) * 0.5) * canvas.clientWidth;
}

function placeLabels() {
  const root = $("labels");
  if (!root || canvas.clientWidth < 20) return;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const radius = globeScreenRadius();
  const fontPx = Math.round(THREE.MathUtils.clamp(30 / view.dist, 11, 18));
  const floor = minLabelPriority();
  const placed = [];
  const shown = [];
  for (const item of labelCatalog) {
    if (item.priority < floor) continue;
    const world = latLonToVector3(item.lat, item.lon, 1.01).applyQuaternion(globe.quaternion);
    if (world.z < 0.28) continue;
    const fade = THREE.MathUtils.smoothstep(world.z, 0.28, 0.62);
    const projected = world.project(camera);
    const x = (projected.x * 0.5 + 0.5) * width;
    const y = (-projected.y * 0.5 + 0.5) * height;
    const labelWidth = item.name.length * fontPx * 0.54 + 8;
    const labelHeight = fontPx + 6;
    const box = { x: x - labelWidth / 2, y: y - labelHeight / 2, w: labelWidth, h: labelHeight };
    const cx = width / 2;
    const cy = height / 2;
    const corners = [
      [box.x, box.y],
      [box.x + box.w, box.y],
      [box.x, box.y + box.h],
      [box.x + box.w, box.y + box.h],
    ];
    if (corners.some(([px, py]) => Math.hypot(px - cx, py - cy) > radius * 0.96)) continue;
    if (placed.some((other) => box.x < other.x + other.w && box.x + box.w > other.x && box.y < other.y + other.h && box.y + box.h > other.y)) {
      continue;
    }
    placed.push(box);
    shown.push({ name: item.name, x, y, fade, fontPx });
    if (shown.length >= (view.dist < 2.4 ? 42 : 26)) break;
  }
  for (let i = 0; i < shown.length; i += 1) {
    let node = labelNodes[i];
    if (!node) {
      node = document.createElement("span");
      node.className = "map-label";
      root.append(node);
      labelNodes.push(node);
    }
    const item = shown[i];
    node.hidden = false;
    node.textContent = item.name;
    node.style.left = `${item.x}px`;
    node.style.top = `${item.y}px`;
    node.style.fontSize = `${item.fontPx}px`;
    node.style.opacity = item.fade.toFixed(3);
  }
  for (let i = shown.length; i < labelNodes.length; i += 1) labelNodes[i].hidden = true;
}

function syncStars() {
  if (!dark()) {
    if (starField) {
      scene.remove(starField);
      starField.geometry.dispose();
      starField.material.dispose();
      starField = null;
    }
    return;
  }
  if (starField) return;
  const count = 420;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    const direction = new THREE.Vector3(Math.random() * 2 - 1, Math.random() * 2 - 1, Math.random() * 2 - 1).normalize();
    direction.multiplyScalar(14 + Math.random() * 10);
    positions[i * 3] = direction.x;
    positions[i * 3 + 1] = direction.y;
    positions[i * 3 + 2] = direction.z;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  starField = new THREE.Points(
    geometry,
    new THREE.PointsMaterial({ color: 0xf7f4ee, size: 1.15, sizeAttenuation: false, transparent: true, opacity: 0.8, depthWrite: false })
  );
  scene.add(starField);
}

function paintEarth() {
  const colors = palette();
  const night = dark();
  renderer.setClearColor(colors.bg, 1);
  ambient.intensity = night ? 0.88 : 0.72;
  sun.intensity = night ? 0.95 : 1.2;
  sun.color.set(night ? 0xd7e6f2 : 0xfff6e8);
  earth.material.specular.set(colors.specular);
  earth.material.shininess = night ? 14 : 22;
  atmosphere.material.uniforms.glowColor.value.set(colors.glow);
  atmosphere.material.uniforms.strength.value = night ? 0.95 : 0.42;
  const blend = night ? THREE.AdditiveBlending : THREE.NormalBlending;
  if (atmosphere.material.blending !== blend) {
    atmosphere.material.blending = blend;
    atmosphere.material.needsUpdate = true;
  }
  syncStars();
  const sat = layers.satellite && satelliteImage ? "sat" : "plain";
  const key = `${night}|${layers.land}|${sat}`;
  if (key !== surfaceKey) {
    surfaceKey = key;
    const w = 4096;
    const h = 2048;
    const plate = document.createElement("canvas");
    plate.width = w;
    plate.height = h;
    const ctx = plate.getContext("2d");
    if (layers.satellite && satelliteImage) {
      ctx.drawImage(satelliteImage, 0, 0, w, h);
    } else {
      const ocean = ctx.createLinearGradient(0, 0, 0, h);
      ocean.addColorStop(0, colors.oceanTop);
      ocean.addColorStop(0.42, colors.oceanMid);
      ocean.addColorStop(0.55, colors.oceanEq);
      ocean.addColorStop(1, colors.oceanTop);
      ctx.fillStyle = ocean;
      ctx.fillRect(0, 0, w, h);
      if (layers.land && land) {
        ctx.fillStyle = colors.land;
        ctx.beginPath();
        traceCollection(ctx, land, w, h);
        ctx.fill();
      }
    }
    const texture = new THREE.CanvasTexture(plate);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    if (earth.material.map) earth.material.map.dispose();
    earth.material.map = texture;
    earth.material.needsUpdate = true;
  }
  rebuildLines();
  buildLabelCatalog();
}

function scoreOf(pin) {
  const value = pin.possibility && typeof pin.possibility.value === "number" ? pin.possibility.value : 0.4;
  return Math.max(0, Math.min(1, value));
}

function orientOutward(mesh, outward) {
  mesh.quaternion.setFromUnitVectors(Z_AXIS, outward.clone().normalize());
}

function rebuildPins() {
  while (pinGroup.children.length) {
    const child = pinGroup.children[0];
    pinGroup.remove(child);
    child.traverse((obj) => {
      if (obj.material && obj.material !== AREA_MATERIAL) obj.material.dispose();
    });
  }
  const list = $("pin-list");
  list.innerHTML = "";
  for (const pin of pins) {
    if (pin.lat == null || pin.lon == null) continue;
    const score = scoreOf(pin);
    const fresh = !opened.has(pin.id);
    const group = new THREE.Group();
    const position = latLonToVector3(pin.lat, pin.lon, 1.02);
    group.position.copy(position);
    group.userData.pin = pin;
    group.userData.scale = 0.9 + score * 0.35;
    group.userData.pulse = fresh;
    const core = new THREE.Mesh(
      PIN_CORE,
      new THREE.MeshBasicMaterial({
        color: fresh ? 0xc9a227 : new THREE.Color().setHSL(0.12, 0.55, 0.28 + score * 0.2),
        depthTest: false,
      })
    );
    core.userData.pin = pin;
    core.renderOrder = 4;
    group.add(core);
    const ring = new THREE.Mesh(
      PIN_RING,
      new THREE.MeshBasicMaterial({
        color: fresh ? 0xc9a227 : 0xf4efe6,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: fresh ? 0.95 : 0.8,
        depthTest: false,
      })
    );
    ring.userData.pin = pin;
    ring.renderOrder = 4;
    orientOutward(ring, position);
    group.add(ring);
    if (pin.bayesian && typeof pin.bayesian.value === "number") {
      const bayes = new THREE.Mesh(
        BAYES_RING,
        new THREE.MeshBasicMaterial({ color: 0x3d6f8a, side: THREE.DoubleSide, depthTest: false })
      );
      bayes.userData.pin = pin;
      bayes.renderOrder = 4;
      orientOutward(bayes, position);
      group.add(bayes);
    }
    pinGroup.add(group);
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

function ringCenter(ring) {
  let lat = 0;
  let lon = 0;
  const origin = ring[0].lon;
  for (const point of ring) {
    lat += point.lat;
    let delta = point.lon - origin;
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    lon += origin + delta;
  }
  return { lat: lat / ring.length, lon: lon / ring.length };
}

function toward(center, point, t) {
  let delta = point.lon - center.lon;
  if (delta > 180) delta -= 360;
  if (delta < -180) delta += 360;
  return { lat: center.lat + (point.lat - center.lat) * t, lon: center.lon + delta * t };
}

function drawArea(ring) {
  while (areaGroup.children.length) {
    const child = areaGroup.children[0];
    areaGroup.remove(child);
    if (child.geometry) child.geometry.dispose();
    if (child.material && child.material !== AREA_MATERIAL) child.material.dispose();
  }
  areaRing = null;
  if (!ring || ring.length < 3) return;
  const center = ringCenter(ring);
  const bands = [0.0, 0.62, 0.86, 1];
  const alphas = [0.24, 0.12, 0.045, 0];
  const positions = [];
  const alpha = [];
  const samples = bands.map((t, index) => ring.map((point) => {
    const at = t === 0 ? center : toward(center, point, t);
    return { at, alpha: alphas[index] };
  }));
  for (let band = 0; band < bands.length - 1; band += 1) {
    const inner = samples[band];
    const outer = samples[band + 1];
    for (let i = 0; i < ring.length; i += 1) {
      const j = (i + 1) % ring.length;
      const quad = [inner[i], outer[i], outer[j], inner[i], outer[j], inner[j]];
      for (const sample of quad) {
        const lift = 1.012 + sample.alpha * 0.004;
        const vertex = latLonToVector3(sample.at.lat, sample.at.lon, lift);
        positions.push(vertex.x, vertex.y, vertex.z);
        alpha.push(sample.alpha);
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("alpha", new THREE.Float32BufferAttribute(alpha, 1));
  const mesh = new THREE.Mesh(geometry, AREA_MATERIAL);
  mesh.renderOrder = 1;
  areaGroup.add(mesh);
  const outlinePts = [];
  for (const point of ring) {
    const vertex = latLonToVector3(point.lat, point.lon, 1.018);
    outlinePts.push(vertex.x, vertex.y, vertex.z);
  }
  const first = latLonToVector3(ring[0].lat, ring[0].lon, 1.018);
  outlinePts.push(first.x, first.y, first.z);
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute("position", new THREE.Float32BufferAttribute(outlinePts, 3));
  const outline = new THREE.Line(
    lineGeo,
    new THREE.LineBasicMaterial({ color: 0x8a6a10, transparent: true, opacity: 0.9, depthWrite: false })
  );
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
  const hash = pin.h || "";
  $("hash-short").textContent = hash ? `${hash.slice(0, 12)}…` : "";
  const copy = $("hash-copy");
  copy.hidden = !hash;
  copy.dataset.hash = hash;
  copy.dataset.prev = pin.prev || "";
  copy.textContent = "Copy";
  $("why").textContent = area && area.why ? area.why : "The shaded region is an estimate, not an exact point.";
  $("why-details").open = false;
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

function pinYear(pin) {
  const match = String(pin.clock || "").match(/(\d{4})/);
  return match ? Number(match[1]) : eraYear;
}

function showEraForPin(year) {
  const bundled = nearestEra(year);
  eraYear = bundled;
  $("era").value = String(bundled);
  $("era-value").textContent = String(bundled);
  const source = "Source: aourednik/historical-basemaps, simplified offline subset.";
  $("era-note").textContent = bundled === year
    ? `Showing ${bundled} borders for this pin's date. ${source}`
    : `Showing ${bundled} borders, the nearest bundled era to this pin's date (${year}). ${source}`;
  paintEarth();
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
  showEraForPin(pinYear(pin));
  let area = null;
  try {
    area = await post("area_estimate", {
      event: pin.event,
      date: pin.clock,
      lat: pin.lat,
      lon: pin.lon,
      place: pin.place,
      year: pinYear(pin),
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
  if (Math.hypot(dx, dy) > 3) {
    start.moved = true;
    $("hint").classList.add("gone");
  }
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
  const hits = ray.intersectObjects(pinGroup.children, true);
  if (hits[0] && hits[0].object.userData.pin) openPin(hits[0].object.userData.pin.id);
}
canvas.addEventListener("pointerup", endPointer);
canvas.addEventListener("pointercancel", (event) => pointers.delete(event.pointerId));
canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  spin = false;
  $("hint").classList.add("gone");
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
$("hash-copy").addEventListener("click", async () => {
  const hash = $("hash-copy").dataset.hash || "";
  if (!hash) return;
  const prev = $("hash-copy").dataset.prev || "";
  const text = prev ? `${hash}\nprev ${prev}` : hash;
  let copied = false;
  try {
    await navigator.clipboard.writeText(text);
    copied = true;
  } catch (_err) {
    const area = document.createElement("textarea");
    area.value = text;
    document.body.append(area);
    area.select();
    copied = document.execCommand("copy");
    area.remove();
  }
  $("hash-copy").textContent = copied ? "Copied" : "Copy";
  if (copied) setTimeout(() => { $("hash-copy").textContent = "Copy"; }, 1200);
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
  rebuildLines();
  const pinScale = view.dist / 2.15;
  const t = performance.now() / 1000;
  for (const child of pinGroup.children) {
    let scale = pinScale * (child.userData.scale || 1);
    if (child.userData.pulse) scale *= 1 + 0.08 * Math.sin(t * 3.2);
    child.scale.setScalar(scale);
  }
  placeLabels();
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
