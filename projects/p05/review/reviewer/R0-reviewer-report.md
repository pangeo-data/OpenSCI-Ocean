# P05 Reviewer Report — R0

**Manuscript:** SWOT KaRIn Constraints on the Deep Ocean Mixing Energy Deficit
**Reviewer:** Anonymous (AI-simulated peer review)
**Date:** 2026-06-08

---

## Overall Assessment

The energy deficit problem (Munk & Wunsch 1998) is a classic and important question. SWOT's submesoscale-resolving capability does offer a genuinely new observational window. However, the current manuscript has critical technical problems — most fundamentally, no real data is used — and the proposed methodology contains several physical leaps that are not adequately justified.

## Critical Technical Issues

### 1. Synthetic data invalidates all results

The analysis code `p05_analysis.py` contains zero data I/O. Every dataset is generated in-memory:

- `generate_synthetic_ssh()` (line 42): SSH field = Gaussian eddies + sinusoidal internal tides + white noise. The spectral properties are determined by the construction, not by ocean physics.
- Fig 1 energy flux (line 152): Six hotspot locations hardcoded as `(lon, lat, amplitude)` tuples. The "SWOT vs conventional altimetry" bar chart (line 191) uses manually assigned values.
- Fig 3 "SWOT vs microstructure" scatter plot (line 384): 60 random points generated with `rng.uniform(-5, -2, n_obs)`. The R-squared value (~0.97) is an artifact of the generation method (log-normal perturbation of self-correlated data), not a real validation.
- Fig 4 energy budget (line 448): All values (`mw_vals`, `swot_vals`) are hand-typed lists.

**Technical requirement:** Before any scientific review is meaningful, the analysis must use real data. Minimum viable analysis: download SWOT L3 SSH for one 10x10 degree box (e.g., South China Sea, 115-125E, 15-25N), compute the 2D wavenumber spectrum, and compare with CMEMS DUACS gridded SSH for the same region/period.

### 2. Internal tide separation — the unsolved prerequisite

The manuscript assumes that internal tide SSH signals can be cleanly extracted from total SSH anomaly. In reality, this is one of the hardest problems in satellite altimetry:

**Coherent internal tides:** These are phase-locked to astronomical forcing and can be extracted by harmonic analysis over long time series. Zhao et al. (2016) needed 20+ years of along-track data. SWOT has ~2 years with 21-day repeat — insufficient for reliable harmonic fitting, especially for separating M2 from S2 (period difference requires ~14.7-day temporal resolution, which 21-day repeat cannot provide).

**Incoherent internal tides:** Modulated by mesoscale eddies, these are not phase-locked and appear as broadband noise in the SSH spectrum. They are inseparable from balanced (geostrophic) submesoscale motions in a single SSH snapshot.

**Technical requirement:** The manuscript must explicitly state:
- Which internal tide component (coherent, incoherent, or total) is being estimated
- What temporal filtering / harmonic analysis method is used
- How the method handles the aliasing of M2/S2 with SWOT's 21-day repeat
- What fraction of the 15–50 km SSH variance is attributable to internal tides vs. balanced motions vs. near-inertial waves

Without this separation, "submesoscale SSH variance" cannot be equated with "internal tide energy."

### 3. Wavenumber spectrum → energy flux: missing transfer function

The manuscript proposes: SSH wavenumber spectrum E(k) → energy cascade rate → internal tide energy flux. The physical gaps:

**(a) SSH spectrum is not an energy spectrum.** SSH variance spectral density has units of m²/(cycles/m). Converting to kinetic energy spectral density requires assuming geostrophic balance: `KE(k) = (g/f)² × k² × SSH_spectrum(k)`. But at 15–50 km wavelengths, geostrophic balance breaks down — ageostrophic motions (internal waves, near-inertial oscillations, tidal currents) contribute significantly to SSH variance but have different energy-flux relationships.

**(b) Spectral slope ≠ energy cascade rate.** The manuscript states "SWOT SSH wavenumber spectral slope can directly diagnose energy cascade efficiency." This is only true under specific assumptions (isotropic, homogeneous, statistically stationary turbulence with a known cascade direction). In the real ocean near internal tide generation regions, the spectrum reflects a superposition of forced internal tides, freely propagating internal waves, and balanced eddies — each with different spectral slopes and cascade properties. A single spectral slope cannot uniquely determine the cascade rate.

