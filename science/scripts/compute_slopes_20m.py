"""
Compute slope statistics at a shared 20 m baseline for:
  - Earth AOIs (Copernicus DEM / SRTM)
  - Lunar south-polar patch (LRO LOLA)
  - Jezero (USGS 20 m elevation model)

Rule (docs/DATA_SOURCES.md): one baseline for every body — 20 m.
Targets stay null until this script writes real values; --apply does that with provenance.

Slope method: Horn (1981) 3x3 finite difference on the DEM.
  dz/dx = ((z3 + 2*z6 + z9) - (z1 + 2*z4 + z7)) / (8 * dx)
  dz/dy = ((z7 + 2*z8 + z9) - (z1 + 2*z2 + z3)) / (8 * dy)
  slope = atan(hypot(dz/dx, dz/dy))

Baseline honesty:
  - DEM finer than 20 m  -> slope block-averaged to ~20 m support.
  - DEM ~20 m            -> used as-is.
  - DEM coarser than 20 m-> reported as `coarser_than_baseline`, never upsampled.
                            (A 30 m SRTM pixel cannot be made honest 20 m support.)

Usage (after downloading DEMs):
  python science/scripts/compute_slopes_20m.py \
      --earth-dem dems/srtm_atacama.tif --aoi cell_atacama

  python science/scripts/compute_slopes_20m.py --jezero-dem dems/jezero_20m.tif
  python science/scripts/compute_slopes_20m.py --lola-dem dems/lola_spole.tif

  # several Earth AOIs in one run (pairs match by order)
  python science/scripts/compute_slopes_20m.py \
      --earth-dem a.tif --aoi cell_a \
      --earth-dem b.tif --aoi cell_b

  # write mean slopes into science/profiles (targets.json + earth_cells.csv)
  python science/scripts/compute_slopes_20m.py --jezero-dem ... --apply
  python science/scripts/run_pipeline.py --skip-power

Requires: numpy + rasterio (pip install -r science/requirements.txt)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
PROFILES = SCIENCE / "profiles"
OUT = SCIENCE / "cache" / "slopes_20m.json"
TARGETS = PROFILES / "targets.json"
EARTH_CELLS = PROFILES / "earth_cells.csv"

DEFAULT_BASELINE_M = 20.0
SLOPE_THRESHOLDS_DEG = (10.0, 15.0, 20.0, 25.0)


# --------------------------------------------------------------------------- #
# DEM loading
# --------------------------------------------------------------------------- #

def _pixel_size_m(ds, transform, height: int) -> tuple[float, float]:
    """Pixel spacing in metres for the DEM window (handles geographic CRS)."""
    t = transform
    px_x = math.hypot(t.a, t.d)
    px_y = math.hypot(t.b, t.e)
    if px_x <= 0 or px_y <= 0:
        raise SystemExit("DEM transform has a zero pixel size — cannot compute slope")

    crs = ds.crs
    if crs is None or crs.is_projected:
        factor = 1.0
        if crs is not None:
            try:
                from pyproj import CRS

                factor = CRS.from_user_input(crs).linear_units_factor[1]
            except Exception:  # pyproj missing or unit-less CRS
                factor = 1.0
        return px_x * factor, px_y * factor

    # Geographic CRS: convert degrees to metres at the window's mid-latitude.
    mid_lat = t.f + t.e * (height / 2.0)
    mid_lat = max(-89.9, min(89.9, mid_lat))
    m_per_deg_lat = 110_540.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(mid_lat))
    return px_x * m_per_deg_lon, px_y * m_per_deg_lat


def load_dem(path: Path, max_pixels: int, bbox=None) -> tuple[object, float, float, dict]:
    """Read a DEM band as float64, mask nodata, return (z, dx, dy, meta).

    `bbox` is (min_lon, min_lat, max_lon, max_lat) in EPSG:4326 and is only used
    for Earth DEMs whose CRS differs from WGS84.
    """
    import numpy as np

    try:
        import rasterio
        from rasterio.windows import Window, from_bounds
    except ImportError:
        raise SystemExit(
            "rasterio is required: pip install -r science/requirements.txt"
        )

    with rasterio.open(path) as ds:
        if ds.count < 1:
            raise SystemExit(f"{path}: no raster bands")

        window = None
        if bbox is not None:
            bounds = bbox
            if ds.crs is not None and not ds.crs.is_geographic:
                try:
                    from rasterio.warp import transform_bounds

                    bounds = transform_bounds("EPSG:4326", ds.crs, *bbox)
                except Exception as exc:
                    raise SystemExit(f"{path}: could not transform AOI bbox: {exc}")
            window = (
                from_bounds(*bounds, transform=ds.transform)
                .round_offsets()
                .round_lengths()
            )
            window = window.intersection(Window(0, 0, ds.width, ds.height))
            if window.width < 3 or window.height < 3:
                raise SystemExit(
                    f"{path}: AOI window has <3 pixels — DEM does not cover the AOI"
                )

        z = ds.read(1, window=window).astype("float64") if window else ds.read(1).astype("float64")
        if z.size > max_pixels:
            raise SystemExit(
                f"{path}: {z.size:,} pixels exceeds --max-pixels {max_pixels:,}. "
                "Clip the DEM to the AOI first."
            )

        nodata = ds.nodata
        invalid = ~np.isfinite(z)
        if nodata is not None:
            invalid |= z == nodata
        scale = ds.scales[0] if ds.scales else 1.0
        offset = ds.offsets[0] if ds.offsets else 0.0
        if scale not in (None, 1.0) or offset not in (None, 0.0):
            z = z * (scale if scale is not None else 1.0) + (
                offset if offset is not None else 0.0
            )
        z[invalid] = float("nan")

        transform = ds.window_transform(window) if window else ds.transform
        height = int(window.height) if window else ds.height
        dx, dy = _pixel_size_m(ds, transform, height)
        meta = {
            "crs": str(ds.crs) if ds.crs else None,
            "width": int(window.width) if window else ds.width,
            "height": height,
            "nodata": nodata,
            "unit": (ds.units[0] if ds.units else None),
            "windowed": window is not None,
        }
    return z, dx, dy, meta



# --------------------------------------------------------------------------- #
# Slope math
# --------------------------------------------------------------------------- #

def horn_slope(z, dx: float, dy: float):
    """Horn 3x3 slope in degrees; NaN where the 3x3 neighbourhood is incomplete."""
    import numpy as np

    p = np.pad(z, 1, mode="constant", constant_values=np.nan)
    z1 = p[:-2, :-2]
    z2 = p[:-2, 1:-1]
    z3 = p[:-2, 2:]
    z4 = p[1:-1, :-2]
    z5 = p[1:-1, 1:-1]
    z6 = p[1:-1, 2:]
    z7 = p[2:, :-2]
    z8 = p[2:, 1:-1]
    z9 = p[2:, 2:]

    dzdx = ((z3 + 2.0 * z6 + z9) - (z1 + 2.0 * z4 + z7)) / (8.0 * dx)
    dzdy = ((z7 + 2.0 * z8 + z9) - (z1 + 2.0 * z2 + z3)) / (8.0 * dy)
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))

    valid = np.isfinite(z5)
    for neighbour in (z1, z2, z3, z4, z6, z7, z8, z9):
        valid &= np.isfinite(neighbour)
    slope[~valid] = np.nan
    return slope


def block_mean(arr, factor: int):
    """Non-overlapping factor×factor block mean, ignoring NaN (all-NaN -> NaN)."""
    import numpy as np

    h = (arr.shape[0] // factor) * factor
    w = (arr.shape[1] // factor) * factor
    if h == 0 or w == 0:
        return arr
    blocks = arr[:h, :w].reshape(h // factor, factor, w // factor, factor)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(blocks, axis=(1, 3))


def at_baseline(slope, native_m: float, baseline_m: float):
    """Aggregate slope to the baseline support. Returns (slope, analysis_m, status, factor)."""
    tolerance = baseline_m * 0.05
    if native_m > baseline_m + tolerance:
        return slope, native_m, "coarser_than_baseline", None
    if native_m >= baseline_m - tolerance:
        return slope, native_m, "matches", 1
    factor = max(1, int(round(baseline_m / native_m)))
    if factor <= 1:
        return slope, native_m, "matches", 1
    return block_mean(slope, factor), native_m * factor, "downsampled_from_finer", factor


def summarise_slope(slope) -> dict:
    import numpy as np

    flat = slope[np.isfinite(slope)]
    if flat.size == 0:
        return {
            "mean_slope_deg": None,
            "median_slope_deg": None,
            "p95_slope_deg": None,
            "max_slope_deg": None,
            "valid_fraction": 0.0,
            "thresholds": {},
        }
    pct = {
        f"pct_gt_{int(t)}deg": round(float(np.mean(flat > t) * 100.0), 1)
        for t in SLOPE_THRESHOLDS_DEG
    }
    return {
        "mean_slope_deg": round(float(np.mean(flat)), 2),
        "median_slope_deg": round(float(np.median(flat)), 2),
        "p95_slope_deg": round(float(np.percentile(flat, 95)), 2),
        "max_slope_deg": round(float(np.max(flat)), 2),
        "valid_fraction": round(float(flat.size / slope.size), 4),
        "thresholds": pct,
    }


def compute_site(
    site_id: str,
    body: str,
    path: Path,
    baseline_m: float,
    max_pixels: int,
    bbox=None,
) -> dict:
    z, dx, dy, meta = load_dem(path, max_pixels, bbox)
    native_m = max(dx, dy)
    native_slope = horn_slope(z, dx, dy)
    slope, analysis_m, status, factor = at_baseline(native_slope, native_m, baseline_m)
    stats = summarise_slope(slope)

    import numpy as np

    elevation = z[np.isfinite(z)]
    result = {
        "siteId": site_id,
        "body": body,
        "dem": str(path),
        "sourceCrs": meta["crs"],
        "native_resolution_m": round(native_m, 2),
        "analysis_resolution_m": round(analysis_m, 2),
        "baseline_m": baseline_m,
        "baselineStatus": status,
        "resampleFactor": factor,
        "elev_min_m": round(float(np.min(elevation)), 2) if elevation.size else None,
        "elev_max_m": round(float(np.max(elevation)), 2) if elevation.size else None,
        **stats,
    }
    if status == "coarser_than_baseline":
        result["warning"] = (
            f"DEM native spacing {native_m:.1f} m is coarser than the "
            f"{baseline_m:.0f} m baseline; slope is reported at native support "
            "and must not be described as 20 m."
        )
    return result


# --------------------------------------------------------------------------- #
# Write computed values into profiles
# --------------------------------------------------------------------------- #

def _slope_source(result: dict) -> str:
    dem = Path(result["dem"]).name
    return (
        f"Computed from {dem} — Horn 3x3 gradient, "
        f"{result['analysis_resolution_m']} m support ({result['baselineStatus']})"
    )


def apply_results(results: dict[str, dict]) -> None:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    changed_targets = []
    for target in targets:
        result = results.get(target["id"])
        if not result or result["mean_slope_deg"] is None:
            continue
        feature = target.setdefault("features", {}).setdefault("slope_roughness", {})
        feature["value"] = result["mean_slope_deg"]
        feature["unit"] = "deg"
        feature["source"] = _slope_source(result)
        feature["notes"] = (
            f"AOI mean slope {result['mean_slope_deg']}°; "
            f"P95 {result['p95_slope_deg']}°; "
            f"{result['thresholds'].get('pct_gt_15deg', '—')}% of valid pixels >15°. "
            "Shared 20 m baseline with Earth AOIs and Jezero."
        )
        feature["computedFrom"] = {
            "dem": Path(result["dem"]).name,
            "baseline_m": result["baseline_m"],
            "analysis_resolution_m": result["analysis_resolution_m"],
            "baselineStatus": result["baselineStatus"],
            "method": "Horn 1981 3x3 finite difference",
            "computedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        changed_targets.append(target["id"])
    if changed_targets:
        TARGETS.write_text(
            json.dumps(targets, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    with EARTH_CELLS.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    changed_cells = []
    for row in rows:
        result = results.get(row["id"])
        if not result or result["mean_slope_deg"] is None:
            continue
        row["slope_roughness"] = f"{result['mean_slope_deg']}"
        changed_cells.append(row["id"])
    if changed_cells:
        with EARTH_CELLS.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"  applied to targets.json: {', '.join(changed_targets) or '—'}")
    print(f"  applied to earth_cells.csv: {', '.join(changed_cells) or '—'}")
    if changed_targets or changed_cells:
        print("  next: python science/scripts/run_pipeline.py --skip-power")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _load_cell_bbox(radius_km: float) -> dict[str, tuple[float, float, float, float]]:
    """Build a lon/lat bbox around each Earth cell so big DEMs can be windowed."""
    boxes: dict[str, tuple[float, float, float, float]] = {}
    if not EARTH_CELLS.exists():
        return boxes
    with EARTH_CELLS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                lat = float(row["lat"])
                lon = float(row["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            dlat = radius_km / 110.54
            dlon = radius_km / (111.32 * max(0.01, math.cos(math.radians(lat))))
            boxes[row["id"]] = (lon - dlon, lat - dlat, lon + dlon, lat + dlat)
    return boxes


def _merged_cache() -> dict:
    if OUT.exists():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"baseline_m": DEFAULT_BASELINE_M, "sites": {}}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="20 m baseline slope statistics for Earth, Moon, and Mars DEMs"
    )
    parser.add_argument(
        "--earth-dem",
        type=Path,
        action="append",
        default=[],
        help="GeoTIFF DEM for an Earth AOI (repeat with --aoi)",
    )
    parser.add_argument(
        "--aoi",
        action="append",
        default=[],
        help="Earth cell id from earth_cells.csv (repeat, matched to --earth-dem order)",
    )
    parser.add_argument("--jezero-dem", type=Path, help="USGS Jezero 20 m GeoTIFF")
    parser.add_argument("--lola-dem", type=Path, help="LOLA polar DEM GeoTIFF")
    parser.add_argument(
        "--baseline",
        type=float,
        default=DEFAULT_BASELINE_M,
        help="Shared baseline in metres (default 20)",
    )
    parser.add_argument(
        "--aoi-radius-km",
        type=float,
        default=25.0,
        help="Radius around an Earth cell centre used to window a large DEM (default 25 km)",
    )
    parser.add_argument(
        "--max-pixels",
        type=int,
        default=40_000_000,
        help="Refuse DEMs larger than this many pixels (default 40M)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write computed means into targets.json and earth_cells.csv",
    )
    args = parser.parse_args()

    if not (args.earth_dem or args.jezero_dem or args.lola_dem):
        print(
            "No DEM paths provided — slopes stay null on purpose.\n"
            "Download DEMs first, then pass --earth-dem / --jezero-dem / --lola-dem.\n"
            "Method: Horn 3x3 gradient in degrees; baseline 20 m for every body."
        )
        print(f"\nOutput would be written to {OUT}")
        return

    if len(args.earth_dem) != len(args.aoi):
        raise SystemExit(
            f"--earth-dem ({len(args.earth_dem)}) and --aoi ({len(args.aoi)}) "
            "must be given the same number of times, in matching order"
        )

    jobs: list[tuple[str, str, Path, tuple[float, float, float, float] | None]] = [
        (aoi, "earth", dem, None) for dem, aoi in zip(args.earth_dem, args.aoi)
    ]
    if args.jezero_dem:
        jobs.append(("mars_jezero_ref", "mars", args.jezero_dem, None))
    if args.lola_dem:
        jobs.append(("moon_spole_ref", "moon", args.lola_dem, None))

    # Window large Earth DEMs around the AOI centre instead of reading the whole raster.
    cell_boxes = _load_cell_bbox(args.aoi_radius_km)
    jobs = [
        (site, body, path, cell_boxes.get(site))
        for site, body, path, box in jobs
    ]

    for _, _, path, _ in jobs:
        if not path.exists():
            raise SystemExit(f"DEM not found: {path}")

    results: dict[str, dict] = {}
    for site_id, body, path, bbox in jobs:
        print(f"Computing {body} slope: {site_id} <- {path.name}")
        result = compute_site(
            site_id, body, path, args.baseline, args.max_pixels, bbox
        )
        results[site_id] = result
        print(
            f"  native {result['native_resolution_m']} m · "
            f"analysis {result['analysis_resolution_m']} m ({result['baselineStatus']}) · "
            f"mean {result['mean_slope_deg']}° · P95 {result['p95_slope_deg']}°"
        )
        if "warning" in result:
            print(f"  WARNING: {result['warning']}")

    cache = _merged_cache()
    cache["baseline_m"] = args.baseline
    cache["method"] = "Horn 1981 3x3 finite difference; block-averaged to baseline when finer"
    cache["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cache.setdefault("sites", {}).update(results)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}")

    if args.apply:
        apply_results(results)


if __name__ == "__main__":
    main()
