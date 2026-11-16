# MarsTwin — Report & Slide Deck Source Material

This file is the narrative companion to the code. It collects the problem framing, method, results, limitations and presentation structure for a written report or a short slide deck. It is not the app's technical README; see [`README.md`](README.md) for setup and architecture.

---

## 1. Title and thesis

**MarsTwin: an analog Earth atlas that shows where the comparison holds — and where it breaks.**

Most "Mars on Earth" maps answer a visual question: *does this landscape look like Mars?* MarsTwin answers an operational question: *which Earth sites are useful for testing surface hardware and field operations, and what can they never rehearse?*

The product is a decision aid. It screens twenty arid, cold or barren Earth cells against two concrete destinations, validates the screen against sites the literature already knows, removes those controls, and promotes a short list of new candidates with a field card and a gap report.

**One-sentence pitch:**

> MarsTwin screens Earth's best Mars and Moon analogs, proves the famous sites still win, then surfaces new field-test candidates with an honest account of what Earth cannot simulate.

---

## 2. The problem

Analog-site lists are abundant and often interchangeable. A site is described as "Mars-like" because it is dry, cold, red, dusty or volcanic. That is useful for outreach. It is not enough for a team deciding where to take a rover, a thermal chamber, a wheel rig or a drill.

Three problems recur:

1. **One score hides the trade-offs.** A site can be excellent for aridity and poor for slope, or good for thermal swing and irrelevant for ice. A single "match %" flattens that.
2. **Famous sites crowd out new ones.** Atacama and the Dry Valleys are genuinely important, but a candidate list that only ever rediscovers them is not a screen.
3. **Earth limits disappear into the score.** Gravity, vacuum, radiation and planetary protection cannot be simulated by choosing a different desert. They must be reported as hard gaps.

MarsTwin addresses all three: a six-signal fingerprint, a validation gate that excludes the control group, and a field card that keeps the gaps visible.

---

## 3. What was built

### 3.1 The atlas

An interactive Esri World Imagery map shows all twenty Earth cells. The user switches between **Mars (Jezero Crater)** and the **Moon (south-polar rim)**, selects a cell, and sees:

- its rank and composite score for that destination;
- a six-signal fingerprint;
- measured air-temperature swing, rainfall and NDVI;
- the current state of slope and mineralogy (null until sourced);
- a static satellite thumbnail and a link to the field card.

A terrain layer and place-label overlay are available for context. The map is a screening surface, not a rover traverse planner.

### 3.2 The field card

Each promoted candidate gets a card with four sections:

1. **What carries over** — the measured reasons the site earned a closer look.
2. **What we would test** — a concrete field plan: thermal soak, wheel–soil test, timed rover shift.
3. **Where the analogy breaks** — gravity, atmosphere, radiation, mineralogy, air-versus-ground temperature.
4. **Gap report** — hard limits, partial limits and manageable mismatches, each with a short explanation.

This is the unit of output. The map is navigation; the card is the argument.

### 3.3 The reality check

The validation page is the scientific honesty check. It shows the known analogs, their rank for each destination and whether the control group passed. Only after the pass does the app present new candidates.

The current pass rule: **at least one known analog in the top three of twenty**. The controls are then removed from the candidate pool, so a promoted site is never simply a famous site with a new label.

### 3.4 The method page

The method page exposes the data run, sources, weights, transforms and deliberate blanks. It is designed to answer judge questions without requiring a code read:

- What was measured?
- What was fetched live?
- What is still pending?
- Why is a value null?
- What does the composite actually mean?

---

## 4. Method

### 4.1 Use case

**Thermal cycling + mobility surface rehearsal.**

Find arid, low-vegetation terrain with a high diurnal air-temperature swing and traversable slopes for rover thermal and wheel/surface checkout under Earth gravity — then document what does not transfer to the Moon or Mars.

The use case is deliberately concrete. It determines the weights, but the six-signal fingerprint remains visible so a reader can disagree with the weighting.

