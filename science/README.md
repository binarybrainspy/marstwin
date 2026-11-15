# MarsTwin science pipeline

Solo · **6 dimensions** · hardware-test use case · **null beats fake numbers**.

## Quick run

```bash
# from repo root
pip install -r science/requirements.txt
python science/scripts/run_pipeline.py
```

Fetches NASA POWER air climatology and MODIS NDVI (MOD13Q1, ORNL DAAC; cached in `science/cache/`), scores cells, writes `apps/web/public/data/*.json`. `--skip-power` is the offline path: it reuses caches and makes no network calls.

Optional real slopes (needs local DEMs): `python science/scripts/compute_slopes_20m.py --earth-dem ... --jezero-dem ... --lola-dem ... --apply` then re-run the pipeline.

## Rules locked in code

| Rule | Implementation |
|------|----------------|
| Slopes null until 20 m DEM | `compute_slopes_20m.py` (Horn 3x3, shared baseline) writes values + provenance; contract rejects unsourced slopes |
| Lunar mineralogy uncitable | `value: null` + use-case weight `0` |
| NDVI sourced or null | `lib/ndvi.py` MOD13Q1 250 m annual mean; failed / missing coverage sets `vegetation_ndvi` to null, never a stub |
| Air↔air thermal | POWER T2M vs MEDA ~60 K at Jezero |
| PSR ~40 K | Gap report hard limit, not an Earth similarity score |

## Next sources

See `docs/DATA_SOURCES.md` — DEM slopes → MODIS LST track → EMIT / LOLA / Diviner / HiRISE / Odyssey.
