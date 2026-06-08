# P03: Testing Neglected Eddy Boundary Signals with SWOT Altimetry

> This project tests whether SWOT-resolved SSH-gradient rims provide a better coordinate for organizing SST, chlorophyll, and PACE-derived tracer anomalies than conventional AVISO/py-eddy-tracker eddy-core coordinates.

## Status

| Item | Content |
|---|---|
| Current stage | D0 Explore / idea proposal |
| Lead / proposer | TBD |
| Target journal | TBD (Stage 2 cross-tracer result could support Nature Communications / Science Advances; Stage 1 alone likely supports Ocean Science, GRL, JGR Oceans, or Remote Sensing of Environment) |
| Start date | 2026-06-07 |
| Expected submission | TBD |

## D0 Priority Checklist

- [ ] Confirm with maintainers whether P03 can be used for this topic.
- [ ] Verify SWOT L3/L2 access routes and product versions (AVISO L3 Basic/Expert/Unsmoothed; PO.DAAC L2 Version D).
- [ ] Verify py-eddy-tracker access and confirm it can be applied to AVISO/DUACS geostrophic currents to produce eddy center, effective radius, and contour for the SWOT period (2024–2026).
- [ ] Verify DUACS DT2024 effective resolution documentation for each pilot region.
- [ ] Compile literature seed list with verified references across all categories (see References section below — all citations require manual verification before manuscript use).
- [ ] Produce 3-region prototype figure set for collaborator discussion.
- [ ] Decide whether Stage 2 tracer download proceeds in parallel or is gated on Stage 1 signal strength.

## Scientific Question

Conventional multimission altimetry (AVISO/DUACS) defines mesoscale eddies through gridded sea-level anomaly contours and composites tracer anomalies around an eddy center and effective radius. This eddy-core framework has produced foundational insights — from eddy-induced chlorophyll modulation to heat and carbon transport estimates — but it operates at an effective spatial resolution where eddy rims, sharp SSH gradients, and non-axisymmetric peripheral structures are inevitably smoothed (DUACS DT2024 effective resolution: ~100–200 km depending on latitude and region).

SWOT KaRIn wide-swath altimetry provides an unprecedented two-dimensional altimetric view of SSH gradients around mesoscale eddies. The question is not whether AVISO is "wrong," but whether the higher-resolution SSH structure changes where we think eddy-induced anomalies are concentrated.

Here, "rim" means an Eulerian SSH-gradient or geostrophic-speed feature, not a material transport barrier. This distinction is critical: SWOT resolves spatial structure in SSH, but it cannot by itself prove material trapping, leakage, or causality.

The central scientific question is:

> **Do SST, chlorophyll, and PACE-derived tracer anomalies align more closely with the SWOT-resolved peripheral high-gradient rim than with the traditional AVISO/py-eddy-tracker eddy center or effective radius?**

This project proceeds in two stages. Stage 1 uses altimetry alone to test whether a SWOT-resolved rim signal is robust after fair filtering and negative controls. Stage 2 tests whether independent tracer datasets are statistically better organized by the SWOT rim than by the conventional eddy-core coordinate. Altimetry-only Stage 1 cannot claim material trapping or leakage.

## Core Narrative

> AVISO/DUACS enabled a global eddy-core paradigm, but its effective resolution smooths the dynamically active peripheral zone where eddies interact with surrounding waters. SWOT now allows us to test whether this peripheral high-gradient rim — sharper, less axisymmetric, and potentially offset from the conventional eddy radius — is where eddy-induced tracer anomalies actually concentrate. If the rim signal is robust, it could provide a physically grounded refinement to eddy-centered compositing.

## Hypotheses

1. **H1 — Sharper, less axisymmetric rim**: SWOT resolves eddy peripheral SSH gradients that are systematically sharper and less axisymmetric than those represented in AVISO/DUACS gridded products. py-eddy-tracker eddy contours provide the AVISO-side baseline for rim shape and effective radius. Tested via rim sharpness and rim asymmetry/coherence metrics in Stage 1.

