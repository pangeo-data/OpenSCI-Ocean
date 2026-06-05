# P01: SWOT View of Near-Surface Wind Kinetic Energy and Submesoscale Air-Sea Coupling

> This project asks how near-surface wind-speed kinetic energy seen by SWOT is distributed globally, why it is enhanced in western boundary current regions, and whether geostationary SST can reveal submesoscale air-sea coupling processes that traditional wind products miss.

## Status

| Item | Content |
|---|---|
| Current stage | D0 Explore |
| Lead / proposer | Kris19999 |
| Target journal | TBD; candidate journals include Geophysical Research Letters, Journal of Geophysical Research: Oceans, Ocean Modelling, and Remote Sensing of Environment |
| Start date | 2026-06-05 |
| Expected submission | TBD |

## Scientific Question

Where are submesoscale anomalies of near-surface wind kinetic energy concentrated in the global ocean from the SWOT perspective, why are they stronger in western boundary current regions, and can this enhancement be explained by submesoscale air-sea coupling over sharp SST fronts?

The central working idea is that western boundary current regions are already expected to host strong near-surface wind kinetic energy, but the mechanism and fine-scale structure may be underestimated by traditional wind products. By combining SWOT wind speed, SWOT KaRIn SSH, high-frequency geostationary SST, and legacy wind products, the project can test whether enhanced wind kinetic energy is organized around sharp SST fronts and SSH-resolved submesoscale structures. The Gulf Stream and Kuroshio Extension are natural test regions because they combine strong SST fronts, energetic mesoscale and submesoscale activity, and known atmosphere responses to oceanic thermal fronts.

The key scientific contribution is not only to map the distribution of SWOT-derived wind kinetic energy, but to explain why western boundary current hotspots are strong. The proposed explanation is that submesoscale SST fronts and ocean surface structures modulate near-surface winds through air-sea coupling, producing fine-scale wind kinetic energy anomalies that are difficult to resolve in conventional scatterometer or reanalysis products.

## Hypotheses

1. SWOT-derived near-surface wind kinetic energy anomalies are expected to be enhanced in western boundary current extensions, especially the Gulf Stream and Kuroshio Extension.
2. The enhancement is hypothesized to be partly caused by submesoscale air-sea coupling over sharp SST fronts, not only by large-scale atmospheric forcing.
3. Regions with strong wind-speed kinetic energy anomalies should have strong geostationary SST gradients and SWOT SSH gradients, suggesting coupling between oceanic submesoscale structures and atmospheric boundary-layer adjustment.
4. SWOT may reveal finer-scale wind-speed kinetic energy structures than traditional scatterometer or reanalysis wind products, particularly near fronts, filaments, and eddy edges.
5. Coupling metrics based on wind-speed gradients versus SST gradients, and cross-spectral coherence between wind-speed kinetic energy, SST, and SSH gradients, can distinguish frontal coupling signals from background wind variability.

## Data

All candidate datasets are public and reproducible. Raw data should not be committed to the repository; only download scripts, access notes, and processed figure outputs should be tracked.

- SWOT KaRIn Level-2 Low Rate SSH: global SSH / SSH anomaly on swath grids from PO.DAAC.
- GOES ABI SST / NOAA ACSPO SST: high-frequency SST over the Americas and the Gulf Stream sector.
- Himawari-8/9 AHI SST: high-frequency SST over the western Pacific and Kuroshio Extension sector.
- Public wind products, used as comparison and sensitivity datasets:
  - SWOT L2 wind speed / backscatter-derived wind information where appropriate.
  - ASCAT ocean vector winds, especially MEaSUREs-OSVW and MetOp ASCAT, for comparison with existing satellite wind views.
  - ERA5 10 m winds as a gridded background and sensitivity product.
  - CCMP ocean surface winds as an optional gridded comparison product.

## Method

The analysis should start from two regional pilot domains before attempting a global synthesis:

