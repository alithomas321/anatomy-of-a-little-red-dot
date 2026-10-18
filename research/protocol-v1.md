# Three-object observational protocol — 2026-09-10

Frozen before downloading or inspecting any selected spectrum. Published catalog values have been inspected for selection. This is a local prespecified analysis, not an externally registered study. Amendments must be dated and retain this record.

## Question and scope

How reliably do three public JWST spectra measure the red-to-blue brightness contrast near hydrogen's Balmer limit, and which analysis choices affect that answer? The primary result is a pair of band fluxes and their ratio. It is not a measurement of the identity, age, stellar mass or black-hole mass of these objects, nor a population frequency or a novelty claim.

Use exactly three adopted (`use_dG26=True`) PRISM spectra from de Graaff et al. 2026 catalog v2, Zenodo 21977747, all from RUBIES GO-4233. The catalog FITS has been retrieved and matches the release MD5 a7055bc0a466628a212dd13640f88969. Its 181 entries include duplicate observations; do not count these as independent objects. Membership comes from the published catalog; do not reconstruct its internally inconsistent printed slope-selection inequalities.

1. RUBIES-UDS-154183, **The Cliff**, z=3.548925327627479: the previously named strong-contrast anchor; adopted root `rubies-uds31-v4`.
2. RUBIES-UDS-40579, **RUBIES-BLAGN-1**, z=3.113558: the luminous comparison already discussed in the Cliff paper; root `rubies-uds1-v4`.
3. RUBIES-UDS-182791, z=4.717405: a published weak-contrast comparison. Within adopted GO-4233 sources with 3<z<5 and published median ratio 0.8–1.3, choose the smallest fractional 16–84 percentile width. This selects 182791 from 182791, 119957, 167741 and 23438; root `rubies-uds21-v4`.

Selection deliberately uses prior results to illustrate contrast and precision, before making our own measurements. It is not representative or independent confirmation of a population distribution. The third object has a different redshift/resolution; do not interpret object differences as intrinsic without those qualifications. No non-LRD control is included in this three-object scope. Flat/smooth synthetic controls will check methods, not establish astrophysics.

## Acquisition and acceptance

Retrieve only the catalog-linked `.spec.fits` products, which document both 1D and 2D HDUs. Record exact URL, retrieval time, bytes, hashes, FITS program/source coordinates, extraction software, CRDS and calibration version, exposure identifiers and times. Compare catalog coordinates to FITS coordinates (require <0.1 arcsec, otherwise investigate). Check PRISM/CLEAR, monotonic wavelengths, physical column units, finite positive errors, coverage and the 2D trace/background. Preserve all raw bytes. Do not silently replace an unusable selected object with a better-looking one.

The paper and catalog disagree about archive aggregate version v4.4/v4.5, while extraction roots are v4. Product headers and hashes define the actual inputs. The Cliff 2025 paper used v3, local nod-background subtraction, z=3.548 and reported 6.9 (-1.5,+2.8). Attempt a documented v3 product comparison for that same object if publicly available. This is a reduction sensitivity check on the same observations, not a fourth object or independent observation.

## Primary estimator

Rest wavelength = observed wavelength/(1+z). Work in the archive's f_nu flux density, converted to microjanskys if necessary. No luminosity or distance correction is needed for a same-object ratio.

Define B = red/blue, red=4000–4100 Å and blue=3620–3720 Å in the source frame, following the Cliff paper. These are labels for two bands: the blue band straddles 3646 Å and is not entirely blueward of the physical edge. Neither band is guaranteed free of blended lines. B alone is a color contrast, not proof of a discontinuity.

Use a photon-counting top-hat average: mean f_nu = integral(f_nu dλ/λ)/integral(dλ/λ). Infer pixel edges halfway between adjacent wavelength centers, and integrate a piecewise-constant spectrum with exact fractional edge overlap. Do not inverse-variance weight the baseline: that changes the passband and biases a structured spectrum. Require complete valid band coverage; do not interpolate gaps or clip negative fluxes. This is an explicit implementation of the published band convention; the paper does not publish all filter-sampling options, so assess discretization separately.

