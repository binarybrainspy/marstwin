"""MODIS NDVI (MOD13Q1) via the ORNL DAAC point-subset API.

No Earthdata login required.
  API:  https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset
  Docs: https://modis.ornl.gov/data/modis_webservice.html

Sampling rule: 250 m / 16-day NDVI composites in a +/-1 km box (~9x9 pixels)
around the cell centre. This is a *point sample*, not a 0.5 degree cell mean —
say so on the method page and in the gap report.

Scale: raw integers x 0.0001. Fill values are masked; negative NDVI
(snow / rock / water) is kept and treated as barren by the 0-target similarity.

Paging: the API serves at most 10 composites per request, so one year is
fetched in ~3 windows. Responds are cached under science/cache/.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ORS_BASE = "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset"
PRODUCT = "MOD13Q1"
BAND = "250m_16_days_NDVI"
DEFAULT_YEAR = 2025
DEFAULT_BOX_KM = 1
DEFAULT_TIMEOUT_S = 60
DEFAULT_WORKERS = 3
# MOD13Q1: -3000 fill; valid NDVI raw range roughly -2000..10000.
RAW_MIN, RAW_MAX = -2000, 10000
MAX_COMPOSITES_PER_REQUEST = 10
COMPOSITE_DAYS = 16


def _fetch_chunk(
    lat: float,
    lon: float,
    year: int,
    start_day: int,
    end_day: int,
    box_km: int,
    timeout: int,
    attempts: int = 2,
) -> dict[str, Any]:
    params = {
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "startDate": f"A{year}{start_day:03d}",
        "endDate": f"A{year}{end_day:03d}",
        "band": BAND,
        "kmAboveBelow": box_km,
        "kmLeftRight": box_km,
    }
    url = f"{ORS_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "MarsTwin/0.1"})

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            error = RuntimeError(f"ORNL MODIS HTTP {exc.code}: {detail}")
            # Missing coverage will never succeed on retry.
            if "No data available" in detail or exc.code < 500:
                raise error from exc
            last_error = error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(2.0 * attempt)

    raise RuntimeError(f"ORNL MODIS request failed after {attempts} attempts: {last_error}")


def _last_composite_day(subset: list[dict[str, Any]], fallback: int) -> int:
    if not subset:
        return fallback
    calendar = subset[-1].get("calendar_date")
    if not calendar:
        return fallback
    try:
        return date.fromisoformat(calendar).timetuple().tm_yday
    except ValueError:
        return fallback


def summarise(subset: list[dict[str, Any]], year: int, scale: float) -> dict[str, Any]:
    """Pool valid NDVI pixels across composites into one annual summary."""
    raw: list[float] = []
    for composite in subset:
        for value in composite.get("data", []):
            if isinstance(value, (int, float)) and RAW_MIN <= value <= RAW_MAX:
                raw.append(float(value))

    base = {
        "product": PRODUCT,
        "band": BAND,
        "year": year,
        "n_composites": len(subset),
        "n_pixels": len(raw),
        "scale": scale,
    }
    if not raw:
        return {
            **base,
            "ndvi_mean": None,
            "ndvi_median": None,
            "ndvi_p10": None,
            "ndvi_p90": None,
            "ndvi_min": None,
            "ndvi_max": None,
        }

    values = np.asarray(raw, dtype="float64") * scale
    return {
        **base,
        "ndvi_mean": round(float(np.mean(values)), 4),
        "ndvi_median": round(float(np.median(values)), 4),
        "ndvi_p10": round(float(np.percentile(values, 10)), 4),
        "ndvi_p90": round(float(np.percentile(values, 90)), 4),
        "ndvi_min": round(float(np.min(values)), 4),
        "ndvi_max": round(float(np.max(values)), 4),
    }


def fetch_ndvi_summary(
    lat: float,
    lon: float,
    year: int = DEFAULT_YEAR,
    box_km: int = DEFAULT_BOX_KM,
    timeout: int = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Fetch one year of MOD13Q1 NDVI around a point and summarise it."""
    subset: list[dict[str, Any]] = []
    scale = 0.0001
    day = 1
    windows = 0
    while day <= 366 and windows < 6:
        end = min(day + (MAX_COMPOSITES_PER_REQUEST - 1) * COMPOSITE_DAYS - 1, 366)
        payload = _fetch_chunk(lat, lon, year, day, end, box_km, timeout)
        chunk = payload.get("subset") or []
        if not chunk:
            break
        if windows == 0:
            try:
                scale = float(payload.get("scale", scale))
            except (TypeError, ValueError):
                pass
        subset.extend(chunk)
        next_day = _last_composite_day(chunk, end) + 1
        if next_day <= day or next_day + COMPOSITE_DAYS > 366:
            break
        day = next_day
        windows += 1

    return summarise(subset, year, scale)


