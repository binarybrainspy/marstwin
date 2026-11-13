# Target Profiles (Fill Tonight)

Every number needs a **source**. Prefer official NASA / PDS / peer-reviewed summaries.  
Replace placeholders when the challenge Resources tab unlocks.

---

## Use case (lock one)

**ID:** `uc_thermal_mobility`  
**Title:** Thermal cycling + mobility surface rehearsal  
**Body focus:** both (UI), science depth priority: _______________  

**One-sentence intent:**  
> Find Earth terrain where diurnal thermal stress and traversable arid surfaces let a team rehearse rover thermal/mobility ops under Earth gravity, then document what does not transfer.

**Dimension weights (sum ≈ 1):**

| Dimension | Weight | Why |
|-----------|--------|-----|
| diurnal_temp_range | 0.30 | Thermal cycling fidelity |
| slope_roughness | 0.25 | Mobility / traversability |
| precipitation | 0.20 | Aridity |
| vegetation_ndvi | 0.15 | Barren surface proxy |
| ice_permafrost | 0.10 | Avoid false cold-desert matches if use case is arid warm |
| mineralogy | 0.00 | Stretch |
| logistics | 0.00 | Optional Day 2 |

**Earth limits always listed:** gravity, atmosphere, radiation, biosphere.

---

## Moon target (example slot: south-polar–adjacent concept)

| Field | Value | Source |
|-------|-------|--------|
| id | `moon_spole_analog_ref` | — |
| name | *(e.g. near Shackleton / PSR-adjacent reference — pick exact site tomorrow)* | |
| lat | | |
| lon | | |
| rationale | Why this target for the use case | |

### Features

| Dimension | Value | Unit | Source / URL | Notes |
|-----------|-------|------|--------------|-------|
| slope_roughness | | deg or m/m | | |
| diurnal_temp_range | | K | Diviner | Polar thermal behavior differs from equator — be careful |
| precipitation | 0 | — | N/A vacuum | Map as “N/A → treat via aridity proxy on Earth” |
| vegetation_ndvi | 0 | — | N/A | |
| mineralogy | | | | |
| ice_permafrost | | | | PSR ice relevance vs Earth ice — gap note required |
| albedo_dust | | | | |

**Analogy caveats to write into Gap Report early:**
- Lunar vacuum + radiation do not transfer
- Polar illumination geometry ≠ Earth day/night
- Gravity 1/6 g

---

## Mars target (example slot: arid mid-latitude or classic rover-relevant site)

| Field | Value | Source |
|-------|-------|--------|
| id | `mars_arid_ref` | — |
| name | *(e.g. Jezero vicinity OR a thermal/dust reference — pick one)* | |
| lat | | |
| lon | | |
| rationale | | |

### Features

| Dimension | Value | Unit | Source / URL | Notes |
|-----------|-------|------|--------------|-------|
| slope_roughness | | | MOLA / HiRISE lit. | |
| diurnal_temp_range | | K | THEMIS / literature | |
| precipitation | ~0 | | | Dust / vapor nuances in notes |
| vegetation_ndvi | 0 | | | |
| mineralogy | | | CRISM | Stretch |
| ice_permafrost | | | Odyssey neutron | If site is ice-relevant |
| albedo_dust | | | | |

**Analogy caveats:**
- 0.38 g gravity
- CO₂ atmosphere / dust devil regime
- Radiation / no thick magnetosphere

---

## Known analogs (validation seeds)

| id | name | lat | lon | body | whyFamous | citation |
|----|------|-----|-----|------|-----------|----------|
| ka_atacama | Atacama Desert | | | mars | Hyper-arid Mars analog | |
| ka_dry_valleys | McMurdo Dry Valleys | | | mars | Cold desert | |
| ka_iceland | Iceland volcanic terrains | | | both | Volcanic / basaltic | |
| ka_hawaii | Hawaiʻi volcanic fields | | | moon/mars | Volcanic ops heritage | |

---

## Official Resources paste zone

When the challenge Resources tab opens, paste dataset names + access notes here:

```
(paste tomorrow)
```
