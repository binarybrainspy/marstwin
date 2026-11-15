# MarsTwin science pipeline

Solo-scoped: **6 dimensions**, hardware-test use case (`uc_thermal_mobility`).

## Quick run

```bash
# from repo root
pip install -r science/requirements.txt
python science/scripts/run_pipeline.py
```

Exports JSON into `apps/web/public/data/` for the Vite app.

## Current data

| File | Role |
|------|------|
| `profiles/earth_cells.csv` | Coarse demo cells (known analogs + new candidates) |
| `lib/scoring.py` | Per-dimension similarity + weighted composite |
| `scripts/run_pipeline.py` | Score → validate → export |

## Next (when Resources unlock)

1. Replace CSV placeholders with real SRTM slope, MODIS ΔT, POWER precip, NDVI
2. Cite Moon/Mars target numbers from official list
3. Expand grid (arid-land mask) without changing the JSON contracts
4. Fine-refine top 1–2 non-famous sites
