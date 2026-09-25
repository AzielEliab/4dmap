import * as THREE from "/static/vendor/three.module.min.js";

const ERAS = [1914, 1945, 1994, 2010];
const OPENED_KEY = "4dmap-opened-pins";
const Y_AXIS = new THREE.Vector3(0, 1, 0);
const X_AXIS = new THREE.Vector3(1, 0, 0);

const $ = (id) => document.getElementById(id);

const DIST_MIN = 1.55;
const DIST_MAX = 14;
const view = { lon: 10, lat: 18, dist: 4.6 };
let userMoved = false;
const layers = {
  land: true, borders: true, satellite: false, street: false, lidar: false, topo: false, shadow: false, anomaly: false,
  bathy: false, sst: false, ice: false, coast: false,
  features: false, subsurface: false,
};
let spin = true;
let pins = [];
let places = [];
let land = null;
let borders = {};
let eraYear = 1914;
let sliderOwnsYear = false;
let sealingPattern = false;
const sealedPairs = new Set();
let sealingRecal = false;
const sealedRecal = new Set();
let satelliteImage = null;
let satelliteNote = "";
let satelliteStamp = "";
let topoImage = null;
let topoStamp = "";
let earthReq = 0;
let placeReq = 0;
let catalogReq = 0;
let featureRows = [];
let subsurfaceRows = [];
let anomalyRows = [];
let successors = {};
let borderReq = 0;
let focusFeatureId = "";
let matrixEdges = [];
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
const catalogGroup = new THREE.Group();
const anomalyGroup = new THREE.Group();
globe.add(catalogGroup);
globe.add(anomalyGroup);
const FEATURE_DOT = new THREE.SphereGeometry(0.0065, 12, 10);
const areaGroup = new THREE.Group();
globe.add(areaGroup);
const lineGroup = new THREE.Group();
globe.add(lineGroup);
const tetherGroup = new THREE.Group();
globe.add(tetherGroup);
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
      border: "#f3e6c0",
      coast: "#d7efe4",
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
      land: "#d7e6d4",
      landEdge: "#c9dcc8",
      border: "#1d332c",
      coast: "#2f4f46",
    grid: "#6d8b99",
    glow: "#8eb4cc",
      specular: "#7f9eab",
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

function fitDistance() {
  const w = canvas.clientWidth || innerWidth;
  const h = canvas.clientHeight || innerHeight;
  const aspect = w / Math.max(h, 1);
  const vHalf = THREE.MathUtils.degToRad(16);
  const hHalf = Math.atan(Math.tan(vHalf) * aspect);
  const limb = Math.min(vHalf, hHalf) * 0.7;
  return THREE.MathUtils.clamp(1 / Math.sin(limb), DIST_MIN, DIST_MAX);
}

function resize() {
  const w = canvas.clientWidth || innerWidth;
  const h = canvas.clientHeight || innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / Math.max(h, 1);
  camera.updateProjectionMatrix();
  if (!userMoved) view.dist = fitDistance();
}

function nearestEra(year) {
  return ERAS.reduce((best, item) => (Math.abs(item - year) < Math.abs(best - year) ? item : best), ERAS[0]);
}

