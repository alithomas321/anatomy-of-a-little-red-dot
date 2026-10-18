"""Exploratory same-observation extraction checks; never overwrite v1 artifacts.

Methods fixed in research/amended-v2/extraction-methods.md before execution.
Uses existing reduced products, not detector-level or individual-nod reprocessing.
"""
from pathlib import Path
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import tempfile

import numpy as np
from astropy.io import fits
from scipy.stats import norm

from measure import ROOT, SAMPLES, BANDS, load, weights, fieller

OUT = ROOT / "data/derived/amended-v2"
FIG = ROOT / "figures/amended-v2"
METHOD = ROOT / "research/amended-v2/extraction-methods.md"
APERTURES = [(1, 0), (2, 0), (3, 0), (2, -1), (2, 1)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_sum(flux_sum, profile_sum, var_sum):
    valid = np.isfinite(flux_sum + profile_sum + var_sum) & (profile_sum > 0) & (var_sum > 0)
    flux = np.full_like(flux_sum, np.nan, dtype=float)
    err = np.full_like(flux_sum, np.nan, dtype=float)
    flux[valid] = flux_sum[valid] / profile_sum[valid]
    err[valid] = np.sqrt(var_sum[valid]) / profile_sum[valid]
    return flux, err, valid


def image_extract(sci, wht, profile, center, radius, shift=0):
    """Linear profile amplitude; SCI and inverse-variance WHT already calibrated.

    The saved drizzle source applies path loss before making these images.
    Errors are diagonal-WHT formal errors, not measured correlated errors.
    """
    rows = np.arange(sci.shape[0])[:, None]
    mask = (np.abs(rows - (center + shift)) <= radius)
    valid = mask & np.isfinite(sci + wht + profile) & (wht > 0) & (profile > 0)
    weight = np.where(valid, wht, 0.)
    prof = np.where(valid, profile, 0.)
    denom = (weight * prof**2).sum(axis=0)
    usable = np.isfinite(denom) & (denom > 0)
    operator = np.zeros_like(sci)
    operator[:, usable] = (weight * prof)[:, usable] / denom[usable]
    flux = (operator * np.where(valid, sci, 0.)).sum(axis=0)
    err = np.full(sci.shape[1], np.nan)
    err[usable] = np.sqrt(1. / denom[usable])
    flux[~usable] = np.nan
    return flux, err, usable, operator


def band_result(x, flux, err, valid):
    W = np.array([weights(x, b) for b in BANDS])
    coverage = W[:, valid].sum(axis=1)
    if not np.allclose(coverage, 1., atol=1e-9):
        return {"supported": False, "coverage": coverage.tolist()}
    mean = W @ np.where(valid, flux, 0.)
    WE = W * np.where(valid, err, 0.)
    cov = WE @ WE.T
    sig = np.sqrt(np.diag(cov))
    return dict(supported=True, coverage=coverage.tolist(), blue_uJy=float(mean[0]),
                red_uJy=float(mean[1]), blue_formal_error_uJy=float(sig[0]),
                red_formal_error_uJy=float(sig[1]), blue_formal_sn=float(mean[0]/sig[0]),
                ratio=float(mean[1]/mean[0]), red_minus_blue_uJy=float(mean[1]-mean[0]),
                fieller95_diagonal=fieller(mean, cov, norm.ppf(.975)))


def exposure_files(d):
    # v3 lacks SFILE cards; SLITS preserves both versions' exposure identities.
    return sorted({str(x).strip() for x in d['slits']['filename']})


def exposure_set(d):
    # Processing suffixes differ (v3 _phot, v4 _clear_prism_raw), while the
    # standard JWST visit/activity/exposure/detector identifier is unchanged.
    return sorted({'_'.join(name.split('_')[:4]) for name in exposure_files(d)})


def synthetic_checks():
    """Synthetic checks of arithmetic, not evidence about the three objects."""
    rng = np.random.default_rng(9182026)
    ny, nx = 15, 11
    row = np.arange(ny)[:, None]
    profile = np.exp(-.5*((row-7)/1.1)**2) * np.linspace(.8, 1.2, nx)
    true_flux = np.linspace(.02, .3, nx)
    # Corrected flux is original flux / known path loss before image creation.
    pathloss = np.linspace(.8, .95, nx)
    sci = profile * true_flux / pathloss
    wht = (2. + row/3) * np.linspace(30., 60., nx)
    errors = []
    variance_errors = []
    for radius, shift in APERTURES:
        f, e, valid, operator = image_extract(sci, wht, profile, 7, radius, shift)
        assert np.all(valid)
        errors.append(float(np.max(np.abs(f - true_flux/pathloss))))
        expected = np.sum(operator**2/wht, axis=0)
        variance_errors.append(float(np.max(np.abs(e**2-expected))))
    assert max(errors) < 1e-13
    assert max(variance_errors) < 1e-13
    f, e, valid, op = image_extract(sci, wht, profile, 7, 2)
    draws = rng.normal(size=(100000, ny))/np.sqrt(wht[:, 3])
    empirical = float(np.var(draws @ op[:, 3], ddof=1))
    expected = float(e[3]**2)
    assert abs(empirical/expected-1) < .02
    empty = image_extract(sci, np.zeros_like(wht), profile, 7, 2)
    assert not empty[2].any() and np.isnan(empty[0]).all()
    ps = profile.sum(axis=0)
    rawvariance = np.sum(1/wht, axis=0)
    ns = native_sum(sci.sum(axis=0), ps, rawvariance)
    assert np.allclose(ns[0], true_flux/pathloss, atol=1e-13)
    assert np.allclose(ns[1]**2, rawvariance/ps**2, atol=1e-13)
    x = np.linspace(3300., 4400., 100)
    flat = band_result(x, np.ones(100)*.2, np.ones(100)*.01, np.ones(100, bool))
    assert abs(flat['ratio']-1) < 1e-12
    # Both extraction operators preserve a constant known spectrum.
    flatimage = profile*.2
    im = image_extract(flatimage, wht, profile, 7, 2)
    nsflat = native_sum(flatimage.sum(axis=0), ps, rawvariance)
    assert np.allclose(im[0], .2) and np.allclose(nsflat[0], .2)
    b, r, delta = .02, .18, .005
    derivative = (b-r)/(b+delta)**2
    h = 1e-7
    numeric = ((r+delta+h)/(b+delta+h)-(r+delta-h)/(b+delta-h))/(2*h)
    assert np.isclose(derivative, numeric, rtol=1e-8)
    assert np.isclose((r+delta)-(b+delta), r-b)
    assert b+(-b) == 0
    return dict(all_passed=True, kind="synthetic_arithmetic_only", seed=9182026,
                profile_recovery_max_absolute_error=max(errors),
                analytic_variance_max_absolute_error=max(variance_errors),
                independent_pixel_monte_carlo_trials=100000,
                monte_carlo_variance_over_analytic=empirical/expected,
                zero_weight_coverage_rejected=True, native_sum_recovery=True,
                flat_color_recovery=True, offset_derivative_and_cancellation=True)


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k,v in row.items()})


