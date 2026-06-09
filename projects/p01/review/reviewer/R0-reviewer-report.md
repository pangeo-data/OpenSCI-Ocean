# P01 Reviewer Report — R0

**Manuscript:** SWOT 揭示的亚中尺度海气耦合尺度依赖：基于 Gulf Stream 真实观测的 D1 初稿
**Reviewer:** Anonymous (AI-simulated peer review)
**Date:** 2026-06-09

---

## Overall Assessment

This D1 package demonstrates that the SWOT/GOES real-data collocation pipeline works, which is a legitimate engineering milestone. The manuscript's self-awareness about limitations is commendable — it repeatedly states what current results can and cannot prove. However, several fundamental scientific issues must be confronted before this project can advance. The most consequential is the circularity of using SWOT sigma0-derived wind speed to claim submesoscale air-sea coupling: sigma0 at fronts is contaminated by current-induced roughness changes, so the signal may not be atmospheric at all. Additionally, the gradient coupling diagnostic — the one test that actually probes submesoscale coupling — returns effectively zero signal in all three cases. This is not a minor caveat; it may be the most important result in the package.

## Major Issues

### 1. The circularity of SWOT sigma0-derived wind speed at ocean fronts

This is the single most critical issue for the entire project.

`wind_speed_karin` is derived from `sig0_karin` via an empirical geophysical model function (GMF), the same measurement principle as scatterometers but without multi-azimuth viewing geometry and without vector wind retrieval. At mesoscale, this works reasonably well because the atmosphere genuinely adjusts to SST anomalies, and the sigma0 signal is dominated by wind-driven roughness.

At submesoscale, the situation is fundamentally different. Ocean surface currents modulate sea surface roughness through current-wave interaction (wave refraction, straining, and blocking by currents). In the Gulf Stream, sharp SST fronts are co-located with sharp current fronts and SSH gradient maxima. When `wind_speed_karin` shows spatial structure at a front, three sources contribute to the sigma0 signal:

1. **Wind-driven roughness** (the signal you want): atmospheric boundary layer adjustment to SST anomaly
2. **Current-driven roughness** (contamination): surface current gradients modulating wave steepness and short-wave energy
3. **Rain/swell/sea-state contamination** (noise): especially problematic in the Gulf Stream's energetic wave environment

The project cannot distinguish (1) from (2) using SWOT data alone. If warm-side SST corresponds to the Gulf Stream jet (strong current, smooth surface downstream of front), the sigma0-derived wind speed could be *lower* on the warm side — not because the atmosphere is responding to SST, but because the current field is modulating surface roughness. This could explain why case 003_102 shows a negative SST-wind slope.

**Recommendation:** This circularity must be explicitly addressed in the README, the manuscript, and the analysis plan. Specifically:

- Add a section titled "Sigma0-wind separation challenge" to the README.
- In D2, compare SWOT wind_speed_karin with independent wind measurements (ASCAT, ERA5) at the same fronts. If ASCAT also shows wind enhancement at the front, the signal is likely atmospheric. If only SWOT shows it, it may be current-driven roughness.
- Consider using `sig0_karin` directly as the diagnostic variable rather than the derived wind speed, and discuss what sigma0 variations at fronts actually measure.
- The Kaouah et al. (2025) reference is essential here — if that paper addresses the sigma0/wind separation at submesoscale, it must be read carefully before proceeding.

### 2. Gradient coupling is zero — this is the most important result

The gradient regression results are:

```
003_048: grad slope = -0.026, r = -0.052
003_076: grad slope = -0.040, r = -0.038
003_102: grad slope =  0.016, r =  0.010
```

All slopes are near zero. All correlations are near zero. The manuscript acknowledges this but treats it as a minor caveat: "梯度回归目前较弱". In reality, this is the single most informative result in the entire D1 package, because the gradient diagnostic is the one that actually tests submesoscale coupling.

The point-to-point SST-wind regression (slope ≈ 1.14 m/s/°C for cases 048 and 076) is dominated by the large-scale cross-frontal contrast: cold shelf water (low wind) vs. warm Gulf Stream (high wind). This is well-known mesoscale coupling — or possibly just the large-scale meridional wind/SST co-gradient. It does not test submesoscale coupling.

The gradient diagnostic asks: at locations where SST changes sharply (fronts, filaments), does the wind speed also change sharply? The answer, in all three cases, is **no**. This has three possible interpretations:

