# P03 Reviewer Report — R0

**Manuscript:** Testing Neglected Eddy Boundary Signals with SWOT Altimetry
**Reviewer:** Anonymous (AI-simulated peer review)
**Date:** 2026-06-08

---

## Overall Assessment

This is a well-designed D0 proposal with unusually strong self-awareness — the Claims and Guardrails section is more honest than many published papers' Discussion sections. The two-stage design (altimetry-only Stage 1 → tracer response Stage 2) with explicit decision gates is commendable. However, several scientific and methodological concerns must be addressed.

## Major Issues

### 1. Novelty boundary: resolution improvement vs. new physics

The central risk is that Stage 1 confirms what is almost certain a priori: a higher-resolution instrument resolves sharper gradients. The proposal needs to answer: **what would be surprising?**

- If SWOT rim radius is systematically *smaller* than py-eddy-tracker effective radius → the conventional eddy-core paradigm overestimates eddy size. This has quantifiable consequences for transport estimates.
- If SWOT rim radius is systematically *larger* → eddies influence a wider region than previously thought.
- If the offset varies systematically with eddy age, polarity, or background shear → there is a dynamical story.

**Recommendation:** Define in advance what rim offset magnitude (in normalized units) would constitute a physically meaningful result vs. a trivially expected resolution difference.

### 2. Fair-resolution test logic

Step 1.3 proposes filtering SWOT to DUACS resolution as a null test. But this test has a logical asymmetry:
- If rim signals **disappear** after filtering → you've shown resolution matters (obvious)
- If rim signals **survive** after filtering → you've shown DUACS should have detected them but didn't (interesting, but raises questions about DUACS processing rather than rim physics)

The more informative test would be: does the rim offset *change continuously* as filter scale varies from 15 km to 200 km, or is there a critical scale where it appears/disappears abruptly? A phase-transition-like behavior would be far more interesting than a binary survives/disappears result.

### 3. Tracer composite confound with background fronts

Stage 2's biggest threat is not noise but signal contamination. In western boundary current regions (Kuroshio Extension, Gulf Stream), strong background SST fronts run parallel to the eddy propagation corridor. Eddies embedded in these fronts will show apparent rim-aligned tracer anomalies simply because the rim intersects the pre-existing front.

Step 1.5's background-front control is a good start but needs strengthening:
- The residual-anomaly test (subtract smoothed field) is sensitive to the smoothing scale choice.
- **Suggestion:** Add a "front rotation" control — rotate the background gradient direction by 90° and check whether rim-aligned tracer signals persist. If signals disappear when the front is perpendicular to the rim, the signal is front-driven, not rim-driven.

### 4. py-eddy-tracker as the AVISO baseline — is it fair?

py-eddy-tracker uses SSH contours to define eddies. The "effective radius" and "maximum-speed contour" from py-eddy-tracker are themselves resolution-dependent products of DUACS gridded SSH. Comparing SWOT-derived rim with py-eddy-tracker-derived radius is not purely a rim-vs-core test — it also embeds the DUACS gridding and py-eddy-tracker algorithm choices.

**Suggestion:** Include a sensitivity test where you apply py-eddy-tracker to SWOT SSH (degraded to various resolutions) rather than to DUACS, to separate the effect of the eddy detection algorithm from the SSH product.

### 5. PACE as exploratory — be honest about sample size

The proposal correctly flags PACE as exploratory, but the temptation to show beautiful PACE hyperspectral results will be strong. The minimum sample size threshold should be declared now (e.g., N ≥ 30 cloud-free collocations per region). If PACE cannot meet this threshold, it should be mentioned as future work, not included in figures.

## Minor Issues

- References: 13 citations listed, all need DOI verification. Archer et al. (2025, Nature) and Dibarboure et al. (2025, Ocean Science) are very recent — confirm they are formally published, not just preprints.
- D0 Checklist: all 7 items unchecked. Suggest setting a 2-week deadline for items 1–4 (data access verification) before committing to D1.
- The proposal mentions "3-region prototype figure set for collaborator discussion" — this is the most important near-term deliverable. Prioritize this over further proposal refinement.

## Summary

**Strengths:** Rigorous two-stage design; explicit guardrails and decision gates; honest about what each stage can and cannot claim; strong literature awareness.

**Weaknesses:** Core novelty risk (resolution improvement ≠ new physics); Stage 2 causal inference requires stronger null models; fair-resolution test needs more nuanced design.

**Recommendation:** Address major issues 1–3 before proceeding to D1. The proposal is strong enough that a well-executed Stage 1 prototype (even with 10–20 eddies in one region) would quickly clarify whether the rim story has legs.
