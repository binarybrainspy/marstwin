"""
Compute mean slope (degrees) at a shared 20 m baseline for:
  - Earth AOIs (Copernicus DEM / SRTM)
  - Lunar south-polar patch (LRO LOLA)
  - Jezero (USGS 20 m elevation model)

Intentional: targets.slope_roughness stays null until this script writes real values.

Usage (after DEMs are downloaded locally):
  python science/scripts/compute_slopes_20m.py --earth-dem path.tif --aoi cell_atacama
  python science/scripts/compute_slopes_20m.py --jezero-dem usgs_jezero_20m.tif
  python science/scripts/compute_slopes_20m.py --lola-dem lola_spole.tif

Baseline rule: gradient over 20 m ground distance (same for all bodies).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "science" / "cache" / "slopes_20m.json"


def slope_deg_from_dz_dx(dz: float, dx_m: float = 20.0) -> float:
    return math.degrees(math.atan(abs(dz) / dx_m))


def main() -> None:
    parser = argparse.ArgumentParser(description="20 m baseline slope stats")
    parser.add_argument("--earth-dem", type=Path, help="GeoTIFF DEM for an Earth AOI")
    parser.add_argument("--jezero-dem", type=Path, help="USGS Jezero 20 m GeoTIFF")
    parser.add_argument("--lola-dem", type=Path, help="LOLA polar DEM GeoTIFF")
    parser.add_argument("--aoi", type=str, help="Earth cell id label for cache")
    args = parser.parse_args()

    if not any([args.earth_dem, args.jezero_dem, args.lola_dem]):
        print(
            "No DEM paths provided.\n"
            "Slopes remain null on purpose.\n"
            "Download DEMs, then re-run with --earth-dem / --jezero-dem / --lola-dem.\n"
            f"Results will be written to {OUT}"
        )
        print(
            "\nBaseline: 20 m. Formula: slope_deg = atan(|dz|/20) in degrees; "
            "report mean (and optionally P95) inside each AOI."
        )
        sys.exit(0)

    try:
        import numpy as np  # noqa: F401
        import rasterio
        from rasterio import features  # noqa: F401
    except ImportError:
        print("Install rasterio + numpy to compute slopes: pip install rasterio numpy")
        sys.exit(1)

    # Placeholder hook — full windowed gradient lands when DEMs are local.
    print(
        "DEM paths received. Implement windowed 20 m gradient next "
        "(rasterio.open → numpy gradient scaled to meters → mean slope deg)."
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "baseline_m": 20,
        "note": "Scaffold only — fill mean_slope_deg per site after DEM math lands",
        "sites": {},
    }
    if args.jezero_dem:
        payload["sites"]["mars_jezero_ref"] = {
            "dem": str(args.jezero_dem),
            "mean_slope_deg": None,
        }
    if args.lola_dem:
        payload["sites"]["moon_spole_ref"] = {
            "dem": str(args.lola_dem),
            "mean_slope_deg": None,
        }
    if args.earth_dem and args.aoi:
        payload["sites"][args.aoi] = {
            "dem": str(args.earth_dem),
            "mean_slope_deg": None,
        }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote scaffold {OUT}")


if __name__ == "__main__":
    main()
