"""Load / write MarsTwin science profiles and web exports."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from .scoring import DIMENSION_KEYS

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
PROFILES = SCIENCE / "profiles"
CACHE = SCIENCE / "cache"
WEB_DATA = ROOT / "apps" / "web" / "public" / "data"

# Profiles owned by science — edited here, synced to the UI on pipeline run
PROFILE_JSON = ("targets.json", "usecases.json", "known_analogs.json")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_cells(path: Path | None = None) -> list[dict]:
    path = path or (PROFILES / "earth_cells.csv")
    cells = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = {}
            for key in DIMENSION_KEYS:
                raw = (row.get(key) or "").strip()
                features[key] = None if raw == "" else float(raw)
            cells.append(
                {
                    "id": row["id"],
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                    "cellDeg": float(row["cell_deg"]),
                    "regionHint": row.get("region_hint") or None,
                    "isKnownAnalog": row.get("is_known_analog", "").lower() == "true",
                    "knownAnalogId": row.get("known_analog_id") or None,
                    "features": features,
                    "tempKind": "air",
                }
            )
    return cells


def load_profiles() -> tuple[list[dict], list[dict], list[dict]]:
    """Return (usecases, targets, known_analogs) from science/profiles."""
    usecases = load_json(PROFILES / "usecases.json")
    targets = load_json(PROFILES / "targets.json")
    known = load_json(PROFILES / "known_analogs.json")
    return usecases, targets, known


def assert_target_contracts(targets: list[dict]) -> None:
    """Fail fast if saved targets violate locked null / cite rules."""
    by_id = {t["id"]: t for t in targets}
    moon = by_id.get("moon_spole_ref")
    mars = by_id.get("mars_jezero_ref")
    if moon is None or mars is None:
        raise SystemExit(
            "targets.json must include moon_spole_ref and mars_jezero_ref"
        )

    def val(t: dict, key: str):
        feat = t.get("features", {}).get(key) or {}
        return feat.get("value")

    # Slopes are null until the 20 m DEM script writes a value *with provenance*.
    # compute_slopes_20m.py --apply adds `computedFrom`; hand-typed slopes are rejected.
    for tid, dem_label in (
        ("moon_spole_ref", "LRO LOLA"),
        ("mars_jezero_ref", "USGS Jezero 20 m"),
    ):
        feature = by_id[tid].get("features", {}).get("slope_roughness") or {}
        value = feature.get("value")
        if value is None:
            continue
        if not feature.get("computedFrom"):
            raise SystemExit(
                f"{tid} slope_roughness must stay null until compute_slopes_20m.py "
                f"writes {dem_label} provenance (computedFrom)"
            )
        try:
            float(value)
        except (TypeError, ValueError):
            raise SystemExit(
                f"{tid} slope_roughness value is not numeric: {value!r}"
            )

    # Lunar mineralogy uncitable
    if val(moon, "mineralogy") is not None:
        raise SystemExit("moon mineralogy must stay null (no citable value)")

    # Moon diurnal left null (PSR ≠ Earth day/night fake ΔT)
    if val(moon, "diurnal_temp_range") is not None:
        raise SystemExit("moon diurnal_temp_range must stay null until a cited comparable exists")

    # Jezero MEDA air amplitude
    mars_dt = val(mars, "diurnal_temp_range")
    if mars_dt is None:
        raise SystemExit("mars_jezero_ref diurnal_temp_range must be set (MEDA air ~60 K)")

    print(
        f"Target contracts OK — nulls locked, slopes null-or-DEM-provenanced; "
        f"Jezero MEDA air dT={mars_dt} K @ {mars['lat']}, {mars['lon']}"
    )


def sync_profiles_to_web() -> None:
    """Copy science profiles into apps/web/public/data for the React app."""
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    for name in PROFILE_JSON:
        src = PROFILES / name
        dst = WEB_DATA / name
        shutil.copy2(src, dst)
        print(f"  synced {src.name} -> web public/data")
