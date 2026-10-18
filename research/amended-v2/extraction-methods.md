# Exploratory extraction and background sensitivity — amended v2

Method choices recorded before executing the new extraction analysis, 2026-09-18 (America/New_York). This is a post-v1 exploratory extension: the September 10 products, frozen redshifts, bands and results remain intact. It uses only the three existing objects and already saved FITS products. Human science/claims review remains pending.

## Fixed question and comparisons

How much does the faint blue-band brightness change under available extraction choices and archived reductions, and how does that affect the apparent red/blue contrast? Keep the v1 rest-frame bands 3620–3720 and 4000–4100 Å, dλ/λ weights, wavelength edge convention, and exact catalog redshifts in `analysis/sample.json`. The blue band straddles 3646 Å and is not an uncontaminated continuum measurement. Compare blue and red flux separately before interpreting any ratio.

1. Preserve the original SPEC1D optimal extraction as reference. Propagate its supplied errors and report the already available archive `full_err` blue-band error as a separate diagnostic.
2. Use the saved native-pixel sums as a direct alternative estimator: `flux_sum/profile_sum`, with conditional diagonal uncertainty `sqrt(var_sum)/abs(profile_sum)`. Pinned `msaexp` source `80b81b4`, `pixel_table_to_1d`, defines `flux_sum` as the sum of `sci/pathloss`, `var_sum` as the sum of `var_total/pathloss**2`, and `profile_sum` as the sum of the profile within yslit = −3…+3. Thus this is a calibrated profile-normalized sum of the *same* samples, not a raw uncorrected aperture. The header and array identities will be checked. The fainter object's header uses a different msaexp commit (`92b1aa6`); the same columns permit an arithmetic diagnostic, but the pinned source is not a claim that every implementation detail of that commit was independently audited.
3. For the already combined 2D SCI, WHT and PROFILE images, test profile-weighted extraction in central row apertures of radius 1, 2 and 3 around the fixed YTRACE; use integer centers only, with inclusive bounds. Also test shifting the radius-2 aperture center by −1 or +1 row. Use positive-profile pixels only within those apertures; expected negative nod traces are not sky. For each wavelength, a = sum(SCI * WHT * PROFILE)/sum(WHT * PROFILE²), with formal diagonal variance 1/sum(WHT * PROFILE²). Do **not** multiply by `path_corr`: the pinned `drizzle_grating_group` source already supplies SCI with `sci/pathloss` and variance with `var_total/pathloss**2` (lines 4519–4552). This is not an independent calibration or exact reproduction of the unresampled optimal extraction. No empirical wavelength-dependent rescaling, outcome-selected aperture, new background fit, or source recentering will be applied. Report the radius-3 2D-to-SPEC1D band differences and flag any substantial mismatch (absolute difference > 0.5 reference supplied σ or > 5% of reference red flux). All 2D alternatives remain conditional on their saved profile and the combined-image calibration even if their reference agreement is good.
4. Measure existing Cliff v3 global-background, v3 nod/local-background, and v4 products at the **same frozen catalog z**. Report matched band differences (µJy, fractional change, and difference divided by reference supplied σ for scale only). Shared exposures make them correlated; no independent-difference significance or quadrature noise subtraction will be claimed. Changes to reduction/calibration/extraction co-vary and prevent isolation of a unique background effect. Source exposure sets must match before this interpretation.
5. Quantify an explicit hypothetical additive extracted-spectrum offset. Add the same δ to both band means, with δ spanning −1…+1 times the archive-rescaled blue-band error (fall back to supplied error only if no ancillary column exists). This is a mathematical stress test, not an estimate or probability distribution for residual background. Report (R+δ)/(B+δ), poles at δ=−B, and the fixed difference R−B, which cancels this common offset. Also compute the differential offset R−B needed to equalize the bands: it is a scale, not an inferred error. Do not treat the BACKGROUND image (already subtracted sky) as residual uncertainty.

## Uncertainty and scientific limits

No saved covariance matrix or uncombined pixel table is available. All formal propagated errors assume diagonal stored errors/weights and fixed profiles; resampling/nod subtraction creates dependence not reconstructed here. Alternatives reuse the same source photons and fitted profile, so their spread is neither an independent repeatability estimate nor a confidence interval. In particular, two ratios from the same product must not be combined as independent evidence. The exercise can identify fragility and consistency under these bounded choices, but cannot certify a clean continuum, exclude extended light/neighbors, measure detector-level background error, prove a Balmer edge, identify the physical power source, or establish a population result.

## Validation fixed before outcomes