- Gulf Stream: GOES-East SST plus SWOT KaRIn SSH and public wind products.
- Kuroshio Extension: Himawari SST plus SWOT KaRIn SSH and public wind products.

Initial diagnostics:

1. Collocate SWOT swaths, geostationary SST, and wind products in space and time.
2. Derive along-swath SSH gradients from SWOT as indicators of fine-scale ocean structures.
3. Apply scale separation to isolate mesoscale and submesoscale bands, with sensitivity tests for filtering length scales.
4. Estimate near-surface wind-speed kinetic energy proxy from SWOT wind speed, for example `K10 = 0.5 * U10^2`, and analyze its anomaly and filtered components.
5. Compare SWOT-derived wind-speed kinetic energy structures with ASCAT, ERA5, and CCMP to identify what is new in the SWOT view and what traditional products may miss.
6. Compute air-sea coupling coefficients, especially regression slopes between wind-speed gradients and SST gradients, using GOES and Himawari SST for high-frequency frontal structure.
7. Use co-spectrum, coherence, and phase diagnostics to test whether SST fronts, SSH gradients, wind-speed gradients, and wind kinetic energy anomalies are scale aligned at submesoscales.
8. Compare Gulf Stream and Kuroshio Extension results against weaker-gradient control regions.

## Expected Outputs

- A D0 feasibility note with verified data access routes and literature map.
- Reproducible Python scripts for collocation, filtering, wind-speed kinetic energy proxy, coupling coefficients, and cross-spectral diagnostics.
- Candidate figures:
  1. SWOT swath coverage overlapping GOES/Himawari SST in the two pilot domains.
  2. Spatial distribution of filtered SSH/SST gradients and wind-speed kinetic energy anomalies.
  3. Regression-based coupling coefficients between wind-speed gradients and geostationary SST gradients for Gulf Stream and Kuroshio Extension.
  4. Cross-spectral coherence between SST gradients, SSH gradients, wind-speed gradients, and wind kinetic energy anomalies.
  5. A global/regional hotspot map comparing SWOT wind kinetic energy anomalies with previous wind products, highlighting fine-scale structures missing from traditional observations.

## Feasibility And Risks

- SWOT has excellent spatial resolution but limited revisit time, so collocation windows and sampling bias must be handled carefully.
- Geostationary SST is cloud-limited; composites or quality-controlled clear-sky sampling are required.
- This project focuses on near-surface wind-speed kinetic energy, not oceanic wind work `tau dot u_o`.
- SWOT wind speed gives wind-speed magnitude, so it can support `0.5 * U10^2`-type diagnostics but not vector wind stress curl/divergence unless external wind direction is added.
- Scatterometer and reanalysis winds may be too coarse for some submesoscale diagnostics; they should be used mainly to evaluate how the SWOT view differs from previous products.
- The mechanism claim must be tested carefully: western boundary current wind kinetic energy can reflect both atmospheric forcing and ocean-front-induced coupling.
- Geostationary SST is essential for the mechanism test because it can resolve high-frequency frontal structure that may be smeared in daily or coarse SST products.
- Causal language should be conservative: coupling signals can be identified, but mechanism attribution requires careful controls.
- AI-generated references must be manually verified before citation.

## Contributor Role

The proposer has worked on ocean submesoscale processes from the master's stage to the present, is affiliated with a National Science Fund for Distinguished Young Scholars team, and has published three related papers in journals including JGR and Ocean Modelling. The proposer can contribute domain-expert AI review, physical interpretation, figure processing, reference verification, and manuscript-level scientific correction, especially for submesoscale dynamics and submesoscale air-sea interaction.

## Progress Log

| Date | Stage | Content | Output |
|---|---|---|---|
| 2026-06-05 | D0 | Drafted local topic proposal and workflow scaffold | README, data source notes, analysis plan, literature seed, AI log |

## AI Interaction Log

See `logs/2026-06-05_D0_topic_proposal.md`.

## References

See `literature/literature_seed.md` for a seed list. Each reference must be manually checked before being moved into the manuscript bibliography.
