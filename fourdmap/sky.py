"""Local sun, moon, and bright-star positions.

This is a short Meeus-style calculation kept inside the package.
It is not a full star catalog and it is not proof of a place.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

# RA in hours, Dec in degrees, J2000. A short list, not the sky.
STARS: dict[str, tuple[float, float]] = {
    "polaris": (2.530, 89.264),
    "sirius": (6.752, -16.716),
    "canopus": (6.399, -52.696),
    "rigel": (5.242, -8.202),
    "betelgeuse": (5.919, 7.407),
    "vega": (18.616, 38.784),
    "altair": (19.846, 8.868),
    "antares": (16.490, -26.432),
    "aldebaran": (4.599, 16.509),
    "spica": (13.420, -11.161),
}


def _julian(when: datetime) -> float:
    when = when.astimezone(timezone.utc)
    y, m = when.year, when.month
    d = when.day + (when.hour + when.minute / 60 + when.second / 3600) / 24
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def _gmst_deg(n: float) -> float:
    return (280.46061837 + 360.98564736629 * n) % 360.0


def _alt_az(ra_rad: float, dec_rad: float, lat_deg: float, lon_deg: float, gmst: float) -> tuple[float, float]:
    lst = math.radians((gmst + lon_deg) % 360.0)
    ha = lst - ra_rad
    lat = math.radians(lat_deg)
    alt = math.asin(math.sin(lat) * math.sin(dec_rad) + math.cos(lat) * math.cos(dec_rad) * math.cos(ha))
    az = math.atan2(-math.sin(ha), math.tan(dec_rad) * math.cos(lat) - math.sin(lat) * math.cos(ha))
    return math.degrees(alt), math.degrees(az) % 360.0


def sun_alt_az(when: datetime, lat_deg: float, lon_deg: float) -> dict[str, float]:
    n = _julian(when) - 2451545.0
    mean_lon = (280.460 + 0.9856474 * n) % 360.0
    anomaly = math.radians((357.528 + 0.9856003 * n) % 360.0)
    ecl = math.radians(mean_lon + 1.915 * math.sin(anomaly) + 0.020 * math.sin(2 * anomaly))
    eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(eps) * math.sin(ecl), math.cos(ecl))
    dec = math.asin(math.sin(eps) * math.sin(ecl))
    alt, az = _alt_az(ra, dec, lat_deg, lon_deg, _gmst_deg(n))
    return {"altitude_deg": alt, "azimuth_deg": az}


def moon_alt_az(when: datetime, lat_deg: float, lon_deg: float) -> dict[str, float]:
    """Low-precision moon. Good enough to say up or down, not a lunar survey."""
    n = _julian(when) - 2451545.0
    L = math.radians((218.316 + 13.176396 * n) % 360.0)
    M = math.radians((134.963 + 13.064993 * n) % 360.0)
    F = math.radians((93.272 + 13.229350 * n) % 360.0)
    lon = L + math.radians(6.289 * math.sin(M))
    lat = math.radians(5.128 * math.sin(F))
    eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.sin(lon) * math.cos(eps) - math.tan(lat) * math.sin(eps), math.cos(lon))
    dec = math.asin(math.sin(lat) * math.cos(eps) + math.cos(lat) * math.sin(eps) * math.sin(lon))
    alt, az = _alt_az(ra, dec, lat_deg, lon_deg, _gmst_deg(n))
    # Elongation from the sun, rough phase in 0..1.
    sun = sun_alt_az(when, lat_deg, lon_deg)
    phase = (1 - math.cos(math.radians((13.176396 * n) % 360.0))) / 2
    return {"altitude_deg": alt, "azimuth_deg": az, "phase": phase, "sun_altitude_deg": sun["altitude_deg"]}


def star_alt_az(name: str, when: datetime, lat_deg: float, lon_deg: float) -> dict[str, float] | None:
    key = name.strip().lower()
    if key not in STARS:
        return None
    ra_h, dec = STARS[key]
    n = _julian(when) - 2451545.0
    alt, az = _alt_az(math.radians(ra_h * 15.0), math.radians(dec), lat_deg, lon_deg, _gmst_deg(n))
    return {"name": key, "altitude_deg": alt, "azimuth_deg": az, "catalog": "J2000 short list"}


def stars_in_text(text: str, when: datetime, lat_deg: float, lon_deg: float) -> list[dict[str, float]]:
    low = text.lower()
    found = []
    for name in STARS:
        if name in low:
            row = star_alt_az(name, when, lat_deg, lon_deg)
            if row:
                found.append(row)
    return found
