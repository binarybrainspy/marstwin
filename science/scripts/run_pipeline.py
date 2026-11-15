"""
MarsTwin coarse pipeline — score Earth cells vs Moon/Mars targets, validate, export JSON.

Usage (from repo root):
  python science/scripts/run_pipeline.py

Reads:
  science/profiles/earth_cells.csv
  apps/web/public/data/usecases.json
  apps/web/public/data/targets.json
  apps/web/public/data/known_analogs.json

Writes:
  apps/web/public/data/coarse_results.json
  apps/web/public/data/candidates.json  (non-famous top sites for mars_arid_ref by default)
  apps/web/public/data/method.json
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
WEB_DATA = ROOT / "apps" / "web" / "public" / "data"
sys.path.insert(0, str(SCIENCE))

from lib.scoring import (  # noqa: E402
    DIMENSION_KEYS,
    extract_target_values,
    rank_results,
    score_cell,
    validate_known,
)


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
                raw = row.get(key, "").strip()
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
                }
            )
    return cells


def build_candidates(
    ranked: list[dict],
    cells_by_id: dict[str, dict],
    use_case: dict,
    target_id: str,
    limit: int = 2,
) -> list[dict]:
    """Top non-famous cells become analogy-card stubs for the UI."""
    cards = []
    for r in ranked:
        cell = cells_by_id[r["cellId"]]
        if cell.get("isKnownAnalog"):
            continue
        name = cell.get("regionHint") or cell["id"]
        cards.append(
            {
                "siteId": cell["id"],
                "name": name,
                "lat": cell["lat"],
                "lon": cell["lon"],
                "targetIds": [target_id],
                "useCaseId": use_case["id"],
                "transfers": [
                    "High diurnal thermal swing useful for thermal-cycling rehearsal",
                    "Low vegetation / arid surface for mobility and dust-adjacent checkout",
                    "Moderate slopes suitable for traversable test traverses",
                ],
                "breaks": [
                    "Earth gravity and atmosphere do not transfer",
                    "Illumination / radiation environment is not planetary",
                    "Mineralogy proxy is coarse — refine with EMIT where available",
                ],
                "tests": [
                    "Instrument thermal soak / diurnal cycle checkout",
                    "Wheel–soil interaction and slope climb on arid regolith analog",
                    "Ops rehearsal: timed EVA/rover shift under thermal stress",
                ],
                "scaleNotes": (
                    f"Coarse cell ~{cell['cellDeg']}°. "
                    "Fine refine: local DEM slope stats + MODIS ΔT + POWER precip (Day 2)."
                ),
                "fingerprint": r["dimensions"],
                "gaps": [
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
                        "id": "g_bio",
                        "category": "biosphere",
                        "title": "Biosphere / contamination",
                        "detail": "Earth biology and planetary protection constraints are unique to terrestrial tests.",
                        "severity": "partial",
                    },
                ],
            }
        )
        if len(cards) >= limit:
            break
    return cards


def method_doc() -> dict:
    return {
        "coarseResolutionDeg": 0.5,
        "fineResolutionM": None,
        "dimensions": [
            {
                "key": "slope_roughness",
                "earthSource": "SRTM/ASTER-derived slope (fixture CSV for now)",
                "targetSource": "LOLA / MOLA literature placeholders",
                "transform": "similarity = 1 - clip(|e-t|/20°, 0, 1)",
            },
            {
                "key": "diurnal_temp_range",
                "earthSource": "MODIS / POWER-style ΔT (fixture)",
                "targetSource": "Diviner / THEMIS placeholders",
                "transform": "similarity = 1 - clip(|e-t|/120 K, 0, 1)",
            },
            {
                "key": "precipitation",
                "earthSource": "NASA POWER / climate normals (fixture)",
                "targetSource": "0 for vacuum/arid Mars ref",
                "transform": "similarity = 1 - clip(|e-t|/500 mm, 0, 1)",
            },
            {
                "key": "vegetation_ndvi",
                "earthSource": "NDVI (fixture)",
                "targetSource": "0 barren target",
                "transform": "similarity = 1 - clip(|e-t|/0.6, 0, 1)",
            },
            {
                "key": "mineralogy",
                "earthSource": "Proxy 0-1 (EMIT later)",
                "targetSource": "Composition affinity proxy",
                "transform": "similarity = 1 - clip(|e-t|/0.8, 0, 1)",
            },
            {
                "key": "ice_permafrost",
                "earthSource": "Proxy 0-1 (fixture)",
                "targetSource": "Ice relevance proxy",
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
            "Fixture cell set is tiny — replace with coarse global/arid-mask grid when Resources unlock",
            "Target feature values need official citations from challenge Resources",
            "Mineralogy and ice are proxies until EMIT / neutron products are wired",
            "Composite score is secondary; per-dimension fingerprint is primary",
        ],
    }


def main() -> None:
    use_cases = load_json(WEB_DATA / "usecases.json")
    targets = load_json(WEB_DATA / "targets.json")
    known = load_json(WEB_DATA / "known_analogs.json")
    cells = load_cells(SCIENCE / "profiles" / "earth_cells.csv")
    cells_by_id = {c["id"]: c for c in cells}
    use_case = use_cases[0]

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

    # Candidates from Mars arid ranking (hardware-test narrative default)
    mars_ranked = [r for r in all_results if r["targetId"] == "mars_arid_ref"]
    mars_ranked = sorted(mars_ranked, key=lambda r: r["rank"])
    candidates = build_candidates(
        mars_ranked, cells_by_id, use_case, "mars_arid_ref", limit=2
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
            f"ranks={[h['analogId']+':'+str(h['rank']) for h in v['knownAnalogsInTop']]}"
        )


if __name__ == "__main__":
    main()