1. The atmosphere does not respond to submesoscale SST structures (saturation/decay hypothesis).
2. SWOT sigma0-derived wind speed does not have sufficient spatial resolution or signal-to-noise ratio to detect submesoscale wind responses.
3. The Gaussian smoothing (sigma=1 pixel) applied in gradient computation, combined with the very different native resolutions of GOES SST (~2 km) and SWOT wind (~6 km posting but ~20+ km effective resolution for wind), destroys any real gradient coupling signal.

**Recommendation:** The zero gradient coupling should be elevated from a caveat to a central result. The manuscript should ask: is this a null detection (coupling doesn't exist at this scale), a sensitivity limit (SWOT wind speed cannot detect it), or a processing artifact (resolution mismatch and smoothing)? Each interpretation leads to a different D2 strategy.

### 3. Coherence values are spurious and must be removed

The reported peak coherence values are:

```
003_048: 0.996 at ~2.67 km
003_076: 0.999 at ~11.64 km
003_102: 0.988 at ~2.46 km
```

These are not physically plausible. Coherence of 0.996–0.999 between SST gradients and wind speed gradients at 2.5 km wavelength would imply near-perfect atmospheric response to the finest SST structures — contradicting the zero gradient slope found in the same data.

The problem is in `spectrum_summary()` (line 182–195 of the pipeline):

1. The function computes along-track means of gradient fields, producing one-dimensional series.
2. It calls `scipy.signal.coherence` with `nperseg=min(128, x.size)`.
3. For short series (a few hundred points), the effective degrees of freedom per frequency bin are very small (~2–4).
4. The Gaussian smoothing applied in `gradients_km()` (sigma=1 pixel) imposes shared spectral structure on both fields, inflating coherence at scales comparable to the smoothing kernel.
5. The "wavelength" is reported in pixel-index units, not in physical km — the conversion depends on the actual grid spacing, which varies along the SWOT swath.

Near-unity coherence at the smoothing scale is an artifact, not a signal. Publishing this figure as evidence of "spectral diagnostic worth continuing" is misleading.

**Recommendation:** Remove the coherence results entirely from the D1 package. If spectral diagnostics are to be pursued in D2, they must:

- Use 2D spectral analysis (wavenumber space), not 1D along-track averages
- Account for the different effective resolutions of SWOT wind (~20 km) vs. GOES SST (~2 km)
- Properly window and detrend
- Report degrees of freedom and confidence intervals
- Use synthetic test signals to validate the coherence estimation pipeline before applying it to real data

### 4. Point-to-point SST-wind regression does not test submesoscale coupling

The positive SST-wind slopes (1.14 m/s/°C) in cases 048 and 076 are presented as evidence consistent with "经典 warm SST-enhanced wind speed 框架". But this interpretation conflates two very different phenomena:

**Large-scale co-gradient:** The Gulf Stream separates cold continental shelf water (typically low wind speed in summer) from warm open-ocean water (typically higher wind speed). A positive SST-wind regression across the entire swath is expected from the large-scale atmospheric state, independent of any local air-sea coupling.

**Local coupling:** True SST-wind coupling means that *anomalous* SST (relative to the background) causes *anomalous* wind speed. To isolate this, you need to:

1. Remove the large-scale SST and wind gradients (e.g., subtract a 200 km low-pass field)
2. Compute the regression on anomalies
3. Test whether the anomaly regression is significant

The current pipeline does none of this. The regression is computed on raw SST and raw wind speed across the full swath window. The positive slope could be entirely explained by the synoptic-scale atmospheric gradient.

**Recommendation:** In D2:

- Compute anomalies by subtracting a spatially smoothed background (at least 100 km scale)
- Test SST-wind regression on anomalies at multiple scales (10, 20, 50, 100 km high-pass)
- If the anomaly regression is positive and significant at fine scales, THEN there is evidence for submesoscale coupling
- If the anomaly regression weakens or disappears at fine scales, that IS the regime transition (or at least coupling decay)

This is the actual test described in the README's Step 4 (scale-dependent coupling coefficients), but it was not implemented in D1.

### 5. Three cases from consecutive days is not a sample

All three cases are from September 2–4, 2023, within a single SWOT cycle, in the same season, likely under the same synoptic weather regime. This cannot support any statistical claim, even qualitative ones like "case dependency suggests scale dependence."

The case dependency could simply reflect:

- Different SWOT swath geometry and viewing angle
- Different GOES cloud coverage patterns
- A passing weather system that changed wind direction between September 2 and September 4
- Different parts of the Gulf Stream being sampled (case 003_102 is 20° east of the other two cases)

**Recommendation:** Before interpreting case variability as evidence for scale-dependent coupling:

- Check ERA5 for the synoptic weather state on September 2–4, 2023
- Map the three cases relative to Gulf Stream frontal position (from SSH or SST)
- Note that cases 048/076 are at 73–78°W while case 102 is at 52–55°W — these sample completely different oceanographic regimes (Gulf Stream separation zone vs. North Atlantic Current)
- D2 should aim for at least 20–30 cases across multiple seasons and multiple SWOT cycles

### 6. K10 = 0.5 * U² is computed but never meaningfully used

The wind kinetic energy proxy K10 is computed (line 221 of the pipeline) and its range is reported in the results JSON, but it is never analyzed for spatial structure, never compared to SSH/SST structures, and never decomposed by scale.

The README's Step 3 lists elaborate K10-based diagnostics (anomalies, gradients, collocation with SST/SSH gradients), but none are implemented. The figures show only raw SST, wind speed, SSHA, gradients, and the SST-wind scatter plot — no K10 panel.

**Recommendation:** Either:
- Implement K10 diagnostics as described in the README (spatial anomalies, gradient collocation, comparison with SSH structures), or
- Remove K10 from the current D1 scope and defer it to D2

Do not compute a variable that is only used to report its min/max range.

## Minor Issues

### 7. Hard-coded Windows paths break portability

The pipeline has:

```python
RAW = Path(r"D:\AI-try\data\p01")
```

The runbook references:

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\...\python.exe'
```

No one outside the original author's Windows machine can run this. Add a `config.yaml` or environment variable for the data root, and document the expected directory structure.

### 8. SST temperature conversion is fragile

Line 153:

```python
sst_out = np.where(sst_out > 100, sst_out - 273.15, sst_out)
```

This assumes any SST value > 100 is in Kelvin. GOES ACSPO L3C SST uses Kelvin by default, but the threshold of 100 could misclassify fill values, extreme interpolation artifacts, or other data products. Read the `units` attribute from the NetCDF file instead.

### 9. Figures lack geographic context

None of the case figures include coastlines, bathymetry contours, or the Gulf Stream path (e.g., from the 15°C isotherm at 200 m or the SSH-derived mean dynamic topography). Without geographic context, it is impossible to know whether the SWOT swath is sampling the Gulf Stream front, the Sargasso Sea, the continental shelf, or a mix. Case 003_048 appears to partially cover the shelf break near Cape Hatteras; case 003_102 appears to be in the open North Atlantic. These are fundamentally different oceanographic regimes.

### 10. GOES SST coverage is very low in case 003_048

Case 003_048 has only 12.8% SST coverage (2709 out of 21109 SWOT pixels). The SST panel in Figure 1 confirms that most of the swath has no SST. The high correlation (r = 0.88) in this case is based on a small, spatially clustered subset of the swath. This is not necessarily invalid, but the effective spatial degrees of freedom are much smaller than 2709, because adjacent pixels are strongly correlated.

### 11. Unverified reference

Kaouah et al. (2025) "Submesoscale Air-Sea Interactions as Revealed by SWOT" in GRL is flagged as needing manual DOI verification. This is the single most relevant reference for P01's core approach. It must be verified and read before D2 — if it already addresses SWOT sigma0-derived wind at submesoscale fronts, P01 must position itself relative to that work.

### 12. No time window sensitivity

The manuscript plans time-window sensitivity tests (Step 1) but none are implemented. The nearest GOES file is selected without checking the time gap. For case 003_048, the gap is ~37 minutes (SWOT 15:23 vs. GOES 16:00). For case 003_102, the gap is ~19 minutes (SWOT 13:40 vs. GOES 14:00). These are reasonable, but the sensitivity to time window choice should be documented.

## Summary

**Strengths:** Functional real-data pipeline; conservative QC approach; exceptional self-awareness about limitations; honest reporting of negative/ambiguous results; clear D2 roadmap.

**Weaknesses:** Fundamental circularity in using sigma0-derived wind to test air-sea coupling at fronts; zero gradient coupling signal not adequately interpreted; spurious coherence values; point-to-point regression conflates large-scale gradient with local coupling; sample size (n=3 cases from 3 days) cannot support any scientific inference.

**Recommendation:** Address major issues 1–4 before proceeding to D2. The zero gradient coupling result should be treated as the central finding of D1, not as a limitation. The most urgent action is to confront the sigma0 circularity head-on — if SWOT wind_speed_karin cannot be separated from current-driven roughness at submesoscale fronts, the entire project framing must change.