2. **H2 — Rim position offset**: The SWOT-derived rim radius (maximum `|∇SSH|` or geostrophic speed) differs from the py-eddy-tracker-derived effective radius or maximum-speed contour by a nonzero median normalized offset, with confidence intervals excluding zero after noise, filtering, and swath-position controls. A Stage 1 signal is considered meaningful only if the median absolute normalized offset exceeds the estimated rim-location uncertainty.

3. **H3 — Tracer anomalies are rim-organized**: At least one mature tracer product, with SST and conventional ocean color as primary tests and PACE as an exploratory ecological case, shows stronger and more radially localized tracer anomaly peaks in rim-aligned coordinates than in py-eddy-tracker-radius-aligned or center-aligned coordinates under identical samples. Tested in Stage 2.

4. **Null hypotheses**:

   - **Stage 1 null**: SWOT vs. py-eddy-tracker rim differences are explained by filtering, mapping resolution, product choice, swath noise, or random eddy-center perturbations. After fair filtering to DUACS-like effective resolution, no robust rim offset, sharpness, or asymmetry remains.
   - **Stage 2 null**: Given the same eddies and tracer observations, rim-aligned coordinates do not improve tracer composite strength, localization, or explained variance relative to py-eddy-tracker-radius or center-aligned coordinates.
   - **Background-front null**: Apparent rim tracer anomalies are explained by pre-existing large-scale SST/chlorophyll fronts rather than by the SSH-defined eddy rim.

## Data

All datasets are public. Raw data should not be committed to the repository.

### Stage 1: Altimetry-based rim detection

- **SWOT KaRIn L2 Low Rate SSH** (PO.DAAC Version D) — primary rim detection product. 2×2 km² swath-aligned grid with 250×250 m² native grid option. Preferred over L3 for independence from nadir/DUACS processing.
- **SWOT KaRIn L3 Low Rate SSH Expert / Unsmoothed** (AVISO/DUACS) — secondary rim product for sensitivity check. L3 Basic may be used for rapid prototyping but the primary analysis should use L2 or L3 Expert/Unsmoothed to avoid product-dependence concerns when comparing against DUACS/py-eddy-tracker.
- **AVISO/DUACS gridded SSH / SLA / ADT / geostrophic currents** (CMEMS DT2024) — conventional reference product. Documented effective resolution ~100–200 km depending on latitude.
- **py-eddy-tracker** (open-source, Pegliasco et al. 2022) applied to AVISO/DUACS geostrophic velocity fields — produces eddy center, effective radius, eddy edges, and maximum-speed contours from the same AVISO gridded product. This provides the AVISO-side baseline for rim comparison, using the same algorithm that built the META atlas but applied directly to the SWOT-period geostrophic currents.

### Stage 2: Tracer response

- **SST** (GHRSST / OSTIA / GOES/Himawari geostationary) — primary Stage 2 tracer; geostationary sensors provide higher temporal coverage for matchup with SWOT snapshots.
- **Ocean color / chlorophyll** (ESA OC-CCI / MODIS / VIIRS) — primary Stage 2 biological tracer.
- **PACE** (OCI hyperspectral) — exploratory ecological case study; shorter record and cloud constraints acknowledged.
- **Argo / BGC-Argo** — subsurface vertical section validation at selected rim-crossing transects.

## Method

### Stage 1: Eddy rim detection from altimetry

**Step 1.1 — Pilot regions and eddy selection**

Pilot regions (Phase 1): Kuroshio Extension, Gulf Stream, Agulhas Return Current. Prioritize py-eddy-tracker-detected eddies with clear SWOT swath intersection. Eddy selection criteria should be pre-declared where possible to avoid beautiful-case selection bias.

Expansion (Phase 2, if pilot stable): North Pacific subtropical gyre, South Atlantic eddy corridor.

**Step 1.2 — Three core Stage 1 diagnostics**

Only three primary metrics are computed in Stage 1. All use `|∇SSH|` and geostrophic speed — physically grounded quantities that do not require novel indices. Smoothing and gradient computation methods must be documented; rim-location uncertainty must be estimated.