function eraCopy(year) {
  const bundled = nearestEra(year);
  const source = "Source: aourednik/historical-basemaps, simplified offline subset.";
  const estimate = `estimated borders; source year ${bundled}.`;
  const coarse = "These lines are a coarse public estimate, not a surveyed boundary.";
  if (bundled === year) {
    return `${estimate} ${coarse} ${source}`;
  }
  return `No bundled borders for ${year}. nearest public borders: ${bundled}. ${estimate} ${coarse} ${source}`;
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

function addDashedLines(geometry, color, opacity) {
  const material = new THREE.LineDashedMaterial({
    color,
    transparent: true,
    opacity,
    dashSize: 0.018,
    gapSize: 0.012,
    depthWrite: false,
  });
  const lines = new THREE.LineSegments(geometry, material);
  lines.computeLineDistances();
  lines.renderOrder = 2;
  lineGroup.add(lines);
}

function rebuildLines() {
  const colors = palette();
  const year = nearestEra(eraYear);
  const key = `${year}|${dark()}|${layers.land}|${layers.borders}|${Boolean(layers.satellite && satelliteImage)}`;
  if (key === lineKey) return;
  lineKey = key;
  while (lineGroup.children.length) {
    const child = lineGroup.children[0];
    lineGroup.remove(child);
    if (child.material) child.material.dispose();
  }
  if (layers.land && land && !(layers.satellite && satelliteImage)) {
    addLines(lineGeometry("coast", land, 1.004, 1), colors.coast, 1);
  }
  if (layers.borders && borders[year]) {
    addDashedLines(lineGeometry(`era-${year}`, borders[year], 1.007, 1), colors.border, 0.72);
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
    const modern = successors[name] || "";
    labelCatalog.push({
      name,
      modern: modern && modern !== name ? modern : "",
      lon: (box.west + box.east) / 2,
      lat: (box.south + box.north) / 2,
      priority: box.area,
    });
  }
  if (layers.anomaly) {
    for (const row of anomalyRows) {
      if (row.lat == null || row.lon == null || !row.name) continue;
      labelCatalog.push({
        name: row.name,
        modern: "",
        lon: row.lon,
        lat: row.lat,
        priority: 240,
      });
    }
  }
  labelCatalog.sort((a, b) => b.priority - a.priority);
}

function minLabelPriority() {
  if (view.dist > 3.3) return 180;
  if (view.dist > 2.7) return 70;
  if (view.dist > 2.3) return 22;
  return 6;
}

function overlapsChrome(box) {
  const nodes = [document.querySelector("header"), $("hint"), $("pin-form"), $("legend"), $("layers"), $("pin-card")];
  for (const node of nodes) {
    if (!node || node.hidden) continue;
    const style = getComputedStyle(node);
    if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) continue;
    const rect = node.getBoundingClientRect();
    if (box.x < rect.right && box.x + box.w > rect.left && box.y < rect.bottom && box.y + box.h > rect.top) return true;
  }
  return false;
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
    const modernLine = item.modern ? `Modern name: ${item.modern}` : "";
    const labelWidth = Math.max(item.name.length, modernLine.length) * fontPx * 0.54 + 8;
    const labelHeight = fontPx + 6 + (item.modern ? fontPx : 0);
    const box = { x: x - labelWidth / 2, y: y - labelHeight / 2, w: labelWidth, h: labelHeight };
    const cx = width / 2;
    const cy = height / 2;
    const corners = [
      [box.x, box.y],
      [box.x + box.w, box.y],
      [box.x, box.y + box.h],
      [box.x + box.w, box.y + box.h],
    ];
    if (corners.some(([px, py]) => Math.hypot(px - cx, py - cy) > radius * 0.9)) continue;
    if (overlapsChrome(box)) continue;
    if (placed.some((other) => box.x < other.x + other.w && box.x + box.w > other.x && box.y < other.y + other.h && box.y + box.h > other.y)) {
      continue;
    }
    placed.push(box);
    shown.push({ name: item.name, modern: item.modern || "", x, y, fade, fontPx });
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
    node.replaceChildren();
    const eraName = document.createElement("span");
    eraName.className = "era-name";
    eraName.textContent = item.name;
    node.append(eraName);
    if (item.modern) {
      const modern = document.createElement("span");
      modern.className = "modern-name";
      modern.textContent = `Modern name: ${item.modern}`;
      node.append(modern);
    }
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
  ambient.intensity = night ? 0.55 : 0.48;
  sun.intensity = night ? 0.72 : 0.82;
  sun.color.set(night ? 0xd7e6f2 : 0xfff6e8);
  earth.material.specular.set(colors.specular);
  earth.material.shininess = night ? 18 : 28;
  atmosphere.material.uniforms.glowColor.value.set(colors.glow);
  atmosphere.material.uniforms.strength.value = night ? 0.95 : 0.42;
  const blend = night ? THREE.AdditiveBlending : THREE.NormalBlending;
  if (atmosphere.material.blending !== blend) {
    atmosphere.material.blending = blend;
    atmosphere.material.needsUpdate = true;
  }
  syncStars();
  const sat = layers.satellite && satelliteImage ? `sat:${satelliteStamp}` : "plain";
  const topo = layers.topo && topoImage && !(layers.satellite && satelliteImage) ? `topo:${topoStamp}` : "notopo";
  const key = `${night}|${layers.land}|${sat}|${topo}`;
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
    } else if (layers.topo && topoImage) {
      ctx.drawImage(topoImage, 0, 0, w, h);
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
  const shown = pins.filter((pin) => {
    const match = String(pin.clock || "").match(/(\d{4})/);
    return match ? nearestEra(Number(match[1])) === nearestEra(eraYear) : false;
  });
  for (const pin of shown) {
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
        color: fresh ? 0xf0d060 : 0xc9a227,
        depthTest: false,
        depthWrite: false,
        transparent: true,
        opacity: 1,
      })
    );
    core.userData.pin = pin;
    core.renderOrder = 5;
    group.add(core);
    const ring = new THREE.Mesh(
      PIN_RING,
      new THREE.MeshBasicMaterial({
        color: fresh ? 0xc9a227 : (dark() ? 0xfff6d8 : 0x1c1914),
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.95,
        depthTest: false,
        depthWrite: false,
      })
    );
    ring.userData.pin = pin;
    ring.renderOrder = 5;
    orientOutward(ring, position);
    group.add(ring);
    if (pin.bayesian && typeof pin.bayesian.value === "number") {
      const bayes = new THREE.Mesh(
        BAYES_RING,
        new THREE.MeshBasicMaterial({ color: 0x3d6f8a, side: THREE.DoubleSide, depthTest: false, depthWrite: false, transparent: true, opacity: 0.95 })
      );
      bayes.userData.pin = pin;
      bayes.renderOrder = 5;
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

function circleRing(lat, lon, radiusKm) {
  const steps = 28;
  const dLat = radiusKm / 111.32;
  const cos = Math.cos((lat * Math.PI) / 180) || 0.01;
  const dLon = radiusKm / (111.32 * Math.abs(cos));
  const ring = [];
  for (let i = 0; i < steps; i += 1) {
    const angle = (i / steps) * Math.PI * 2;
    ring.push({
      lat: lat + Math.sin(angle) * dLat,
      lon: lon + Math.cos(angle) * dLon,
    });
  }
  return ring;
}

function drawFeatureDisc(row) {
  if (!$("pin-card").hidden) return;
  if (!row || !row.disc || row.disc.radius_km == null || row.disc.lat == null || row.disc.lon == null) {
    drawArea(null);
    return;
  }
  drawArea(circleRing(Number(row.disc.lat), Number(row.disc.lon), Number(row.disc.radius_km)));
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
  const bands = [0.0, 0.55, 0.82, 1];
  const alphas = [0.42, 0.2, 0.07, 0];
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
    new THREE.LineBasicMaterial({ color: 0x8a6a10, transparent: true, opacity: 0.95, depthWrite: false })
  );
  outline.renderOrder = 3;
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
  await loadPattern();
  await refreshPlaceLabels();
  await loadCatalogs();
}

function rememberOpened(id) {
  opened.add(id);
  localStorage.setItem(OPENED_KEY, JSON.stringify([...opened]));
}

