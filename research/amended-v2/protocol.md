# Bounded exploratory extension — 18 September 2026 (local time)

Recorded before running the new line analysis. The September 10 spectra, results and protocol have already been inspected. This is an explicitly post-pilot amendment, not a blind preregistration. No existing scientific result or frozen choice is replaced.

**Question:** Which parts of the apparent contrast survive the available extraction choices, and which parts require assumptions about faint blue light or overlapping emission?

Use exactly the same three catalog objects, redshifts, preserved FITS bytes, original bands and project-local pinned environment. No new detector data, sample expansion or physical stellar/AGN inference. Preserve all preexisting numerical products. New numerical products go in `data/derived/amended-v2/`; new figures in `figures/amended-v2/`. The pre-work inventory fixes the prior state, including the old reader-facing pages, which are also copied here.

## Extraction/background diagnostic

The companion `extraction-methods.md` records the exact alternatives before their execution. Compare existing Cliff reductions at the same frozen catalog redshift. Inspect calibrated alternate extractions of the combined cutouts only if their normalization can be verified; do not claim to recover individual nods. Treat shared exposures as correlated, negative nod traces as source subtraction, and BACKGROUND as the subtracted estimate rather than an uncertainty. Keep any injected offsets visibly separate from observations. A bound on background uncertainty cannot be manufactured from a supplied background image.

## Line/continuum diagnostic

Fit every valid pixel with center in 3000–4600 Å in linear observed fν, without masking negative measurements. Use the ancillary archive `full_err` after verifying flux/raw-error identity; independent errors remain an assumption. Keep the frozen raw-error calculation as a comparison. Use the original wavelength-dependent Gaussian fλ convolution and pixel quadrature, with a 1 Å latent grid from 2500 to 5100 Å. No data deconvolution.

Use a deliberately limited descriptive continuum: independent linear fν segments from 2800 to 3646 Å and from 3646 to 4800 Å, constant beyond outer endpoints. Four nonnegative endpoint amplitudes permit a kink and a jump fixed at 3646 Å. Fixing the location asks a conditional question; it is not a measurement locating an edge. Nonnegativity is a model assumption, not clipping of observations. The continuum is not a physical population template.

Add independent nonnegative nuisance templates at the six frozen blended positions: 3727, 3869, 3889, 3970, 4102 and 4341 Å. These denote unresolved groups, not an identified flux for each named species. Normalize each convolved template to unit peak, keeping arbitrary amplitude in µJy. Intrinsic Gaussian fλ widths are fixed at FWHM 0 (discrete delta), 1500 and 3000 km/s; each template in a given fit shares that width. Repeat each with nominal R and 1.3R. These six scenarios are sensitivity choices, not measured width or resolution uncertainty. Do not tune the grid, line list or model family to achieve a preferred outcome.

Solve nonnegative linear least squares. Profile the ratio of continuum immediately redward to immediately blueward of 3646 Å by substituting `red_endpoint = q × blue_endpoint`. Use q=0..20 in steps of 0.05, supplemented by 30, 50, 100 and 200. Include q=1 exactly. Report the unrestricted minimum, all profile points, active boundaries, fit residuals and nominal Δχ²≤3.84 grid span. That threshold is an illustrative likelihood-support diagnostic, **not calibrated confidence** with unknown covariance, positivity boundaries, approximate line physics and possible model failure. Hitting a grid end is a limitation; never interpret a scan cap as a measured upper limit. If both endpoint amplitudes vanish, the ratio is undefined even when the constrained profile is computable.

Report descriptive χ²/(n−10), largest standardized residual and residual plots; the degrees of freedom are nominal and ignore active constraints. Compare the no-jump fit and best joint fit without a physical discovery or model-selection significance claim. A poor joint fit is a useful failure: do not enlarge the family to rescue it. Save continuum and line contributions to the original bands, explicitly model-dependent. Do not subtract fitted lines from the observed data and call the remainder measured continuum.

## Controls, provenance and delivery

Verify weighted residual and nonnegative KKT conditions, nested fixed-ratio minima, recovery of a noiseless constructed model, convolution consistency on a finer latent grid, original input/frozen-protocol preservation, and agreement of unchanged original-band calculations. Synthetic data only test software. Inspect code before executing. Use current primary SciPy documentation (Context7, retrieved September 19 UTC) for NNLS semantics; pinned runtime remains the original lockfile. Keep a source audit with primary references and exact version caveats.

Deliver an owner walkthrough with one question, one central figure, conclusion and uncertainty; website-ready original text/figures with a manifest and credit; and a handoff that names remaining human understanding, science, contribution and release decisions. No publication, external contact or agent-supplied human sign-off.
