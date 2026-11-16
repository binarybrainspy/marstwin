"""Build the manifest that tells the frontend what data it is looking at."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PIPELINE_VERSION = "0.6.0"
SCHEMA_VERSION = 1


def build_manifest(
    *,
    cells: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    known_analogs: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    ndvi_year: int,
    ndvi_box_km: int,
    generated_at: str | None = None,
) -> dict[str, Any]:
    ndvi_present = [
        c["id"] for c in cells if c["features"].get("vegetation_ndvi") is not None
    ]
    ndvi_missing = [
        c["id"] for c in cells if c["features"].get("vegetation_ndvi") is None
    ]
    slope_present = [
        c["id"] for c in cells if c["features"].get("slope_roughness") is not None
    ]
    best_ranks = {
        v["targetId"]: min(
            (h["rank"] for h in v.get("knownAnalogsInTop", [])), default=None
        )
        for v in validation
    }

    return {
        "schemaVersion": SCHEMA_VERSION,
        "pipelineVersion": PIPELINE_VERSION,
        "generatedAt": generated_at
        or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "cells": len(cells),
            "targets": len(targets),
            "knownAnalogs": len(known_analogs),
            "candidates": len(candidates),
            "ndviWithData": len(ndvi_present),
            "ndviMissing": len(ndvi_missing),
            "slopesComputed": len(slope_present),
        },
        "ndvi": {
            "product": "MODIS MOD13Q1",
            "band": "250m_16_days_NDVI",
            "year": ndvi_year,
            "boxKm": ndvi_box_km,
            "sampling": (
                "Annual mean of 16-day composites in a point sample around the "
                "cell centre; not a 0.5 degree area mean."
            ),
            "cellsWithData": ndvi_present,
            "cellsMissing": ndvi_missing,
        },
        "slope": {
            "baselineM": 20,
            "method": "Horn 3x3 gradient; finer DEMs block-averaged to 20 m",
            "status": "pending" if not slope_present else "computed",
            "cellsComputed": slope_present,
        },
        "targets": [
            {"id": t["id"], "name": t["name"], "body": t["body"]} for t in targets
        ],
        "validation": [
            {
                "targetId": v["targetId"],
                "passed": v["passed"],
                "notes": v["notes"],
                "bestKnownAnalogRank": best_ranks.get(v["targetId"]),
            }
            for v in validation
        ],
        "sources": [
            {
                "id": "power",
                "name": "NASA POWER",
                "role": "Air temperature and precipitation climatology",
                "url": "https://power.larc.nasa.gov/",
            },
            {
                "id": "modis-ndvi",
                "name": "NASA ORNL DAAC MODIS MOD13Q1",
                "role": "250 m, 16-day vegetation index",
                "url": "https://modis.ornl.gov/",
            },
            {
                "id": "meda",
                "name": "NASA Perseverance MEDA",
                "role": "Jezero Crater air temperature",
                "url": "https://mars.nasa.gov/mars2020/weather/",
            },
            {
                "id": "usgs-jezero",
                "name": "USGS Astrogeology",
                "role": "Jezero Crater 20 m DEM (slope pending)",
                "url": "https://astrogeology.usgs.gov/",
            },
            {
                "id": "lola-diviner",
                "name": "NASA LRO LOLA / Diviner",
                "role": "Lunar polar topography and cold-trap temperatures",
                "url": "https://lunar.gsfc.nasa.gov/",
            },
            {
                "id": "esri-imagery",
                "name": "Esri World Imagery",
                "role": "Earth site imagery (Esri, Maxar, Earthstar Geographics)",
                "url": "https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9",
            },
            {
                "id": "nasa-images",
                "name": "NASA Image and Video Library",
                "role": "Mars, Moon and analog reference imagery",
                "url": "https://images.nasa.gov/",
            },
        ],
        "imagery": {
            "sitePattern": "/images/sites/{cellId}.jpg",
            "hero": "/images/hero-mars.jpg",
            "targets": {
                "mars": "/images/target-mars.jpg",
                "moon": "/images/target-moon.jpg",
            },
            "credits": (
                "Earth imagery: Esri, Maxar, Earthstar Geographics. "
                "Mars/Moon imagery: NASA/JPL-Caltech and partners."
            ),
        },
        "files": [
            "manifest.json",
            "coarse_results.json",
            "candidates.json",
            "method.json",
            "usecases.json",
            "targets.json",
            "known_analogs.json",
        ],
        "notes": [
            "Match score is a screening aid, not a site-selection verdict.",
            "A null observation is shown as unknown and excluded from the weighted score.",
            "Technical method and limitations live in the repository documentation.",
        ],
    }
