# P02: Robustness and Breakdown of Topological Equatorial Waves in the Real Ocean Revealed by SWOT Altimetry

> Does the topological protection predicted for equatorial Kelvin and Yanai waves leave observable dynamical fingerprints in the real, turbulent ocean — and under what conditions does it break down?

## Status

| Item | Content |
|---|---|
| Current stage | 🔬 D0 Explore (候选 / candidate) |
| Lead / proposer | (待确认) |
| Target journal | Nature Communications (primary) |
| Start date | 2026-06-07 |
| Expected submission | TBD |

## D0 Priority Checklist

- [ ] Download SWOT L3 SSH for equatorial Pacific (5°S–5°N, 130°E–80°W); build SSH anomaly Hovmöller diagram along equator
- [ ] Identify eastward-propagating Kelvin wave events from Hovmöller (phase speed ~2.5 m/s); cross-check with ERA5/CCMP wind stress anomalies for western Pacific wind burst sources
- [ ] Verify SWOT KaRIn swath coverage and revisit frequency in equatorial Pacific; estimate number of usable Kelvin wave "snapshots" from science orbit (2023–2025)
- [ ] Download DUACS/AVISO gridded SSH for temporal gap-filling; assess complementarity with SWOT spatial resolution
- [ ] Literature search: existing observational work on equatorial Kelvin/Yanai wave robustness, topological wave theory extensions beyond Delplace et al. 2017, and SWOT-based equatorial wave studies
- [ ] Assess whether 2D meridional structure of Kelvin waves (equatorial trapping, Gaussian e-folding) is resolvable in SWOT KaRIn swath data
- [ ] Identify strong perturbation regions along equatorial Pacific: TIW-active zones, island chains (Gilbert/Line Islands), cold tongue front, strong shear zones

## Scientific Question

Delplace, Marston & Venaille (2017, Science) showed that equatorial Kelvin and Yanai waves have a topological origin: they are edge modes protected by the sign reversal of the Coriolis parameter across the equator, with the bulk Poincaré wave modes carrying non-trivial Chern numbers (±2). This elegant theory was derived from the idealized rotating shallow water model.

But the real ocean is not a clean shallow water system. Equatorial waves encounter wind forcing, background shear, strong eddies, tropical instability waves (TIW), island chains, internal tides, cold tongue fronts, dissipation, and nonlinear wave-wave interactions. The central question is:

**Does the theoretical topological protection leave observable dynamical fingerprints in the real ocean? When is it effective, and when does it fail?**

This is not about proving "the ocean is a topological insulator" — it is about quantifying the conditions under which the topological robustness prediction holds or breaks down, using the first 2D wide-swath SSH observations from SWOT.

## Hypotheses

1. **H1: Observable topological fingerprints exist.** SWOT 2D SSH fields can resolve the meridional-zonal structure of equatorial Kelvin/Yanai waves, and their propagation speed, trapping scale, and frequency-dispersion characteristics are consistent with equivalent shallow water theory.

2. **H2: Kelvin/Yanai waves show statistically higher propagation robustness than non-topological control modes.** When traversing TIW, island chains, or background shear zones, Kelvin/Yanai waves retain higher downstream phase coherence and lower backward-scattering energy than Rossby/TIW/eddy signals under comparable perturbation strength.

3. **H3: Topological protection is conditional, not absolute.** The robustness is controlled by an effective gap-to-perturbation ratio Λ = Δω_eff / (perturbation strength). When Λ >> 1, protection holds (high coherence, low scattering); when Λ ~ 1, protection fails (mode conversion, equatorial leakage, coherence loss).

## Data

All datasets are public. Raw data must not be committed; only download scripts, access notes, and processed outputs are tracked.

**Primary datasets:**

- **SWOT KaRIn L2/L3 LR SSH** (PO.DAAC / AVISO): wide-swath 2D sea surface height — the core observational innovation. L3 for rapid prototyping; L2 Expert for error control and sensitivity analysis.
- **DUACS/AVISO gridded SSH** (CMEMS): traditional along-track altimetry products for temporal gap-filling (SWOT science orbit ~21-day repeat is sparse for equatorial wave tracking).
- **Sentinel-6/Jason series SSH**: along-track data for Hovmöller-based Kelvin wave identification and phase speed estimation.

**Supporting datasets:**

