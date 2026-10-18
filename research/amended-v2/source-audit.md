# Primary-source and method audit for the bounded extension

18 September 2026 local / 19 September UTC. **Exploratory amendment; human science and release review pending.** This audit concerns the same three objects and preserved observations. It neither changes September 10 choices nor independently confirms the papers’ physical conclusions. Source files were inspected as text, not executed.

## What the available products permit

The useful distinction is between a brightness contrast, its dependence on extraction, and a model-dependent continuum estimate. A strong contrast does not ensure that its numerical ratio is precise, or that its origin is a clean discontinuity.

| Check | Supported interpretation | Unsupported interpretation |
| --- | --- | --- |
| Original two-band fluxes | Total extracted light in explicitly defined bands; conditional error propagation | An uncontaminated edge amplitude or identification of the power source |
| Same-exposure Cliff reductions | Sensitivity to the reduction as a whole | Independent replication; an isolated measurement of background error |
| Alternate extractions of combined SCI/WHT/PROFILE | Sensitivity to spatial weighting and an assumed profile; inspect whether faint blue light follows the source | New nod observations, an exact recreation of SPEC1D, or a complete residual-background bound |
| Joint descriptive lines and continuum | Which imposed edge amplitudes fit under a finite stated family; where that family fails | A unique line decomposition, physical line ratios, or a detected physical edge from a poor no-jump fit |

### Exact extraction semantics

The pinned [`80b81b4` extraction source](../evidence/msaexp-slit-combine-80b81b4.py) establishes these facts:

- `get_flat_diff_arrays`, lines 3103–3150: for nod differences, `sky` contains the **negative component from the other nods**. For the non-nodded route it instead contains the sky estimate. `BACKGROUND` is its resampled, path-corrected image. It can contain source light at other nod positions; it is not residual background or its uncertainty.
- `drizzle_grating_group`, lines 4511–4546: SCI and BACKGROUND are already divided by path loss; the profile is separately resampled. Do not apply the path correction again to these arrays.
- `combine_grating_group`, lines 4196–4212 and 4274–4298: WHT is inverse marginal variance; the saved 1D columns preferentially come from the unresampled pixel table. Re-extracting a drizzled cutout changes the operation and does not reconstruct missing covariance. PROFILE is a model, not independent measured morphology.

The corresponding sections were also checked in the newly preserved [`92b1aa6`](evidence/msaexp-slit-combine-92b1aa6.py) source for UDS-182791 and [`c61ccae`](evidence/msaexp-slit-combine-c61ccae.py) for both historical Cliff reductions: the negative-nod `sky` convention and preferred unresampled extraction are present in all three versions. This closes a version-specific evidence gap; it does not reproduce those upstream reductions.

The Cliff v3 local and global reductions share exposures but have different fitted profiles; v4 changes the code/calibration as well. A subtraction between their blue-band values therefore cannot isolate one cause. Blank-row checks should exclude both the positive trace and negative nod traces, retain valid-pixel masks, and acknowledge spatial and spectral correlations. Agreement is useful reassurance within these checks, not proof that all background error is negligible.

## Resolution and overlapping emission

[STScI’s instrument documentation](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-instrumentation/nirspec-dispersers-and-filters) defines its tabulated resolving power using a 2.2-pixel resolution element, typically a fully illuminated aperture. Its PRISM resolving power varies substantially with wavelength. The preserved dispersion reference therefore supplies a **nominal instrument scale**, not a measured object-specific Gaussian line-spread function. The document’s listed latest update is 12 May 2026; a complete local snapshot is in [evidence](evidence/nirspec-dispersers-and-filters-2026-09-19.html).

The pilot’s nominal rest-frame FWHM of about 70–108 Å near 3646 Å is comparable to each 100 Å measurement band. The 3869/3889 Å nuisance templates are separated by only 20 Å, making species-level amplitude attribution particularly fragile. The red band also lies among emission wings. This is why a finite mask or Gaussian line model does not certify line-free continuum. The source-specific numbers come from the preserved pilot calculation, not a new instrument calibration.

## Interpretation of the amended line diagnostic

The [amended protocol](protocol.md) chooses four nonnegative piecewise-linear continuum endpoints and six nonnegative line-group templates, with an edge imposed at 3646 Å. The finite intrinsic-width and resolution choices are sensitivity scenarios. They are not measurements of width or calibrated priors.

