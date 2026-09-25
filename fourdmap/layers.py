"""Network map layers. Called only when the operator turns a layer on.

Satellite, street, and LiDAR each say what they actually fetched.
A failure is "not available here" or "no LiDAR here". No substitute image.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .earth import satellite_slice, topo_slice

SATELLITE_URL = (
    "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    "?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
    "&LAYERS=BlueMarble_ShadedRelief_Bathymetry"
    "&FORMAT=image/jpeg&CRS=EPSG:4326"
    "&BBOX=-90,-180,90,180&WIDTH=1024&HEIGHT=512"
)
SATELLITE_LABEL = (
    "NASA GIBS Blue Marble shaded relief. "
    "This is a base image, not a photograph from the event date."
)
USER_AGENT = "4DMap/0.3.0 (local workbench; Aziel Eliab)"


def _get(url: str, timeout: float = 8.0) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(req, timeout=timeout) as response:  # noqa: S310 — fixed hosts only
        ctype = response.headers.get("Content-Type") or "application/octet-stream"
        return response.read(), ctype.split(";")[0].strip()


def fetch_satellite(year: int | None = None, day: str | None = None) -> dict[str, Any]:
    if year is None and not day:
        slice_note = SATELLITE_LABEL
        source = "NASA GIBS BlueMarble_ShadedRelief_Bathymetry"
        url = SATELLITE_URL
        frame_year = None
        exact = False
    else:
        chosen = satellite_slice(year or day or 1914, day)
        slice_note = chosen["note"]
        source = chosen["source"]
        url = chosen["url"]
        frame_year = chosen["frame_year"]
        exact = chosen["exact"]
    try:
        body, ctype = _get(url)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "available": False,
            "layer": "satellite",
            "message": "Satellite imagery did not load from NASA GIBS. No substitute image is drawn.",
            "reason": str(exc.__class__.__name__),
        }
    if not body or not ctype.startswith("image/"):
        return {
            "ok": False,
            "available": False,
            "layer": "satellite",
            "message": "Satellite imagery did not load from NASA GIBS. No substitute image is drawn.",
            "reason": ctype or "empty",
        }
    return {
        "ok": True,
        "available": True,
        "layer": "satellite",
        "content_type": ctype,
        "body": body,
        "label": slice_note,
        "source": source,
        "frame_year": frame_year,
        "exact": exact,
        "note": slice_note,
        "event_date_imagery": bool(exact),
    }


def fetch_topography(year: int | None = None) -> dict[str, Any]:
    chosen = topo_slice(year if year is not None else 1914)
    try:
        body, ctype = _get(chosen["url"])
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "available": False,
            "layer": "topography",
            "message": "Topography did not load from NASA SRTM. No substitute relief is drawn.",
            "reason": str(exc.__class__.__name__),
            "note": chosen["note"],
            "source": chosen["source"],
            "frame_year": chosen["frame_year"],
        }
    if not body or not ctype.startswith("image/"):
        return {
            "ok": False,
            "available": False,
            "layer": "topography",
            "message": "Topography did not load from NASA SRTM. No substitute relief is drawn.",
            "reason": ctype or "empty",
            "note": chosen["note"],
            "source": chosen["source"],
            "frame_year": chosen["frame_year"],
        }
    return {
        "ok": True,
        "available": True,
        "layer": "topography",
        "content_type": ctype,
        "body": body,
        "label": chosen["note"],
        "source": chosen["source"],
        "frame_year": chosen["frame_year"],
        "exact": False,
        "note": chosen["note"],
    }


def street_lookup(lat: float, lon: float) -> dict[str, Any]:
    url = f"https://api.openstreetcam.org/1.0/nearby/?lat={lat:.5f}&lng={lon:.5f}&distance=80"
    try:
        body, _ctype = _get(url)
        data = json.loads(body.decode("utf-8", errors="replace") or "{}")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeError):
        return {
            "ok": True,
            "available": False,
            "layer": "street",
            "message": "not available here",
            "reason": "Street-level lookup did not return coverage for this anchor.",
            "source": "KartaView / OpenStreetCam",
        }
    photos = _street_photos(data)
    if not photos:
        return {
            "ok": True,
            "available": False,
            "layer": "street",
            "message": "not available here",
            "reason": "No street-level frame was returned for this anchor.",
            "source": "KartaView / OpenStreetCam",
        }
    return {
        "ok": True,
        "available": True,
        "layer": "street",
        "message": "Nearby street-level frames. They are not the event, and they are not an exact point.",
        "source": "KartaView / OpenStreetCam",
        "photos": photos[:3],
    }


def _street_photos(data: Any) -> list[dict[str, Any]]:
    rows: list[Any] = []
    if isinstance(data, dict):
        for key in ("currentPageItems", "photos", "data", "result"):
            inner = data.get(key)
            if isinstance(inner, list):
                rows = inner
                break
            if isinstance(inner, dict):
                for key2 in ("data", "photos", "items"):
                    if isinstance(inner.get(key2), list):
                        rows = inner[key2]
                        break
    elif isinstance(data, list):
        rows = data
    photos = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = row.get("fileurl") or row.get("lth_name") or row.get("image") or row.get("url") or row.get("thumb")
        if not isinstance(url, str) or not url.startswith("http"):
            continue
        photos.append({"url": url, "source": "KartaView / OpenStreetCam"})
    return photos


def lidar_lookup(lat: float, lon: float) -> dict[str, Any]:
    url = (
        "https://epqs.nationalmap.gov/v1/json"
        f"?x={lon:.5f}&y={lat:.5f}&units=Meters&wkid=4326"
    )
    try:
        body, _ctype = _get(url)
        data = json.loads(body.decode("utf-8", errors="replace") or "{}")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeError):
        return {
            "ok": True,
            "available": False,
            "layer": "lidar",
            "message": "no LiDAR here",
            "reason": "USGS 3DEP did not return an elevation for this anchor.",
            "source": "USGS 3DEP EPQS",
        }
    value = _elevation(data)
    if value is None:
        return {
            "ok": True,
            "available": False,
            "layer": "lidar",
            "message": "no LiDAR here",
            "reason": "USGS 3DEP has no elevation sample at this anchor. Coverage is mainly the United States.",
            "source": "USGS 3DEP EPQS",
        }
    if abs(value) < 0.001:
        return {
            "ok": True,
            "available": False,
            "layer": "lidar",
            "message": "no LiDAR here",
            "reason": "USGS 3DEP returned a zero sample, which is water or a gap, not a LiDAR scan.",
            "source": "USGS 3DEP EPQS",
            "point_cloud": False,
        }
    return {
        "ok": True,
        "available": True,
        "layer": "lidar",
        "elevation_m": value,
        "message": (
            f"USGS 3DEP elevation sample at the reported anchor: {value:.0f} m. "
            "This is a height sample, not a LiDAR point cloud and not proof of the place."
        ),
        "source": "USGS 3DEP EPQS",
        "point_cloud": False,
    }


def _elevation(data: Any) -> float | None:
    if not isinstance(data, dict):
        return None
    raw = data.get("value")
    if raw is None and isinstance(data.get("USGS_Elevation_Point_Query_Service"), dict):
        raw = data["USGS_Elevation_Point_Query_Service"].get("Elevation_Query", {}).get("Elevation")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value <= -100000 or value >= 10000:
        return None
    return value
