# P01 Editorial Decision — R0

**Journal:** Nature Communications / GRL / JGR: Oceans
**Manuscript:** SWOT 揭示的亚中尺度海气耦合尺度依赖：基于 Gulf Stream 真实观测的 D1 初稿
**Decision: Major Revision required before D2 advancement**
**Date:** 2026-06-09

---

Dear Authors,

Thank you for submitting the D1 real-data pilot package. The engineering achievement — building a functional SWOT/GOES collocation pipeline with conservative QC — is acknowledged. The manuscript's intellectual honesty about its limitations is well above average for an AI-assisted draft. However, the reviewer has identified several issues that must be resolved before D2 can proceed productively.

## 1. The sigma0 circularity must be resolved as a gating question

The reviewer correctly identifies that `wind_speed_karin` is derived from `sig0_karin`, and that sigma0 at ocean fronts reflects both wind-driven and current-driven surface roughness. At submesoscale, current effects on sigma0 may dominate wind effects, making it impossible to claim "submesoscale wind response to SST" from SWOT data alone.

**Required before D2:**

- Read and cite Kaouah et al. (2025) — if it exists, it likely addresses this exact issue
- For the existing 3 cases, download ERA5 10 m wind at the SWOT pass times. If ERA5 shows no wind anomaly at the front but SWOT does, the SWOT signal is likely current-driven roughness, not atmospheric coupling
- Add a "Sigma0 interpretation" section to the README that explicitly states what `wind_speed_karin` can and cannot tell us at submesoscale fronts
- If the circularity cannot be broken, consider pivoting the project to "SWOT sigma0 as a multi-signal probe of submesoscale ocean-atmosphere boundary" rather than "SWOT wind speed reveals submesoscale air-sea coupling"

## 2. The zero gradient coupling is the real D1 result — frame it accordingly

The gradient regression (|grad SST| vs. |grad wind|) is effectively zero in all three cases. This is the diagnostic that tests submesoscale front-driven coupling, and it returned a null result. The manuscript buries this as "梯度耦合信号尚不稳健" (Section 4.3), but it should be the central conclusion:

> The D1 pilot found no evidence of submesoscale gradient coupling between SWOT wind speed and GOES SST in the Gulf Stream. This null result may reflect: (a) genuine absence of atmospheric response at these scales, (b) insufficient SWOT wind speed resolution, or (c) sigma0 contamination by current-driven roughness.

This framing is more honest and more publishable than "the pipeline works, stay tuned." A well-characterized null result is a contribution; a vague "needs more data" is not.

## 3. Remove the spurious coherence results

Peak coherence of 0.996–0.999 is an artifact of shared Gaussian smoothing and low degrees of freedom. Including these numbers — even with caveats — damages the credibility of the package. Remove them entirely from the D1 deliverables. Spectral analysis should be rebuilt from scratch in D2 with proper 2D methods, windowing, and synthetic validation.

## 4. Separate large-scale gradient from local coupling before claiming SST-wind relationship

The positive SST-wind slope (~1.14 m/s/°C) may simply reflect the shelf-to-open-ocean atmospheric gradient, not local air-sea coupling. Before this can be cited as evidence of coupling, the analysis must:

- Subtract a large-scale background from both SST and wind speed
- Recompute the regression on anomalies
- If the anomaly regression vanishes, the original slope was not coupling evidence

This is not a D2 task — it should be done immediately on the existing 3 cases, as it determines whether the current pipeline output has any coupling content at all.

## 5. Expand the sample before interpreting case variability

Three cases from September 2–4 in the same SWOT cycle cannot support claims about case dependency. Moreover, cases 048/076 and case 102 are geographically separated by ~20° of longitude and sample different oceanographic regimes. The negative slope in case 102 may simply reflect a different ocean basin, not "背景状态调制."

## Journal fit assessment

In its current state, the D1 package is a data engineering demonstration, not a scientific manuscript. The pathway to each target journal:

- **Nature Communications:** Requires a demonstrated regime transition with statistical significance across multiple regions. Current distance: very large. The sigma0 circularity must be resolved first, and the zero gradient coupling result is working against the NC story.
- **GRL:** A well-characterized null result ("SWOT wind speed does not detect submesoscale air-sea coupling in the Gulf Stream — here is why") could work as a 4-figure GRL letter if the reasons (resolution limit, sigma0 contamination, coupling physics) are cleanly separated.
- **JGR: Oceans:** A methods paper on SWOT/geostationary SST collocation and the challenges of submesoscale sigma0 interpretation could be publishable if accompanied by 30+ cases across multiple regions and seasons.

The most realistic near-term publication path may not be the one the proposal envisions (regime transition revealed by SWOT), but rather a methodological contribution that honestly characterizes what SWOT wind speed can and cannot tell us about submesoscale air-sea coupling.

---

## Recommended D2 priority list

1. **Resolve the sigma0 circularity** — ERA5/ASCAT comparison at the 3 existing cases. This is the gating question.
2. **Recompute SST-wind regression on anomalies** — subtract 100+ km low-pass background from both fields.
3. **Remove spurious coherence** — delete from D1 outputs; rebuild spectral pipeline in D2 with synthetic validation.
4. **Expand to 20+ cases** across at least 2 SWOT cycles, including winter cases (stronger fronts, stronger coupling).
5. **Add geographic context** — coastlines, bathymetry, Gulf Stream path in all figures.
6. **Verify Kaouah et al. (2025)** — this reference is critical for positioning P01.
7. **Implement the scale-dependent coupling test** described in README Step 4 — this is the core science, and it has not been attempted yet.
8. **Confront the zero gradient result** — is it a physical null, a resolution limit, or a processing artifact? Design a targeted test to distinguish these.

---

I encourage the authors to treat the sigma0 circularity and the zero gradient coupling as the two defining issues of this project. If both can be resolved — sigma0 wind can be validated at submesoscale, and gradient coupling can be detected after proper background removal — the project has genuine potential. If not, a well-argued negative result is still publishable and still contributes to the field.

Sincerely,
*Editorial Office*