### 4.2 Dimensions and weights

| Dimension | Weight | Why it is in the screen |
|-----------|--------|--------------------------|
| Diurnal ΔT | 32% | Thermal-cycling fidelity |
| Slope / roughness | 28% | Mobility and traversability |
| Precipitation | 18% | Aridity |
| Vegetation (NDVI) | 14% | Barren-surface proxy |
| Ice / permafrost | 8% | Cold-trap relevance; low for the warm-arid case |
| Mineralogy | 0% | Null until citable |

### 4.3 Similarity transform

```text
similarity = 1 − clip(|earth − target| / scale, 0, 1)
```

| Dimension | Scale |
|-----------|-------|
| Diurnal ΔT | 120 K |
| Slope | 20° |
| Precipitation | 500 mm/yr |
| NDVI | 0.6 |
| Ice proxy | 0.8 |

The composite is a weighted mean over dimensions where both Earth and target values exist. Missing dimensions are excluded and the remaining weights are renormalised.

### 4.4 Validation protocol

1. Score all twenty cells for both destinations.
2. Check where the four known analogs land.
3. Pass a destination if at least one control is in the top three.
4. Remove the controls from the candidate pool.
5. Promote the highest-ranked remaining cells as field cards.

This ordering matters. Without it, "new candidate" is a marketing label rather than a result.

### 4.5 Locked data rules

- **Slope:** null until computed at a shared 20 m baseline across Earth, Jezero and the lunar pole. Coarser DEMs are flagged, not relabelled.
- **Temperature:** air↔air (POWER T2M vs MEDA) or ground↔ground (MODIS LST vs rover TIRS / Diviner). Never mixed without a label.
- **Mineralogy:** null and zero-weighted until a citable per-site value exists.
- **NDVI:** MODIS MOD13Q1 250 m, 2025 annual mean in a ~2 km point sample. Missing coverage stays null.
- **Moon ΔT:** left null. The ~40 K PSR regime is a hard gap, not an Earth score.
- **Null beats a fake number.** Unknown values are shown as unknown and excluded from the weighted score.

---

## 5. Data provenance

| Source | Role | Current status |
|--------|------|----------------|
| NASA POWER | Earth air temperature and precipitation climatology | Live, cached |
| NASA ORNL DAAC MODIS MOD13Q1 | 250 m, 16-day NDVI; 2025 annual mean | Live, 19/20 cells |
| NASA Perseverance MEDA | Jezero air-temperature diurnal amplitude (~60 K at 1.45 m) | Cited in target profile |
| USGS Astrogeology | Jezero 20 m DEM | Pending slope computation |
| NASA LRO LOLA / Diviner | Lunar polar topography and cold-trap context | Pending slope / gap reference |
| Esri World Imagery | Earth basemap and site thumbnails | Live |
| NASA Image and Video Library | Mars, Moon and analog reference imagery | Explicitly cited |
| EMIT / CRISM | Mineralogy | Not yet citable; dimension excluded |

The manifest records the run date, pipeline version, NDVI year, slope status, counts, validation and imagery paths. It is the single answer to "which data produced this screen?"

---

## 6. Results

### 6.1 Validation

| Destination | Best known analog | Rank | Controls in top three | Result |
|-------------|-------------------|------|-----------------------|--------|
| Mars — Jezero Crater | Atacama Desert | 1 | 1 | Pass |
| Moon — south-polar rim | McMurdo Dry Valleys | 1 | 2 | Pass |

Mars known-analog ranks: Atacama 1, Dry Valleys 16, Iceland 19, Hawaiʻi 20.  
Moon known-analog ranks: Dry Valleys 1, Atacama 2, Iceland 17, Hawaiʻi 20.

The Mars control set is carried by Atacama. The Moon control set is carried by the Dry Valleys, with Atacama also placing high. The volcanic controls do not rank highly under this thermal/mobility weighting — a useful reminder that "famous analog" is use-case dependent.

