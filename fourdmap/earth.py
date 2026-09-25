"""Era slices for public earth layers. No network. No invented imagery.

A year before the public archive gets the nearest real frame and says so.
The note never calls that frame by the historical year.
Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

MODIS_START = "2000-02-24"
OISST_START = "1981-09-01"
SEAICE_START = "1978-10-01"
GEBCO_YEAR = 2023
SRTM_DATE = "2000-02-11"
BUNDLED_ERAS = (1914, 1945, 1994, 2010)

GIBS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"


def _year(value: Any, default: int = 1914) -> int:
    text = str(value or "").strip()
    digits = ""
    for ch in text:
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                break
        elif digits:
            break
    if len(digits) == 4:
        return int(digits)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _wms(layer: str, when: str | None = None) -> str:
    url = (
        f"{GIBS}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
        f"&LAYERS={layer}&FORMAT=image/jpeg&CRS=EPSG:4326"
        "&BBOX=-90,-180,90,180&WIDTH=1024&HEIGHT=512"
    )
    if when:
        url += f"&TIME={when}"
    return url


def satellite_slice(year: Any, day: str | None = None) -> dict[str, Any]:
    """NASA GIBS only. Before MODIS, the nearest frame is 2000-02-24."""
    wanted = _year(year)
    day_text = str(day or "")
    if wanted > 2000 or (wanted == 2000 and (not day_text or day_text >= MODIS_START)):
        date = f"{wanted:04d}-07-01"
        if day_text[:4] == f"{wanted:04d}" and len(day_text) >= 10:
            date = day_text[:10]
        exact = date >= MODIS_START
        if not exact:
            date = MODIS_START
        note = (
            f"Public frame {date}. Source: NASA GIBS MODIS Terra CorrectedReflectance TrueColor."
            if exact
            else (
                f"nearest public frame: {date[:4]}. "
                "Source: NASA GIBS MODIS Terra. "
                f"This is not {wanted} imagery."
            )
        )
        return {
            "layer": "satellite",
            "exact": exact,
            "frame_year": int(date[:4]),
            "frame_date": date,
            "source": "NASA GIBS MODIS Terra CorrectedReflectance TrueColor",
            "note": note,
            "image": True,
            "url": _wms("MODIS_Terra_CorrectedReflectance_TrueColor", date),
        }
    note = (
        f"nearest public frame: 2000. "
        "Source: NASA GIBS MODIS Terra CorrectedReflectance TrueColor. "
        f"This is not {wanted} imagery."
    )
    return {
        "layer": "satellite",
        "exact": False,
        "frame_year": 2000,
        "frame_date": MODIS_START,
        "source": "NASA GIBS MODIS Terra CorrectedReflectance TrueColor",
        "note": note,
        "image": True,
        "url": _wms("MODIS_Terra_CorrectedReflectance_TrueColor", MODIS_START),
    }


def lidar_slice(year: Any) -> dict[str, Any]:
    wanted = _year(year)
    return {
        "layer": "lidar",
        "exact": False,
        "frame_year": None,
        "frame_date": None,
        "source": "USGS 3DEP EPQS",
        "image": False,
        "note": (
            f"modern elevation; no LiDAR for this era ({wanted}). "
            "Source: USGS 3DEP. This sample is present-day, not "
            f"{wanted}."
        ),
    }


def topo_slice(year: Any) -> dict[str, Any]:
    """SRTM is a 2000 elevation model. No historical topo sheet is fetched."""
    wanted = _year(year)
    source = "NASA SRTM Color Index"
    return {
        "layer": "topography",
        "exact": False,
        "frame_year": 2000,
        "frame_date": SRTM_DATE,
        "source": source,
        "image": True,
        "note": (
            "modern topography; no era sheet for this year. "
            f"Source: {source} ({SRTM_DATE}). "
            f"This is not a {wanted} topographic sheet."
        ),
        "url": _wms("SRTM_Color_Index"),
    }


def _nearest_bundled(year: int) -> int:
    return min(BUNDLED_ERAS, key=lambda item: abs(item - year))


def ocean_slice(product: str, year: Any) -> dict[str, Any]:
    wanted = _year(year)
    kind = str(product or "bathymetry").strip().lower()
    if kind in {"bathy", "bathymetry"}:
        return {
            "layer": "ocean",
            "product": "bathymetry",
            "exact": False,
            "frame_year": GEBCO_YEAR,
            "frame_date": str(GEBCO_YEAR),
            "source": "GEBCO 2023",
            "image": False,
            "note": (
                f"nearest public frame: {GEBCO_YEAR}. "
                "Source: GEBCO 2023 bathymetry. "
                f"This is a present-day compilation, not {wanted} ocean depth."
            ),
        }
    if kind in {"sst", "temperature"}:
        if wanted < 1981:
            return {
                "layer": "ocean",
                "product": "sst",
                "exact": False,
                "frame_year": 1981,
                "frame_date": OISST_START,
                "source": "NOAA OISST",
                "image": False,
                "note": (
                    "nearest public frame: 1981. "
                    "Source: NOAA Optimum Interpolation Sea Surface Temperature. "
                    f"This is not {wanted} sea temperature."
                ),
            }
        date = OISST_START if wanted == 1981 else f"{wanted:04d}-07-01"
        return {
            "layer": "ocean",
            "product": "sst",
            "exact": True,
            "frame_year": wanted,
            "frame_date": date,
            "source": "NOAA OISST",
            "image": False,
            "note": (
                f"Public frame {date}. "
                "Source: NOAA Optimum Interpolation Sea Surface Temperature."
            ),
        }
    if kind in {"seaice", "ice", "sea-ice"}:
        if wanted < 1978:
            return {
                "layer": "ocean",
                "product": "seaice",
                "exact": False,
                "frame_year": 1978,
                "frame_date": SEAICE_START,
                "source": "NSIDC / NOAA sea ice",
                "image": False,
                "note": (
                    "nearest public frame: 1978. "
                    "Source: NSIDC / NOAA sea-ice concentration. "
                    f"This is not {wanted} sea ice."
                ),
            }
        date = SEAICE_START if wanted == 1978 else f"{wanted:04d}-09-15"
        return {
            "layer": "ocean",
            "product": "seaice",
            "exact": True,
            "frame_year": int(date[:4]),
            "frame_date": date,
            "source": "NSIDC / NOAA sea ice",
            "image": False,
            "note": f"Public frame {date}. Source: NSIDC / NOAA sea-ice concentration.",
        }
    bundled = _nearest_bundled(wanted)
    exact = bundled == wanted
    note = (
        f"Coastline for {bundled} from the bundled basemap "
        "(aourednik/historical-basemaps, simplified offline subset)."
    )
    if not exact:
        note = f"nearest public frame: {bundled}. {note} This is not a {wanted} survey."
    return {
        "layer": "ocean",
        "product": "coast",
        "exact": exact,
        "frame_year": bundled,
        "frame_date": str(bundled),
        "source": "aourednik/historical-basemaps",
        "image": False,
        "note": note,
    }


def describe_frame(layer: str, year: Any, product: str | None = None, day: str | None = None) -> dict[str, Any]:
    name = str(layer or "").strip().lower()
    if name == "lidar":
        return lidar_slice(year)
    if name in {"topo", "topography"}:
        return topo_slice(year)
    if name == "ocean":
        return ocean_slice(product or "bathymetry", year)
    if name == "street":
        return {
            "layer": "street",
            "exact": False,
            "source": "KartaView / OpenStreetCam",
            "image": False,
            "note": "Street view is present-day where a frame exists. It is not the historical era.",
        }
    return satellite_slice(year, day)
