# What the joint line check establishes

**Exploratory extension of the September 10 pilot; human science review pending.** The methods were fixed in [protocol.md](protocol.md) before execution of this diagnostic, after the original results were known. [All numerical scenarios](../../data/derived/amended-v2/line-summary.csv) and [full fits/profiles](../../data/derived/amended-v2/line-fits.json) retain both archive-rescaled and original errors.

## A useful counterexample, with limits

The large measured band contrast does not uniquely require a sharp jump at 3646 Å. When the declared continuum and six blended emission groups are fit together, The Cliff and RUBIES-BLAGN-1 can be described almost equally well by a continuum continuous at that wavelength. That continuum is allowed to change slope there: **continuous does not mean featureless or a single straight line**. This is a descriptive alternative, not a validated physical explanation or proof that a Balmer discontinuity is absent.

| Object | Pixels | Best χ² / nominal dof | Extra χ² when jump is removed | Largest residual, best model |
| --- | ---: | ---: | ---: | ---: |
| The Cliff | 39 | 28.15 / 29 | 0.065 | 1.86 archive-error units |
| RUBIES-BLAGN-1 | 35 | 16.48 / 25 | 0.730 | 1.53 archive-error units |
| RUBIES-UDS-182791 | 54 | 70.29 / 44 | 6.507 | 3.89 archive-error units |

These are the nominal-resolution, intrinsically unresolved-line scenarios with the ancillary archive-rescaled errors. The fit has ten nonnegative coefficients; the stated degrees of freedom simply subtract ten and do not correct for active boundaries. χ² is a weighted residual score under the assumed independent errors. Its change is not a calibrated detection significance. With the original smaller errors, BLAGN-1's best score is 61.45/25 and its largest residual is 3.01 error units: apparent model adequacy depends materially on the error prescription.

Across all six width/resolution scenarios with archive errors, removing the jump costs only 0.038–0.149 for The Cliff and 0.539–0.817 for BLAGN-1. The weak object's extra cost varies from 2.806 to 9.257, and its best models retain residuals as large as 3.85–4.30 archive-error units. A conspicuous residual occurs near 4322 Å. Do not turn this model inadequacy or resolution sensitivity into a claimed downward physical edge. Do not tune more components until it passes.

## The three different ratios

1. **Observed band ratio:** the original extracted total light in 4000–4100 Å divided by that in 3620–3720 Å. It remains 8.65, 3.05 and 1.19; nothing in this fit overwrites it.
2. **Fitted continuum band ratio:** the model's convolved continuum contribution averaged in those same bands. In the nominal fits it is 4.44, 2.66 and 1.49. Those are conditional model outputs, not new continuum measurements. Both emission and the adjustment of a noisy continuum across the whole fitting region matter; one must not attribute the difference from the observed ratio entirely to lines.
3. **Latent jump ratio q:** the unconvolved continuum immediately above 3646 Å divided by that immediately below. Its nominal best values are 1.16, 0.82 and 0.52. The slopes, convolution and finite passbands make q fundamentally different from the band ratio. The edge location was imposed, never measured.

Profiling q while refitting every other coefficient gives discrete nominal Δχ²≤3.84 grid spans 0–4.90, 0.05–1.25 and 0.25–0.85 in the nominal scenarios. These are contiguous on the saved grid but **are not physical confidence intervals**. The full grid, active boundaries and scenario results are retained. No scan reaches its 200 cap in these runs; that does not certify the chosen model family as complete. The code separately labels a finite ratio, a zero blue endpoint with positive red endpoint, and two zero endpoints.

The nominal fitted red-band line fractions are 13.2%, 9.8% and 11.5%; across the six archive-error scenarios they vary approximately 10.3–14.2%, 6.7–10.8% and 5.1–18.5%. These numbers describe how this particular basis allocates flux. They are **not measured species fractions** and are unsuitable as standalone website claims.

## Why this is not a physical line decomposition

The six positive templates are nuisance groups at the frozen approximate line positions. The model has no absorption, complete high-order Balmer series, nebular continuum, stellar population physics or source-specific slit/line-spread function. In particular, the 3869 and 3889 Å groups overlap strongly at the assumed resolution. Free amplitudes do not identify the species that emitted the light. Gaussian line widths of 0, 1500 and 3000 km/s, and R multipliers 1 and 1.3, are specified alternatives, not width measurements or resolution uncertainties.

The fixed continuum kink is also an assumption. The September 10 fits used different continuum forms, conservative masks and a searched transition; these fits use all pixels, explicitly modeled emission, a linear continuum basis and an imposed transition. Consequently this is a broader demonstration of dependence on assumptions, **not a likelihood contest against the September 10 fits on identical data**. Neither the older jump preference nor the newer continuous counterexample establishes the physical truth.

No measured pixel covariance is available. Archive error scaling and the positivity constraints do not solve that limitation. A realistic physical decomposition would require a separately justified model, an appropriate line-spread function, covariance/calibration treatment and spectroscopic review; higher-resolution or per-exposure work would be a separate bounded decision.

## Verification and credit

[line-checks.json](../../data/derived/amended-v2/line-checks.json) records exact script hash and checks of KKT optimality, constrained/unconstrained nesting, noiseless constructed-model recovery and 1 Å versus 0.5 Å grid consistency. The finer grid changes the checked predictions by at most 0.011 archive-error units. Input wavelength, valid status, flux and raw errors are matched against the ancillary error files; `full_err²=(err×escale)²+(SYS_ERR×max(flux,0))²` is checked numerically. These are software/numerical checks, not independent sky observations or human science approval.

The observed data and original reductions remain credited to NASA/ESA/CSA JWST, RUBIES GO-4233, the DAWN JWST Archive and msaexp. The new code, sensitivity interpretation and figures were prepared with Codex under Alison's direction. [Source audit](source-audit.md) gives the primary evidence and exact version/reuse caveats.
