"""
MarsTwin coarse pipeline — enrich Earth cells, score vs Moon/Mars, validate, export JSON.

Usage (from repo root):
  python science/scripts/run_pipeline.py
  python science/scripts/run_pipeline.py --skip-power   # offline: cache / CSV only
  python science/scripts/run_pipeline.py --force-power  # refetch POWER
  python science/scripts/run_pipeline.py --force-ndvi   # refetch MODIS NDVI
  python science/scripts/run_pipeline.py --skip-ndvi    # keep cached NDVI only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
WEB_DATA = ROOT / "apps" / "web" / "public" / "data"
CACHE = SCIENCE / "cache" / "power_climatology.json"
NDVI_CACHE = SCIENCE / "cache" / "modis_ndvi.json"
sys.path.insert(0, str(SCIENCE))

from lib.io_util import (  # noqa: E402
    assert_target_contracts,
    load_cells,
    load_profiles,
    sync_profiles_to_web,
)
from lib.manifest import build_manifest  # noqa: E402
from lib.ndvi import DEFAULT_YEAR as NDVI_DEFAULT_YEAR, enrich_cells_with_ndvi  # noqa: E402
from lib.power import enrich_cells_with_power  # noqa: E402
from lib.scoring import (  # noqa: E402
    extract_target_values,
    rank_results,
    score_cell,
    validate_known,
)

MARS_TARGET_ID = "mars_jezero_ref"
MOON_TARGET_ID = "moon_spole_ref"

CARD_STORIES = {
    "cell_w_desert_egypt": {
        "headline": "Sand, swing, and open sightlines",
        "story": (
            "Egypt's Western Desert pairs dune seas with gravel plains and almost "
            "no vegetation. The result is a clean, open test surface with a strong "
            "day-night air swing for thermal rehearsals."
        ),
    },
    "cell_taklamakan": {
        "headline": "A cold desert stress test",
        "story": (
            "The Taklamakan sits in a mountain-ringed basin, with migrating dunes "
            "and dust that punish seals, bearings and optics. Its aridity and "
            "temperature swing make it a useful worst-case site."
        ),
    },
}


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
            "id": "g_ndvi_scale",
            "category": "scale",
            "title": "Vegetation sample scale",
            "detail": (
                "NDVI is a MODIS 250 m point sample in a ~2 km box at the cell centre, "
                "not a 0.5° area mean. Bare cover within the cell can differ from the sample."
            ),
            "severity": "manageable",
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
        ndvi = cell["features"].get("vegetation_ndvi")
        dt = cell["features"].get("diurnal_temp_range")
        story = CARD_STORIES.get(
            cell["id"],
            {
                "headline": "A dry, high-swing test surface",
                "story": (
                    "Low vegetation and a wide day-night temperature swing put "
                    "this site near the top of the screen."
                ),
            },
        )
        transfers = []
        if ndvi is not None:
            transfers.append(
                f"Almost no vegetation (MODIS NDVI {ndvi:.3f}) — wheels meet "
                "soil and rock rather than root mat"
            )
        else:
            transfers.append(
                "Vegetation unknown — MODIS has no coverage here, so the "
                "screen leaves it out instead of guessing"
            )
        if dt is not None:
            transfers.append(
                f"{dt:.0f} K day–night air swing (NASA POWER) for "
                "thermal-cycling practice"
            )
        else:
            transfers.append("Air-temperature swing still unknown for this cell")
        if slope is not None:
            transfers.append(
                "Slope stats at the shared 20 m baseline for traverse rehearsal"
            )
        else:
            transfers.append(
                "Slope still unknown — it will use the same 20 m baseline as "
                "Jezero and the lunar poles"
            )

        cards.append(
            {
                "siteId": cell["id"],
                "name": name,
                "lat": cell["lat"],
                "lon": cell["lon"],
                "targetIds": [target_id],
                "useCaseId": use_case["id"],
                "rank": r["rank"],
                "composite": r["composite"],
                "headline": story["headline"],
                "story": story["story"],
                "transfers": transfers,
                "breaks": [
                    "Earth's gravity and thick atmosphere do not transfer",
                    "Light and radiation are planetary, not terrestrial",
                    "Mineralogy is blank until a citable site value exists",
                    "Air temperature here is not the same as ground temperature",
                ],
                "tests": [
                    "Run a full thermal soak through a site day–night cycle",
                    "Drive a wheel–soil test once 20 m slopes are filled",
                    "Rehearse a timed rover shift under thermal stress",
                ],
                "scaleNotes": (
                    f"Screen cell ~{cell['cellDeg']}°. "
                    "Vegetation: MODIS 250 m point sample. "
                    "Slopes: pending shared 20 m baseline. "
                    "Temperature: air, NASA POWER."
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
                "earthSource": (
                    "DEM slope at 20 m baseline (SRTM/Copernicus) via "
                    "compute_slopes_20m.py; null until computed"
                ),
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
                "earthSource": (
                    "MODIS MOD13Q1 250 m 16-day NDVI — annual mean in a ~2 km box "
                    "around the cell centre (ORNL DAAC subset API)"
                ),
                "targetSource": "0 barren target",
                "transform": "similarity = 1 - clip(|e-t|/0.6, 0, 1); null when the fetch fails",
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
            "NDVI is a MODIS 250 m point sample (~2 km box), not a 0.5° area mean; null when fetch fails",
            "Composite is secondary; fingerprint + gap report are primary",
        ],
    }


def main() -> None:
    # Windows consoles default to cp1252; keep Unicode output (Δ, →) from crashing.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="MarsTwin coarse pipeline")
    parser.add_argument("--skip-power", action="store_true", help="Do not call POWER API")
    parser.add_argument("--force-power", action="store_true", help="Refetch POWER even if cached")
    parser.add_argument(
        "--skip-ndvi",
        action="store_true",
        help="Do not call the ORNL MODIS NDVI API (use cached values only)",
    )
    parser.add_argument(
        "--force-ndvi",
        action="store_true",
        help="Refetch MODIS NDVI even if cached",
    )
    parser.add_argument(
        "--ndvi-year",
        type=int,
        default=NDVI_DEFAULT_YEAR,
        help=f"MODIS NDVI year to sample (default {NDVI_DEFAULT_YEAR})",
    )
    args = parser.parse_args()

    use_cases, targets, known = load_profiles()
    assert_target_contracts(targets)
    sync_profiles_to_web()
    cells = load_cells()
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

    ndvi_fetch = not (args.skip_ndvi or args.skip_power)
    print("Enriching cells with MODIS NDVI (MOD13Q1, 250 m, ORNL DAAC)…")
    cells = enrich_cells_with_ndvi(
        cells,
        NDVI_CACHE,
        year=args.ndvi_year,
        fetch=ndvi_fetch,
        force=args.force_ndvi and ndvi_fetch,
    )

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

    manifest = build_manifest(
        cells=cells,
        targets=targets,
        known_analogs=known,
        validation=validations,
        candidates=candidates,
        ndvi_year=args.ndvi_year,
        ndvi_box_km=1,
    )

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
    (WEB_DATA / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"Wrote {WEB_DATA / 'coarse_results.json'}")
    print(f"Wrote {WEB_DATA / 'candidates.json'} ({len(candidates)} cards)")
    print(f"Wrote {WEB_DATA / 'method.json'}")
    print(f"Wrote {WEB_DATA / 'manifest.json'} (v{manifest['pipelineVersion']})")
    for v in validations:
        print(
            f"  validation {v['targetId']}: passed={v['passed']} "
            f"ranks={[h['analogId'] + ':' + str(h['rank']) for h in v['knownAnalogsInTop']]}"
        )


if __name__ == "__main__":
    main()
