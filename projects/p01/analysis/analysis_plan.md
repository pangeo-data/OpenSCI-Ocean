# D0 Analysis Plan

## Working Title

SWOT view of near-surface wind kinetic energy and submesoscale air-sea coupling in western boundary current extensions

## Primary Research Question

Where are submesoscale anomalies of near-surface wind kinetic energy concentrated from the SWOT perspective, why are they stronger in western boundary current regions, and can geostationary SST reveal the submesoscale air-sea coupling mechanism behind this enhancement?

## Variables

- SSH / SLA from SWOT KaRIn
- SST from GOES ABI and Himawari AHI
- SWOT wind speed and wind-speed kinetic energy proxy
- Wind speed from ASCAT, ERA5, and/or CCMP for comparison with previous products
- Derived SST gradient magnitude, downwind SST gradient, and crosswind SST gradient
- Derived SSH gradient and optional SSH-gradient-based structure metrics
- Filtered wind-speed kinetic energy anomaly

## Candidate Diagnostics

### 1. Collocation

Create matched SWOT-SST-wind samples for the Gulf Stream and Kuroshio Extension.

- Start from SWOT pass time and swath coordinates.
- Extract nearest clear-sky geostationary SST images within candidate windows such as +/-30 minutes, +/-1 hour, and +/-3 hours.
- Extract wind products within the same window, or interpolate gridded wind products to the SWOT/SST grid.
- Preserve quality flags and sampling masks.

### 2. Filtering And Scale Separation

Apply spatial filtering to separate mesoscale and submesoscale bands.

- Candidate mesoscale band: wavelengths larger than 100 km.
- Candidate submesoscale band: approximately 10-100 km, adjusted for region, data resolution, SWOT noise, and filtering robustness.
- Use sensitivity tests for cutoff scales and filter shape.

### 3. Near-Surface Wind-Speed Kinetic Energy

Estimate a wind-speed kinetic energy proxy from SWOT wind speed:

```text
K10 = 0.5 * U10^2
```

where `U10` is near-surface wind speed. If air density is needed for dimensional energy density, use:

```text
E10 = 0.5 * rho_air * U10^2
```

The initial project does not estimate oceanic wind work `tau dot u_o`. The focus is the spatial distribution and submesoscale anomaly structure of wind-speed kinetic energy as seen by SWOT, and how that view differs from ASCAT, ERA5, CCMP, or other previous wind products.

### 4. Air-Sea Coupling Coefficients

Estimate coupling using regressions such as:

```text
|grad U10| = alpha |grad SST| + residual
|grad K10| = beta |grad SST| + residual
K10' = gamma SST_front_metric + residual
```

The user-proposed core variable, wind-speed gradient versus temperature gradient, should be treated as the first simple coupling metric. Curl/divergence metrics can be added later only if vector winds from external products are introduced.

The mechanism test should focus on whether local wind kinetic energy enhancement is statistically tied to high-frequency SST frontal structure:

- Stronger coupling coefficient in western boundary current regions than in weak-front control regions.
- Stronger coherence between `K10` anomalies and SST gradients at submesoscale bands in SWOT/geostationary-SST pairs than in traditional wind/SST products.
- Consistent alignment of wind-speed gradients with SST fronts across multiple SWOT passes, rather than isolated case-study coincidences.

### 5. Cross-Spectral Analysis

Use co-spectrum, coherence, and phase between:

- SST gradient and wind-speed gradient
- SST gradient and wind-speed kinetic energy anomaly
- SSH gradient and wind-speed kinetic energy anomaly
- SWOT wind-speed kinetic energy and previous-product wind-speed kinetic energy

This step tests whether the strongest coupling occurs at overlapping spatial scales rather than only in pointwise regressions.

## Pilot Workflow

1. Select one or more SWOT passes over the Gulf Stream and Kuroshio Extension, prioritizing strong SST-front conditions in GOES/Himawari imagery.
2. Download or access matching SST and wind data.
3. Produce a first collocation figure for each region.
4. Compute SST gradients, SSH gradients, wind-speed gradients, and `K10` anomalies.
5. Compare SWOT-derived `K10` structures against previous wind products.
6. Estimate regional air-sea coupling coefficients and compare them with weaker-front control regions.
7. Run a sensitivity test for filtering length scale and collocation time window.
8. Decide whether the D1 manuscript should remain a two-region mechanism study or expand to a global hotspot survey.

## Figure Plan

1. Map of candidate study regions and SWOT pass coverage.
2. Gulf Stream example: SST front, SWOT SSH gradient, wind-speed gradient.
3. Kuroshio Extension example: SST front, SWOT SSH gradient, wind-speed gradient.
4. Scatter/regression plot for wind-speed gradient versus SST gradient.
5. Cross-spectral coherence plot showing whether wind kinetic energy anomalies and SST fronts align at submesoscales.
6. Optional global hotspot map of SWOT near-surface wind kinetic energy anomaly and its difference from previous products.

## Human Review Priorities

- Verify whether the selected wind product can support the claimed spatial scale.
- Keep the diagnostic focused on near-surface wind-speed kinetic energy, not oceanic wind-work input.
- Separate "where is wind kinetic energy strong?" from "why is it strong?" so the coupling mechanism is tested rather than assumed.
- Check whether coupling signs match known physical mechanisms.
- Test sensitivity to rain/cloud flags, land contamination, and diurnal warming.
- Keep global claims separate from regional pilot evidence unless sampling is sufficient.