- Check synthetic profile-amplitude recovery for known fluxes across every fixed aperture, including a known pre-applied path-loss scaling; check zero weighted coverage raises a supported failure instead of fabricating flux.
- Check analytic diagonal variance and explicit linear operator propagation on a small deterministic fixture; compare Monte Carlo variance for independent simulated pixels with fixed seed and sufficient trials (synthetic check only).
- Check profile-normalized native sums recover their known injected flux and uncertainty in a synthetic fixture; check both estimators recover a flat-color ratio of one.
- Check common-offset ratio derivative/cancellation and the known pole analytically.
- Verify checksums of all consumed raw FITS/reference source inputs against the existing retrieval manifest, preserve their hashes in the output, and record runtime versions/code/method hashes.
- Recalculate v1 reference band means and compare to the frozen measurement JSON to numerical precision. Require exact exposure-set matches for historical Cliff comparisons.
- Save machine-readable extraction summaries, per-pixel alternatives, offset grid, input provenance and validation under `data/derived/amended-v2/extraction*`; optional diagnostic figure under `figures/amended-v2/extraction*`. Reproduction: `PYTHONDONTWRITEBYTECODE=1 analysis/.venv/bin/python analysis/amended_v2_extraction.py` from the project directory.

## Source completion and implementation notes

During the parallel source audit, the exact `92b1aa6` and historical `c61ccae` extraction sources were retrieved and retained under `research/amended-v2/evidence/`; their versions, full commits, retrieval times, hashes and MIT licenses are recorded in [source-manifest.json](source-manifest.json). The matching `92b1aa6` `pixel_table_to_1d` code confirms the same native sums and path-loss semantics used above; its audit closes the implementation-version caveat in choice 2. These source files are read as evidence, never imported or executed. The final extraction provenance verifies their manifest hashes.

The first execution stopped at a deliberately strict exposure-file check before writing science outputs: the historical products lack the v4 `SFILE` cards and use `_phot` instead of `_clear_prism_raw` processing suffixes. The check now reads `SLITS.filename`, compares the standard JWST visit/activity/exposure/detector identifiers, and separately requires matching `start_time` and `exposure_time` columns to 10⁻⁶ in their stored units. The three exposure identities and observing times agree. This is an implementation correction, not a change to the comparison sample or method.

For nod-differenced products, `BACKGROUND`/`sky` is the subtracted other-nod component and can itself contain negative/positive source traces; it is **not** an independent blank-sky measurement or a residual-error map. No part of this analysis subtracts it again or converts its amplitude into uncertainty.

## Results and interpretation

All values below are remeasured from the local FITS products at the frozen catalog redshifts. Their exact values, formal errors and conditional Fieller sets are in [extraction-results.json](../../data/derived/amended-v2/extraction-results.json); tabular variants are in [extraction-summary.csv](../../data/derived/amended-v2/extraction-summary.csv).

| Object | Archive optimal blue (µJy) | Native sum blue (µJy) | Archive ratio | Native sum ratio |
| --- | ---: | ---: | ---: | ---: |
| The Cliff | 0.02196 ± 0.00902 | 0.01776 ± 0.01919 | 8.650 | 10.590 |
| RUBIES-BLAGN-1 | 0.13121 ± 0.00927 | 0.13737 ± 0.01349 | 3.045 | 3.038 |
| RUBIES-UDS-182791 | 0.08919 ± 0.00872 | 0.09313 ± 0.01302 | 1.191 | 1.086 |

Errors in this table use supplied diagonal variances, not archive rescaling and not a complete systematic-error model. The native sum gives greater weight to noisier pixels away from the bright center. It is less precise than the optimized profile weighting and is not automatically a better extraction. The Cliff's red means change from 0.18995 to 0.18812 µJy (−1.0%), while its blue means change by −0.00419 µJy (−19.1%). That small absolute blue change makes a large ratio change. The native-sum blue signal/error is 0.93, and its diagonal-Gaussian 95% Fieller set has no finite positive upper end: the positive branch begins at 3.322. The other branch is ≤−9.400 because negative denominator values were retained. This demonstrates denominator fragility, not an unphysical negative intrinsic spectrum or a rejection of the archive optimal extraction.

RUBIES-BLAGN-1 has comparable fractional changes in blue and red means (+4.7%, +4.4%), preserving a ratio near three. RUBIES-UDS-182791 changes from a red-minus-blue difference of 0.01708 to 0.00800 µJy and remains compatible with equal-band brightness. The native-sum 95% Fieller intervals are 2.509–3.800 for BLAGN-1 and 0.699–1.649 for 182791, conditional on the diagonal errors and fixed profile.

