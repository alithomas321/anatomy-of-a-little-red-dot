# Observational extension — 18 September 2026

**Exploratory/amended v2; human science, contribution and release review pending.** This is a bounded continuation of the same three-object pilot. The September 10 report, frozen sample/protocol, raw data and all previous numerical/figure products are preserved. The project has no Git repository; a [pre-work inventory](amended-v2/pre-work-inventory.json) and final file manifest document preservation and the exact resulting state. No legacy/project-external files were changed by this task.

## Supported outcome

The original total-light band contrasts survive as the original measurements. The extension supplies stronger evidence that their size and interpretation need separate treatment. The Cliff's blue-band precision depends on extraction weighting, and its box extraction has no finite positive upper Fieller bound. BLAGN-1's band ratio is stable under the tested extraction choices. UDS-182791 remains weak and defeats the limited joint spectral model. A specified continuous-at-3646 Å continuum plus emission describes the two strong-contrast spectra nearly as well as the same model with a jump. This supplies a concrete counterexample to inferring a unique sharp edge from their band ratios.

The extension is not an independent observation, an astrophysical control sample, a complete residual-background assessment, a physical emission-line decomposition, a population study or a claim that an edge is absent. Synthetic fixtures test calculation only. See the [current case study](../CASE_STUDY.md) for the plain-language argument.

## What changed after the frozen pilot

[The amended protocol](amended-v2/protocol.md) and [extraction choices](amended-v2/extraction-methods.md) were written after seeing the September 10 outputs, before the new corresponding analyses ran. This authorizes a new declared diagnostic family; it does not retroactively amend the original prespecification. No outcome-selected new sample, tuned band, recentering, empirical correction or expanded family was introduced to force an answer.

The three primary observations, ancillary error files, two historical Cliff reductions, nominal dispersion reference, redshifts and band convention are identical to v1. The bands remain 3620–3720 and 4000–4100 Å in rest wavelength, averaged as fν with dλ/λ weights; the first straddles 3646 Å. All blue/red fluxes below are observed µJy. The original catalog/paper BLAGN-1 redshift difference and live-S3/v4.4/v4.5 identity caveat remain unresolved and are not relabeled.

## Extraction and background: what the saved data can establish

| Object | Optimal blue ± supplied error | Native sum blue ± formal error | Optimal → native sum ratio |
| --- | ---: | ---: | ---: |
| The Cliff | 0.02196 ± 0.00902 | 0.01776 ± 0.01919 | 8.65 → 10.59 |
| RUBIES-BLAGN-1 | 0.13121 ± 0.00927 | 0.13737 ± 0.01349 | 3.045 → 3.038 |
| RUBIES-UDS-182791 | 0.08919 ± 0.00872 | 0.09313 ± 0.01302 | 1.191 → 1.086 |

The native sum is `flux_sum/profile_sum` from the saved unresampled-pixel aggregates, with diagonal error `sqrt(var_sum)/profile_sum`, rather than a newly extracted detector product. The same spatial profile supplies its aperture normalization. The code checks the units, path-loss metadata and ±3 yslit sum interval. Native sum semantics are verified against each relevant pinned source revision. No path-loss correction is applied twice.

The Cliff's native-sum blue signal/error is 0.93; the optimal supplied-error value is 2.43 (2.25 with archive rescaling). For the native sum the full 95% Fieller set is disjoint: **(−∞, −9.40] ∪ [3.32, ∞)**. A physical positive-ratio interpretation still has no finite upper end. The negative branch is not discarded from the numerical record. Neither this result nor the 19% change in the blue central value proves the optimal extraction is wrong; its weighting gives different precision. The native red flux changes by only about 1%. No same-exposure difference significance is calculated without cross-estimator covariance.

Five fixed central aperture/one-row-centering alternatives from the combined SCI/WHT/PROFILE images yield ratios 9.187–9.508, 3.008–3.010 and 1.123–1.126. They are conditional profile-weighted diagnostics. All radius-3 comparisons to the native optimal extraction remain below the predeclared mismatch flag threshold; that is a numerical agreement check, not validation of the fixed profile or all background systematics. WHT supplies marginal variances, not the missing resampling/nod covariance.

At the **same frozen z=3.5489253276**, Cliff v3 global, v3 local/nod and v4 ratios are 7.117, 6.444 and 8.650. Exposure identifiers, start times and exposure times agree. Local minus global v3 changes blue by +0.000884 µJy and red by −0.012835 µJy. These are not independent reductions of different sky realizations; profile, extraction and calibration differ. The background procedure is not the only changed factor.