def diagnostic_figure(results, offsets):
    cache_root=Path(tempfile.gettempdir())/'anatomy-lrd-amended-v2-extraction-cache'
    os.environ.setdefault('MPLCONFIGDIR', str(cache_root/'matplotlib'))
    os.environ.setdefault('XDG_CACHE_HOME', str(cache_root))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": "anatomy-lrd-extraction-amended-v2",
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.3), gridspec_kw={"height_ratios": [1.1, 1]})
    labels = {"spec1d_optimal": "Archive optimal", "native_profile_normalized_sum": "Native-pixel sum",
              "image_r1_shift0": "2D radius 1", "image_r2_shift0": "2D radius 2",
              "image_r3_shift0": "2D radius 3", "image_r2_shift-1": "2D center −1",
              "image_r2_shift1": "2D center +1"}
    for j,s in enumerate(SAMPLES):
        rows = [r for r in results if r['id']==s['id'] and r['product']=='v4']
        ax=axes[0,j]
        for k,r in enumerate(rows):
            color="#294e77" if k<2 else "#818a94"
            ax.errorbar(r['blue_uJy'], k, xerr=r['blue_formal_error_uJy'], fmt='o',
                        color=color, capsize=3, ms=5)
        ax.set_yticks(range(len(rows)), [labels[r['variant']] for r in rows] if j==0 else [])
        ax.invert_yaxis(); ax.axvline(0,color="#555555",lw=.8)
        ax.set_title(s['nickname'], weight='bold')
        ax.set_xlabel("Blue-band brightness (µJy)")
        ax.grid(axis='x',alpha=.15)
        ax=axes[1,j]
        rows=[r for r in offsets if r['id']==s['id']]
        ax.plot([r['offset_in_archive_blue_sigma'] for r in rows],
                [r['ratio'] if r['ratio'] is not None and abs(r['ratio'])<100 else np.nan for r in rows],
                color="#c05f32",lw=2)
        ax.axvline(0,color="#777777",lw=.8,ls='--'); ax.axhline(1,color="#777777",lw=.8)
        ax.set_xlabel("Assumed common offset / blue error")
        if j==0: ax.set_ylabel("Red / blue")
        ax.grid(alpha=.15)
    fig.suptitle("Same photons, different extraction choices", fontsize=18, weight='bold', x=.08, ha='left')
    fig.text(.08,.91,"Top: formal diagonal errors; 2D variants are conditional sensitivity checks. Bottom: hypothetical offset, not measured sky error.",fontsize=10)
    fig.text(.08,.025,"Blue band: 3620–3720 Å; red band: 4000–4100 Å. Three selected objects; no clean-edge or population inference. Human review pending.",fontsize=9,color="#555555")
    fig.subplots_adjust(left=.17,right=.985,top=.83,bottom=.13,wspace=.21,hspace=.48)
    for suffix in ("png","svg"):
        fig.savefig(FIG/f"extraction-sensitivity.{suffix}",dpi=180,
                    metadata={"Date":None} if suffix=='svg' else {"Software":"Anatomy of a Little Red Dot"})
    plt.close(fig)