**(c) Horizontal energy flux ≠ vertical energy flux to deep ocean.** Even if horizontal internal tide energy flux is correctly estimated from SSH, the fraction that propagates vertically to produce deep mixing depends on: topographic roughness spectrum, background stratification profile, internal wave-wave interaction rates, and local dissipation. These are not observable from SWOT.

**Technical requirement:** Either (i) restrict claims to horizontal surface energy flux (what SWOT can actually constrain) and avoid the vertical-to-deep inference, or (ii) incorporate Argo N² profiles and a parameterization framework (e.g., de Lavergne et al. 2019) with fully propagated uncertainties.

### 4. Garrett & Kunze parameterization misapplication

The Methods section lists "Garrett & Kunze parameterization → K_rho constraint." The G&K parameterization estimates turbulent dissipation rate from the finescale (10–100 m vertical) internal wave shear/strain spectrum. It requires:
- Vertical profiles of velocity shear and/or density strain (from CTD, LADCP, or Argo)
- Assumption of a Garrett-Munk background internal wave spectrum
- Correction for latitude, stratification, and distance from generation sites

None of these inputs come from satellite SSH. The G&K parameterization cannot be applied to horizontal SSH wavenumber spectra — it operates in the vertical wavenumber domain on completely different physical quantities.

**Technical requirement:** Either (i) use Argo float profiles to compute finescale parameterization K_rho independently and compare with SWOT-derived surface energy flux as a cross-validation, or (ii) remove the G&K parameterization from the methodology and use a different approach to connect surface observations to mixing estimates.

### 5. South China Sea as study region — good choice, with caveats

The README identifies the South China Sea as the "best case study region." This is reasonable — Luzon Strait is the strongest internal tide generation site globally, with:
- Well-documented mode-1 M2 internal tide (Zhao et al. 2016)
- Extensive mooring observations (Alford et al. 2015)
- Strong submesoscale activity

However, the South China Sea is also one of the most complex internal wave environments on Earth — multiple generation sites, mode conversion at the continental shelf, interaction with Kuroshio intrusion, and strong mesoscale-internal tide interaction. Extrapolating from this extreme case to a global energy budget would be unjustified.

**Technical recommendation:** Frame the South China Sea analysis as a regional case study that demonstrates SWOT's capability, not as a representative sample for global budget estimation.

## Minor Technical Issues

- The Okubo-Weiss calculation (line 127) uses `np.gradient` with grid spacing in the wrong axis order — `np.gradient(u, dy, dx)` computes `du/dy` and `du/dx`, but the comment says "du_dx, du_dy". Verify axis conventions when real data is used.
- The geostrophic velocity calculation (line 89) uses a single Coriolis parameter at 22°N. For a regional study this may be acceptable, but for any analysis spanning more than ~5° latitude, the beta-plane approximation should be used.
- Spectral analysis (line 98) uses a raw 2D FFT without windowing. Real SSH data will have edge effects and gaps — use a multitaper or Welch method with appropriate windowing.
- AI interaction log (README line 69) references "P02" path, not "P05" — template copy error.

## Feasibility Assessment

| Component | Feasibility | Timeline estimate |
|---|---|---|
| SWOT L3 data download for South China Sea | High — data publicly available | 2 days |
| 2D wavenumber spectrum computation | High — standard FFT analysis | 3 days |
| Internal tide separation (coherent component) | Medium — needs harmonic fitting, short record is limiting | 1–2 weeks |
| Comparison with conventional altimetry spectrum | High — CMEMS DUACS readily available | 3 days |
| Argo N² profiles for vertical structure | High — Argo coverage in SCS is good | 3 days |
| G&K finescale parameterization from Argo | Medium — requires careful Argo profile selection and QC | 1 week |
| Global energy budget closure claim | Low — far beyond what one regional study can support | Not recommended |

## Summary

**Strengths:** Classic and important problem; SWOT genuinely offers new observational capability at relevant scales; South China Sea is a well-chosen study region with rich ancillary data.

**Weaknesses:** No real data used; SSH-to-deep-mixing inference chain has multiple broken links; Garrett & Kunze parameterization cannot be applied to horizontal SSH spectra; global budget claim vastly exceeds the scope of a regional satellite study.

**Recommendation:** Major revision with substantially reduced scope. Focus on what SWOT can uniquely contribute: the first high-resolution 2D SSH wavenumber spectrum in a key internal tide generation region, with quantification of the additional variance in the 15–50 km band compared to conventional altimetry. Cross-validate with Argo-derived finescale estimates. Do not claim to close the global energy budget.