The profiled `q` is the ratio of latent fν immediately across the **imposed** edge. It differs from both the original observed band ratio and the model continuum band ratio, which also depend on slopes and convolution. A good fit only shows compatibility with this family. The family omits absorption, detailed high-order Balmer emission and pseudo-continuum; rejection of its no-jump member does not distinguish those omissions from an astrophysical discontinuity. Nonnegativity constrains the model while observed negative pixels remain valid data.

Report residual adequacy before interpreting profile shapes. Preserve boundaries and the full profile grid, including any separated supported intervals; a scan ending at 200 is not an upper confidence limit. Δχ²=3.84 is a declared diagnostic threshold, not calibrated confidence with unknown covariance, constrained amplitudes and an approximate line-spread function. Synthetic recovery and optimality checks establish numerical behavior only. Do not subtract best-fit lines from observations and label the remainder measured continuum.

The parent task checked nonnegative least-squares semantics through Context7 `/scipy/scipy` on 19 September UTC, referencing the [official SciPy implementation](https://github.com/scipy/scipy/blob/main/scipy/optimize/_nnls.py): minimize the residual norm subject to nonnegative coefficients. This current-main documentation is unpinned and is not an environment change. Execution uses the project’s pinned SciPy 1.18.1. The parent’s retrieval is recorded separately in the source manifest without pretending that its response was locally snapshotted.

## Primary literature cross-check

| Primary source and exact version | Relevant evidence and boundary |
| --- | --- |
| [de Graaff et al., The Cliff, arXiv:2503.16600v2](https://arxiv.org/html/2503.16600v2), 14 July 2025; §§2.2, 3.1–3.2 | Uses v3 local nod subtraction; defines the two finite bands and reports 6.9 with asymmetric errors. The paper also uses higher-resolution spectroscopy and additional evidence for physical interpretation. Its line analysis models resolution/calibration uncertainty. Our total-light ratio neither reproduces that full inference nor overturns it. |
| [Wang et al., RUBIES-BLAGN-1, arXiv:2403.02304v3](https://arxiv.org/html/2403.02304v3), 27 December 2024; §II.2 and Table 2 | Reports z=3.1034±0.0002 and excludes its second PRISM visit after wavelength/flux discrepancies. It applies a photometry-informed spectral correction. The preserved project input is the first visit but is not thereby identical to the paper’s corrected science spectrum. The existing catalog/paper redshift check remains relevant. |
| [de Graaff et al., LRD sample, arXiv:2511.21820v2](https://arxiv.org/html/2511.21820v2), 17 August 2026; §§2.3–2.4, 4.1 | Uses higher-resolution data where available and explicit calibration/LSF assumptions. It cautions that limited resolution prevents detailed component interpretation and that Gaussian components need not be physically distinct. Its population and physical claims cannot be inherited by these three selected examples. |

These three exact HTML versions were preserved on September 10 and checked against their live versioned pages on September 19 UTC. The paper convention alone does not specify every detail of this project’s band integration or error treatment; agreement is a benchmark, not exact published-error replication.

## Provenance, rights and remaining tradeoff

[source-manifest.json](source-manifest.json) gives new resource URLs, UTC retrieval times, byte counts and SHA-256 hashes, plus hash-verified references to prior evidence. Full commit mappings are `80b81b41b2c7eb8c2a3a9a08bf120e233f5bc3d0`, `92b1aa6bcab577449724c936fc161b0b2033ea9e`, and `c61ccae17f4e7a32f2e5b80722c37e83eb2533e6`. The original [retrieval manifest](../../data/retrieval-manifest.json) remains authoritative for the September 10 acquisitions.

The [catalog record 21977747](https://zenodo.org/records/21977747) and [DJA record 15472354](https://zenodo.org/records/15472354) state CC BY 4.0; the latter identifies v4.4. Their license does not resolve the existing v4.4/v4.5/live-S3 identity mismatch. Public [DJA release documentation](https://dawn-cph.github.io/dja/blog/2025/05/01/nirspec-merged-table-v4/) also distinguishes applied path loss from photometric rescaling and records residual calibration caveats. Keep actual FITS identities and literal headers; do not silently certify a different release. All three preserved code revisions have the same MIT license, separately retained for the newly added revisions. The paper HTML states arXiv’s perpetual non-exclusive license; do not assume that means CC BY or copy paper figures. This audit’s original text and project-generated figures can be prepared for human review; raw archive redistribution and third-party figures require their own rights check.

A defensible stopping point is a demonstrated limitation in these products. Individual-nod or detector re-reduction could target background/profile uncertainty but would require a separate calibration workflow and would still not supply missing spectral resolution. It is not necessary to finish this bounded explanation and has not been undertaken. Human understanding, scientific interpretation, contribution wording and public release remain pending.
