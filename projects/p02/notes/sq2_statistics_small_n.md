# SQ2 Statistical Framework for Small N (ClaudeB Notes)

> Working notes for Concern #2 (event count). If total Kelvin wave events N < 10, standard parametric tests have poor power. This note outlines viable alternatives.

## The Problem

SQ2 asks: "Do Kelvin/Yanai waves show statistically higher robustness than non-topological control modes?"

README_research v0.1 targets 3–5 "golden events" and proposes p < 0.05 as the significance threshold. With N=5 paired observations (Kelvin vs Rossby for same event), a paired t-test has very low power unless the effect size is enormous.

## Viable Approaches for Small N

### 1. Sign test (N ≥ 5 is minimum)

If all N events show Kelvin more robust than Rossby (i.e., all signs are positive), one-sided sign test:
- N=5, all same sign: p = 2⁻⁵ = 0.031 (significant at α=0.05)
- N=4, all same sign: p = 2⁻⁴ = 0.063 (not significant)

Implication: need N ≥ 5 with ALL events showing the expected direction. One exception kills significance.

### 2. Permutation test

For each event, compute ΔB = B_Rossby - B_Kelvin (backward-scattering difference). Under the null, the sign of ΔB is equally likely ±. Enumerate all 2^N sign permutations, compute the test statistic for each. This is exact (no distributional assumptions).

With N=5: 32 permutations, manageable. With N=10: 1024, still fine.

### 3. Bootstrap confidence intervals

Resample the N paired differences with replacement, compute the mean. Repeat 10,000 times. Report the 95% bootstrap CI for the mean difference. If CI excludes zero, declare significant.

Advantage: doesn't assume normality. Works for N ≥ 5. Reports effect size naturally.

### 4. Multiple metrics per event (multivariate)

Each event yields 4 metrics: B (scattering), C (coherence), M (mode conversion), L (leakage). Rather than testing each separately (multiple comparison problem), combine into a single "robustness score":

R = w₁(1-B) + w₂C + w₃(1-M) + w₄(1-L)

where weights w_i derived from OSSE (how much does each metric actually change between topological and non-topological modes in the synthetic experiment?).

Then test H₀: R_Kelvin = R_Rossby with a single paired test.

### 5. Effect size reporting (always do this)

Report Cohen's d = mean(ΔR) / sd(ΔR) regardless of p-value. NC audience cares about "how much more robust" not just "is it significant."

Guideline: d > 0.8 is "large effect." If d > 1.5 with N=5, the story is convincing even without p < 0.05.

## Recommendations for A

1. **Target N ≥ 8 events** (relax "golden event" criteria — not all need perfect SWOT coverage; some can be DUACS-only for the statistical comparison)
2. **Primary test**: permutation test on the multivariate robustness score R
3. **Always report**: effect size (Cohen's d) + bootstrap 95% CI
4. **OSSE calibration**: use OSSE to determine expected effect size → power analysis → confirm N is sufficient
5. **If N < 5**: shift SQ2 framing from "statistically significant difference" to "consistent with topological prediction in all observed cases" (descriptive, not inferential). Still publishable in NC if the Λ mechanism (SQ3) is strong.

## What NC Reviewers Expect

NC does not require p < 0.05 for all claims. For observational studies with limited sample size, they accept:
- Clear effect size with uncertainty quantification
- Multiple lines of evidence (Hovmöller + 2D structure + metrics consistency)
- OSSE showing the method can detect the effect if it exists
- Honest power analysis stating "we can detect effects of size d > X with N events"

The paper should NOT claim "statistical proof" with N=5. Frame as "observational evidence consistent with topological prediction" + "Λ framework provides mechanistic explanation."