- **ERA5/CCMP wind stress**: identify western Pacific wind burst sources that generate Kelvin wave events.
- **TAO/TRITON mooring array**: in-situ validation of equatorial wave passage (subsurface temperature, currents).
- **Argo profiles**: thermocline depth and stratification for equivalent shallow water phase speed estimation.
- **GLORYS/ECCO/HYCOM reanalysis**: background current fields, relative vorticity, and shear for perturbation strength estimation.
- **SST (OSTIA/OISST)**: TIW identification and cold tongue front tracking.
- **Bathymetry (GEBCO)**: island chain locations and topographic interaction zones.

**Synthetic datasets (OSSE):**

- 1.5-layer or multi-layer equatorial shallow water model to generate synthetic Kelvin, Yanai, Rossby, and TIW-like signals.
- Sampled along SWOT orbital tracks with KaRIn-like noise added.
- Used to validate the AI decomposition method — without OSSE, AI-separated signals lack credibility.

## Method

### Module A: Equatorial wave event catalog

Build event catalog using traditional methods (no AI dependency at this stage):

1. Construct SSH anomaly Hovmöller diagrams along equatorial Pacific
2. Identify eastward-propagating Kelvin wave events (phase speed ~2.5 m/s)
3. Confirm sources via wind stress anomaly (western Pacific wind bursts)
4. Use SWOT 2D swath data to extract meridional structure of identified events
5. Search for Yanai wave candidates in 2D longitude-latitude SSH structure
6. Annotate strong perturbation zones traversed by each event (TIW, islands, cold tongue fronts, strong shear)

Event catalog fields: event ID, time, source region, propagation path, phase speed, amplitude, meridional e-folding scale, perturbation types encountered, upstream/downstream analysis windows, data coverage quality.

### Module B: Physics-guided AI mode decomposition

A physics-guided multimodal decomposition framework (not a black-box deep learning model). Inputs: SSH_SWOT, SSH_DUACS, wind stress, SST, surface currents, buoyancy frequency, bathymetry.

Output decomposition: η = η_K + η_Y + η_R + η_TIW + η_sub + η_tide + ε

Physical constraints in loss function:
- Reconstruction accuracy (L_rec)
- Frequency-dispersion relation (L_disp) — each mode should follow its theoretical dispersion
- Equatorial meridional trapping (L_meridional) — Kelvin/Yanai confined to equatorial waveguide
- Propagation direction (L_direction) — Kelvin/Yanai eastward
- Energy conservation or weak dissipation (L_energy)
- Uncertainty quantification (L_uncertainty)

Architecture recommendation: U-Net/ConvLSTM reconstruction + physics-guided latent decomposition + uncertainty ensemble.

OSSE validation is critical: train and validate on synthetic data before applying to real observations.

### Module C: Topological robustness metrics

Four diagnostic quantities:

1. **Backward-scattering index** B = E_west / (E_east + E_west) — topologically robust modes should maintain low B after traversing perturbation regions
2. **Phase coherence retention** C = |⟨A_up · A*_down⟩| / √(⟨|A_up|²⟩⟨|A_down|²⟩) — coherence between upstream and downstream complex amplitudes
3. **Mode conversion rate** M = (E_R + E_TIW + E_sub) / (E_K + E_Y + E_R + E_TIW + E_sub) — energy transferred to non-topological modes
4. **Equatorial leakage rate** L = E(|y| > y_c) / (E(|y| < y_c) + E(|y| > y_c)) — energy escaping the equatorial waveguide

Compare all four metrics: Kelvin/Yanai vs. Rossby/TIW under matched perturbation strength. The statistical advantage of topological modes over non-topological control modes is the core evidence.

### Module D: Effective topological control parameter

Λ = Δω_eff / (|∂_y U| + |ζ| + α·E_IT + β·E_sub + γ·D)

Where Δω_eff is the effective modal frequency gap, |∂_y U| is background shear, |ζ| is relative vorticity, E_IT is internal tide energy, E_sub is submesoscale perturbation strength, D is dissipation/observational residual.

Test the framework:
- Λ >> 1 → high coherence, low scattering (topological protection holds)
- Λ ~ 1 → mode conversion, leakage, coherence loss (protection breaks down)

This parameter elevates the paper from case studies to a generalizable mechanism.

## Research Roadmap

### Phase 1: Feasibility verification (first priority)

Goal: confirm SWOT can see equatorial Kelvin/Yanai wave events. Download equatorial Pacific SWOT L3/L2 SSH; build 2023–2025 SSH anomaly; construct Hovmöller diagrams; identify Kelvin wave events using DUACS + wind forcing; extract SWOT 2D meridional sections.

Deliverable: a set of clear event identification figures. **If this step fails, do not force the topological story.**