function fillCard(pin, area) {
  $("card-event").textContent = pin.event || "Pin";
  $("card-date").textContent = pin.clock || "";
  $("card-place").textContent = pin.placeLine || pin.place || "No place words on this pin.";
  const people = Array.isArray(pin.who) ? pin.who.filter(Boolean) : [];
  $("card-time").textContent = pin.time || "no time in source";
  const geo = pin.lat != null && pin.lon != null
    ? `${pin.lat}, ${pin.lon}${String(pin.note || "").includes("place estimated") ? " · place estimated" : ""}`
    : "no geo in source";
  $("card-geo").textContent = geo;
  $("card-who").textContent = people.length ? people.join(", ") : "no person in source";
  $("card-reason").textContent = pin.note || "";
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
  const neighbors = matrixEdges.filter((edge) => edge.from === pin.id || edge.to === pin.id);
  if (!neighbors.length) {
    $("pattern-card").textContent = "No connected pattern yet.";
  } else {
    $("pattern-card").textContent = neighbors.map((edge) => {
      const other = edge.from === pin.id ? edge.to_event : edge.from_event;
      return `${other}. ${edge.reason}. ${edge.delta}. ${edge.distance}.`;
    }).join(" ");
  }
  const badge = $("card-badge");
  const fromMatch = String(pin.note || "").includes("from corpus/upload");
  badge.hidden = !fromMatch;
  $("pin-card").hidden = false;
  document.body.classList.add("card-open");
  drawTethers(pin.id);
}

async function coverage(pin) {
  const lines = [];
  if (layers.street) {
    const response = await fetch(`/v1/tiles/street?lat=${encodeURIComponent(pin.lat)}&lon=${encodeURIComponent(pin.lon)}`);
    const data = await response.json();
    lines.push(data.available ? data.message : `Street view: ${data.message || "not available here"}`);
  }
  if (layers.lidar) {
    const response = await fetch(`/v1/tiles/lidar?lat=${encodeURIComponent(pin.lat)}&lon=${encodeURIComponent(pin.lon)}&year=${encodeURIComponent(activeYear())}`);
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
  sliderOwnsYear = false;
  eraYear = bundled;
  $("era").value = String(bundled);
  $("era-value").textContent = String(bundled);
  const source = "Source: aourednik/historical-basemaps, simplified offline subset.";
  $("era-note").textContent = bundled === year
    ? `Showing ${bundled} borders for this pin's date. estimated borders; source year ${bundled}. ${source}`
    : `Showing ${bundled} borders, the nearest bundled era to this pin's date (${year}). nearest public borders: ${bundled}. estimated borders; source year ${bundled}. ${source}`;
  paintEarth();
  refreshFrames();
  refreshPlaceLabels();
  loadBorderNote();
  rebuildPins();
}

async function openPin(id) {
  const pin = pins.find((item) => item.id === id);
  if (!pin) return;
  $("feature-card").hidden = true;
  focusFeatureId = "";
  focusId = id;
  rememberOpened(id);
  rebuildPins();
  spin = false;
  view.lon = pin.lon;
  view.lat = Math.max(-70, Math.min(70, pin.lat));
  view.dist = 1.85;
  userMoved = true;
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
  userMoved = true;
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
    view.dist = startDist + (1.85 - startDist) * ease;
    applyView();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

const MONTHS = {
  january: "01", february: "02", march: "03", april: "04", may: "05", june: "06",
  july: "07", august: "08", september: "09", october: "10", november: "11", december: "12",
};

function timeHit(pin, q) {
  const clock = String(pin.clock || "");
  const year = (clock.match(/(\d{4})/) || [])[1];
  const month = (clock.match(/\d{4}-(\d{2})/) || [])[1];
  if (!year) return false;
  if (/^\d{4}$/.test(q) && (year === q || String(nearestEra(Number(year))) === q)) return true;
  for (const [name, num] of Object.entries(MONTHS)) {
    if (!q.includes(name) || month !== num) continue;
    if (!/\d{4}/.test(q) || q.includes(year)) return true;
  }
  return false;
}

async function search(query) {
  const list = $("search-results");
  list.innerHTML = "";
  const q = query.trim().toLowerCase();
  if (!q) return;
  const tokens = q.split(/\s+/).filter(Boolean);
  const hits = pins.filter((pin) => tokens.every((token) => {
    const people = Array.isArray(pin.who) ? pin.who.join(" ") : "";
    const blob = `${pin.event || ""} ${people} ${pin.place || ""} ${pin.clock || ""} ${pin.time || ""} ${(pin.eraTerms || []).join(" ")}`.toLowerCase();
    return blob.includes(token) || timeHit(pin, token) || placeAliasHit(pin, token);
  }));
  const featureHits = [...featureRows, ...subsurfaceRows].filter((row) => {
    const blob = `${row.name || ""} ${(row.aliases || []).join(" ")} ${row.type || ""}`.toLowerCase();
    return blob.includes(q);
  });
  const anomalyHits = anomalyRows.filter((row) => {
    const blob = `${row.name || ""} ${(row.aliases || []).join(" ")} ${row.type || ""}`.toLowerCase();
    return blob.includes(q);
  });
  if (!hits.length && !featureHits.length && !anomalyHits.length) {
    const item = document.createElement("li");
    item.textContent = "No pin or public feature matches that.";
    list.append(item);
    return;
  }
  for (const pin of hits) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    const when = pin.clock ? ` · ${pin.clock.slice(0, 10)}` : "";
    const whereName = pin.eraName || pin.place || "";
    const where = whereName ? ` · ${whereName}` : "";
    button.textContent = `${pin.event || pin.id}${when}${where}`;
    button.addEventListener("click", () => {
      list.innerHTML = "";
      $("search").value = "";
      flyTo(pin);
      openPin(pin.id);
    });
    item.append(button);
    list.append(item);
  }
  for (const row of featureHits) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `Feature · ${row.name} · ${typeLabel(row.type)}`;
    button.addEventListener("click", () => {
      list.innerHTML = "";
      $("search").value = "";
      if (row.group === "subsurface") {
        layers.subsurface = true;
        $("layer-sub").checked = true;
      } else {
        layers.features = true;
        $("layer-features").checked = true;
      }
      drawCatalog();
      flyTo(row);
      showFeature(row);
    });
    item.append(button);
    list.append(item);
  }
  for (const row of anomalyHits) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `Anomaly · ${row.name}`;
    button.addEventListener("click", () => {
      list.innerHTML = "";
      $("search").value = "";
      layers.anomaly = true;
      $("layer-anomaly").checked = true;
      drawAnomalies();
      flyTo(row);
      showFeature(row);
    });
    item.append(button);
    list.append(item);
  }
}

