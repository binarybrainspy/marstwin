# NASA Space Apps Challenge: Analog Earth Locations Strategy Guide

**Purpose of this document**  
This file consolidates all provided analysis, recommendations, and details about the NASA Space Apps Challenge challenge on identifying and characterizing terrestrial analogs for the Moon and Mars. It is structured so an agent can quickly grasp the challenge requirements, judging signals, recommended approach, data sources, preparation timeline, differentiation strategies, and key risks.

---

## 1. Core Insight from the Challenge Statement

The challenge statement reveals exactly what judges will reward. The goal is **not**:
- Simply rediscovering well-known analog sites
- Finding one place that merely “looks like” the Moon or Mars

It explicitly names Antarctica, the Atacama, Iceland, and Hawaii as already widely studied. Many existing public repositories are global similarity scorers that rank cells on a coarse grid — this is precisely what the statement warns against.

### What the statement requires
- Teams must explain **what is similar**, **how similar**, and **where the analogy breaks down**.
- Explicitly address Earth’s limits (gravity, vacuum, radiation, etc.).
- The “gap report” (limitations of the analogy) is a required deliverable and needs real design space in the project.
- Think about **scale** and **processes** as well as places. A continent-wide score is insufficient.
- Connect the analog to a concrete **use case**: testing instruments, rehearsing operations, finding resources, or reducing risk.

---

## 2. Rules Check on Preparation

- Official 2026 participant rules could not be located at the time of writing.
- Older Space Apps rule sets indicate:
  - All design elements and code must be created **during** the event.
  - Planning and discussing in advance is allowed.
  - Open-source libraries and existing APIs are permitted.
- This corrects earlier assumptions about building reusable pipeline pieces beforehand.
- **Until the 2026 terms are read**: stick to planning, data exploration, and learning now. Write all project code on **November 14–15**.
- Reference for older rules: https://spaceapps2019.ut.ee/?p=5

---

## 3. Recommended Concept: Method + Case Study

**Primary recommendation**: A method that finds candidates + a case study that proves it works.

### Approach
1. **Screen coarsely, then refine**
   - Score Earth regions on roughly 6–8 dimensions:
     - Slope and roughness
     - Diurnal temperature range
     - Precipitation
     - Vegetation
     - Surface mineralogy (where available)
     - Ice or permafrost
   - Re-examine the top candidates at much finer resolution.
   - This directly addresses the scale requirement.

2. **Show a fingerprint, not one number**
   - For each candidate, display per-dimension similarity to:
     - A Moon south-pole target
     - One Mars target

3. **Validate, then exclude**
   - Demonstrate that the method ranks known analogs highly.
   - Then remove the famous sites and examine what remains.

4. **Deep-dive the top one or two new candidates**
   - Produce an “analogy card” for each:
     - What transfers
     - What does not transfer
     - What you would test there

### Alternative concepts (lower priority)
- **Single-site deep dive**: Lower risk, more story-driven.
- **Process-based analog** (e.g., lava tubes or dust): More distinctive but harder to finish in 48 hours.

**Preferred path**: The multi-stage method + case study approach.

---

## 4. Data Sources (High Confidence)

### Earth
- Elevation: SRTM or ASTER
- Land surface temperature: MODIS
- Vegetation: NDVI
- Climate: NASA POWER
- Imagery: GIBS
- Surface mineralogy (arid regions): EMIT

### Moon
- Topography: LRO LOLA
- Temperature: Diviner
- Imagery: LROC

### Mars
- Topography: MOLA
- Imagery/spectral: HiRISE, CRISM, THEMIS
- Ice: Odyssey neutron data

**Note**: The challenge statement directs teams to the Resources tab for the official list. That list was not accessible at the time of writing; paste it when available to verify formats and access methods.

---

## 5. Allowed Preparation (Before November 14)

- Set up Earthdata login.
- Read the 2026 Participant Terms carefully.
- Write Moon and Mars target profiles on paper, with a cited source for every number.
- Finalize the feature list and decide how validation will be performed.
- Assign roles and agree on a rough 48-hour schedule.

---

## 6. 48-Hour Execution Plan

### Day 1
- Build data pipeline
- Run coarse screen
- Perform validation against known analogs

### Day 2
- Refine top candidates
- Build analogy cards
- Create the map
- Record the demo
- Write the report

---

## 7. Team Context Question

Are you working solo or with a team? What are your teammates’ strengths?  
This determines how much mapping, visualization, and storytelling can realistically be planned.

---

## 8. Why Choose “Analog Earth Locations” Despite Crowding

This challenge is popular. Public repositories already:
- Score Earth land cells against Moon and Mars site profiles
- Display results on a 3D globe
- Validate against known analogs
- Flag “new” candidate sites

Examples:
- https://github.com/KraKEn-bit/TerraNova
- https://github.com/ABRUBAB/ShadowAstra_Atlas

### Reasons to still pursue it
1. The challenge statement specifically asks teams to **identify and characterize new terrestrial analogs**. A well-argued contribution still has room to stand out.
2. It is primarily a Python data pipeline + simple map — more feasible to finish in 48 hours than a full Mars 3D explorer.
3. Judges reward scientific validity. A scoring method rigorously checked against known analog sites is worth more than a polished globe.

---

## 9. Differentiation Strategies

### Option A: Africa-focused analogs
- Examine the Sahara, Namib, Danakil Depression, and similar sites.
- Compare against known analogs such as the Atacama and Antarctic Dry Valleys.
- Note: One existing repository already mentions Tibesti and Ahaggar as recurring candidates. Any Africa-focused work must go deeper than name-dropping these locations.

### Option B: Hardware-test requirements (strong fit for mechatronics backgrounds)
- Start from a specific engineering test need (e.g., soil and wheel mechanics, thermal cycling).
- Recommend sites according to those concrete requirements.
- Some teams already match sites by task; keep the mapping highly specific and grounded.

**Caveat**: Only a sample of existing repositories was reviewed. No guarantee exists that others are not already pursuing these angles.

---

## Summary for Quick Agent Orientation

| Aspect                  | Key Takeaway                                      |
|-------------------------|---------------------------------------------------|
| What judges want        | Characterization + gap analysis + use case        |
| What to avoid           | Coarse global scorers, rediscovering famous sites |
| Recommended approach    | Coarse → fine multi-feature method + analogy cards|
| Validation strategy     | Rank known analogs high, then exclude them        |
| Primary risk            | Over-scoping; finish the science story first      |
| Prep allowed            | Planning, data exploration, target profiles only  |
| Code window             | November 14–15 only                               |

This document preserves every substantive point from the original analysis so an agent can act on it without needing the raw text.