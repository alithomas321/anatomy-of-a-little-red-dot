"""Bounded, post-v1 descriptive line/continuum diagnostic. Offline only.

See research/amended-v2/protocol.md. No physical line decomposition or
calibrated edge-confidence claim follows from these conditional fits.
"""
import os
for key in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
    os.environ.setdefault(key, '1')
import json
import hashlib
import numpy as np
from scipy.optimize import nnls
from astropy.table import Table
from astropy.io import fits
import astropy.units as u
from measure import ROOT, SAMPLES, load, weights, BANDS, LINES
from shapes import kernel

OUT = ROOT/'data/derived/amended-v2'
GRID = np.arange(2500., 5100.1, 1.)
RATIOS = np.r_[np.arange(0., 20.001, .05), 30., 50., 100., 200.]


def latent_basis(width, grid=GRID):
    """Four nonnegative continuum endpoints + six independent line groups."""
    left = grid < 3646.
    t = np.clip((grid-2800.)/(3646.-2800.), 0., 1.)
    u = np.clip((grid-3646.)/(4800.-3646.), 0., 1.)
    C = np.column_stack([(1-t)*left, t*left, (1-u)*(~left), u*(~left)])
    columns = []
    for wavelength in LINES:
        if width == 0:
            # Unit integrated f_lambda delta, linearly split if grid misses center.
            g = np.zeros(len(grid)); j = np.searchsorted(grid, wavelength)
            f = (wavelength-grid[j-1])/(grid[j]-grid[j-1])
            g[j-1] = (1-f)/np.gradient(grid)[j-1]
            g[j] = f/np.gradient(grid)[j]
        else:
            sigma = wavelength*width/299792.458/2.354820045
            g = np.exp(-.5*((grid-wavelength)/sigma)**2)/(np.sqrt(2*np.pi)*sigma)
        # The existing kernel converts input f_nu to f_lambda and back.
        columns.append(g*(grid/wavelength)**2)
    return np.column_stack([C, *columns])


def matrix(d, select, width, rscale, grid=GRID):
    latent = latent_basis(width, grid)
    A = kernel(d, select, rscale, grid)@latent
    normalization = np.ones(A.shape[1]); normalization[4:] = np.max(A[:,4:], axis=0)
    return A/normalization, latent/normalization


def solve(A, y, e, ratio=None):
    if ratio is None:
        transform = np.eye(A.shape[1])
    else:
        # Reduced coefficients: outer blue, blue edge, outer red, six lines.
        transform = np.zeros((A.shape[1], A.shape[1]-1))
        transform[0,0] = 1.; transform[1,1] = 1.; transform[2,1] = ratio
        transform[3:,2:] = np.eye(A.shape[1]-3)
    Aw = (A@transform)/e[:,None]; yw = y/e
    # Unit-norm columns improve conditioning without altering the constraint.
    norms = np.linalg.norm(Aw,axis=0)
    p, rnorm = nnls(Aw/norms, yw, maxiter=5000)
    v = p/norms; coefficients = transform@v
    residual = Aw@v-yw
    grad = (Aw/norms).T@residual
    active = p <= 1e-8
    kkt = max(float(np.max(np.abs(grad[~active]),initial=0)),
              float(np.max(np.maximum(-grad[active],0),initial=0)))
    assert np.isclose(rnorm*rnorm, residual@residual, rtol=1e-9, atol=1e-9)
    assert kkt < 1e-6, kkt
    return coefficients, float(residual@residual), kkt