### 6.2 Top-ranked cells

**Mars / Jezero:**

1. Atacama Desert — 0.855
2. Western Desert (Egypt) — 0.849
3. Taklamakan — 0.845
4. Dasht-e Lut — 0.836
5. Atacama valley floor — 0.833

**Moon / south-polar rim:**

1. McMurdo Dry Valleys — 0.869
2. Atacama Desert — 0.762
3. Western Desert (Egypt) — 0.747
4. Taklamakan — 0.716
5. Tibesti — 0.714

### 6.3 Promoted field cards

Both promoted candidates are for the Mars destination:

**Western Desert (Egypt)** — rank 2, composite 0.849.

- NDVI 0.090; 31 K day–night air swing; no measured rainfall.
- Story: dune seas and gravel plains with almost no vegetation; a clean, open test surface for thermal rehearsals.
- Field plan: thermal soak, wheel–soil test once slopes are filled, timed rover shift under thermal stress.

**Taklamakan** — rank 3, composite 0.845.

- NDVI 0.054; 33 K day–night air swing; 58 mm/yr rainfall in the POWER climatology.
- Story: a mountain-ringed cold desert with migrating dunes and dust that punish seals, bearings and optics; a worst-case site.
- Field plan: same thermal/mobility sequence, with dust and abrasion added to the risk list.

These are not claims that Egypt or the Taklamakan are "better than Mars." They are claims that, under this screen, they deserve the next field study.

---

## 7. Why the result is credible

1. **The control group is checked first.** Famous sites must pass before new candidates appear.
2. **The score is decomposed.** A reader can see which dimension drove a rank and which dimensions are unknown.
3. **Nulls are visible.** Slope and mineralogy are not silently filled. A low-confidence ranking is allowed to look low-confidence.
4. **Scale is labelled.** The 0.5° cell, the 250 m NDVI sample and the 20 m slope baseline are all stated.
5. **Hard limits are outside the score.** Gravity, vacuum, radiation and contamination are reported as gaps, not traded against rainfall.
6. **The data is reproducible.** Profiles, cached API values, static JSON and a manifest make the run auditable.

---

## 8. Limitations and future work

### Known limitations

- **Slopes are pending.** This is the largest open item. The 20 m baseline and the computation code exist, but the DEM products have not been run for all sites.
- **Mineralogy is absent.** The dimension is null and zero-weighted.
- **Ice is a proxy.** It is a screening signal, not a site-specific ice-stability model.
- **NDVI is a point sample.** A 2 km box can misrepresent a heterogeneous 0.5° cell.
- **The cell set is small and curated.** Twenty sites are enough for a demo, not a global survey.
- **The Moon comparison is deliberately incomplete.** The thermal regime and PSR cold traps are not Earth-rehearsable.
- **Accessibility and logistics are not scored.** A scientifically interesting site may be operationally impractical.

### Next steps

1. Run the shared 20 m slope pipeline on Earth DEMs, LOLA polar DEM and the USGS Jezero DEM.
2. Add a citable mineralogy layer (EMIT for Earth, CRISM for Mars, a cited lunar product for the Moon).
3. Replace the ice proxy with an Odyssey-informed layer where the use case requires it.
4. Add a ground-temperature track using MODIS LST and labelled rover/Diviner observations.
5. Expand the candidate pool beyond the curated twenty and add a sensitivity analysis on the weights.
6. Add an operational scorecard for access, power, communications and sample return — clearly labelled as Earth-only planning factors.

---

## 9. Slide deck outline

### Slide 1 — Title

**MarsTwin**  
*The closest thing to Mars is still Earth. The question is which part.*  
NASA Space Apps 2026 · Analog Earth Locations

Visual: the atlas map with the Jezero-or-Moon toggle visible.

### Slide 2 — The problem

Most analog maps answer "does it look like Mars?"  
Field teams need "what can we test here, and what can we never test?"

Three bullets: one score hides trade-offs; famous sites crowd out new ones; Earth limits vanish into the score.