As a separate mathematical stress test, adding an identical offset to both measured bands leaves red-minus-blue unchanged while altering their ratio. An offset of ±one archive blue-band error moves the Cliff ratio from 14.77 at the negative end to 6.30 at the positive end; the other objects span 3.36–2.81 and 1.215–1.173. This is **not a measured background error or a confidence envelope**. No residual-sky distribution can be inferred from BACKGROUND: for nod products that image includes the negative component from other nods. The hypothetical offset is retained to explain a denominator's sensitivity, not to enlarge the observational error bars.

Full definitions, source line references and further results are in [extraction-methods.md](amended-v2/extraction-methods.md), [machine-readable outputs](../data/derived/amended-v2/extraction-results.json) and [extraction figure](../figures/amended-v2/extraction-sensitivity.png).

## Joint line/continuum diagnostic

[line-results.md](amended-v2/line-results.md) gives all assumptions, numerical results and failures. A four-endpoint nonnegative continuum with a fixed possible jump at 3646 Å is forward-convolved with six nuisance emission groups. The grid uses three intrinsic line widths and two nominal resolving-power scalings, with archive-rescaled and raw errors retained separately. Negative observations remain data; only model amplitudes are constrained positive.

Under nominal resolution and archive errors, removing the jump costs only Δχ²=0.065 for The Cliff and 0.730 for BLAGN-1. Their best joint χ² values are 28.15/29 and 16.48/25 nominal degrees of freedom. Across the six width/resolution scenarios the no-jump cost remains small. The original raw errors give worse residuals, especially BLAGN-1 (61.45/25). Adequacy is conditional on the adopted error model.

For UDS-182791, χ²=70.29/44 and a residual of 3.89 archive-error units near 4322 Å flag limitations of the model. The no-jump cost also depends strongly on assumed resolution. A nominal fitted downward jump is not evidence for a physical downward discontinuity. The result is retained as a failed physical interpretation, not repaired by selecting more components.

The observed band ratio, model-continuum band ratio and latent jump ratio are different quantities. The joint continuum fit can adjust weak blue light using the entire fitted region; the change in its band ratio cannot be assigned entirely to line subtraction. Absorption, complete higher Balmer emission, pseudo-continuum and a source-specific LSF are absent. No amplitudes are attributed to individual species and no fitted remainder is called measured continuum. The plotted profile threshold is a descriptive diagnostic, not calibrated confidence.

## Evidence, version provenance and verification

The [source audit](amended-v2/source-audit.md) verifies the original primary papers and exact extraction revisions, adds read-only source snapshots for `92b1aa6` and `c61ccae`, and records current STScI resolution guidance. The original `80b81b4` source and all original FITS remain fixed by their prior hashes. The [new source manifest](amended-v2/source-manifest.json) records URLs, dates, bytes, hashes, commit mappings and reuse caveats. No downloaded upstream source was executed. The unresolved release/license mapping matters before raw-data redistribution; website assets contain original figures, not copied paper figures or a raw-data bundle.

Execution uses the existing isolated Python 3.12.13 environment and unchanged full dependency lock. Context7 supplied current primary NNLS documentation; it did not change the pinned runtime. [Reproduction instructions](../analysis/AMENDED_V2.md) run only this bounded extension offline. Numerical checks include analytic/Monte Carlo extraction-operator variance, synthetic flux recovery, zero-coverage rejection, common-offset cancellation, exact original-band agreement, matched exposure sets, NNLS optimality/nesting and finer-grid convolution. Noisy ratios retain unbounded confidence sets.

The final [verification record](../data/derived/amended-v2/verification.json) and [artifact manifest](../data/derived/amended-v2/final-state-manifest.json) bind verification to this delivered state. An independent agent reviewed the method/code and reader-facing claims; that is agent review, not human scientific approval. Original image renderings were inspected for readable labels and correct plotted quantities. Passing numerical checks does not certify the completeness of the astrophysics.

## Owner decision and stopping point

This bounded version can end with a demonstrated limitation. Use the [walkthrough](owner-walkthrough-v2.md) to establish Alison's understanding and revise the personal contribution wording before any release. Human science review should focus on the continuous-model counterexample, line/LSF assumptions, faint-denominator language and covariance caveat.

A later exposure-level project could assess nod-to-nod behavior and extraction/background choices with a pinned calibration pipeline. It would require new calibrated exposure products, per-exposure masks/profiles and more validation; it still would not supply higher spectral resolution or guarantee an identifiable Balmer edge. Higher-resolution joint modeling is a different possible project. Neither was needed or started here. The recommended next action is owner/science review of this result, with expansion deferred until a specific remaining question justifies that cost.