def full_errors(s, d):
    with fits.open(ROOT/'data/raw/spectra'/s['file'].replace('.spec.fits','.spec.zfit.fits')) as h:
        t = Table.read(h['SPEC1D'])
        systematic = h['SPEC1D'].header['SYS_ERR']
    use = d['valid'] & (d['x']>=3000) & (d['x']<=4600)
    assert np.allclose(t['wave'].quantity.to_value(u.um)[use],d['wave'][use],rtol=0,atol=0)
    assert np.all(t['valid'][use])
    assert np.allclose(t['flux'][use],d['flux'][use],rtol=0,atol=0)
    assert np.allclose(t['err'][use],d['err'][use],rtol=0,atol=0)
    assert np.all(np.isfinite(t['full_err'][use])) and np.all(t['full_err'][use]>0)
    expected=(np.asarray(t['err'][use])*np.asarray(t['escale'][use]))**2 + (systematic*np.maximum(t['flux'][use],0))**2
    assert np.allclose(np.asarray(t['full_err'][use])**2,expected,rtol=1e-10,atol=0)
    return np.asarray(t['full_err'])


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    records=[];checks=[]
    for s in SAMPLES:
        d=load(s);use=d['valid']&(d['x']>=3000)&(d['x']<=4600)
        y=d['flux'][use];efull=full_errors(s,d)[use]
        W=np.array([weights(d['x'],b)[use] for b in BANDS])
        assert np.allclose(W.sum(axis=1),1)
        for width in [0.,1500.,3000.]:
            for rscale in [1.,1.3]:
                A,latent=matrix(d,use,width,rscale)
                for error_name,e in [('archive_full_err',efull),('raw_err',d['err'][use])]:
                    coeff,chi,kkt=solve(A,y,e)
                    profile=[];profile_kkt=[]
                    for q in RATIOS:
                        pp,cc,kk=solve(A,y,e,q);profile.append(cc);profile_kkt.append(kk)
                    profile=np.array(profile)
                    assert np.all(profile>=chi-1e-7)
                    nojump,nchi,_=solve(A,y,e,1.)
                    support=RATIOS[profile<=chi+3.84]
                    model=A@coeff;cont=A[:,:4]@coeff[:4]
                    ratio=float(coeff[2]/coeff[1]) if coeff[1]>1e-10 else None
                    ratio_state=('finite' if coeff[1]>1e-10 else
                                 'blue_endpoint_zero_red_positive' if coeff[2]>1e-10 else
                                 'both_endpoints_zero')
                    bands_cont=W@cont;bands_lines=W@(model-cont)
                    record=dict(id=s['id'],nickname=s['nickname'],error_model=error_name,
                        intrinsic_fwhm_kms=width,R_multiplier=rscale,n=int(use.sum()),nominal_k=10,
                        chi2=chi,chi2_per_nominal_dof=chi/(len(y)-10),
                        max_abs_standardized_residual=float(np.max(abs((model-y)/e))),
                        coefficients=coeff.tolist(),active_zero_indices=np.flatnonzero(coeff<1e-8).tolist(),
                        conditional_jump_ratio=ratio,nojump_chi2=nchi,nojump_delta_chi2=nchi-chi,
                        ratio_state=ratio_state,
                        nojump_coefficients=nojump.tolist(),
                        ratio_grid=RATIOS.tolist(),profile_chi2=profile.tolist(),
                        nominal_support_grid=support.tolist(),support_hits_upper_cap=bool(len(support) and support[-1]==RATIOS[-1]),
                        continuum_band_means_uJy=bands_cont.tolist(),line_band_means_uJy=bands_lines.tolist(),
                        continuum_band_ratio=float(bands_cont[1]/bands_cont[0]) if bands_cont[0]>1e-10 else None,
                        fitted_line_fraction_of_red_band=float(bands_lines[1]/(W@model)[1]),
                        x_A=d['x'][use].tolist(),flux_uJy=y.tolist(),err_uJy=e.tolist(),
                        best_total_uJy=model.tolist(),best_continuum_uJy=cont.tolist(),
                        nojump_total_uJy=(A@nojump).tolist(),nojump_continuum_uJy=(A[:,:4]@nojump[:4]).tolist(),
                        best_residual_sigma=((y-model)/e).tolist(),
                        kkt_max=max(kkt,max(profile_kkt)))
                    records.append(record)
                # Synthetic constructed signal tests recovery of model prediction,
                # not unique physical coefficients in a blended problem.
                synthetic=np.array([.04,.07,.20,.28,.05,.03,.02,.04,.08,.10])
                signal=A@synthetic
                p,cc,_=solve(A,signal,efull)
                assert np.max(abs(A@p-signal)/efull)<1e-7
                q0=synthetic[2]/synthetic[1]
                pfix,cf,_=solve(A,signal,efull,q0)
                assert cf<1e-12
                # Compare same physical coefficients/normalization on 0.5 Å grid.
                fine=np.arange(2500.,5100.1,.5)
                Kfine=kernel(d,use,rscale,fine)
                raw=latent_basis(width)
                normalization=np.max((kernel(d,use,rscale,GRID)@raw)[:,4:],axis=0)
                norms=np.r_[np.ones(4),normalization]
                Afine=Kfine@latent_basis(width,fine)/norms
                best=records[-2]
                delta=float(np.max(abs(Afine@np.array(best['coefficients'])-np.array(best['best_total_uJy']))/efull))
                assert delta<.1,delta
                checks.append(dict(id=s['id'],width_kms=width,R_multiplier=rscale,
                    noiseless_prediction_max_error_sigma=float(np.max(abs(A@p-signal)/efull)),
                    fixed_true_ratio_chi2=cf,finer_grid_max_change_sigma=delta))
        nominal=next(r for r in records if r['id']==s['id'] and r['intrinsic_fwhm_kms']==0 and r['R_multiplier']==1 and r['error_model']=='archive_full_err')
        print(s['nickname'], 'nominal jump',nominal['conditional_jump_ratio'], 'chi2/dof',nominal['chi2_per_nominal_dof'],
              'no-jump delta',nominal['nojump_delta_chi2'], 'support', [min(nominal['nominal_support_grid']),max(nominal['nominal_support_grid'])] if nominal['nominal_support_grid'] else [],flush=True)
    (OUT/'line-fits.json').write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
    cols=['id','error_model','intrinsic_fwhm_kms','R_multiplier','n','chi2','chi2_per_nominal_dof',
          'max_abs_standardized_residual','conditional_jump_ratio','nojump_delta_chi2',
          'continuum_band_ratio','fitted_line_fraction_of_red_band','support_hits_upper_cap','kkt_max']
    Table(rows=[{k:r[k] for k in cols} for r in records]).write(OUT/'line-summary.csv',format='ascii.csv',overwrite=True)
    report={'meaning':'Numerical checks; synthetic recovery is not observational evidence or human science review.',
        'script_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest(),
        'checks':checks,'max_kkt_violation':max(r['kkt_max'] for r in records),'status':'passed'}
    (OUT/'line-checks.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