### Slide 3 — The product

One atlas, two destinations, six signals, one reality check.

Visual: screenshot of the Atlas page with the selected cell panel and fingerprint.

### Slide 4 — The method

Six dimensions and their weights.  
Similarity equation.  
Nulls excluded, weights renormalised.  
Composite is a screening aid.

Visual: the six-signal table plus the fingerprint radar.

### Slide 5 — The validation gate

Known analogs first. Pass if at least one control is in the top three. Then remove the controls.

Results:
- Mars: Atacama #1.
- Moon: Dry Valleys #1, Atacama #2.
- 2/2 destinations pass.

Visual: the Reality Check page, with "CONTROL PASSED" badges.

### Slide 6 — New candidates

Western Desert (Egypt) and Taklamakan.

Why they rose: low NDVI, strong air-temperature swing, low rainfall.  
What is still unknown: slope, mineralogy.

Visual: two field cards side by side.

### Slide 7 — The field card

What transfers / what we would test / where it breaks / gap report.

Read one line from each section.

Visual: close-up of a field card.

### Slide 8 — The gaps

Gravity, atmosphere/vacuum, radiation, air-vs-ground temperature, biosphere, PSR cold traps.

Key line: *Earth can rehearse the surface. It cannot rehearse the planet.*

Visual: gap report cards, with hard-limit labels.

### Slide 9 — Provenance

NASA POWER · MODIS MOD13Q1 · MEDA · USGS · LRO LOLA/Diviner · Esri · NASA Image Library.

The manifest records the run date, pipeline version, NDVI vintage and slope status.

Visual: Method page data-run strip and manifest chip.

### Slide 10 — Limitations and next steps

Slopes pending. Mineralogy null. Ice is a proxy. NDVI is a point sample.

Next: 20 m slopes, citable mineralogy, ground-temperature track, sensitivity analysis.

Visual: the "deliberate blanks" section of the Method page.

### Slide 11 — Close

**MarsTwin does not claim a site is Mars. It shows what a site can prove.**

Call to action: open the atlas, pick a destination, read the gap report.

Visual: full-bleed Mars target image with the product name.

---

## 10. 90-second demo script

> "This is MarsTwin. It screens twenty of Earth's driest and coldest landscapes against two real destinations: Jezero Crater on Mars and the lunar south pole.
>
> The first thing we do is not rank new sites. It is check the sites we already trust. For Mars, Atacama comes in at number one. For the Moon, the Dry Valleys come in at number one, with Atacama second. Both destinations pass the control test.
>
> Only then do we remove the famous sites and ask what is left. The screen promotes the Western Desert of Egypt and the Taklamakan. Both are arid, both have a strong day–night air-temperature swing, and both have very low vegetation. Those are the reasons they earn a field card.
>
> But the card is not a verdict. It separates what transfers from what breaks. We can rehearse a thermal soak and a wheel–soil test. We cannot rehearse one-third gravity, vacuum, radiation or the lunar cold traps. Slope and mineralogy are still unknown, and we show them as unknown rather than filling them in.
>
> That is the point of the atlas: not to find a perfect Earth Mars, but to make the limits of the analogy explicit before a team spends money in the field."

---

## 11. Written report outline

### Abstract

A short statement of the problem, the six-signal screen, the validation gate, the two promoted candidates and the central limitation: Earth can rehearse surface processes but not planetary conditions.

### 1. Introduction

Why analog sites matter for hardware testing and operations. Why visual similarity is insufficient. The need for a use-case-weighted, decomposed and validated screen.

### 2. Related approach

Known analog catalogues and the "Mars on Earth" framing. The gap: few tools expose per-dimension similarity, nulls, validation and operational limits in one place.

### 3. Data and study area

Twenty Earth cells at 0.5°; two targets; four known analogs. Sources: POWER, MOD13Q1, MEDA, USGS, LOLA/Diviner, Esri, NASA Image Library.

### 4. Method

