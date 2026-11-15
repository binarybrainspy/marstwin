"""NASA POWER climatology fetch — air temperature + precipitation.

API docs: https://power.larc.nasa.gov/
No Earthdata login required for the public POWER API.

We use T2M (air at 2 m) so Earth diurnal ΔT can be compared to MEDA air temps
at Jezero — not MODIS LST.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"


def fetch_climatology(lat: float, lon: float, timeout: int = 60) -> dict[str, Any]:
    params = {
        "parameters": "T2M_MAX,T2M_MIN,PRECTOTCORR",
        "community": "AG",
        "longitude": f"{lon:.4f}",
        "latitude": f"{lat:.4f}",
        "format": "JSON",
    }
    url = f"{POWER_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "MarsTwin/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def summarize_power(payload: dict[str, Any]) -> dict[str, float | None]:
    """Return mean annual diurnal air ΔT (K) and precip (mm/yr)."""
    props = payload.get("properties", {}).get("parameter", {})
    t_max = props.get("T2M_MAX", {})
    t_min = props.get("T2M_MIN", {})
    precip = props.get("PRECTOTCORR", {})

    def monthly_values(block: dict) -> list[float]:
        out = []
        for k, v in block.items():
            if k.upper() == "ANN":
                continue
            if v is None:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            # POWER uses -999 for missing
            if fv <= -900:
                continue
            out.append(fv)
        return out

    maxima = monthly_values(t_max)
    minima = monthly_values(t_min)
    diurnal = None
    if maxima and minima and len(maxima) == len(minima):
        deltas = [a - b for a, b in zip(maxima, minima)]
        diurnal = sum(deltas) / len(deltas)
    elif maxima and minima:
        diurnal = (sum(maxima) / len(maxima)) - (sum(minima) / len(minima))

    precip_ann = precip.get("ANN")
    precip_mm = None
    if precip_ann is not None:
        try:
            # PRECTOTCORR climatology ANN is mm/day → mm/yr
            precip_mm = float(precip_ann) * 365.25
            if precip_mm < 0:
                precip_mm = None
        except (TypeError, ValueError):
            precip_mm = None

    return {
        "diurnal_temp_range": None if diurnal is None else round(diurnal, 2),
        "precipitation": None if precip_mm is None else round(precip_mm, 1),
    }


def enrich_cells_with_power(
    cells: list[dict[str, Any]],
    cache_path: Path,
    sleep_s: float = 0.35,
    force: bool = False,
) -> list[dict[str, Any]]:
    cache: dict[str, Any] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    for cell in cells:
        cid = cell["id"]
        if not force and cid in cache and cache[cid].get("ok"):
            summary = cache[cid]["summary"]
        else:
            try:
                payload = fetch_climatology(cell["lat"], cell["lon"])
                summary = summarize_power(payload)
                cache[cid] = {
                    "ok": True,
                    "lat": cell["lat"],
                    "lon": cell["lon"],
                    "summary": summary,
                    "source": "NASA POWER climatology T2M_MAX/T2M_MIN/PRECTOTCORR",
                }
                print(f"  POWER ok {cid}: ΔT={summary['diurnal_temp_range']} K, "
                      f"precip={summary['precipitation']} mm/yr")
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
                cache[cid] = {"ok": False, "error": str(exc)}
                print(f"  POWER fail {cid}: {exc}")
                summary = {}
            time.sleep(sleep_s)

        if summary:
            if cell["features"].get("diurnal_temp_range") is None:
                cell["features"]["diurnal_temp_range"] = summary.get("diurnal_temp_range")
            if cell["features"].get("precipitation") is None:
                cell["features"]["precipitation"] = summary.get("precipitation")
            cell["tempKind"] = "air"
            cell["powerSource"] = "NASA POWER T2M (air, 2 m)"

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return cells
