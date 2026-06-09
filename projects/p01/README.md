# P01: Scale-Dependent Regime Transition in Submesoscale Air-Sea Coupling Revealed by SWOT

> Does air-sea coupling undergo a regime transition from mesoscale to submesoscale, and can SWOT wind speed, SWOT SSH, and geostationary SST reveal where and how the coupling physics changes?

## Status

| Item | Content |
|---|---|
| Current stage | D1 Draft (real-data Gulf Stream pilot) |
| Lead / proposer | Kris19999 |
| Target journal | Nature Communications (high-impact target); GRL or JGR: Oceans as realistic fallback targets |
| Start date | 2026-06-05 |
| Expected submission | TBD |

## D0 Priority Checklist

- [x] Verify SWOT L2 sigma0-derived wind speed quality in a Gulf Stream pilot box.
- [x] Download/use SWOT KaRIn L2 SSH for the same swaths and characterize SSH gradients, fronts, and eddy-edge structures.
- [x] Download/use concurrent GOES-East SST and quantify clear-sky collocation with SWOT passes.
- [x] Compute first-pass coupling diagnostics using SWOT wind speed and geostationary SST, not ASCAT as the primary wind field.
- [ ] Extend the workflow to Himawari SST and the Kuroshio Extension.
- [ ] Add ASCAT, ERA5, and CCMP as coarse-scale benchmarks for traditional wind products.
- [ ] Complete manual literature verification on SWOT-derived wind speed and submesoscale air-sea coupling.

## Scientific Question

The revised scientific framing is stronger than a simple global map of wind kinetic energy: this project asks whether air-sea coupling changes character from mesoscale to submesoscale. The central observational question is whether SWOT can reveal fine-scale wind-speed responses to SST fronts that are smoothed or missed by traditional scatterometer and reanalysis products.

The mesoscale framework for SST-wind coupling describes a quasi-linear response: warm SST anomalies destabilize the atmospheric boundary layer and accelerate near-surface winds. The open question is what happens when the ocean contains sharp submesoscale fronts and filaments at O(2-50 km) scales. Three outcomes are possible:

1. **Continuity**: the mesoscale coupling relationship extends smoothly to finer scales.
2. **Saturation or decay**: the atmospheric boundary layer cannot adjust to the finest SST structures, so coupling weakens.
3. **Regime transition**: sharp fronts, filaments, and dynamically intense structures trigger a different boundary-layer response, visible as changes in coupling slope, coherence, phase, or wind-speed kinetic energy anomalies.

The Gulf Stream and Kuroshio Extension are the primary pilot regions because they combine strong SST fronts, energetic submesoscale ocean structures, and previously documented ocean-atmosphere coupling. The key new element is that SWOT wind speed may resolve wind structures at scales where ASCAT, CCMP, and ERA5 are too smooth.

## Core Position After Discussion

The group-revised regime-transition framing is scientifically stronger and should be retained. The main adjustment proposed here is not to change the scientific logic, but to change the hierarchy of wind datasets: the primary atmospheric response field should be **SWOT L2 wind speed**, not ASCAT.

ASCAT is valuable, but it should not replace SWOT as the main wind dataset for this project. Its main role should be to provide a coarse-scale benchmark for traditional wind products and to help evaluate what is smoothed or missed relative to SWOT. If the story is that SWOT reveals submesoscale air-sea coupling missed by traditional satellites, SWOT wind speed must be central.

## Hypotheses

1. SWOT wind speed reveals submesoscale near-surface wind-speed and wind-kinetic-energy structures that are weakened or absent in ASCAT, CCMP, and ERA5.
2. The scale-dependent air-sea coupling coefficient changes from mesoscale to submesoscale, especially in the Gulf Stream and Kuroshio Extension.
3. The strongest SWOT wind-speed kinetic energy anomalies are tied to sharp geostationary-SST fronts and SWOT SSH-gradient structures.
4. SWOT SSH gradients help identify the dynamical ocean structures that set the regime boundary, while GOES/Himawari SST provides the thermal frontal forcing.
5. ASCAT, ERA5, and CCMP should be used primarily as coarse-scale benchmarks for traditional wind products; sub-25-km wind-response claims should come from SWOT wind speed.

## Data

All datasets are public. Raw data must not be committed; only download scripts, access notes, quality-control notes, and processed outputs should be tracked.

### Primary observational triad

- **SWOT L2 sigma0-derived wind speed**: primary atmospheric response field. Used to quantify wind-speed anomalies, wind-speed gradients, and near-surface wind kinetic energy proxy at SWOT swath resolution.
- **SWOT KaRIn L2 Low Rate SSH**: primary ocean dynamic structure field. Used to identify SSH gradients, fronts, eddies, filaments, strain-related structures, and dynamical conditioning of coupling regimes.
- **Geostationary SST**: primary thermal-frontal field.
  - GOES-East ABI SST / NOAA ACSPO for the Gulf Stream.
  - Himawari-8/9 AHI SST for the Kuroshio Extension.

### Supporting datasets

- **ASCAT vector winds**: coarse-scale benchmark for traditional satellite winds and consistency checks at ASCAT-resolvable scales.
- **ERA5 10 m winds and surface fields**: background atmospheric state, synoptic filtering, stability context, and sensitivity tests.
- **CCMP ocean surface winds**: gridded traditional wind-product comparison.

## Method

### Pilot regions

- **Gulf Stream**: GOES-East SST + SWOT wind speed + SWOT SSH, with ASCAT/ERA5/CCMP as comparison products.
- **Kuroshio Extension**: Himawari SST + SWOT wind speed + SWOT SSH, with ASCAT/ERA5/CCMP as comparison products.