Use case, weights, similarity transform, composite, validation rule, candidate promotion, gap taxonomy, manifest/provenance.

### 5. Results

Validation table; top-ranked cells; promoted field cards; fingerprint interpretation; sensitivity caveats.

### 6. Discussion

What the result means. Why the volcanic controls fall under this weighting. Why the Moon comparison is structurally incomplete. The role of nulls as a credibility mechanism.

### 7. Limitations

Slopes pending, mineralogy absent, ice proxy, NDVI scale, curated cell set, no logistics score.

### 8. Future work

20 m slopes, citable mineralogy, ground-temperature track, larger candidate pool, weight sensitivity, operational scorecard.

### 9. Conclusion

MarsTwin is a screening and communication tool. Its contribution is not a new "most Mars-like place" but a repeatable way to show which comparisons hold, which do not, and what evidence is still missing.

### Appendix

- Data manifest fields.
- JSON contract summary.
- Source URLs.
- Reproducibility commands.
- Image credits.

---

## 12. Visual asset checklist

For a slide deck or report, reuse these existing assets:

| Asset | Path | Use |
|-------|------|-----|
| Atlas map | live `/screen` | Title and product slides |
| Selected-cell panel | live `/screen` | Fingerprint and scale slide |
| Reality-check page | live `/validate` | Validation slide |
| Field cards | live `/candidates/cell_w_desert_egypt` and `/candidates/cell_taklamakan` | Candidate and gap slides |
| Method page | live `/method` | Provenance and limitations |
| Mars target | `apps/web/public/images/target-mars.jpg` | Title / closing |
| Moon target | `apps/web/public/images/target-moon.jpg` | Two-destination slide |
| Atacama | `apps/web/public/images/analog-atacama.jpg` | Control-group slide |
| Dry Valleys | `apps/web/public/images/analog-dry-valleys.jpg` | Control-group slide |
| Site thumbnails | `apps/web/public/images/sites/*.jpg` | Candidate montage |
| World locator | `apps/web/public/images/world.jpg` | Global context |

If a screenshot is used, include the data-run date and the "slopes pending" label so the visual matches the state of the data.

---

## 13. Judge Q&A prompts

**"Why only twenty sites?"**  
Twenty is enough to demonstrate a validated screen and a field-card workflow. The architecture is extensible; the constraint is deliberate scoping, not a claim of global coverage.

**"Why is the Moon score lower?"**  
The lunar target is deliberately incomplete. Polar thermal behaviour is illumination-driven and the ~40 K cold-trap regime has no Earth analogue. Leaving the Moon ΔT null is more honest than borrowing an Earth day–night number.

**"Why are slopes missing?"**  
Because the baseline is locked at 20 m and the DEM products have not been run for every site. Showing null is preferable to substituting a coarser slope and relabelling it.

**"Isn't Atacama obvious?"**  
Yes — and that is the point of the control group. The validation gate proves the screen can recover a known answer before it asks anyone to trust a new one.

**"What is new here?"**  
The combination of a use-case-weighted six-signal fingerprint, a control-first validation gate, explicit null handling, and a gap report that keeps planetary limits outside the score.

**"Can this select a landing site?"**  
No. It is a screening and communication tool. Site selection needs engineering, logistics, policy and higher-resolution data.

---

## 14. Credits and attribution

Earth imagery: **Esri, Maxar, Earthstar Geographics** — World Imagery and reference layers.  
Mars, Moon and analog reference imagery: **NASA / JPL-Caltech and partners**, via the NASA Image and Video Library.  
Science data: **NASA POWER**, **NASA ORNL DAAC MODIS MOD13Q1**, **NASA Perseverance MEDA**, **USGS Astrogeology**, **NASA LRO LOLA / Diviner**.

Individual image credits are stored in `apps/web/public/images/credits.json`; Earth imagery provenance is in `apps/web/public/images/sources.json`.

---

*MarsTwin is a screening aid, not a site-selection verdict.*
