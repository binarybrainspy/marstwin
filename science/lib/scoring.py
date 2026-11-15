"""Similarity scoring for MarsTwin — six dimensions, use-case weights."""

from __future__ import annotations

from typing import Any

DIMENSION_KEYS = [
    "slope_roughness",
    "diurnal_temp_range",
    "precipitation",
    "vegetation_ndvi",
    "mineralogy",
    "ice_permafrost",
]

# Physically motivated scales for |earth - target| → similarity
# similarity = 1 - clip(|e - t| / scale, 0, 1)
SCALES: dict[str, float] = {
    "slope_roughness": 20.0,  # degrees
    "diurnal_temp_range": 120.0,  # K
    "precipitation": 500.0,  # mm/yr (aridity-sensitive)
    "vegetation_ndvi": 0.6,  # index
    "mineralogy": 0.8,  # proxy 0-1
    "ice_permafrost": 0.8,  # proxy 0-1
}


def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def dim_similarity(earth: float | None, target: float | None, key: str) -> float | None:
    if earth is None or target is None:
        return None
    scale = SCALES[key]
    return 1.0 - clip01(abs(float(earth) - float(target)) / scale)


def score_cell(
    earth_features: dict[str, float | None],
    target_features: dict[str, float | None],
    weights: dict[str, float],
) -> tuple[list[dict[str, Any]], float | None]:
    dimensions: list[dict[str, Any]] = []
    num = 0.0
    den = 0.0

    for key in DIMENSION_KEYS:
        e = earth_features.get(key)
        t = target_features.get(key)
        sim = dim_similarity(e, t, key)
        dimensions.append(
            {
                "key": key,
                "similarity": None if sim is None else round(sim, 4),
                "earthValue": None if e is None else float(e),
                "targetValue": None if t is None else float(t),
            }
        )
        if sim is not None:
            w = float(weights.get(key, 0.0))
            if w > 0:
                num += w * sim
                den += w

    composite = None if den == 0 else round(num / den, 4)
    return dimensions, composite


def extract_target_values(target: dict[str, Any]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    feats = target.get("features", {})
    for key in DIMENSION_KEYS:
        cited = feats.get(key)
        if cited is None:
            out[key] = None
        else:
            out[key] = cited.get("value")
    return out


def rank_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        results,
        key=lambda r: (r["composite"] is None, -(r["composite"] or 0.0)),
    )
    for i, r in enumerate(ranked, start=1):
        r["rank"] = i
    return ranked


def validate_known(
    ranked: list[dict[str, Any]],
    cells_by_id: dict[str, dict[str, Any]],
    known_analogs: list[dict[str, Any]],
    use_case_id: str,
    target_id: str,
    top_fraction: float = 0.5,
) -> dict[str, Any]:
    """With a small demo cell set, top_fraction=0.5 is lenient; tighten when grid grows."""
    n = len(ranked)
    cutoff = max(1, int(n * top_fraction))
    top_ids = {r["cellId"] for r in ranked[:cutoff]}

    hits = []
    for analog in known_analogs:
        cell_id = analog.get("cellId")
        if not cell_id:
            continue
        match = next((r for r in ranked if r["cellId"] == cell_id), None)
        if match is None:
            continue
        hits.append(
            {
                "analogId": analog["id"],
                "rank": match["rank"],
                "composite": match["composite"],
            }
        )

    in_top = [h for h in hits if ranked[h["rank"] - 1]["cellId"] in top_ids]
    best_rank = min((h["rank"] for h in hits), default=999)
    # Hardware-test narrative: at least one famous analog must land in top 3.
    # Not all famous sites should match every target (e.g. Dry Valleys vs arid Mars).
    passed = best_rank <= 3

    return {
        "useCaseId": use_case_id,
        "targetId": target_id,
        "topFraction": top_fraction,
        "knownAnalogsInTop": sorted(hits, key=lambda h: h["rank"]),
        "passed": passed,
        "notes": (
            f"Best known-analog rank={best_rank}; "
            f"{len(in_top)}/{len(hits)} in top {top_fraction:.0%} (n={n}). "
            "Pass rule: ≥1 known analog in top 3."
        ),
    }