### Step 1: Collocation and quality control

Collocate SWOT wind speed, SWOT SSH, geostationary SST, and comparison wind products. Apply quality flags for SWOT, cloud masks for SST, rain/land contamination checks, and time-window sensitivity tests.

### Step 2: Multi-scale decomposition

Filter SWOT wind speed, SST, and SSH into scale bands such as 10, 20, 50, 100, 200, and 500 km. The key point is to avoid letting the coarser comparison products define the finest scale that SWOT can test.

### Step 3: SWOT-based wind-speed response diagnostics

Use SWOT wind speed as the core wind field:

```text
K10_SWOT = 0.5 * U10_SWOT^2
```

Primary diagnostics:

- `U10_SWOT'` and `K10_SWOT'` anomalies.
- `|grad U10_SWOT|` and `|grad K10_SWOT|`.
- Spatial collocation with `|grad SST_geo|` and `|grad SSH_SWOT|`.
- Differences between SWOT-resolved structures and ASCAT/ERA5/CCMP structures.

### Step 4: Scale-dependent coupling coefficients

Primary SWOT-based coefficients:

```text
|grad U10_SWOT| = alpha(lambda) |grad SST_geo| + residual
|grad K10_SWOT| = beta(lambda) |grad SST_geo| + residual
K10_SWOT' = gamma(lambda) SST_front_metric + residual
```

The coefficients should be estimated as functions of wavelength or filter cutoff `lambda`. A break, plateau, or phase shift in these curves would indicate scale-dependent coupling or a possible regime transition.

Vector-wind curl/divergence diagnostics are not part of the initial core analysis. They can be revisited later only if they become necessary for a separate mechanism test.

### Step 5: Spectral and coherence analysis

Compute co-spectrum, coherence, and phase between:

- SWOT wind-speed gradients and geostationary SST gradients.
- SWOT wind kinetic energy anomalies and geostationary SST fronts.
- SWOT wind kinetic energy anomalies and SWOT SSH gradients.
- SWOT wind speed and traditional wind products, to quantify what traditional products miss.

### Step 6: Controls and interpretation

Repeat the analysis in weaker-front regions to test whether the scale-dependent coupling signature is specific to western boundary currents. Interpret results cautiously because wind kinetic energy can be affected by both large-scale atmospheric forcing and ocean-front-induced boundary-layer adjustment.

## Expected Outputs

- A D0 feasibility note on SWOT wind speed quality, collocation statistics, and initial coupling diagnostics.
- A data-requirements and discussion note in `literature/`.
- Reproducible scripts for collocation, filtering, SWOT wind kinetic energy, coupling coefficients, and spectral diagnostics.
- Candidate figures:
  1. SWOT wind speed / `K10_SWOT` structures over GOES/Himawari SST fronts.
  2. Comparison of SWOT wind speed with ASCAT/ERA5/CCMP in the same region.
  3. Scale-dependent coupling coefficient curves based on SWOT wind speed and geostationary SST.
  4. Coherence and phase spectra between SWOT wind speed, SST fronts, and SWOT SSH gradients.
  5. Gulf Stream versus Kuroshio Extension comparison.
  6. Control-region null or weak-coupling result.

## Feasibility and Risks

**Critical risks:**

- SWOT wind speed quality and rain/sea-state contamination must be checked carefully before making submesoscale claims.
- SWOT provides wind speed magnitude, not a full vector wind. This D1 package therefore focuses on wind-speed and wind-speed-kinetic-energy diagnostics, not vector-wind curl/divergence diagnostics.
- Collocation between SWOT, clear-sky geostationary SST, and comparison wind products may be limited by clouds and sampling.

**Scientific risks:**

- A regime transition may not exist; the coupling may be continuous, weak, or dominated by atmospheric background variability.
- Western boundary current wind kinetic energy may be strong because of both atmospheric forcing and ocean-front coupling. The mechanism must be tested rather than assumed.
- Traditional products may differ from SWOT because of resolution and sampling, not necessarily because SWOT is always more accurate.

**Pivot strategy:**

If a clear regime transition is not detected, the project can still become a GRL/JGR-style paper on how SWOT changes the observed scale dependence of wind-SST coupling and reveals fine-scale wind-speed kinetic energy structures missed by traditional products.

## Contributor Role

The proposer has worked on ocean submesoscale processes from the master's stage to the present, is affiliated with a National Science Fund for Distinguished Young Scholars team, and has published three related papers in JGR and Ocean Modelling. The proposer can contribute domain-expert AI review, physical interpretation, figure processing, reference verification, and manuscript-level scientific correction, especially for submesoscale dynamics and submesoscale air-sea interaction.

## Progress Log

| Date | Stage | Content | Output |
|---|---|---|---|
| 2026-06-05 | D0 | Initial topic proposal: SWOT wind kinetic energy distribution and coupling | Original local proposal |
| 2026-06-08 | D0 | Revised after group discussion: retain scale-dependent regime-transition question, restore SWOT wind speed as the primary atmospheric response field | Updated README and Chinese discussion note |
| 2026-06-09 | D1 real-data pilot | Rebuilt a compact D1 package from real Gulf Stream SWOT L2 LR SSH Expert wind speed / SSH and GOES-16 ABI SST. Three collocated cases passed QC and cloud-screening thresholds. | `analysis/p01_d1_realdata_pipeline.py`, `analysis/d1_results_summary.json`, `figures/p01_d1_*.png`, `manuscript/v1_ai_draft/P01-D1-Manuscript-CN.md` |

## AI Interaction Log

See `logs/2026-06-05_D0_topic_proposal.md`.

## References

See `literature/literature_seed.md`. All references must be manually verified before manuscript use.