1. **Rim offset**: distance between the radius of maximum SWOT `|∇SSH|` (or geostrophic speed) and the py-eddy-tracker-derived effective radius or maximum-speed contour, normalized by the py-eddy-tracker-derived radius. Stage 1 uses py-eddy-tracker-derived radius as the denominator. Only after the SWOT rim is independently defined does Stage 2 use SWOT-rim-normalized coordinates.

2. **Rim sharpness**: enhancement of `|∇SSH|` or geostrophic speed in the annular zone (r/R ~ 0.7–1.3, where R is py-eddy-tracker-derived radius) relative to the eddy core (r/R < 0.3) and far exterior (r/R > 1.5). Sensitivity tests repeat this in SWOT-rim-normalized coordinates after the rim is independently detected.

3. **Rim asymmetry / azimuthal coherence**: azimuthal variance of rim radius, angular coverage of coherent high-gradient rim segments, or deviation from the py-eddy-tracker contour after common filtering. This metric directly tests the "less axisymmetric" component of H1.

Supplementary shape diagnostics (perimeter-to-area circularity, filament-like protrusion index) may be reported in an appendix but do not drive Stage 1 conclusions.

**Step 1.3 — Fair-resolution null-model test**

Filter SWOT SSH to region-dependent DUACS effective resolution, with sensitivity tests at 100, 150, and 200 km cutoff wavelengths. The fair-resolution test should include not only low-pass filtering, but also common gridding, common masks, matched time windows, and sensitivity to filter type. The comparison should be interpreted as a resolution-and-mapping test, not a pure resolution test. If rim signals disappear under fair filtering, the Stage 1 null cannot be rejected, and the project pivots (see Decision Gates).

**Step 1.4 — Negative controls**

- **Random-center control**: repeat rim metrics with eddy centers randomly shifted within ±2R, avoiding overlap with the original rim and preserving regional sampling.
- **Azimuthal rotation control**: rotate the SSH field around the eddy center; verify that rim asymmetry signals disappear under randomization.
- **Random-time control**: pair SWOT rims with tracer fields from unrelated dates in the same season to check for coincidental alignment.
- **Tracer-shift control**: spatially shift tracer anomalies relative to the SSH rim while preserving regional gradients.
- **No-eddy / weak-gradient control**: repeat the pipeline in nearby regions without detected eddies or with weak SSH gradients.
- **Across-swath artifact check**: test whether apparent rim sharpness, offset, or asymmetry varies systematically with SWOT across-swath position or noise floor.

**Step 1.5 — Background front control**

Many eddy-rim tracer anomalies may reflect eddy–background-front intersection rather than self-contained eddy boundary dynamics. Both are physically interesting but are different claims. Two tests:

1. **Residual-anomaly test**: remove large-scale background SST/Chl gradient via local anomaly (de-season, de-trend, subtract smoothed field) before rim compositing.
2. **Front-conditioned test**: quantify whether rim signals remain after conditioning on pre-existing background front strength and orientation.

This separates "the eddy rim organizes anomalies independently" from "the eddy rim matters where it intersects a background front."

### Stage 2: Tracer–rim response

**Step 2.1 — Collocation with lag windows**

For eddies with well-characterized Stage 1 rim, collocate SST, chlorophyll, and PACE using time windows of 0, ±1, ±3, and ±7 days relative to the SWOT snapshot. SST is expected near-synchronous; chlorophyll may respond with 1–7 day lag; PACE phytoplankton community structure may reflect longer water-mass history. Account for eddy propagation between SWOT and tracer observation times.

**Step 2.2 — Rim-conditioned composite analysis**