function placeAliasHit(pin, q) {
  if (!q || q.length < 4) return false;
  for (const place of places) {
    const names = [place.name, ...(place.aliases || [])].map((item) => String(item).toLowerCase());
    if (!names.some((name) => name.includes(q))) continue;
    const modern = String(place.name).toLowerCase();
    if (String(pin.place || "").toLowerCase().includes(modern)) return true;
    if (pin.lat != null && Math.abs(pin.lat - place.lat) < 0.6 && Math.abs(pin.lon - place.lon) < 0.6) return true;
  }
  return false;
}

const TYPE_LABELS = {
  volcano: "Volcano",
  deep: "Marine deep",
  region: "Region",
  crater: "Crater",
  waterfall: "Waterfall",
  river: "River",
  lake: "Lake",
  peak: "Peak",
  canyon: "Canyon",
  reef: "Reef",
  strait: "Strait",
  desert: "Desert",
  ice: "Ice sheet",
  plate: "Plate boundary",
  cave: "Cave",
  cavern: "Cavern",
  tunnel: "Tunnel",
  mine: "Mine",
};

function typeLabel(type) {
  return TYPE_LABELS[type] || type || "Feature";
}

function checkedTypes(prefix, ids) {
  const chosen = new Set();
  for (const [id, type] of ids) {
    const box = $(id);
    if (box && box.checked) chosen.add(type);
  }
  return chosen;
}

const FEATURE_TYPE_IDS = [
  ["feat-volcano", "volcano"], ["feat-deep", "deep"], ["feat-region", "region"],
  ["feat-crater", "crater"], ["feat-waterfall", "waterfall"], ["feat-river", "river"],
  ["feat-lake", "lake"], ["feat-peak", "peak"], ["feat-canyon", "canyon"],
  ["feat-reef", "reef"], ["feat-strait", "strait"], ["feat-desert", "desert"],
  ["feat-ice", "ice"], ["feat-plate", "plate"],
];
const SUB_TYPE_IDS = [
  ["sub-cave", "cave"], ["sub-cavern", "cavern"], ["sub-tunnel", "tunnel"],
  ["sub-mine", "mine"], ["sub-other", "other"],
];

function visibleFeatures() {
  const chosen = checkedTypes("feat", FEATURE_TYPE_IDS);
  return featureRows.filter((row) => chosen.has(row.type));
}

function visibleSubsurface() {
  const chosen = checkedTypes("sub", SUB_TYPE_IDS);
  const known = new Set(["cave", "cavern", "tunnel", "mine"]);
  return subsurfaceRows.filter((row) => chosen.has(row.type) || (chosen.has("other") && !known.has(row.type)));
}

function showFeature(row) {
  $("pin-card").hidden = true;
  document.body.classList.remove("card-open");
  const card = $("feature-card");
  if (!row) {
    focusFeatureId = "";
    $("feature-name").textContent = "Subsurface";
    $("feature-type").textContent = "";
    $("feature-source").textContent = "";
    $("feature-era").textContent = "no public subsurface map here.";
    $("feature-note").textContent = "No entrance or survey plate from the public catalog is at this click.";
    card.hidden = false;
    drawFeatureDisc(null);
    return;
  }
  focusFeatureId = row.id || "";
  $("feature-name").textContent = row.name || "";
  $("feature-type").textContent = typeLabel(row.type);
  $("feature-source").textContent = row.source || "";
  $("feature-era").textContent = row.era_note || "";
  $("feature-note").textContent = "This marker is a catalog location. It is not an event pin.";
  card.hidden = false;
  const chipId = row.group === "subsurface" ? "chip-sub" : row.group === "anomaly" ? "chip-anomaly" : "chip-features";
  const layerOn = row.group === "subsurface" ? layers.subsurface : row.group === "anomaly" ? layers.anomaly : layers.features;
  if (layerOn && row.era_note) showChip(chipId, row.era_note, true);
  drawFeatureDisc(row);
}

function showAnomaly(row) {
  if (row) {
    showFeature(row);
    return;
  }
  $("pin-card").hidden = true;
  document.body.classList.remove("card-open");
  focusFeatureId = "";
  $("feature-name").textContent = "Anomaly";
  $("feature-type").textContent = "";
  $("feature-source").textContent = "";
  $("feature-era").textContent = "no public anomaly outline here.";
  $("feature-note").textContent = "No cited geographic outline is at this click.";
  $("feature-card").hidden = false;
  if ($("pin-card").hidden) drawArea(null);
}

function drawAnomalies() {
  while (anomalyGroup.children.length) {
    const child = anomalyGroup.children[0];
    anomalyGroup.remove(child);
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
  }
  if (!layers.anomaly) {
    showChip("chip-anomaly", "", false);
    return;
  }
  const rows = anomalyRows;
  for (const row of rows) {
    const ring = row.ring || [];
    if (ring.length >= 3) {
      const positions = [];
      const lifted = ring.map((pair) => latLonToVector3(pair[1], pair[0], 1.014));
      for (let i = 0; i < lifted.length; i += 1) {
        const a = lifted[i];
        const b = lifted[(i + 1) % lifted.length];
        positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      const material = new THREE.LineDashedMaterial({
        color: 0x1f6f78,
        transparent: true,
        opacity: 0.95,
        dashSize: 0.02,
        gapSize: 0.012,
        depthWrite: false,
      });
      const lines = new THREE.LineSegments(geometry, material);
      lines.computeLineDistances();
      lines.renderOrder = 3;
      anomalyGroup.add(lines);
      const face = new THREE.BufferGeometry();
      const facePos = [];
      const origin = lifted[0];
      for (let i = 1; i < lifted.length - 1; i += 1) {
        facePos.push(origin.x, origin.y, origin.z, lifted[i].x, lifted[i].y, lifted[i].z, lifted[i + 1].x, lifted[i + 1].y, lifted[i + 1].z);
      }
      face.setAttribute("position", new THREE.Float32BufferAttribute(facePos, 3));
      const mesh = new THREE.Mesh(
        face,
        new THREE.MeshBasicMaterial({
          color: 0x1f6f78,
          transparent: true,
          opacity: 0.16,
          depthWrite: false,
          side: THREE.DoubleSide,
        })
      );
      mesh.userData.anomaly = row;
      mesh.renderOrder = 2;
      anomalyGroup.add(mesh);
    }
  }
  const focused = rows.find((row) => row.id === focusFeatureId);
  const note = rows.length
    ? (focused && focused.era_note ? focused.era_note : rows[0].era_note)
    : "no public anomaly outline here.";
  showChip("chip-anomaly", note, true);
  buildLabelCatalog();
}

function addCatalogLine(line, color) {
  const positions = [];
  for (let i = 0; i < line.length - 1; i += 1) {
    const a = line[i];
    const b = line[i + 1];
    if (!a || !b || Math.abs(a[0] - b[0]) > 180) continue;
    const va = latLonToVector3(a[1], a[0], 1.012);
    const vb = latLonToVector3(b[1], b[0], 1.012);
    positions.push(va.x, va.y, va.z, vb.x, vb.y, vb.z);
  }
  if (!positions.length) return;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.9, depthWrite: false });
  const lines = new THREE.LineSegments(geometry, material);
  lines.renderOrder = 3;
  catalogGroup.add(lines);
}