def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    checks=synthetic_checks()
    frozen=json.loads((ROOT/'data/derived/measurements.json').read_text())
    frozen={r['id']:r for r in frozen}
    manifest=json.loads((ROOT/'data/retrieval-manifest.json').read_text())
    manifest={r['path']:r for r in manifest}
    source_manifest_path=ROOT/'research/amended-v2/source-manifest.json'
    source_manifest=json.loads(source_manifest_path.read_text())
    manifest.update({r['path']:r for r in source_manifest['resources']})
    results=[]; pixels=[]; offsets=[]; audit=[]; comparisons=[]; offset_summary=[]
    consumed={Path(__file__).resolve(),METHOD,ROOT/'analysis/measure.py',ROOT/'analysis/sample.json',
              ROOT/'analysis/requirements.lock',ROOT/'data/derived/measurements.json',
              ROOT/'data/retrieval-manifest.json',ROOT/'data/raw/catalog/jwst_nirspec_prism_disp.fits',
              ROOT/'research/evidence/msaexp-slit-combine-80b81b4.py',source_manifest_path,
              ROOT/'research/amended-v2/evidence/msaexp-slit-combine-92b1aa6.py',
              ROOT/'research/amended-v2/evidence/msaexp-slit-combine-c61ccae.py'}
    reference_data={}
    for s in SAMPLES:
        d=load(s);reference_data[s['id']]=d;consumed.add(d['path'])
        hdr=d['header']; tab=d['table']
        assert hdr['WITHPATH'] and hdr['TOMUJY']==1
        assert hdr['YMIN1D']==-3 and hdr['YMAX1D']==3
        base=band_result(d['x'],d['flux'],d['err'],d['valid'])
        for k in ('blue_uJy','red_uJy'):
            assert np.isclose(base[k],frozen[s['id']][k],rtol=1e-13,atol=1e-14)
        ref=dict(id=s['id'],nickname=s['nickname'],product='v4',variant='spec1d_optimal',
                 z=s['z'],formal_error_basis='SPEC1D supplied; diagonal',**base)
        results.append(ref)
        native=native_sum(np.array(tab['flux_sum']),np.array(tab['profile_sum']),np.array(tab['var_sum']))
        br=band_result(d['x'],*native)
        results.append(dict(id=s['id'],nickname=s['nickname'],product='v4',variant='native_profile_normalized_sum',
                            z=s['z'],formal_error_basis='var_sum/profile_sum²; diagonal',**br))
        arrays={'spec1d_optimal':(d['flux'],d['err'],d['valid']),
                'native_profile_normalized_sum':native}
        for radius,shift in APERTURES:
            name=f'image_r{radius}_shift{shift}'
            im=image_extract(d['images']['SCI'],d['images']['WHT'],d['images']['PROFILE'],
                             int(hdr['YTRACE']),radius,shift)
            br=band_result(d['x'],*im[:3]);arrays[name]=im[:3]
            results.append(dict(id=s['id'],nickname=s['nickname'],product='v4',variant=name,
                                z=s['z'],formal_error_basis='combined WHT diagonal; fixed profile',**br))
        for name,(flux,err,valid) in arrays.items():
            for i in np.flatnonzero((d['x']>=3000)&(d['x']<=4600)):
                pixels.append(dict(id=s['id'],variant=name,wave_rest_A=float(d['x'][i]),
                    wave_observed_um=float(d['wave'][i]),flux_uJy=float(flux[i]) if valid[i] else None,
                    formal_error_uJy=float(err[i]) if valid[i] else None,valid=bool(valid[i])))
        ancillary=d['path'].with_name(s['file'].replace('.spec.fits','.spec.zfit.fits'))
        consumed.add(ancillary)
        with fits.open(ancillary) as h:
            ft=h['SPEC1D'].data
            region=(d['x']>=3000)&(d['x']<=4600)
            assert np.allclose(ft['wave'],d['wave'])
            assert np.allclose(ft['flux'][region],d['flux'][region])
            assert np.allclose(ft['err'][region],d['err'][region])
            full=np.asarray(ft['full_err'])
            assert np.allclose(full[region]**2,(ft['err'][region]*ft['escale'][region])**2+
                               (h['SPEC1D'].header['SYS_ERR']*np.maximum(ft['flux'][region],0))**2)
            rescaled=band_result(d['x'],d['flux'],full,d['valid'] & np.asarray(ft['valid']))
        sigma=rescaled['blue_formal_error_uJy'];b=base['blue_uJy'];r=base['red_uJy']
        for units in np.linspace(-1.,1.,201):
            delta=float(units*sigma);denom=b+delta
            ratio=None if abs(denom)<1e-14 else (r+delta)/denom
            offsets.append(dict(id=s['id'],offset_in_archive_blue_sigma=float(units),
                offset_uJy=delta,blue_after_uJy=b+delta,red_after_uJy=r+delta,ratio=ratio,
                scenario='hypothetical common additive extracted-spectrum offset'))
        offset_summary.append(dict(id=s['id'],archive_blue_error_uJy=sigma,
            archive_blue_sn=b/sigma,blue_zero_offset_uJy=-b,blue_zero_offset_in_archive_sigma=-b/sigma,
            ratio_offset_minus_1sigma=(r-sigma)/(b-sigma),ratio_offset_plus_1sigma=(r+sigma)/(b+sigma),
            red_minus_blue_unchanged_uJy=r-b, differential_offset_to_equal_bands_uJy=r-b,
            common_offset_changes_difference=False))
        audit.append(dict(id=s['id'],file=s['file'],version=hdr['VERSION'],with_pathloss=bool(hdr['WITHPATH']),
            dimensions=list(d['images']['SCI'].shape),pixel_table_available='PIXTAB' in d['headers'],
            trace_row=float(hdr['YTRACE']),native_yslit_range=[hdr['YMIN1D'],hdr['YMAX1D']],
            exposure_files=exposure_files(d),exposure_ids=exposure_set(d),
            audited_source_commit='92b1aa6' if s['id']=='RUBIES-UDS-182791' else '80b81b4',
            source_commit_exact_match=any(c in hdr['VERSION'] for c in ['80b81b4','92b1aa6']),
            archived_full_err_formula_verified=True))
    cliff=SAMPLES[0]
    for label,filename in [('v3_global',cliff['file'].replace('-v4','-v3')),
                           ('v3_local_nod',cliff['file'].replace('uds31-v4','uds31-nod-v3'))]:
        d=load(cliff,filename);consumed.add(d['path'])
        assert exposure_set(d)==exposure_set(reference_data[cliff['id']])
        reference_slits=reference_data[cliff['id']]['slits']
        for column in ('start_time','exposure_time'):
            assert np.allclose(np.sort(d['slits'][column]),np.sort(reference_slits[column]),rtol=0,atol=1e-6)
        br=band_result(d['x'],d['flux'],d['err'],d['valid'])
        results.append(dict(id=cliff['id'],nickname=cliff['nickname'],product=label,
                            variant='spec1d_optimal',z=cliff['z'],
                            formal_error_basis='historical SPEC1D supplied; diagonal',**br))
        audit.append(dict(id=cliff['id'],file=filename,version=d['header']['VERSION'],
                          same_exposure_set_as_v4=True,exposure_times_match_v4=True,
                          exposure_files=exposure_files(d),exposure_ids=exposure_set(d),
                          audited_source_commit='c61ccae',source_commit_exact_match='c61ccae' in d['header']['VERSION'],
                          diffs=bool(d['header']['DIFFS']),crds_ctx=d['header']['CRDS_CTX'],
                          cal_ver=d['header']['CAL_VER']))
    for row in results:
        assert row['supported']
        base=next(r for r in results if r['id']==row['id'] and r['product']=='v4' and r['variant']=='spec1d_optimal')
        delta={f'delta_{band}_uJy':row[f'{band}_uJy']-base[f'{band}_uJy'] for band in ('blue','red')}
        for band in ('blue','red'):
            delta[f'delta_{band}_over_reference_supplied_error']=delta[f'delta_{band}_uJy']/base[f'{band}_formal_error_uJy']
            delta[f'delta_{band}_fraction']=delta[f'delta_{band}_uJy']/base[f'{band}_uJy']
        delta['difference_error_not_estimated']=True
        delta['image_reconstruction_mismatch_flag']=bool(row['variant']=='image_r3_shift0' and any(
            abs(delta[f'delta_{band}_uJy'])>.5*base[f'{band}_formal_error_uJy'] or
            abs(delta[f'delta_{band}_uJy'])>.05*base['red_uJy'] for band in ('blue','red')))
        comparisons.append(dict(id=row['id'],product=row['product'],variant=row['variant'],**delta))
    # Historical local/global comparison directly at the same redshift.
    loc=next(r for r in results if r['product']=='v3_local_nod')
    glob=next(r for r in results if r['product']=='v3_global')
    historical=dict(z=cliff['z'],same_exposures=True,independent=False,
                    local_minus_global_blue_uJy=loc['blue_uJy']-glob['blue_uJy'],
                    local_minus_global_red_uJy=loc['red_uJy']-glob['red_uJy'],
                    local_minus_global_ratio=loc['ratio']-glob['ratio'])
    provenance=[]
    for path in sorted(consumed):
        relative=str(path.relative_to(ROOT));digest=sha(path)
        rec=dict(path=relative,sha256=digest,bytes=path.stat().st_size)
        if relative in manifest:
            source=manifest[relative]
            assert source['sha256']==digest,relative
            rec['existing_manifest_verified']=True
            for k in ('requested_url','resolved_url','retrieved_utc','md5'):
                if k in source: rec[k]=source[k]
        elif '/data/raw/' in str(path):
            raise AssertionError('Raw input missing from retrieval manifest: '+relative)
        provenance.append(rec)
    checks.update(v1_reference_band_fluxes_reproduced=True,historical_cliff_exposure_sets_match=True,
                  every_variant_has_full_band_coverage=True,raw_input_manifest_hashes_verified=True)
    payload=dict(description='Post-v1 exploratory same-observation extraction sensitivity',
                 human_review_pending=True,bands_A=BANDS,results=results,comparisons=comparisons,
                 common_offset_summary=offset_summary,historical_same_z=historical,product_audit=audit,
                 limitations=['Shared exposures: alternatives are not independent.',
                   'Diagonal formal errors do not reconstruct nod/resampling covariance.',
                   'Combined 2D extraction is not exact unresampled SPEC1D recovery.',
                   'Hypothetical additive offset is not a measured background error.',
                   'No uncontaminated continuum/edge/source/population inference.'])
    (OUT/'extraction-results.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    (OUT/'extraction-validation.json').write_text(json.dumps(checks,indent=2,allow_nan=False)+'\n')
    (OUT/'extraction-provenance.json').write_text(json.dumps(dict(inputs=provenance,
        python=sys.version,platform=platform.platform(),packages={p:importlib.metadata.version(p)
            for p in ('numpy','scipy','astropy','matplotlib')},
        command='PYTHONDONTWRITEBYTECODE=1 analysis/.venv/bin/python analysis/amended_v2_extraction.py'),
        indent=2,allow_nan=False)+'\n')
    write_csv(OUT/'extraction-summary.csv',results)
    write_csv(OUT/'extraction-matched-differences.csv',comparisons)
    write_csv(OUT/'extraction-pixels.csv',pixels)
    write_csv(OUT/'extraction-offset-grid.csv',offsets)
    diagnostic_figure(results,offsets)
    print(json.dumps(dict(checks=checks,summary=[{k:r[k] for k in
        ('id','product','variant','blue_uJy','red_uJy','ratio')} for r in results],
        offset_summary=offset_summary,historical_same_z=historical),indent=2))


if __name__=='__main__':
    main()