### Phase 2: OSSE and AI decomposition

Goal: validate AI decomposition reliability. Build equatorial shallow water model; generate synthetic Kelvin/Yanai/Rossby/TIW signals; add SWOT-like noise and sampling; compare AI decomposition against traditional methods (EOF, wavenumber-frequency filtering); quantify uncertainty.

Deliverable: AI method validation figures and error tables.

### Phase 3: Real event robustness diagnostics

Goal: quantify Kelvin/Yanai robustness in the real ocean. Build event catalog; annotate perturbation zones; compute backward-scattering index, phase coherence, equatorial leakage, mode conversion rate; compare with Rossby/TIW control modes.

Deliverable: statistical evidence for topological robustness (or lack thereof) in the real ocean.

### Phase 4: Unified mechanism

Goal: elevate from case studies to theoretical framework. Estimate equivalent shallow water phase speed; estimate effective spectral gap Δω_eff; compute background shear, vorticity, internal tide energy, submesoscale perturbation; construct Λ; test Λ vs. robustness metrics across events; find breakdown threshold.

Deliverable: mechanism figure showing Λ as a unifying parameter across events, ocean basins, and perturbation types.

## Expected Outputs

Planned figures for the manuscript (following NC format):

1. **Figure 1: Theory and observational framework** — equatorial Coriolis parameter reversal, Kelvin/Yanai as topological edge modes, SWOT wide-swath SSH observation, real-ocean perturbations, research goal (robustness + breakdown)
2. **Figure 2: SWOT-observed equatorial wave 2D structure** — Kelvin/Yanai event SSH anomaly maps, Hovmöller diagrams, phase speed estimates, meridional profiles, comparison with shallow water theory
3. **Figure 3: AI decomposition validation** — OSSE truth vs. SWOT-sampled vs. AI-reconstructed vs. traditional filtering, error bars and uncertainty
4. **Figure 4: Topological robustness observational evidence** — Kelvin/Yanai traversing perturbation regions, upstream/downstream coherence, backward-scattering index, mode conversion rate, comparison with Rossby/TIW controls (the main figure)
5. **Figure 5: Robustness breakdown mechanism and unified parameter** — Λ vs. coherence/scattering/conversion/leakage across events, perturbation types marked (eddies, TIW, islands, shear, internal tides), breakdown threshold identification

## Feasibility and Risks

**Critical risks:**

- SWOT temporal sampling (~21-day repeat) may be too sparse to track fast equatorial Kelvin waves (~2.5 m/s, crossing Pacific in ~2 months). Mitigation: combine with DUACS daily gridded products and along-track altimetry for event identification; use SWOT only for 2D spatial structure snapshots.
- AI mode decomposition reliability — separating overlapping equatorial wave modes from real SSH is extremely challenging. Mitigation: OSSE validation is mandatory; physical constraint losses provide guardrails; compare with traditional methods.
- Reviewers may argue that observed robustness can be explained by classical equatorial wave theory without invoking topology. Response: the Λ parameter directly connects the topological spectral gap to observed robustness breakdown, providing explanatory power that classical Hovmöller tracking lacks.
- The effective spectral gap Δω_eff in the real ocean is much less clean than in the idealized model. The definition and estimation method need careful justification.

**Manageable risks:**

- Cross-disciplinary barrier (topological physics + physical oceanography): proposer should clarify theoretical physics background or identify collaborators.
- Equatorial Pacific SWOT data quality: KaRIn near-equatorial performance needs assessment (geoid model accuracy, tidal corrections).
- If topological robustness advantage is not statistically significant, pivot to documenting the perturbation-response budget of equatorial waves without the topological framing.

## Contributor Role

(Pending — proposer to confirm background and contribution scope)

## Progress Log

| Date | Stage | Content | Output |
|---|---|---|---|
| 2026-06-07 | D0 | Participant submitted 14-page research proposal with reference paper (Delplace et al. 2017, Science) | Proposal PDF + README |

## AI Interaction Log

See `logs/` for detailed interaction records.

## References

Verified references:

- Delplace, P., Marston, J. B., & Venaille, A. (2017). Topological origin of equatorial waves. *Science*, 358, 1075–1077. DOI: 10.1126/science.aan8819 ✓ (verified — reference paper provided by proposer)

References to verify from proposal:

- Bulk-interface correspondence for equatorial waves (JFM follow-up to Delplace 2017)
- SWOT mission overview (NASA/JPL)
- SWOT ocean products documentation (PO.DAAC, AVISO)