function addCatalogDot(row, color) {
  const mesh = new THREE.Mesh(
    FEATURE_DOT,
    new THREE.MeshBasicMaterial({ color, depthTest: false, depthWrite: false, transparent: true, opacity: 0.95 })
  );
  mesh.position.copy(latLonToVector3(row.lat, row.lon, 1.025));
  mesh.userData.feature = row;
  mesh.renderOrder = 4;
  catalogGroup.add(mesh);
}

function drawCatalog() {
  while (catalogGroup.children.length) {
    const child = catalogGroup.children[0];
    catalogGroup.remove(child);
    if (child.geometry && child.geometry !== FEATURE_DOT) child.geometry.dispose();
    if (child.material) child.material.dispose();
  }
  if (layers.features) {
    for (const row of visibleFeatures()) {
      if (row.line) addCatalogLine(row.line, 0x1f6f78);
      if (row.lat != null && row.lon != null) addCatalogDot(row, 0x1f6f78);
    }
  }
  if (layers.subsurface) {
    for (const row of visibleSubsurface()) {
      if (row.line) addCatalogLine(row.line, 0x8a5a32);
      if (row.lat != null && row.lon != null) addCatalogDot(row, 0x8a5a32);
    }
  }
  const featureCount = layers.features ? visibleFeatures().length : 0;
  const subCount = layers.subsurface ? visibleSubsurface().length : 0;
  if (layers.features) {
    const rows = visibleFeatures();
    const focused = rows.find((row) => row.id === focusFeatureId);
    const shape = "modern catalog shape; no historical extent in source";
    const hold = "catalog only; not enough pins to recalibrate.";
    let note = "No public feature of that type is in this catalog.";
    if (rows.length && focused && focused.era_note) note = focused.era_note;
    else if (rows.length) {
      const changed = rows.find((row) => row.recalibrated && row.era_note);
      note = changed
        ? changed.era_note
        : `${featureCount} public features. modern catalog name; no era name in source. ${shape}. ${hold}`;
    }
    showChip("chip-features", note, true);
  } else showChip("chip-features", "", false);
  if (layers.subsurface) {
    const rows = visibleSubsurface();
    const dated = rows.find((row) => (row.era_note || "").includes("Survey year"));
    const note = rows.length
      ? `${rows.length} public entrances. ${(dated || rows[0]).era_note}`
      : "no public subsurface map here.";
    showChip("chip-sub", note, true);
  } else showChip("chip-sub", "", false);
}

async function loadCatalogs() {
  const ticket = ++catalogReq;
  const year = eraYear;
  const [features, subsurface, anomalies] = await Promise.all([
    fetch(`/v1/features?year=${encodeURIComponent(year)}`).then((response) => response.json()),
    fetch(`/v1/subsurface?year=${encodeURIComponent(year)}`).then((response) => response.json()),
    fetch(`/v1/anomalies?year=${encodeURIComponent(year)}`).then((response) => response.json()),
  ]);
  if (ticket !== catalogReq) return;
  featureRows = features.features || [];
  subsurfaceRows = subsurface.features || [];
  anomalyRows = anomalies.features || [];
  drawCatalog();
  drawAnomalies();
  if (focusFeatureId && !$("feature-card").hidden) {
    const row = [...featureRows, ...subsurfaceRows].find((item) => item.id === focusFeatureId);
    if (row) showFeature(row);
  }
  if (ticket === catalogReq) await sealRecalibrations();
}

