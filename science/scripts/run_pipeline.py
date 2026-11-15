"""
MarsTwin coarse pipeline — enrich Earth cells, score vs Moon/Mars, validate, export JSON.

Usage (from repo root):
  python science/scripts/run_pipeline.py
  python science/scripts/run_pipeline.py --skip-power   # use cache / CSV only
  python science/scripts/run_pipeline.py --force-power  # refetch POWER
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
WEB_DATA = ROOT / "apps" / "web" / "public" / "data"
CACHE = SCIENCE / "cache" / "power_climatology.json"
sys.path.insert(0, str(SCIENCE))

from lib.power import enrich_cells_with_power  # noqa: E402
from lib.scoring import (  # noqa: E402
    DIMENSION_KEYS,
    extract_target_values,
    rank_results,
    score_cell,
    validate_known,
)

MARS_TARGET_ID = "mars_jezero_ref"
MOON_TARGET_ID = "moon_spole_ref"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_cells(path: Path) -> list[dict]:
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


def default_gaps(for_moon: bool) -> list[dict]:
    gaps = [
        {
            "id": "g_gravity",
            "category": "gravity",
            "title": "Gravity mismatch",
            "detail": "Earth 1 g vs Moon ~1/6 g / Mars ~0.38 g — loads and sinkage do not scale 1:1.",
            "severity": "hard_limit",
        },
        {
            "id": "g_atmo",
            "category": "atmosphere_vacuum",
            "title": "Atmosphere / vacuum",
            "detail": "Convective cooling and pressure effects on Earth invalidate vacuum thermal behavior.",
            "severity": "hard_limit",
        },
        {
            "id": "g_rad",
            "category": "radiation",
            "title": "Radiation environment",
            "detail": "Earth magnetosphere and atmosphere shield radiation; planetary surface dose does not transfer.",
            "severity": "hard_limit",
        },
        {
            "id": "g_temp_kind",
            "category": "other",
            "title": "Air vs ground temperature",
            "detail": (
                "Jezero MEDA diurnal amplitude used here is air (~60 K at 1.45 m). "
                "Earth POWER uses T2M air — compare air↔air. MODIS LST is ground and must not be mixed unlabeled."
            ),
            "severity": "partial",
        },
        {
            "id": "g_bio",
            "category": "biosphere",
            "title": "Biosphere / contamination",
            "detail": "Earth biology and planetary protection constraints are unique to terrestrial tests.",
            "severity": "partial",
        },
    ]
    if for_moon:
        gaps.insert(
            3,
            {
                "id": "g_psr_cold",
                "category": "temporal",
                "title": "PSR cold-trap temperatures",
                "detail": (
                    "Diviner-class permanently shadowed regions reach ~40 K. "
                    "No Earth surface reaches that regime — thermal analogy for shadowed lunar ops is a hard gap."
                ),
                "severity": "hard_limit",
            },
        )
    return gaps


def build_candidates(
    ranked: list[dict],
    cells_by_id: dict[str, dict],
    use_case: dict,
    target_id: str,
    limit: int = 2,
) -> list[dict]:
    for_moon = target_id == MOON_TARGET_ID
    cards = []
    for r in ranked:
        cell = cells_by_id[r["cellId"]]
        if cell.get("isKnownAnalog"):
            continue
        name = cell.get("regionHint") or cell["id"]
        slope = cell["features"].get("slope_roughness")
        transfers = [
            "Low vegetation / arid surface for mobility and dust-adjacent checkout",
            "Air-temperature diurnal swing from NASA POWER for thermal-cycling rehearsal (air↔air vs MEDA)",
        ]
        if slope is not None:
            transfers.insert(
                0, "Slope stats at shared 20 m baseline suitable for traverse rehearsal"
            )
        else:
            transfers.append(
                "Slope pending — will use same 20 m DEM baseline as Jezero USGS + lunar LOLA"
            )

        cards.append(
            {
                "siteId": cell["id"],
                "name": name,
                "lat": cell["lat"],
                "lon": cell["lon"],
                "targetIds": [target_id],
                "useCaseId": use_case["id"],
                "transfers": transfers,
                "breaks": [
                    "Earth gravity and atmosphere do not transfer",
                    "Illumination / radiation environment is not planetary",
                    "Lunar mineralogy left uncitable — zero-weighted / null",
                    "Do not treat POWER air ΔT as MODIS land-surface ΔT",
                ],
                "tests": [
                    "Instrument thermal soak / diurnal cycle checkout (air-side matched)",
                    "Wheel–soil interaction once 20 m slopes are filled",
                    "Ops rehearsal: timed rover shift under thermal stress",
                ],
                "scaleNotes": (
                    f"Coarse cell ~{cell['cellDeg']}°. "
                    "Slopes: null until LOLA / USGS Jezero / Earth DEM at 20 m baseline. "
                    "Thermal: NASA POWER T2M air climatology."
                ),
                "fingerprint": r["dimensions"],
                "gaps": default_gaps(for_moon=for_moon),
            }
        )
        if len(cards) >= limit:
            break
    return cards


def method_doc() -> dict:
    return {
        "coarseResolutionDeg": 0.5,
        "fineResolutionM": 20,
        "dimensions": [
            {
                "key": "slope_roughness",
                "earthSource": "Pending DEM slope at 20 m baseline (SRTM/Copernicus)",
                "targetSource": "LOLA polar DEM + USGS Jezero 20 m — compute, do not invent",
                "transform": "similarity = 1 - clip(|e-t|/20°, 0, 1); null until computed",
            },
            {
                "key": "diurnal_temp_range",
                "earthSource": "NASA POWER T2M_MAX − T2M_MIN (air, 2 m climatology)",
                "targetSource": "MEDA air ~60 K at Jezero; Moon diurnal left null (PSR ≠ Earth day/night)",
                "transform": "similarity = 1 - clip(|e-t|/120 K, 0, 1); air↔air only",
            },
            {
                "key": "precipitation",
                "earthSource": "NASA POWER PRECTOTCORR (mm/yr)",
                "targetSource": "0 for vacuum / Mars (no rain)",
                "transform": "similarity = 1 - clip(|e-t|/500 mm, 0, 1)",
            },
            {
                "key": "vegetation_ndvi",
                "earthSource": "Manual/NDVI stub → GIBS/MODIS NDVI next",
                "targetSource": "0 barren target",
                "transform": "similarity = 1 - clip(|e-t|/0.6, 0, 1)",
            },
            {
                "key": "mineralogy",
                "earthSource": "EMIT planned",
                "targetSource": "Null (no citable lunar site mineralogy); Mars pending CRISM",
                "transform": "Excluded while null; use-case weight = 0",
            },
            {
                "key": "ice_permafrost",
                "earthSource": "Proxy (Odyssey-informed later)",
                "targetSource": "High near lunar PSR; low at Jezero",
                "transform": "similarity = 1 - clip(|e-t|/0.8, 0, 1)",
            },
        ],
        "exclusions": [
            "Atacama Desert",
            "McMurdo Dry Valleys",
            "Iceland volcanic terrains",
            "Hawaiʻi volcanic fields",
        ],
        "limitations": [
            "Slopes intentionally null until 20 m DEM script (Earth + LOLA + USGS Jezero)",
            "Moon diurnal ΔT left null — PSR ~40 K floor is a gap, not a fake score",
            "Mineralogy zero-weighted until citable",
            "Temperature path is air↔air (POWER vs MEDA); MODIS LST is a separate track",
            "NDVI still stub values — wire GIBS/MODIS next",
            "Composite is secondary; fingerprint + gap report are primary",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MarsTwin coarse pipeline")
    parser.add_argument("--skip-power", action="store_true", help="Do not call POWER API")
    parser.add_argument("--force-power", action="store_true", help="Refetch POWER even if cached")
    args = parser.parse_args()

    use_cases = load_json(WEB_DATA / "usecases.json")
    targets = load_json(WEB_DATA / "targets.json")
    known = load_json(WEB_DATA / "known_analogs.json")
    cells = load_cells(SCIENCE / "profiles" / "earth_cells.csv")
    use_case = use_cases[0]

    if not args.skip_power:
        print("Enriching cells with NASA POWER climatology (air T2M + precip)…")
        cells = enrich_cells_with_power(
            cells, CACHE, force=args.force_power
        )
    elif CACHE.exists():
        print("Applying cached POWER values only…")
        cells = enrich_cells_with_power(cells, CACHE, force=False)
    else:
        print("WARNING: no POWER cache and --skip-power set; precip/ΔT may be null")

    cells_by_id = {c["id"]: c for c in cells}

    all_results: list[dict] = []
    validations: list[dict] = []

    for target in targets:
        tvals = extract_target_values(target)
        batch = []
        for cell in cells:
            dims, composite = score_cell(cell["features"], tvals, use_case["weights"])
            batch.append(
                {
                    "cellId": cell["id"],
                    "targetId": target["id"],
                    "useCaseId": use_case["id"],
                    "dimensions": dims,
                    "composite": composite,
                }
            )
        ranked = rank_results(batch)
        all_results.extend(ranked)
        validations.append(
            validate_known(
                ranked,
                cells_by_id,
                known,
                use_case["id"],
                target["id"],
                top_fraction=0.5,
            )
        )

    mars_ranked = sorted(
        [r for r in all_results if r["targetId"] == MARS_TARGET_ID],
        key=lambda r: r["rank"],
    )
    candidates = build_candidates(
        mars_ranked, cells_by_id, use_case, MARS_TARGET_ID, limit=2
    )

    coarse = {
        "cells": [
            {
                "id": c["id"],
                "lat": c["lat"],
                "lon": c["lon"],
                "cellDeg": c["cellDeg"],
                "features": c["features"],
                "regionHint": c.get("regionHint"),
                "isKnownAnalog": c.get("isKnownAnalog", False),
                "knownAnalogId": c.get("knownAnalogId"),
                "tempKind": c.get("tempKind", "air"),
            }
            for c in cells
        ],
        "results": all_results,
        "validation": validations,
    }

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "coarse_results.json").write_text(
        json.dumps(coarse, indent=2), encoding="utf-8"
    )
    (WEB_DATA / "candidates.json").write_text(
        json.dumps(candidates, indent=2), encoding="utf-8"
    )
    (WEB_DATA / "method.json").write_text(
        json.dumps(method_doc(), indent=2), encoding="utf-8"
    )

    print(f"Wrote {WEB_DATA / 'coarse_results.json'}")
    print(f"Wrote {WEB_DATA / 'candidates.json'} ({len(candidates)} cards)")
    print(f"Wrote {WEB_DATA / 'method.json'}")
    for v in validations:
        print(
            f"  validation {v['targetId']}: passed={v['passed']} "
            f"ranks={[h['analogId'] + ':' + str(h['rank']) for h in v['knownAnalogsInTop']]}"
        )


if __name__ == "__main__":
    main()
