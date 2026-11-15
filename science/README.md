# MarsTwin science pipeline

Solo · **6 dimensions** · hardware-test use case · **null beats fake numbers**.

## Quick run

```bash
# from repo root
python science/scripts/run_pipeline.py
```

Fetches NASA POWER air climatology (cached in `science/cache/`), scores cells, writes `apps/web/public/data/*.json`.

## Rules locked in code

| Rule | Implementation |
|------|----------------|
| Slopes null until 20 m DEM | Empty CSV cols + `compute_slopes_20m.py` scaffold |
| Lunar mineralogy uncitable | `value: null` + use-case weight `0` |
| Air↔air thermal | POWER T2M vs MEDA ~60 K at Jezero |
| PSR ~40 K | Gap report hard limit, not an Earth similarity score |

## Next sources

See `docs/DATA_SOURCES.md` — NDVI/GIBS → DEM slopes → MODIS LST track → EMIT / LOLA / Diviner / HiRISE / Odyssey.
