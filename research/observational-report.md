# Observational report — version 1, 10 September 2026

## What this version establishes

Actual PRISM observations support two clear total-light band contrasts and one weak contrast in the prespecified three-object sample. The size of The Cliff’s contrast is poorly constrained; RUBIES-BLAGN-1 is steadier under nearby band shifts; RUBIES-UDS-182791 is consistent with equal original-band brightness and is sensitive to which spectral features enter the bands. No reliable, uncontaminated edge amplitude or precise edge location is established by this analysis. This is a completed first observational reanalysis with explicit limitations, ready for owner and science review.

The [case study](../CASE_STUDY.md) is the reading entry point. Results below come from [measure.py](../analysis/measure.py) and [shapes.py](../analysis/shapes.py), not from plotting published fitted values. Published classifications and measurements serve selection and comparison only.

## Observations and source matching

All three targets are adopted unique sources in de Graaff et al. catalog v2, record [21977747](https://zenodo.org/records/21977747). The frozen [protocol](protocol-v1.md) records selection before any spectrum was retrieved. The deliberately contrasting sample is not representative of little red dots and contains no non-LRD astrophysical control. Synthetic analytic controls test calculations only.

| Target | Catalog redshift | RA, Dec (degrees) | Observation date (UTC) | Primary root |
| --- | ---: | --- | --- | --- |
| RUBIES-UDS-154183 / The Cliff | 3.5489253 | 34.41074855089, −5.12966426274 | 2024-07-25 | rubies-uds31-v4 |
| RUBIES-UDS-40579 / RUBIES-BLAGN-1 | 3.113558 | 34.2441997, −5.2458714 | 2024-01-16 | rubies-uds1-v4 |
| RUBIES-UDS-182791 | 4.717405 | 34.21381285054, −5.08704950317 | 2024-12-19 | rubies-uds21-v4 |

For each source the product stem is `<root>_prism-clear_4233_<source-id>.spec.fits`. The FITS source name, source ID, program and coordinates agree with the catalog; positional separation is zero to stored numerical precision. These are GO-4233 RUBIES PRISM/CLEAR observations, with three 948.278-second exposures, 2844.834 seconds total per primary extraction. The header’s EFFEXPTM describes one exposure; EXPTIME gives the total. Exposure filenames, MSA metadata IDs and observing times are preserved in each `*_exposures.csv`. No new detector-level JWST reduction was performed.

The RUBIES-BLAGN-1 nickname is independently matched to the position in [Wang et al. (2024), Table 2](https://arxiv.org/html/2403.02304v3#S4.T2), within 0.0052 arcsec. That paper reports z=3.1034±0.0002, while the frozen catalog value is 3.113558. This difference is about 742 km/s using c·Δz/(1+z), beyond the original ±300 km/s stress scenario. The cause is unresolved here; catalog and paper redshifts must not be treated as interchangeable precision measurements. The January 16 primary exposure is the first PRISM visit used by the paper, rather than the later visit that it flags for calibration problems.

The [retrieval manifest](../data/retrieval-manifest.json) records every resource’s URL, retrieval timestamp, bytes, MD5 and SHA-256. The [product audit](../data/derived/product-audit.json) records exact file identities, units, coverage, extraction and calibration metadata. Full headers and all derived 1D pixels are saved separately under data/derived/. Original FITS bytes remain under data/raw/.

The catalog release describes DJA v4.5, while the linked archive record identifies v4.4 and the paper’s availability wording differs. The **per-file identity is resolved**, but an exact mapping to the authors’ v4.5 release is not certified. The current inputs are live S3 v4 products fixed by hashes, not silently relabeled v4.5. The two bright sources have msaexp `0.9.5.dev2+g80b81b4`; 182791 has `0.9.4.dev7+g92b1aa6`. All three record `jwst_1298.pmap`, CRDS 12.0.9 and CAL_VER `0.1.dev8704+g9b678d4`. Preserve that calibration string literally; do not replace it with an assumed JWST release number.

## Estimator and uncertainty

Use rest wavelength λ=λobserved/(1+z). The y values remain observed flux density fν in µJy. No cosmological luminosity conversion is needed for this same-object ratio. The band mean is ∫fνdλ/λ divided by ∫dλ/λ, the photon-counting top-hat convention described by [pyphot’s photometry documentation](https://mfouesneau.github.io/pyphot/photometry.html). Band boundaries follow [the Cliff paper](https://arxiv.org/html/2503.16600v2#S3.SS1): blue 3620–3720 Å, red 4000–4100 Å. The blue label is relative to the other band; it straddles 3646 Å.

The baseline treats each extracted sample as constant over midpoint-defined pixel edges and integrates exact fractional overlap. The band weights sum to one. It uses neither inverse-variance weighting nor interpolation over invalid pixels. Three, four and five pixels per band contribute for the respective objects, including fractional boundary samples. Their nominal independent **resolution** content is only about one element per band; that is distinct from noise independence between extracted pixels. Nominal R near 3646 Å is 37.4, 33.6 and 52.0, corresponding to FWHM 97.5, 108.4 and 70.1 Å.

For band-weight matrix W and pixel covariance C, the band means are Wf and their covariance is WCWᵀ. The baseline uses C=diag(err²). The primary 1D FITS tables contain no covariance or rescaling column. Their path-loss correction is already applied; multiplying by `path_corr` again would be incorrect. This was checked against the pinned extraction source.

| Object | Blue mean ± supplied error (µJy) | Red mean ± supplied error (µJy) | Blue signal/error | Ratio at means | 16–84% noise-draw range |
| --- | ---: | ---: | ---: | ---: | ---: |
| The Cliff | 0.02196 ± 0.00902 | 0.18995 ± 0.01034 | 2.43 | 8.65 | 6.05–14.37 |
| RUBIES-BLAGN-1 | 0.13121 ± 0.00927 | 0.39959 ± 0.01125 | 14.16 | 3.05 | 2.83–3.29 |
| RUBIES-UDS-182791 | 0.08919 ± 0.00872 | 0.10627 ± 0.00893 | 10.23 | 1.19 | 1.05–1.36 |

The asymmetric intervals use 200,000 Gaussian draws of the two band means with their propagated covariance and fixed seeds. These are noise propagation, not posterior probabilities under a physical model. Negative draws are retained. Ratios at the observed means and medians of noisy ratios differ when the denominator is weak; both are saved. Do not call the finite central percentile interval a finite overall upper limit.

The Fieller check inverts `(red − B·blue)² ≤ t²(Var(red) + B²Var(blue) − 2B·Cov(red,blue))`, using t=1 and 1.959964 for nominal 68.27% and 95% sets. If the quadratic opens downward the set can be unbounded and disjoint. This is the ratio-confidence problem treated by [Fieller (1954)](https://doi.org/10.1111/j.2517-6161.1954.tb00159.x). It is conditional on Gaussian flux errors and the supplied covariance, not a complete calibration-error assessment.

After the baseline, the associated `.spec.zfit.fits` files were retrieved for all three targets. Their flux and raw errors match exactly around the feature. The reduction source and numerical arrays confirm `full_err²=(err·escale)² + (0.02·max(flux,0))²`. The `full_err` column lacks a FITS unit and `escale` has misleading inherited unit metadata, so numerical equality and the documented construction, not that metadata, establish the flux-unit interpretation. Those ancillary redshift-fit errors are **not certified as the science paper’s exact errors**. They increase band errors by about 8–12%, 86–97% and 11–14%, respectively.

With the archive rescaled errors, 95% intervals are **4.55–67.10**, **2.35–4.17**, and **0.90–1.60**. The first two retain clear red excess; the third includes unity. Under the illustrative adjacent-pixel correlation model Cij=erri·errj·ρ^|i−j| with ρ=0.6, The Cliff’s 95% set has no finite positive upper end; ρ=0.3 gives an upper end near 206. These are sensitivity scenarios, not measured covariance. The ×2 error scenario is also not a new observation. No systematic envelope is formed by adding all these alternatives in quadrature.

## Quality inspection and sensitivity

The [2D panels](../figures/annotated-spectra.png) show centered positive traces with expected negative nod-subtraction traces about five rows away. The original-band pixels are valid with positive errors; there are no coverage gaps in the fitted 3000–4600 Å interval. Visual inspection found no obvious displaced positive trace crossing the measured feature in these reduced cutouts. This limited inspection does not exclude unresolved neighbors, background residuals, or wavelength-dependent slit losses. The files are already combined; the individual nods and their detector-level quality masks were not independently re-extracted.

The primary statistic includes all light in the bands. A ±one-FWHM exclusion around the prespecified emission-line positions leaves **zero usable original red-band coverage for all three targets**. A masked original-band continuum contrast is therefore unavailable. The longer-baseline 3500–3600 / 4150–4250 Å option avoids selected line centers; it does not guarantee freedom from wings, other lines or continuum slope.

| Variant | The Cliff | RUBIES-BLAGN-1 | RUBIES-UDS-182791 |
| --- | ---: | ---: | ---: |
| Original bands | 8.65 | 3.05 | 1.19 |
| Linear interpolation, same bands | 8.48 | 3.02 | 1.20 |
| Inverse-variance weighting, different estimator | 8.19 | 3.04 | 1.16 |
| Shift both bands −50 Å | 11.42 | 2.90 | 1.61 |
| Shift both bands +50 Å | 4.72 | 2.88 | 0.97 |
| Longer-baseline bands | 10.55 | 4.20 | 1.25 |

Band changes alter the quantity being measured. They are correlated sensitivity checks, not independent estimates to average together. The weak source has peaks near [O II], [Ne III]/higher Balmer lines and Hγ; line contamination is a plausible explanation for its moving-band behavior, not a measured decomposition of each line’s contribution. Its original-band result does not show that it has no physical Balmer feature.

The ±300 km/s redshift-placement scenarios yield ranges 8.36–8.90, 3.03–3.04 and 1.13–1.27. These are not adopted redshift uncertainties. The ±5% calibration-tilt scenarios produce approximately ±5% ratio changes and do not reverse the original-band conclusions. They do not bound arbitrary calibration errors. fλ mean and median alternatives are separately saved as different estimands and are not interchanged with fν.

The final literature cross-check adds an explicitly post hoc calculation at Wang et al.’s z=3.1034 for RUBIES-BLAGN-1. It gives **3.013**, compared with the frozen baseline **3.045**, a 1.1% decrease. Its supplied-error 95% interval is **2.63–3.50**; the archive-rescaled interval is **2.35–4.06**. The clear original-band contrast survives this documented alternative. Both variants and their actual redshift are saved in the sensitivity table. The baseline sample and figures retain the catalog redshift; the conditional shape fits were not repeated at the alternate value and should not be used for precise rest-wavelength claims.

## Published comparison and reduction history

The Cliff paper reports 6.9 (−1.5,+2.8), from a v3 local-background reduction at z=3.548. The verified historical `rubies-uds31-nod-v3` product gives **6.48**, with a supplied-error 16–84% interval **5.27–8.38** using that redshift. Its central value is consistent with the paper, but the exact filter sampling, random draws and error rescaling of the original calculation are unavailable here. This is a consistency-level reproduction, not a bit-for-bit reproduction of the paper.

The separate v3 **global**-background file gives 7.16 at the paper redshift; it is retained and explicitly labeled. All three Cliff reductions contain the same three July 2024 exposures, with v3 using `jwst_1225.pmap`, JWST CAL_VER 1.14.0 and msaexp `0.8.6.dev18+gc61ccae`. They are not independent confirmation. The [reduction comparison](../figures/cliff-reduction-comparison.png) shows both changes in band flux and larger v4 errors. Because background, calibration and extraction changed together, the difference cannot be attributed to one cause alone.

Catalog-v2 median ratios are 9.41, 3.01 and 1.20; our independent measurements from extracted pixels are 8.65, 3.05 and 1.19. Agreement is adequate at the broad interval level. The current catalog’s exact extraction release and fitting options remain a limitation for exact replication. No parameter was tuned to force agreement.

## Why the shape fits do not locate a sharp edge

The [shape comparison](../figures/shape-ambiguity.png) fits smooth curvature, a continuous broken power law, and a broken power law with a jump in linear flux space. Each is forward-smoothed in fλ using wavelength-dependent Gaussian resolution and converted back to the pixel-averaged fν prediction. Transition wavelength is profiled over 3400–4100 Å, not fixed at 3646 Å. Baseline and wider line masks, and R multipliers 1.0 and 1.3, were declared before fitting; numerical details are in [protocol amendments](protocol-amendments.md).

Under the supplied independent-error likelihood, a jump improves the fit for the two bright objects relative to these particular smooth forms. That ranking does **not** locate a physical discontinuity: for The Cliff its nominal Δχ²≤3.84 support extends from roughly 3690 Å to the 4100 Å search boundary with the baseline mask, and the minimum moves to the boundary with the wider mask. RUBIES-BLAGN-1 also reaches the boundary; its simple smooth fits have substantial residuals. For the weak object, a smooth curve is the best AICc description, while all allowed transition wavelengths remain supported in the more flexible models.

Much of the possible transition region is masked, so different jumps can connect the surviving blue and red data. Predictions within the masked interval are model-dependent extrapolations, visibly inconsistent with some excluded total-light data. No inference of a redshifted hydrogen edge, a 4000 Å stellar break, a physical jump amplitude or a precise transition uncertainty is warranted. The nominal likelihood-support ranges are not calibrated confidence intervals for an unknown edge, and no physical stellar/AGN model was fitted. The [full fit table](../data/derived/shape-summary.csv) retains AICc, fit penalties, boundaries and failures of interpretation.

## Reproducibility and verification

The isolated environment uses Python 3.12.13 and a pinned full dependency list. [Run instructions](../analysis/README.md) reproduce the tables and figures from preserved inputs without network access. A retrieval manifest separately supports reacquisition with checksum checks; mutable upstream products must never silently replace the saved version. The two original source notes and scaffold provenance retain their original hashes.

The [validation record](../data/derived/validation.json) checks analytic band integrals, brightness-scale invariance, refusal to fill gaps, uncertainty propagation from original-pixel draws, bounded/unbounded ratio behavior, source hashes, and numerical resolution. Increasing the latent spectral sampling from 2 Å to 1 Å changes the checked model predictions by at most about 0.006 supplied-error units. These support the correctness of the calculations; they do not establish that the scientific assumptions are complete. No human science reviewer has signed off on this version.

## Recommended next step

**Review and improve these three cases before expansion.** First, use the short [reading guide](understanding-the-result.md) to let Alison trace one result from observation to band averages, uncertainty and limitation. Then the most useful technical extension is to test the faint blue continuum against individual nod/extraction choices and fit continuum plus nearby lines together with an explicit instrument model. That targets the actual uncertainties exposed here; another collection of similar plots would not resolve them.

Expansion is scientifically worthwhile for a later, fixed sample if that work yields a stable quantity to compare. It is premature as a way to measure the prevalence of Balmer breaks. The remaining work requires spectroscopic judgment, potentially individual-exposure re-extraction and additional calibration checks; it is not just rerunning the script on more filenames. Plan for several focused review and analysis sessions, with more time if re-reduction is necessary, rather than assuming a quick extension. A reviewer should also assess any population wording and physical interpretation before release. No external contact, purchase, publication or deployment occurred.

## Sources and credit

Public observations: NASA/ESA/CSA JWST; RUBIES GO-4233, PIs Anna de Graaff and Gabriel Brammer. Reduced products: DAWN JWST Archive / msaexp. Catalog selection and comparison: de Graaff et al. (2026). New work in this folder: public-product cross-matching, band measurements, uncertainty and sensitivity calculations, conditional shape comparisons, original figures and explanation prepared with Codex under Alison’s direction. Alison’s personal interpretation/review remains pending.

| Source | Role and locally preserved evidence |
| --- | --- |
| [de Graaff et al. 2025, The Cliff](https://arxiv.org/html/2503.16600v2) | Band convention and historical benchmark; `evidence/cliff-2503.16600v2.html` |
| [de Graaff et al. 2026](https://arxiv.org/html/2511.21820v2) | Published membership, catalog semantics and literature context; `evidence/lrd-2511.21820v2.html` |
| [Wang et al. 2024, RUBIES-BLAGN-1](https://arxiv.org/html/2403.02304v3) | Nickname/position and alternate redshift; `evidence/wang-2024-rubies-blagn1-2403.02304v3.html` |
| [Catalog v2, Zenodo 21977747](https://zenodo.org/records/21977747) | FITS + README in data/raw/catalog; license metadata in evidence/ |
| [DJA v4 product documentation](https://dawn-cph.github.io/dja/blog/2025/05/01/nirspec-merged-table-v4/) | Download formula, caveats and uncertainty-helper behavior; preserved HTML |
| [DJA FITS tutorial](https://dawn-cph.github.io/dja/blog/2023/07/18/nirspec-data-products/) | 1D/2D structure; actual headers checked separately |
| [msaexp pinned extraction source](https://github.com/gbrammer/msaexp/blob/80b81b4/msaexp/slit_combine.py) | Confirms already-applied path loss and error propagation; preserved as text, not executed |
| [msaexp pinned spectrum reader](https://github.com/gbrammer/msaexp/blob/80b81b4/msaexp/spectrum.py) | Ancillary error construction; preserved as text |
| [Nominal dispersion reference](https://github.com/gbrammer/msaexp/blob/80b81b4/msaexp/data/jwst_nirspec_prism_disp.fits) | R(λ) used in diagnostics and forward models; local FITS/hash |
| [pyphot photometry definitions](https://mfouesneau.github.io/pyphot/photometry.html) | Photon-counting weighting; independently implemented |
| [Fieller (1954)](https://doi.org/10.1111/j.2517-6161.1954.tb00159.x) | Ratio confidence-set construction |

License metadata for both the catalog and archived DJA v4.4 release states **CC BY 4.0**. msaexp source/reference files are supplied with the preserved **MIT license**. [MAST’s guidance](https://stdatu.stsci.edu/publishing/data-use) describes most holdings as public domain, and [JWST attribution guidance](https://jwst-docs.stsci.edu/accessing-jwst-data/citing-jwst-data) supplies publication-credit requirements. The live S3 per-object files carry no separate license block and their identity with the v4.4 snapshot has not been established. Preserve that distinction before redistributing a bundle. Papers retain their stated rights; no paper figures were copied into the results. This local task does not authorize redistribution or publication.