async function refreshPlaceLabels() {
  const ticket = ++placeReq;
  const year = eraYear;
  const response = await fetch(`/v1/places/era?year=${encodeURIComponent(year)}`);
  if (ticket !== placeReq) return;
  const data = await response.json();
  if (ticket !== placeReq) return;
  const byId = new Map((data.pins || []).map((row) => [row.id, row]));
  for (const pin of pins) {
    const row = byId.get(pin.id);
    if (!row) continue;
    pin.eraTerms = row.terms || [];
    pin.eraName = row.era_name || "";
    pin.placeLine = row.place_line || "";
    pin.modernName = row.modern_name || "";
  }
  if (focusId && !$("pin-card").hidden) {
    const pin = pins.find((item) => item.id === focusId);
    if (pin) $("card-place").textContent = pin.placeLine || pin.place || "No place words on this pin.";
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
  const cause = $("cause").value.trim();
  const uploads = [...document.querySelectorAll("#attach-uploads input:checked")].map((box) => box.value);
  try {
    const result = await post("library_pin", {
      event: name,
      date,
      lat: Number(lat),
      lon: Number(lon),
      place,
      who: who ? who.split(",").map((part) => part.trim()).filter(Boolean) : [],
      cause: cause || undefined,
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
      userMoved = true;
      applyView();
    }
    $("receipt").textContent = result.h ? `hash ${result.h}` : "";
  } catch (err) {
    status.textContent = err.message;
  }
}

function activeYear() {
  if (!sliderOwnsYear && focusId) {
    const pin = pins.find((item) => item.id === focusId);
    if (pin) return pinYear(pin);
  }
  return eraYear;
}

async function frameNote(layer, product, year) {
  const chosen = year == null ? activeYear() : year;
  const query = new URLSearchParams({ layer, year: String(chosen) });
  if (product) query.set("product", product);
  const response = await fetch(`/v1/layers/frame?${query}`);
  return response.json();
}

function showChip(id, text, on) {
  const node = $(id);
  if (!node) return;
  node.hidden = !on;
  node.textContent = on ? text : "";
}

async function refreshFrames() {
  const ticket = ++earthReq;
  const year = activeYear();
  const stale = () => ticket !== earthReq;
  if (layers.satellite) await loadSatellite(year, stale);
  else if (!stale()) showChip("chip-satellite", "", false);
  if (stale()) return;
  if (layers.lidar) {
    const frame = await frameNote("lidar", undefined, year);
    if (stale()) return;
    showChip("chip-lidar", frame.note || "", true);
    if (focusId) {
      const pin = pins.find((item) => item.id === focusId);
      if (pin) coverage(pin);
    }
  } else showChip("chip-lidar", "", false);
  const ocean = [];
  if (layers.bathy) ocean.push(await frameNote("ocean", "bathymetry", year));
  if (layers.sst) ocean.push(await frameNote("ocean", "sst", year));
  if (layers.ice) ocean.push(await frameNote("ocean", "seaice", year));
  if (layers.coast) ocean.push(await frameNote("ocean", "coast", year));
  if (stale()) return;
  showChip("chip-ocean", ocean.map((row) => row.note).filter(Boolean).join(" "), ocean.length > 0);
  if (layers.topo) await loadTopography(year, stale);
  else showChip("chip-topo", "", false);
}

async function loadTopography(year, stale) {
  const chosen = year == null ? activeYear() : year;
  const expired = stale || (() => false);
  const frame = await frameNote("topography", undefined, chosen);
  if (expired() || !layers.topo) return;
  let note = frame.note || "";
  if (layers.satellite && satelliteImage) {
    note = `${note} Satellite is on, so this relief image is not painted over it.`.trim();
  }
  topoStamp = String(frame.frame_date || frame.frame_year || chosen);
  showChip("chip-topo", note, true);
  const response = await fetch(`/v1/tiles/topography?year=${encodeURIComponent(chosen)}`);
  if (expired() || !layers.topo) return;
  if (!response.ok) {
    topoImage = null;
    let message = note;
    try {
      const data = await response.json();
      if (data.note) message = data.message ? `${data.note} ${data.message}` : data.note;
      else if (data.message) message = `${note} ${data.message}`.trim();
    } catch (_err) {
      /* keep the frame note */
    }
    if (expired() || !layers.topo) return;
    showChip("chip-topo", message, true);
    paintEarth();
    return;
  }
  const blob = await response.blob();
  if (expired() || !layers.topo) return;
  if (!blob.type.startsWith("image/")) {
    topoImage = null;
    showChip("chip-topo", `${note} Topography did not load. No substitute relief is drawn.`.trim(), true);
    paintEarth();
    return;
  }
  topoImage = await createImageBitmap(blob);
  if (expired() || !layers.topo) return;
  showChip("chip-topo", note, true);
  paintEarth();
}

async function loadSatellite(year, stale) {
  const chosen = year == null ? activeYear() : year;
  const expired = stale || (() => false);
  satelliteNote = "";
  satelliteImage = null;
  const frame = await frameNote("satellite", undefined, chosen);
  if (expired() || !layers.satellite) return;
  satelliteStamp = String(frame.frame_date || frame.frame_year || chosen);
  showChip("chip-satellite", frame.note || "", true);
  const response = await fetch(`/v1/tiles/satellite?year=${encodeURIComponent(chosen)}`);
  if (expired() || !layers.satellite) return;
  if (!response.ok) {
    let message = frame.note || "Satellite imagery did not load from NASA GIBS. No substitute image is drawn.";
    try {
      const data = await response.json();
      if (data.note) message = data.note;
      else if (data.message) message = `${frame.note || ""} ${data.message}`.trim();
    } catch (_err) {
      /* keep the frame note */
    }
    if (expired() || !layers.satellite) return;
    satelliteNote = message;
    showChip("chip-satellite", message, true);
    paintEarth();
    return;
  }
  const blob = await response.blob();
  if (expired() || !layers.satellite) return;
  if (!blob.type.startsWith("image/")) {
    satelliteNote = `${frame.note || ""} Satellite imagery did not load. No substitute image is drawn.`.trim();
    showChip("chip-satellite", satelliteNote, true);
    paintEarth();
    return;
  }
  satelliteImage = await createImageBitmap(blob);
  if (expired() || !layers.satellite) return;
  satelliteNote = frame.note || "";
  paintEarth();
}

function drawTethers(focus) {
  while (tetherGroup.children.length) {
    const child = tetherGroup.children[0];
    tetherGroup.remove(child);
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
  }
  for (const edge of matrixEdges) {
    const hot = !focus || edge.from === focus || edge.to === focus;
    const start = latLonToVector3(edge.from_lat, edge.from_lon, 1.02);
    const end = latLonToVector3(edge.to_lat, edge.to_lon, 1.02);
    const points = [];
    const steps = 32;
    for (let i = 0; i <= steps; i += 1) {
      const t = i / steps;
      const point = new THREE.Vector3().lerpVectors(start, end, t);
      point.normalize().multiplyScalar(1.03 + Math.sin(Math.PI * t) * 0.22);
      points.push(point);
    }
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(
      geometry,
      new THREE.LineBasicMaterial({
        color: hot ? 0xc9a227 : 0x8a7340,
        transparent: true,
        opacity: hot ? 0.95 : 0.35,
        depthWrite: false,
      })
    );
    line.renderOrder = 3;
    tetherGroup.add(line);
  }
}

async function loadPattern() {
  const response = await fetch("/v1/pattern");
  const data = await response.json();
  matrixEdges = data.edges || [];
  const empty = $("pattern-empty");
  const board = $("pattern-matrix");
  if (!matrixEdges.length) {
    empty.hidden = false;
    empty.textContent = data.message || "No connected pattern yet.";
    board.innerHTML = "";
  } else {
    empty.hidden = true;
    const rows = data.rows || [];
    const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
    const body = rows.map((row) => (
      `<tr><td>${esc(row.event)}</td><td>${esc(row.time)}</td><td>${esc(row.place)}</td><td>${(row.tethered || []).map(esc).join("<br>")}</td></tr>`
    )).join("");
    board.innerHTML = `<table><thead><tr><th>Event</th><th>Time</th><th>Place</th><th>Tether</th></tr></thead><tbody>${body}</tbody></table>`;
  }
  drawTethers(focusId);
  sealOpenTethers();
  if (focusId) {
    const pin = pins.find((item) => item.id === focusId);
    if (pin && !$("pin-card").hidden) {
      const neighbors = matrixEdges.filter((edge) => edge.from === pin.id || edge.to === pin.id);
      $("pattern-card").textContent = neighbors.length
        ? neighbors.map((edge) => {
          const other = edge.from === pin.id ? edge.to_event : edge.from_event;
          return `${other}. ${edge.reason}. ${edge.delta}. ${edge.distance}.`;
        }).join(" ")
        : "No connected pattern yet.";
    }
  }
}

function renderCandidates(candidates) {
  const list = $("candidate-list");
  const empty = $("candidate-empty");
  const undatedList = $("undated-list");
  const undatedEmpty = $("undated-empty");
  list.innerHTML = "";
  if (undatedList) undatedList.innerHTML = "";
  const rows = candidates || [];
  const undated = rows.filter((row) => !row.date || row.era === "undated / era unknown");
  const dated = rows.filter((row) => row.date && row.era !== "undated / era unknown");
  empty.hidden = dated.length > 0;
  if (undatedEmpty) undatedEmpty.hidden = undated.length > 0;
  for (const row of dated) {
    const item = document.createElement("li");
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = row.badge || "from corpus/upload";
    const reason = document.createElement("p");
    reason.textContent = row.reason || "";
    item.append(badge, reason);
    if (row.seal) {
      const placed = document.createElement("p");
      placed.textContent = "High confidence. Sealing onto the lattice.";
      item.append(placed);
    } else if (!row.folded) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "ghost";
      button.textContent = "Confirm";
      button.addEventListener("click", () => {
        if (row.event) $("event").value = row.event;
        if (row.date) $("date").value = row.date;
        if (row.place) $("place").value = row.place;
        if (Array.isArray(row.who) && row.who.length) $("who").value = row.who.join(", ");
        if (row.lat != null) $("lat").value = String(row.lat);
        if (row.lon != null) $("lon").value = String(row.lon);
        $("status").textContent = "This match is not sealed yet. Press Pin to confirm it.";
        $("event").focus();
      });
      item.append(button);
    }
    list.append(item);
  }
  for (const row of undated) {
    const item = document.createElement("li");
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = "undated / era unknown";
    const reason = document.createElement("p");
    reason.textContent = row.reason || "";
    item.append(badge, reason);
    if (undatedList) undatedList.append(item);
  }
}

function pairKey(edge) {
  return [String(edge.from), String(edge.to)].sort().join("|");
}

async function sealRecalibrations() {
  if (sealingRecal) return;
  const rows = [...featureRows, ...subsurfaceRows].filter((row) => (
    row && row.needs_receipt && row.receipt_key && row.receipt_note && !sealedRecal.has(row.receipt_key)
  ));
  if (!rows.length) return;
  sealingRecal = true;
  try {
    for (const row of rows) {
      sealedRecal.add(row.receipt_key);
      await post("pin", {
        axis: "PI",
        note: row.receipt_note,
        src: "4dmap",
      });
    }
  } catch (err) {
    $("receipt").textContent = err.message;
  } finally {
    sealingRecal = false;
  }
}

async function sealOpenTethers() {
  if (sealingPattern) return;
  const open = matrixEdges.filter((edge) => (
    edge && edge.on_lattice === false && edge.from && edge.to && !sealedPairs.has(pairKey(edge))
  ));
  if (!open.length) return;
  sealingPattern = true;
  try {
    for (const edge of open) {
      await post("join", {
        left: edge.from,
        right: edge.to,
        join_type: "T-PI",
        note: `why tethered: ${edge.reason}`,
        src: "4dmap",
      });
      sealedPairs.add(pairKey(edge));
    }
    await loadPins();
  } catch (err) {
    $("receipt").textContent = err.message;
  } finally {
    sealingPattern = false;
  }
}

async function sealCandidate(row) {
  if (!row || !row.seal) return null;
  return post("library_pin", {
    event: row.event,
    date: row.date,
    lat: row.lat,
    lon: row.lon,
    place: row.place,
    who: row.who || [],
    time: row.time || undefined,
    surface: row.surface === "REAL" ? "REAL" : "MOCK",
    src: "aziel-corpus",
    note: `from corpus/upload · ${row.reason}`,
  });
}

async function takeCandidates(candidates) {
  renderCandidates(candidates);
  let sealed = false;
  for (const row of candidates || []) {
    if (!row.seal) continue;
    await sealCandidate(row);
    sealed = true;
  }
  if (sealed) await loadPins();
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
    userMoved = true;
    $("hint").classList.add("gone");
  }
  if (pointers.size === 2) {
    const pts = [...pointers.values()];
    const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    if (start.lastPinch) {
      view.dist = Math.min(DIST_MAX, Math.max(DIST_MIN, view.dist * (start.lastPinch / Math.max(dist, 1))));
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
  if (hits[0] && hits[0].object.userData.pin) {
    openPin(hits[0].object.userData.pin.id);
    return;
  }
  if (layers.features || layers.subsurface) {
    const marks = ray.intersectObjects(catalogGroup.children, true);
    const mark = marks.find((hit) => hit.object.userData.feature);
    if (mark) {
      const row = mark.object.userData.feature;
      flyTo(row);
      showFeature(row);
      return;
    }
  }
  if (layers.anomaly) {
    const marks = ray.intersectObjects(anomalyGroup.children, true);
    const mark = marks.find((hit) => hit.object.userData.anomaly);
    if (mark) {
      const row = mark.object.userData.anomaly;
      flyTo(row);
      showFeature(row);
      return;
    }
    if (!layers.subsurface) {
      const ground = ray.intersectObject(earth, false);
      if (ground.length) showAnomaly(null);
    }
  }
  if (layers.subsurface) {
    const ground = ray.intersectObject(earth, false);
    if (ground.length) showFeature(null);
  }
}
canvas.addEventListener("pointerup", endPointer);
canvas.addEventListener("pointercancel", (event) => pointers.delete(event.pointerId));
canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  spin = false;
  userMoved = true;
  $("hint").classList.add("gone");
  view.dist = Math.min(DIST_MAX, Math.max(DIST_MIN, view.dist + Math.sign(event.deltaY) * 0.18));
  applyView();
}, { passive: false });