def _write_cache(cache_path: Path, cache: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def enrich_cells_with_ndvi(
    cells: list[dict[str, Any]],
    cache_path: Path,
    year: int = DEFAULT_YEAR,
    box_km: int = DEFAULT_BOX_KM,
    fetch: bool = True,
    force: bool = False,
    timeout: int = DEFAULT_TIMEOUT_S,
    workers: int = DEFAULT_WORKERS,
) -> list[dict[str, Any]]:
    """Attach MODIS NDVI means to cells, overwriting hand-typed placeholders.

    Per the project rule, a failed fetch sets vegetation_ndvi to None instead
    of keeping an unsourced number. Fetches run in parallel and the cache is
    written after each cell, so a timeout never discards completed work.
    """
    cache: dict[str, Any] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache = {}

    pending: list[dict[str, Any]] = []
    for cell in cells:
        entry = cache.get(cell["id"])
        usable = (
            not force
            and isinstance(entry, dict)
            and entry.get("ok")
            and entry.get("year") == year
            and entry.get("boxKm") == box_km
        )
        permanent_miss = (
            (entry or {}).get("permanent") and (entry or {}).get("year") == year
        )
        if not usable and fetch and not permanent_miss:
            pending.append(cell)

    fetched = 0
    failed = 0
    if pending:
        pool_size = max(1, min(workers, len(pending)))
        with ThreadPoolExecutor(max_workers=pool_size) as pool:
            futures = {
                pool.submit(
                    fetch_ndvi_summary,
                    cell["lat"],
                    cell["lon"],
                    year,
                    box_km,
                    timeout,
                ): cell
                for cell in pending
            }
            for future in as_completed(futures):
                cell = futures[future]
                cid = cell["id"]
                try:
                    summary = future.result()
                    cache[cid] = {
                        "ok": True,
                        "lat": cell["lat"],
                        "lon": cell["lon"],
                        "year": year,
                        "boxKm": box_km,
                        "summary": summary,
                        "source": f"ORNL DAAC {PRODUCT} subset API",
                        "fetchedAt": datetime.now(timezone.utc).isoformat(
                            timespec="seconds"
                        ),
                    }
                    fetched += 1
                    print(
                        f"  NDVI ok {cid}: mean={summary['ndvi_mean']} "
                        f"({summary['n_composites']} composites)"
                    )
                except Exception as exc:  # noqa: BLE001 — record any fetch failure
                    error_text = str(exc)
                    cache[cid] = {
                        "ok": False,
                        "lat": cell["lat"],
                        "lon": cell["lon"],
                        "year": year,
                        "error": error_text,
                        "permanent": "No data available" in error_text,
                    }
                    failed += 1
                    print(f"  NDVI fail {cid}: {exc}")
                _write_cache(cache_path, cache)

    for cell in cells:
        entry = cache.get(cell["id"])
        usable = (
            isinstance(entry, dict)
            and entry.get("ok")
            and entry.get("year") == year
            and entry.get("boxKm") == box_km
        )
        summary = ((entry or {}).get("summary") or {}) if usable else {}
        mean = summary.get("ndvi_mean")
        # Replace stubs; never fall back to an unsourced value.
        cell["features"]["vegetation_ndvi"] = mean
        if mean is not None:
            cell["ndviSource"] = (
                f"{PRODUCT} {BAND}, {year} annual mean in a "
                f"+/-{box_km} km box (ORNL DAAC)"
            )
            cell["ndviYear"] = year
        else:
            cell.pop("ndviSource", None)
            cell.pop("ndviYear", None)

    if not fetch and not cache:
        print("  WARNING: NDVI fetch disabled and no cache — vegetation stays null")

    _write_cache(cache_path, cache)
    print(f"  NDVI cache: {fetched} fetched, {failed} failed, {len(cache)} entries")
    return cells