Composite tracer anomalies in rim-aligned coordinates (radial distance normalized by each eddy's independently detected SWOT rim radius). Stratify by rim strength (sharp vs. weak), polarity (AE/CE), region, and season. Tracer anomaly sign is not expected to be universal across polarities and regions — rim localization and anomaly sign should be tested separately.

The primary Stage 2 test is whether rim-aligned composites produce a stronger and more radially localized tracer anomaly peak than py-eddy-tracker-radius-aligned or center-aligned composites under identical samples. Use eddy-level bootstrap or permutation tests; do not treat pixels as independent. Bring all tracer products to a fair common resolution and report sample size by tracer, region, season, and lag window.

PACE is treated as exploratory unless cloud-free collocation sample size meets a pre-defined threshold.

**Step 2.3 — Multi-tracer synthesis**

Cross-compare SST, chlorophyll, and PACE responses. If multiple independent tracers concentrate at the same SSH-defined rim position, the case for rim-organized eddy impacts is substantially strengthened.

## Decision Gates

- **Stage 1 → Stage 2 gate**: Proceed to Stage 2 only if Stage 1 rim offset, sharpness, and asymmetry remain significant after fair filtering and negative controls.
- **PACE gate**: Treat PACE as exploratory unless cloud-free collocations exceed a pre-defined sample threshold.
- **Pivot gate**: If SWOT vs. py-eddy-tracker rim differences vanish after fair filtering, pivot to a resolution-sensitivity or null-result note rather than forcing the rim claim.

## Claims and Guardrails

This section defines what each stage can and cannot claim, to prevent overstatement.

1. **Stage 1 can claim only**: SWOT resolves Eulerian SSH-gradient rims that are sharper, less axisymmetric, and potentially offset from py-eddy-tracker-derived effective radii, after fair-resolution and negative-control checks. It cannot claim material trapping boundaries, Lagrangian coherent structures, or transport barriers.
2. **Stage 1 cannot claim**: the discovery of a new ocean phenomenon. The claim is a resolution-driven refinement to the spatial alignment of eddy composites, not a new class of ocean dynamics.
3. **"Filament" language**: Before tracer validation, use only "filament-like SSH protrusions" or "boundary extensions." The term "filament" should be reserved for tracer-confirmed structures.
4. **"Leakage" language**: Leakage zones require Lagrangian particle experiments, surface drifters, or model velocity fields. They are outside the core claim of this project.
5. **Tracer alignment is not causality**: Stage 2 can claim statistical co-location or organization. It cannot by itself prove that the rim caused the tracer anomaly.
6. **PACE interpretation is exploratory**: PACE-derived ecological or community-structure interpretations require retrieval-quality controls, cloud/sampling checks, and independent consistency with SST/chlorophyll or in-situ data.
7. **Pivot condition**: If SWOT vs. py-eddy-tracker rim differences disappear after fair filtering to DUACS effective resolution, the project pivots to a resolution-sensitivity or null-result note rather than forcing the rim claim.
8. **Nature Communications-level claim requires Stage 2**: A paper claiming that tracer anomalies are rim-organized must present cross-region, cross-tracer statistical evidence. Stage 1 alone supports an observational/methods paper (Ocean Science, GRL, JGR Oceans, Remote Sensing of Environment).

## Questions for Collaborators

1. Is `|∇SSH|`, geostrophic speed, or speed-contour displacement the best primary rim definition?
2. Should L2 Expert or L3 Unsmoothed be the primary SWOT product for rim detection?
3. What is the fairest DUACS/py-eddy-tracker comparison strategy — filtering, mapping, or both?
4. Should Stage 2 be strictly gated on Stage 1 signal strength, or proceed in parallel?
5. Which tracer should be the primary Stage 2 test: SST, chlorophyll, or should both carry equal weight?
6. Is the py-eddy-tracker maximum-speed contour or the py-eddy-tracker-derived effective radius the more appropriate AVISO-side baseline for rim offset?

## Expected Outputs

### Stage 1
- 3-region × 3-metric prototype: co-located SWOT SSH, `|∇SSH|`, py-eddy-tracker contours, and tracer anomaly maps for pilot eddies.
- Rim offset, sharpness, and asymmetry statistics across pilot regions.
- Fair-resolution sensitivity curves (100/150/200 km filtering).
- Negative control results (random-center, azimuthal rotation, random-time, no-eddy, across-swath).
- Data-source and access note.

### Stage 2
- Rim-conditioned composite figures for SST, chlorophyll, and PACE.
- Statistical comparison: rim-aligned vs. center-aligned composite strength under bootstrap.
- Multi-tracer synthesis figure.

## Feasibility and Risks

### Critical risks

- **SWOT small-scale SSH includes tides, internal waves, noise, and non-balanced motions.** The analysis must avoid interpreting every fine structure as a quasi-geostrophic eddy rim. Use L2 or L3 Expert/Unsmoothed products with documented noise characteristics. SWOT grid spacing (~2 km) is not the same as effective balanced-flow resolution — gradients and geostrophic speed require product-appropriate filtering.

- **Product-dependence risk**: L3 products may include processing choices and nadir information related to the conventional altimetry system. Use L2 or L3 Expert/Unsmoothed for primary rim detection; treat L3 Basic as a prototyping product.

- **SWOT temporal sampling is sparse.** The 21-day repeat cycle means each eddy is sampled at most a few times per year. Focus on spatial anatomy and snapshot co-location, not lifecycle evolution.

- **Resolution comparison must be fair.** Use region-dependent DUACS effective resolution rather than a single global number. The comparison should include filtering, mapping, masking, and filter-type sensitivity, not just a single low-pass cutoff.

- **High-impact claim requires Stage 2.** If Stage 1 rim signals are weak or inconsistent across regions, the project should publish as a resolution-sensitivity methods paper.

- **Chlorophyll rings are already documented (Xu et al. 2019).** The novelty is not "rings exist," but whether they correspond to a physically sharper, offset SSH rim visible only in SWOT. This distinction must be explicit.

### Manageable risks

- **Eddy–front intersection vs. self-contained rim.** Mitigate via residual-anomaly and front-conditioned tests (Step 1.5). Interpret eddy–front intersection as a physically meaningful mechanism rather than contamination.

- **Rim definitions may be subjective.** Mitigate by using `|∇SSH|` and geostrophic speed maxima — well-understood, physically grounded quantities — rather than novel complexity indices.

- **Tracer matchup sample size.** Use geostationary SST for higher temporal density; report sample sizes transparently by tracer, region, season, and lag window.

- **PACE record length.** PACE (launched 2024) has a short record. Use it as an exploratory case study rather than the sole Stage 2 tracer.

- **SWOT nadir gap.** The ~10 km nadir gap separates the two KaRIn swaths. Large eddies spanning the gap may have incomplete rim coverage. Flag and assess sensitivity.

- **Tracer product mismatch.** SST, chlorophyll, and PACE have different spatial resolution, cloud masks, retrieval errors, and response times. All tracer comparisons need product-specific quality flags and fair-resolution sensitivity tests.

- **Selection bias.** SWOT imagery is visually compelling; there is a real risk of selecting striking examples after seeing the data. Pilot eddies should be selected by pre-declared criteria where possible. Composite significance should be assessed by eddy-level bootstrap or permutation tests, not pixel-level sample size.

- **Tracer sign is not universal.** Chlorophyll response depends on region, season, mixed-layer depth, nutrients, and eddy history. Stage 2 should test rim localization separately from anomaly sign, with polarity, region, and season stratification.

## Contributor Role

The proposer is a mesoscale eddy researcher and can contribute:

- conceptualization of the eddy-rim hypothesis;
- domain-expert review of eddy dynamics and altimetry interpretation;
- literature verification across eddy-core compositing, chlorophyll rings, Lagrangian coherent structures, and SWOT validation;
- physical interpretation and reviewer-style risk assessment;
- validation of AI-generated scripts and figures.

## Progress Log

| Date | Stage | Content | Output |
|---|---|---|---|
| 2026-06-07 | D0 | Initial idea formed: SWOT-resolved eddy rims vs. AVISO/py-eddy-tracker eddy-core framework | README draft |
| 2026-06-08 | D0 | Review round 1: converged from "neglected boundary" to "active peripheral rim"; 3 core diagnostics + guardrails | Revised README |
| 2026-06-08 | D0 | Review round 2 (Codex): softened claims, split nulls, added decision gates, collaborator questions, expanded controls | Revised README |

## AI Interaction Log

Key prompt logs should be stored in `projects/p03/logs/` after the project is accepted into the repository.

## References (seed list — all citations require manual verification before manuscript use)

### Classic altimetry eddy framework
- Chelton, D. B., Schlax, M. G., & Samelson, R. M. (2011). Global observations of nonlinear mesoscale eddies. *Progress in Oceanography*, 91, 167–216. doi:10.1016/j.pocean.2011.01.002
- Chelton, D. B., Gaube, P., Schlax, M. G., Early, J. J., & Samelson, R. M. (2011). The influence of nonlinear mesoscale eddies on near-surface oceanic chlorophyll. *Science*, 334, 328–332. doi:10.1126/science.1208897
- Gaube, P., McGillicuddy, D. J., Chelton, D. B., Behrenfeld, M. J., & Strutton, P. G. (2014). Regional variations in the influence of mesoscale eddies on near-surface chlorophyll. *Journal of Geophysical Research: Oceans*, 119. doi:10.1002/2014JC010111

### Eddy rings, fronts, and tracer response
- Xu, G., Dong, C., Liu, Y., Gaube, P., & Yang, J. (2019). Chlorophyll rings around ocean eddies in the North Pacific. *Scientific Reports*, 9, 2056. doi:10.1038/s41598-018-38457-8
- Zhang, Z., Qiu, B., Klein, P., & Travis, S. (2019). The influence of geostrophic strain on oceanic ageostrophic motion and surface chlorophyll. *Nature Communications*, 10. doi:10.1038/s41467-019-10883-w
- Jones-Kellett, A. E., & Follows, M. J. (2025). The satellite chlorophyll signature of Lagrangian eddy trapping varies regionally and seasonally within a subtropical gyre. *Ocean Science*, 21, 1141–1166. doi:10.5194/os-21-1141-2025

### Eddy boundaries and coherent transport context
- Beron-Vera, F. J., Olascoaga, M. J., & Goni, G. J. (2008). Oceanic mesoscale eddies as revealed by Lagrangian coherent structures. *Geophysical Research Letters*, 35. doi:10.1029/2008GL033957
- Haller, G., & Beron-Vera, F. J. (2013). Coherent Lagrangian vortices: The black holes of turbulence. *Journal of Fluid Mechanics*, 731, R4. doi:10.1017/jfm.2013.391
- Abernathey, R., & Haller, G. (2018). Transport by Lagrangian vortices in the Eastern Pacific. *Journal of Physical Oceanography*, 48, 667–685. doi:10.1175/JPO-D-17-0102.1

### SWOT, DUACS, and eddy atlas data references
- Pegliasco, C., Delepoulle, A., Mason, E., Morrow, R., Faugère, Y., & Dibarboure, G. (2022). META3.1exp: A new global mesoscale eddy trajectory atlas derived from altimetry. *Earth System Science Data*, 14, 1087–1107. doi:10.5194/essd-14-1087-2022
- Dibarboure, G., Anadon, C., Briol, F., et al. (2025). Blending 2D topography images from the Surface Water and Ocean Topography (SWOT) mission into the altimeter constellation with the Level-3 multi-mission DUACS. *Ocean Science*, 21, 283–323. doi:10.5194/os-21-283-2025
- Wang, Y., Zhang, S., & Jia, Y. (2025). Enhanced resolution capability of SWOT sea surface height measurements and their application in monitoring ocean dynamics variability. *Ocean Science*, 21, 931–944. doi:10.5194/os-21-931-2025
- Archer, M., Wang, J., Klein, P., Dibarboure, G., & Fu, L.-L. (2025). Wide-swath satellite altimetry unveils global submesoscale ocean dynamics. *Nature*, 640, 691–696. doi:10.1038/s41586-025-08722-8
- AVISO/DUACS. (2024). SWOT Level-3 KaRIn Low Rate SSH Basic / Expert data products. CNES / AVISO+.
- Surface Water and Ocean Topography Mission. (2025). SWOT Level 2 KaRIn Low Rate Sea Surface Height Data Product, Version D. PO.DAAC. doi:10.5067/SWOT-SSH-D

### PACE / ocean color context
- Werdell, P. J., Behrenfeld, M. J., Bontempi, P. S., et al. (2019). The Plankton, Aerosol, Cloud, ocean Ecosystem Mission: Status, science, advances. *Bulletin of the American Meteorological Society*, 100, 1775–1794. doi:10.1175/BAMS-D-18-0056.1