addEventListener("keydown", (event) => {
  const tag = (event.target && event.target.tagName) || "";
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
  if (event.key === "ArrowLeft") view.lon -= 8;
  else if (event.key === "ArrowRight") view.lon += 8;
  else if (event.key === "ArrowUp") view.lat = Math.min(80, view.lat + 6);
  else if (event.key === "ArrowDown") view.lat = Math.max(-80, view.lat - 6);
  else if (event.key === "+" || event.key === "=") view.dist = Math.max(DIST_MIN, view.dist - 0.2);
  else if (event.key === "-" || event.key === "_") view.dist = Math.min(DIST_MAX, view.dist + 0.2);
  else return;
  spin = false;
  userMoved = true;
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
  sliderOwnsYear = true;
  eraYear = Number($("era").value);
  $("era-value").textContent = String(eraYear);
  $("era-note").textContent = eraCopy(eraYear);
  paintEarth();
  refreshFrames();
  refreshPlaceLabels();
  loadBorderNote();
  loadCatalogs();
  rebuildPins();
});
for (const [id, key] of [
  ["layer-land", "land"],
  ["layer-borders", "borders"],
  ["layer-satellite", "satellite"],
  ["layer-street", "street"],
  ["layer-lidar", "lidar"],
  ["layer-topo", "topo"],
  ["layer-shadow", "shadow"],
  ["layer-bathy", "bathy"],
  ["layer-sst", "sst"],
  ["layer-ice", "ice"],
  ["layer-coast", "coast"],
  ["layer-features", "features"],
  ["layer-sub", "subsurface"],
  ["layer-anomaly", "anomaly"],
]) {
  $(id).addEventListener("change", async () => {
    layers[key] = $(id).checked;
    if (key === "satellite" || key === "lidar" || key === "topo" || key === "bathy" || key === "sst" || key === "ice" || key === "coast") {
      if (key === "satellite" && !layers.satellite) {
        satelliteImage = null;
        satelliteStamp = "";
        paintEarth();
      }
      if (key === "topo" && !layers.topo) {
        topoImage = null;
        topoStamp = "";
        paintEarth();
      }
      await refreshFrames();
    }
    if (key === "features" || key === "subsurface") drawCatalog();
    if (key === "borders") {
      paintEarth();
      if (layers.borders) loadBorderNote();
      else showChip("chip-borders", "", false);
    }
    if (key === "anomaly") drawAnomalies();
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
for (const [id] of [...FEATURE_TYPE_IDS, ...SUB_TYPE_IDS]) {
  $(id).addEventListener("change", drawCatalog);
}
$("feature-close").addEventListener("click", () => {
  $("feature-card").hidden = true;
  focusFeatureId = "";
  if ($("pin-card").hidden) drawArea(null);
});
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
  if (response.ok) {
    await loadUploads();
    if (data.candidates) await takeCandidates(data.candidates);
  }
});
$("corpus-sync").addEventListener("click", async () => {
  const response = await fetch("/v1/corpus");
  const data = await response.json();
  await takeCandidates(data.candidates || []);
  const files = Array.isArray(data.files) ? data.files.length : 0;
  if (files) $("status").textContent = data.message || `Read ${files} corpus files.`;
  if (!data.candidates || !data.candidates.length) {
    $("candidate-empty").hidden = false;
    $("candidate-empty").textContent = data.message || "No corpus or upload match yet.";
  }
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
$("act-tether").addEventListener("click", () => advanced("join", {
  left: $("from-id").value,
  right: $("to-id").value,
  join_type: "T-PI",
  note: "why tethered",
}));
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
  const featureScale = view.dist / 2.4;
  for (const child of catalogGroup.children) {
    if (child.userData.feature) child.scale.setScalar(featureScale);
  }
  placeLabels();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

async function loadBorderNote() {
  const ticket = ++borderReq;
  const year = eraYear;
  let data = null;
  try {
    const response = await fetch(`/v1/borders?year=${encodeURIComponent(year)}`);
    data = await response.json();
  } catch (_err) {
    data = null;
  }
  if (ticket !== borderReq) return;
  successors = (data && data.labels) || {};
  const note = (data && data.note) || eraCopy(year);
  if (!(focusId && !sliderOwnsYear)) $("era-note").textContent = note;
  if (layers.borders) showChip("chip-borders", note, true);
  else showChip("chip-borders", "", false);
  buildLabelCatalog();
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
  loadBorderNote();
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", paintEarth);
  try {
    await loadPins();
  } catch (err) {
    $("status").textContent = err.message;
  }
  try {
    await loadCatalogs();
  } catch (_err) {
    /* A missing catalog does not invent features. */
  }
  loadShadow();
  loadUploads();
  if (!renderer.getContext()) $("globe-fallback").hidden = false;
  frame();
}

boot();