Propagate the supplied errors through linear band weights. Report band signal-to-noise and B at measured band means; generate 200,000 Gaussian band-flux draws with a fixed seed for 16/50/84 percentiles. Preserve negative draws. Also calculate Fieller confidence sets at 68.27% and 95% using the band covariance; if the denominator includes zero at 95%, label the ratio as lacking a finite two-sided 95% bound. A finite central percentile range does not override that warning. Report random errors conditional on the product and independent-pixel assumption, not a complete uncertainty budget. Inspect any supplied error rescaling/covariance before deciding whether it is applicable.

## Prespecified sensitivity checks

- Same windows: piecewise-linear interpolation with propagated original-pixel weights, and inverse-variance weights as a clearly different estimator. Compare f_lambda means/medians separately; never relabel them as the same numerical B.
- Band location: shift both windows by ±50 Å; use wider 3500–3600 and 4150–4250 Å bands as a line-avoiding, longer-baseline alternative. This changes the measured quantity and remains slope-sensitive.
- Emission contamination: mark [O II] 3727, [Ne III] 3869, H8/He I 3889, H epsilon/[Ne III] 3970, H delta 4102 and H gamma 4341. Quantify nominal band coverage after excluding ±one instrumental FWHM around these lines. If the bands become incomplete, report that a fully line-masked original ratio is unsupported rather than filling missing flux.
- Wavelength placement: vary z by ±0.001(1+z), a ±300 km/s sensitivity scenario, not an estimated redshift error; also reproduce the Cliff paper's z=3.548.
- Calibration: multiply by a tilt giving ±5% change in the red/blue band-center ratio. This is a stated stress scenario, not a measured calibration uncertainty; common absolute scaling cancels.
- Noise covariance: use illustrative correlation matrices rho^|i-j| with rho=0.3 and 0.6, plus a 2x error-amplitude stress scenario. These are sensitivity assumptions, not measured covariances. Report their effect on confidence bounds.
- Resolution: record nominal R and independent resolution elements per band; do not equate extracted pixels with independent spectral resolution. Use R multipliers 1.0 and 1.3 for the optional shape descriptions. Do not deconvolve data.

## Shape description, secondary and conditional

If usable continuum pixels span both sides, fit in linear flux space over 3000–4600 Å. Compare a smooth log-quadratic continuum, a continuous broken power law with free transition, and a broken power law that allows a jump. Forward-smooth each at wavelength-dependent PRISM resolution and integrate over output pixels. Fix the emission masks before fitting (half-width = max[0.75 λ/R, λ*1500/c]); repeat at 1.0 λ/R. Fit transition over 3400–4100 Å, never fixed to 3646. Examine residuals, parameter boundaries and profile likelihood; reject a precise location claim if boundary-sensitive or model-dependent. Small-sample corrected AIC is only a descriptive, conditional comparison, not physical evidence for a black hole or a calibrated significance test. If models are inadequate or indistinguishable, say so. Do not expand the model family in pursuit of a preferred answer.

## Quality, controls and delivery

Inspect generated code before execution in the project-local pinned Python environment. Docker is installed but its daemon is unavailable; use the existing filesystem sandbox and disable network during analysis. Verify band weighting with analytic flat/power-law controls, uncertainty propagation against draws, negative-denominator behavior, and input checksums. Synthetic checks must be visually and textually separate from observational results.

Deliver traceable band measurements, annotated 1D/2D spectra, sensitivity and uncertainty figures, source matching and version notes, reproducible scripts/lockfile, and a concise local case study with two plain-language paragraphs. Investigate disagreement with the anchor instead of adjusting choices to match. Recommend review/refinement or expansion based on data quality and systematic uncertainty. Human science/claims review remains necessary before any public release; no publication is authorized.
