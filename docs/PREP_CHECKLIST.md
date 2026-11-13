# Prep Checklist (Tonight — Nov 13)

Allowed now: accounts, reading terms, target profiles on paper, feature list, roles, schedule.  
**Do not** scaffold the Vite app or write UI/pipeline code until 2026 terms confirm.

---

## A. Rules & accounts (do first)

- [ ] Read **2026 Participant Terms** on Space Apps site; note anything about pre-event code
- [ ] Create / verify **Earthdata Login** (urs.earthdata.nasa.gov)
- [ ] Skim challenge **Resources** tab when available; paste official dataset list into `docs/OFFICIAL_RESOURCES.md`
- [ ] Confirm local event timing / submission deadline for your city

---

## B. Product decisions (15–30 min)

- [ ] Solo or team? (fill section below)
- [ ] Primary use case (one sentence)
- [ ] Differentiation: **B hardware-test** (default) / A Africa / A+B
- [ ] Bodies: Moon only / Mars only / **both with shared UI**
- [ ] Final name: MarsTwin / other

### Team context
| Role | Person | Strength |
|------|--------|----------|
| Science / scoring | | |
| Frontend (React) | | |
| Map / viz | | |
| Writing / demo video | | |

If **solo:** cut Mars *or* Moon deep-dive; ship one body excellently + light second fingerprint.

---

## C. Feature list lock (v1)

Must ship:
- [ ] slope_roughness
- [ ] diurnal_temp_range
- [ ] precipitation
- [ ] vegetation_ndvi
- [ ] ice_permafrost (even coarse)

Stretch:
- [ ] mineralogy (EMIT) — only if Resources tab makes it easy
- [ ] albedo_dust
- [ ] logistics (clearly labeled Earth-only)

---

## D. Validation protocol lock

- [ ] Known analog list (≥4) with lat/lon + citation
- [ ] Definition of “ranks high” (e.g. within top 5% of scored cells)
- [ ] Exclusion list = same known set
- [ ] Success criteria for Day 1 evening: validation table green + 3 new candidate stubs

---

## E. Target profiles (paper → JSON Day 1)

Fill `TARGET_PROFILES.md` tonight with **cited numbers**. Empty cells are fine if you mark “TBD cite tomorrow from Resources.”

---

## F. Environment readiness (no project code)

- [ ] Node LTS installed (`node -v`)
- [ ] Git installed
- [ ] Python 3.11+ available if you will run rasters
- [ ] VS Code / Cursor ready
- [ ] Folder `marstwin` ready (this prep pack)
- [ ] Optional: create empty private GitHub repo **without** committing app code yet

---

## G. Mental model rehearsal (5 min)

Say out loud:
1. What is similar  
2. How similar (per dimension)  
3. Where it breaks  
4. What we would test  
5. Why famous sites are excluded after validation
