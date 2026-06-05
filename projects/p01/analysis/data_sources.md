# Data Sources For P01

This file lists candidate public datasets for a D0 feasibility check. Raw data should not be committed to the repository.

## Primary Ocean Data

### SWOT KaRIn Level-2 Low Rate SSH

- Provider: NASA PO.DAAC / CNES / SWOT mission
- Candidate product: SWOT_L2_LR_SSH_D and sub-collections such as Basic, Expert, WindWave, and Unsmoothed
- Coverage: global ocean swaths; science phase begins after the 2023 fast-sampling/calibration phase
- Variables of interest: sea surface height, sea surface height anomaly, significant wave height, wind speed, quality flags, swath coordinates
- Access route: PO.DAAC / Earthdata
- Notes: SSH gradients can support surface geostrophic-current proxies, but submesoscale interpretation requires filtering and quality control.

Official entry:
https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D

## Primary SST Data

### GOES ABI SST / NOAA ACSPO

- Provider: NOAA CoastWatch / NOAA STAR
- Candidate product: ACSPO Global SST from ABI, including GOES-East and GOES-West
- Region: Americas and adjacent oceans; relevant for the Gulf Stream
- Variables of interest: SST, quality flags, clear-sky mask, SSES uncertainty, reference SST differences
- Notes: High temporal sampling is central to the mechanism test because it can resolve frontal structure and short-time-scale SST variability that may explain SWOT wind kinetic energy anomalies. Cloud masking and diurnal warming must be handled.

Official entries:
https://coastwatch.noaa.gov/cwn/processing-algorithms/acspo.html
https://coastwatch.noaa.gov/cwn/products/acspo-global-sst-abi.html

### Himawari-8/9 AHI SST

- Provider: JAXA P-Tree / JAXA Himawari Monitor, with related GHRSST/ACSPO products available through other public portals
- Region: western Pacific; relevant for the Kuroshio Extension
- Variables of interest: SST, quality flags, cloud mask
- Notes: High-frequency SST enables frontal evolution and collocation with SWOT passes. It is required to test whether wind kinetic energy enhancement near the Kuroshio Extension can be linked to submesoscale SST-front coupling. Clear-sky sampling bias must be evaluated.

Official entry:
https://earth.jaxa.jp/en/data/2529/index.html

## Wind Data For SWOT View And Comparison

### SWOT wind speed / backscatter-related wind information

- Provider: SWOT / PO.DAAC
- Use: primary same-swath estimate of near-surface wind speed and wind-speed kinetic energy proxy
- Derived metric: `K10 = 0.5 * U10^2`, with optional `E10 = 0.5 * rho_air * U10^2`
- Limitation: SWOT wind speed is primarily a wind-speed magnitude product; it does not by itself provide vector wind stress or oceanic wind-work input.

### ASCAT Ocean Vector Winds

- Provider: EUMETSAT OSI SAF / KNMI, distributed through PO.DAAC
- Candidate products: MetOp-B/C ASCAT L2 winds; MEaSUREs-OSVW wind vectors and wind stress
- Variables of interest: 10 m wind speed and vector winds
- Notes: Useful as a previous satellite wind-product comparison. Native resolution may smooth the submesoscale structures that SWOT can reveal, making it important for the "what did traditional satellites miss?" question.

Official entries:
https://podaac.jpl.nasa.gov/dataset/ASCATC-L2-25km
https://podaac.jpl.nasa.gov/MEaSUREs-OSVW

### ERA5

- Provider: Copernicus Climate Data Store / ECMWF
- Variables of interest: 10 m wind speed and components, surface fluxes, boundary-layer diagnostics
- Use: gridded background comparison and sensitivity product
- Limitation: effective resolution may be insufficient for true submesoscale wind gradients.

Official entry:
https://cds.climate.copernicus.eu/

### CCMP Ocean Surface Winds

- Provider: Remote Sensing Systems / NASA MEaSUREs, distributed through PO.DAAC
- Use: gridded comparison product and background wind context
- Limitation: gridded analysis may be too smooth for the finest SWOT/SST scales.

Official entry:
https://podaac.jpl.nasa.gov/MEaSUREs-CCMP

## Pilot Regions

### Gulf Stream

- Approximate box: 30-45 N, 80-40 W
- Data combination: SWOT wind speed + SWOT KaRIn SSH + GOES-East/West ABI SST + ASCAT/ERA5/CCMP comparison winds
- Scientific value: strong SST front, strong atmospheric boundary-layer response, energetic mesoscale/submesoscale variability.

### Kuroshio Extension

- Approximate box: 28-45 N, 135-170 E
- Data combination: SWOT wind speed + SWOT KaRIn SSH + Himawari AHI SST + ASCAT/ERA5/CCMP comparison winds
- Scientific value: western boundary current extension, strong SST gradients, energetic eddy-mean-flow interactions.

## Open Feasibility Questions

1. What is the best time-collocation window between SWOT, geostationary SST, and wind products?
2. How does SWOT wind-speed kinetic energy differ from ASCAT/ERA5/CCMP estimates in western boundary current extensions?
3. Are stronger wind kinetic energy anomalies in western boundary currents statistically linked to stronger geostationary-SST coupling coefficients?
4. Which length-scale band should define "submesoscale" for SSH/SST/wind diagnostics in each region?
5. How sensitive are coupling coefficients to cloud masking, diurnal warming, rain contamination, and SWOT quality flags?