The five fixed 2D aperture variants give ratios 9.187–9.508, 3.0078–3.0101 and 1.1231–1.1263. Radius-3 reconstruction differs from original blue means by −0.00140, +0.00219 and +0.00141 µJy; red differences are +0.00301, +0.00175 and −0.00423 µJy. None triggers the prechosen mismatch flag. Those differences divided by a reference error are merely scale comparisons, not the statistical significance of a paired difference. The small aperture spread is expected when all variants keep the same centrally concentrated fitted profile. It does not independently constrain an extended blue component, prove a zero background, or certify extraction invariance under a different source profile.

### Historical reductions at one redshift

For The Cliff, all three products use the same three July 25, 2024 exposures. At z = 3.548925327627479:

| Product | Blue (µJy) | Red (µJy) | Red / blue |
| --- | ---: | ---: | ---: |
| v3 global background | 0.02751 | 0.19581 | 7.117 |
| v3 local/nod background | 0.02840 | 0.18297 | 6.444 |
| v4 nod background | 0.02196 | 0.18995 | 8.650 |

The v3 local-minus-global differences are +0.000884 µJy in blue and −0.012835 µJy in red. Thus even this historical ratio change does not arise only from a change in faint blue flux. The v4 blue value is 0.006437 µJy below v3 local, while its red value is 0.006977 µJy above it. These matched changes are measured product differences, but background, calibration and fitted extraction profile changed together; they do not isolate an independently measured sky correction or constitute three independent detections. The older reductions' smaller quoted errors likewise do not establish that they are more accurate.

### Hypothetical common-offset test

Using the archive-rescaled blue-band error only as a convenient scale, a common offset from −1 to +1 times that error gives:

| Object | Offset scale (µJy) | Ratio at −1 scale | Ratio at +1 scale |
| --- | ---: | ---: | ---: |
| The Cliff | 0.009758 | 14.769 | 6.297 |
| RUBIES-BLAGN-1 | 0.017273 | 3.355 | 2.807 |
| RUBIES-UDS-182791 | 0.009669 | 1.215 | 1.173 |

These endpoints are **not** confidence limits or an observed background range. The test adds the same extracted-flux offset in both bands. The Cliff's denominator reaches zero at δ = −0.021959 µJy, 2.25 of those error units; a ratio pole is therefore close in absolute flux. A common offset leaves the red-minus-blue difference unchanged, explaining why large ratio sensitivity need not erase a red excess. A wavelength-dependent offset need not cancel; these files do not supply a defensible bound on such a residual. Equalizing the two means by changing blue alone would require +0.16799, +0.26838 and +0.01708 µJy, respectively; these are arithmetic scales, not estimates or exclusions of calibration error.

### What the added check establishes

The same observations support a strong red excess in The Cliff and BLAGN-1 under these bounded extraction choices, with a weak third comparison. The Cliff's contrast size remains especially sensitive to how its very faint blue denominator is measured. Neither the consistency of central 2D apertures nor the alternate native sum measures a clean blue continuum independently of emission lines, background or the adopted profile. A narrower numerical aperture range must not replace the broader uncertainty already demonstrated in v1. No new claim of a sharp edge, physical source type, or population behavior follows.

## Verification and deliverables

The final script reproduces every v1 blue/red reference mean to numerical precision, confirms all bands retain complete valid coverage, verifies consumed raw and source checksums, and confirms the same historical exposure identities/times. Synthetic checks recover injected calibrated profile amplitudes with maximum absolute error 5.6×10⁻¹⁷, match analytic variance within 1.8×10⁻¹⁸, and obtain a Monte Carlo/analytic variance ratio 1.00088 in 100,000 independent synthetic noise draws. Zero weight coverage is explicitly rejected. These validate the arithmetic under its assumptions; they do not validate an astrophysical model or real pixel independence.

- [Code](../../analysis/amended_v2_extraction.py), [validation](../../data/derived/amended-v2/extraction-validation.json), [runtime/input provenance](../../data/derived/amended-v2/extraction-provenance.json), and [run log](../../data/derived/amended-v2/extraction-run.log).
- [Matched differences](../../data/derived/amended-v2/extraction-matched-differences.csv), [per-pixel spectra](../../data/derived/amended-v2/extraction-pixels.csv), and [hypothetical offset grid](../../data/derived/amended-v2/extraction-offset-grid.csv).
- Diagnostic [PNG](../../figures/amended-v2/extraction-sensitivity.png) and [SVG](../../figures/amended-v2/extraction-sensitivity.svg). Caption: “The Cliff's blue-band brightness is small compared with the uncertainty of a simple profile-normalized pixel sum. Alternative extractions reuse the same photons. The lower panels show an assumed common offset, not a measured sky-error distribution. The red excess is more secure than its exact ratio.”

Human understanding, science/claims, contribution and release review remain pending. The next defensible action is the owner walkthrough with these limitations visible; detector-level re-reduction would be a separate, larger project whose likely gain and required calibration/nod/covariance work must be weighed first.
