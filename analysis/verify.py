"""Numerical and provenance validation; synthetic checks are not sky evidence."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ.setdefault(k,'1')
import hashlib,json,sys,platform
from datetime import datetime,timezone
import numpy as np
from scipy.stats import norm
from measure import ROOT,SAMPLES,load,weights,measure,fieller,edges
from shapes import kernel,design,fit_fixed


def main():
    report={'utc':datetime.now(timezone.utc).isoformat(),'checks':{},
            'meaning':'Numerical and file-integrity checks, not independent scientific review.'}
    records=json.loads((ROOT/'data/retrieval-manifest.json').read_text())
    for r in records:
        assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
        assert (ROOT/r['path']).stat().st_size==r['bytes']
    report['checks']['retrieved_bytes_preserved']=len(records)
    inherited=json.loads((ROOT/'research/SOURCE_MANIFEST.json').read_text())
    for r in inherited['records']:
        assert hashlib.sha256((ROOT/'research'/r['local_path']).read_bytes()).hexdigest()==r['sha256']
    assert hashlib.sha256((ROOT/'PROVENANCE.json').read_bytes()).hexdigest()==inherited['scaffold_provenance']['sha256']
    fr=json.loads((ROOT/'research/protocol-freeze.json').read_text())
    assert hashlib.sha256((ROOT/'research/protocol-v1.md').read_bytes()).hexdigest()==fr['protocol_sha256']
    assert hashlib.sha256((ROOT/'analysis/sample.json').read_bytes()).hexdigest()==fr['sample_sha256']
    report['checks']['historical_notes_and_frozen_protocol']='unchanged'
    # Analytic f_nu proportional to wavelength: exact for linear interpolation.
    x=np.arange(3000.,4501.,37.);a,b=3620.,3720.
    w=weights(x,(a,b),'linear')
    assert np.isclose(w.sum(),1,atol=1e-12)
    assert np.isclose(w@x,(b-a)/np.log(b/a),rtol=1e-12)
    report['checks']['analytic_linear_spectrum_integral']='matches analytic logarithmic mean'
    d=load(SAMPLES[0]);flat=dict(d);flat['flux']=np.ones(len(d['flux']))
    m=measure(flat);assert np.isclose(m['ratio_at_means'],1,atol=1e-12)
    scaled=dict(d);scaled['flux']=d['flux']*1000;scaled['err']=d['err']*1000
    assert np.isclose(measure(d)['ratio_at_means'],measure(scaled)['ratio_at_means'],rtol=1e-12)
    bad=dict(d);bad['valid']=d['valid'].copy()
    bad['valid'][np.flatnonzero(weights(d['x'],(3620,3720))>0)[0]]=False
    assert measure(bad)['supported'] is False
    report['checks']['flat_control_scale_invariance_and_gap_rejection']='passed on synthetic/modified copies only'
    # Independently sample original pixels, instead of the two band fluxes.
    W=np.array([weights(d['x'],b) for b in [(3620,3720),(4000,4100)]])
    use=(W>0).any(axis=0);rng=np.random.default_rng(38291)
    noise=rng.normal(size=(150000,use.sum()))*d['err'][use]
    band_noise=noise@W[:,use].T
    expected=(W[:,use]*d['err'][use])@(W[:,use]*d['err'][use]).T
    realized=np.cov(band_noise.T)
    rel=np.max(np.abs(np.diag(realized)/np.diag(expected)-1))
    assert rel<.02
    report['checks']['original_pixel_draw_variance_max_fractional_difference']=float(rel)
    # Ratio confidence sets must actually satisfy the inverted Gaussian test.
    mean=np.array([.02,.2]);cov=np.diag([.01**2,.015**2]);z=norm.ppf(.975)
    fs=fieller(mean,cov,z)
    lo,hi=fs['intervals'][0]
    for t in [lo,hi]:
        test=(mean[1]-t*mean[0])**2/(cov[1,1]+t*t*cov[0,0])
        assert np.isclose(test,z*z,rtol=1e-10)
    assert fieller([.005,.2],cov,z)['kind']=='unbounded_disjoint'
    assert fieller([1,3],np.eye(2),1)['kind']=='unbounded_halfline'
    report['checks']['fieller_inversion_and_weak_denominator']='bounded, unbounded and boundary cases verified'
    # A constant f_lambda has f_nu proportional to wavelength squared.
    select=(d['x']>=3000)&(d['x']<=4600)
    grid=np.arange(2500.,5100.1,2.)
    K=kernel(d,select,grid=grid)
    ed=edges(d['x']);a=ed[:-1][select];b=ed[1:][select]
    analytic=(b*b+a*b+a*a)/3
    frac=np.max(np.abs(K@(grid*grid)/analytic-1))
    assert frac<1e-7
    report['checks']['constant_flambda_kernel_max_fractional_error']=float(frac)
    # Check quadrature/grid sensitivity of the fitted predictions using a 1 Å grid.
    fits=json.loads((ROOT/'data/derived/shape-fits.json').read_text())
    checks=[]
    for s in SAMPLES:
        dd=load(s)
        from measure import line_mask
        lm,_=line_mask(dd,.75)
        sel=dd['valid']&lm&(dd['x']>=3000)&(dd['x']<=4600)
        grid=np.arange(2500.,5100.1,1.)
        KK=kernel(dd,sel,grid=grid)
        for r in [q for q in fits if q['id']==s['id'] and q['mask_fwhm']==.75 and q['R_multiplier']==1]:
            scale=r['flux_scale_uJy'];pred=KK@np.exp(design(r['model'],r['transition_A'],grid)@np.array(r['p']))*scale
            old=np.array(r['pred'])*scale
            delta=np.max(np.abs(pred-old)/dd['err'][sel])
            assert delta<.2
            checks.append({'id':s['id'],'model':r['model'],'max_change_in_supplied_sigma':float(delta)})
    report['checks']['one_A_grid_sensitivity']=checks
    assert all(r['success'] for r in fits)
    report['checks']['optimizer_reported_success']='all recorded minima; boundaries are retained in results'
    versions={}
    import importlib.metadata as md
    for p in ['numpy','scipy','astropy','matplotlib']:versions[p]=md.version(p)
    report['environment']={'python':sys.version,'platform':platform.platform(),'packages':versions}
    report['status']='passed'
    (ROOT/'data/derived/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
