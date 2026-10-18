"""Offline observational band measurements. See research/protocol-v1.md."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/derived'
SAMPLES = json.loads((ROOT / 'analysis/sample.json').read_text())
BANDS = ((3620., 3720.), (4000., 4100.))
LINES = {3727.:'[O II]', 3869.:'[Ne III]', 3889.:'H8 / He I',
         3970.:'Hε / [Ne III]', 4102.:'Hδ', 4341.:'Hγ'}


def edges(w):
    return np.r_[w[0] - (w[1]-w[0])/2, (w[:-1]+w[1:])/2,
                 w[-1]+(w[-1]-w[-2])/2]


def load(s, filename=None):
    p = ROOT/'data/raw/spectra'/(filename or s['file'])
    with fits.open(p) as h:
        t = Table.read(h['SPEC1D'])
        hdr = h['SPEC1D'].header.copy()
        imgs = {k: h[k].data.copy() for k in ['SCI','WHT','PROFILE','BACKGROUND'] if k in h}
        slits = Table.read(h['SLITS']) if 'SLITS' in h else None
        headers = {x.name: repr(x.header) for x in h}
    w = (t['wave'].quantity).to_value(u.um)
    f = (t['flux'].quantity).to_value(u.uJy)
    e = (t['err'].quantity).to_value(u.uJy)
    good = np.isfinite(w+f+e) & (e>0)
    if 'npix' in t.colnames:
        good &= np.array(t['npix'])>0
    if 'valid' in t.colnames:
        good &= np.array(t['valid'], bool)
    assert np.all(np.diff(w)>0)
    assert hdr['GRATING']=='PRISM' and hdr['FILTER']=='CLEAR'
    assert hdr['SRCNAME']==f"{s['pid']}_{s['srcid']}"
    sep=SkyCoord(s['ra_deg']*u.deg,s['dec_deg']*u.deg).separation(
        SkyCoord(hdr['SRCRA']*u.deg,hdr['SRCDEC']*u.deg)).arcsec
    assert sep<0.1
    rt=Table.read(ROOT/'data/raw/catalog/jwst_nirspec_prism_disp.fits')
    R=np.interp(w,rt['WAVELENGTH'],rt['R'])
    return dict(s=s,path=p,wave=w,x=w*1e4/(1+s['z']),flux=f,err=e,
                valid=good,R=R,images=imgs,header=hdr,headers=headers,
                slits=slits,table=t,separation_arcsec=sep)


def weights(w, bounds, kind='pixel'):
    """Linear f_nu weights; photon top-hat is d lambda/lambda."""
    lo,hi=bounds
    if kind in ['pixel','ivar']:
        ed=edges(w)
        a=np.maximum(ed[:-1],lo); b=np.minimum(ed[1:],hi)
        result=np.zeros(len(w))
        use=b>a
        result[use]=np.log(b[use]/a[use])/np.log(hi/lo)
        return result
    if kind=='linear':
        result=np.zeros(len(w))
        for i in range(len(w)-1):
            a=max(lo,w[i]); b=min(hi,w[i+1])
            if b<=a: continue
            dx=w[i+1]-w[i]; lg=np.log(b/a)
            result[i]+=(w[i+1]*lg-(b-a))/dx
            result[i+1]+=((b-a)-w[i]*lg)/dx
        return result/np.log(hi/lo)
    raise ValueError(kind)


def fieller(mean, cov, zscore):
    b,r=mean; vb=cov[0,0];vr=cov[1,1];c=cov[0,1]
    A=b*b-zscore*zscore*vb
    B=-2*(b*r-zscore*zscore*c)
    C=r*r-zscore*zscore*vr
    if abs(A)<1e-14*max(b*b,zscore*zscore*vb,1e-30):
        if abs(B)<1e-30:
            return {'kind':'all_real' if C<=0 else 'empty',
                    'intervals':[['-inf','inf']] if C<=0 else []}
        bound=-C/B
        return {'kind':'unbounded_halfline',
                'intervals':[['-inf',bound]] if B>0 else [[bound,'inf']]}
    disc=B*B-4*A*C
    if disc<0:
        return {'kind':'all_real' if A<0 else 'empty','intervals':[['-inf','inf']] if A<0 else []}
    roots=sorted([(-B-np.sqrt(disc))/(2*A),(-B+np.sqrt(disc))/(2*A)])
    if A>0: return {'kind':'bounded','intervals':[roots]}
    return {'kind':'unbounded_disjoint','intervals':[['-inf',roots[0]],[roots[1],'inf']]}


def summarize(mean,cov,seed=101,draws=200000):
    rng=np.random.default_rng(seed)
    d=rng.multivariate_normal(mean,cov,size=draws)
    q=np.percentile(d[:,1]/d[:,0],[16,50,84])
    sd=np.sqrt(np.diag(cov))
    return dict(blue_uJy=mean[0],red_uJy=mean[1],blue_err_uJy=sd[0],red_err_uJy=sd[1],
                blue_sn=mean[0]/sd[0],red_sn=mean[1]/sd[1],cov_blue_red=float(cov[0,1]),
                ratio_at_means=mean[1]/mean[0],ratio_p16_p50_p84=q.tolist(),
                probability_blue_nonpositive=float(norm.cdf(-mean[0]/sd[0])),
                fieller68=fieller(mean,cov,1.),fieller95=fieller(mean,cov,norm.ppf(.975)),
                red_minus_blue_sigma=float((mean[1]-mean[0])/np.sqrt(cov[1,1]+cov[0,0]-2*cov[0,1])))


def measure(d,bands=BANDS,kind='pixel',rho=0.,error_scale=1.,z=None,tilt=0.,seed=101):
    x=d['wave']*1e4/(1+(d['s']['z'] if z is None else z))
    W=np.array([weights(x,band,kind) for band in bands])
    coverage=W[:,d['valid']].sum(axis=1)
    if not np.allclose(coverage,1,atol=1e-9):
        return {'supported':False,'coverage':coverage.tolist()}
    valid=d['valid']
    if kind=='ivar':
        W[:,valid]/=d['err'][valid]**2
        W/=W.sum(axis=1)[:,None]
    # A calibration scenario normalized at the blue band center.
    scl=np.exp(np.log1p(tilt)*(x-3670.)/(4050.-3670.))
    f=np.where(valid,d['flux']*scl,0)
    e=np.where(valid,d['err']*scl*error_scale,0)
    mean=W@f
    WE=W*e
    if rho:
        corr=rho**np.abs(np.arange(len(x))[:,None]-np.arange(len(x))[None,:])
        cov=WE@corr@WE.T
    else:
        cov=WE@WE.T
    result=summarize(mean,cov,seed)
    result.update(supported=True,coverage=coverage.tolist(),bands_A=bands,
                  redshift_used=d['s']['z'] if z is None else z,
                  pixels_contributing=(W>0).sum(axis=1).tolist(),
                  effective_weighted_pixels=(1/(W**2).sum(axis=1)).tolist())
    return result


def line_mask(d,width=.75):
    keep=np.ones(len(d['x']),bool)
    intervals=[]
    for l,name in LINES.items():
        R=np.interp(l,d['x'],d['R'])
        hw=max(width*l/R,l*1500/299792.458)
        keep &= np.abs(d['x']-l)>hw
        intervals.append([l-hw,l+hw,name])
    return keep,intervals


def metadata(d):
    h=d['header']; x=d['x']; reg=(x>3000)&(x<4600)
    W=np.array([weights(x,b) for b in BANDS])
    mask,intervals=line_mask(d,1.)
    out=dict(id=d['s']['id'],file=d['path'].name,sha256=hashlib.sha256(d['path'].read_bytes()).hexdigest(),
             separation_arcsec=d['separation_arcsec'],units={c:str(d['table'][c].unit) for c in d['table'].colnames},
             header={k:h[k] for k in ['VERSION','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX','EXPTIME','NCOMBINE','EFFEXPTM','EXPSTART','EXPEND','DIFFS','WITHPATH','SKY_FILE','YTRACE','NOD_OFFSET','SRCRA','SRCDEC','PROGRAM','SOURCEID','SRCNAME'] if k in h},
             exposure_files=[h[k] for k in h if k.startswith('SFILE')],
             wavelength_observed_um=[float(d['wave'][d['valid']].min()),float(d['wave'][d['valid']].max())],
             good_pixels_in_3000_4600=int((reg&d['valid']).sum()),
             invalid_pixels_in_3000_4600=int((reg&~d['valid']).sum()),
             nominal_R_at_3646=float(np.interp(3646,x,d['R'])),
             nominal_fwhm_A_at_3646=float(3646/np.interp(3646,x,d['R'])),
             approximate_resolution_elements_per_band=[float(np.log(b/a)*np.interp((a+b)/2,x,d['R'])) for a,b in BANDS],
             fully_line_masked_original_band_coverage=(W[:,mask&d['valid']].sum(axis=1)).tolist(),
             line_mask_intervals_A=intervals,
             covariance_supplied=False,extra_error_scaling_supplied=('escale' in d['table'].colnames),
             polynomial_scaling_in_header=any(k.startswith('POLY') for k in h))
    if 'SLITS' not in d['headers']:
        out['observation_time_note']='SLITS table unavailable; header gives reference exposure'
    return out


def write_spectrum(d,label):
    keep,intervals=line_mask(d)
    t=Table(dict(wave_observed_um=d['wave'],wave_rest_A=d['x'],flux_uJy=d['flux'],
                 error_uJy=d['err'],valid=d['valid'],R_nominal=d['R'],
                 shape_mask_keep=keep,
                 blue_band_weight=weights(d['x'],BANDS[0]),red_band_weight=weights(d['x'],BANDS[1])))
    t.write(OUT/(label+'_spectrum.csv'),format='ascii.csv',overwrite=True)
    for name,header in d['headers'].items():
        (OUT/(label+'_'+name+'_header.txt')).write_text(header+'\n')
    if d['slits'] is not None:
        d['slits'].write(OUT/(label+'_exposures.csv'),format='ascii.csv',overwrite=True)


def main():
    OUT.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'data/retrieval-manifest.json').read_text())
    for rec in manifest:
        assert hashlib.sha256((ROOT/rec['path']).read_bytes()).hexdigest()==rec['sha256']
    results=[]; metas=[]; alternatives=[]
    for s in SAMPLES:
        d=load(s); write_spectrum(d,s['id']); metas.append(metadata(d))
        baseline=measure(d,seed=s['srcid'])
        results.append(dict(id=s['id'],nickname=s['nickname'],z=s['z'],**baseline))
        variants=[('baseline',{}),('linear_interpolation',{'kind':'linear'}),
                  ('inverse_variance',{'kind':'ivar'}),
                  ('bands_minus_50A',{'bands':((3570,3670),(3950,4050))}),
                  ('bands_plus_50A',{'bands':((3670,3770),(4050,4150))}),
                  ('line_avoiding_bands',{'bands':((3500,3600),(4150,4250))}),
                  ('redshift_minus_300kms',{'z':s['z']-.001*(1+s['z'])}),
                  ('redshift_plus_300kms',{'z':s['z']+.001*(1+s['z'])}),
                  ('tilt_minus_5pct',{'tilt':-.05}),('tilt_plus_5pct',{'tilt':.05}),
                  ('noise_rho_0.3',{'rho':.3}),('noise_rho_0.6',{'rho':.6}),
                  ('errors_times_2',{'error_scale':2.})]
        # Final source cross-check: an explicitly post hoc literature redshift.
        # Keep the catalog value frozen; do not select whichever ratio is larger.
        if s['id']=='RUBIES-UDS-40579':
            paper={'url':'https://arxiv.org/html/2403.02304v3#S4.T2',
                   'ra_deg':34.244201,'dec_deg':-5.245872,'z':3.1034,
                   'reported_z_error':0.0002}
            paper['separation_arcsec']=float(SkyCoord(s['ra_deg']*u.deg,s['dec_deg']*u.deg).separation(
                SkyCoord(paper['ra_deg']*u.deg,paper['dec_deg']*u.deg)).arcsec)
            assert paper['separation_arcsec']<0.1
            metas[-1]['literature_identity_crosscheck']=paper
            variants.append(('wang_paper_z_3.1034',{'z':paper['z']}))
        # Same samples expressed in f_lambda, reported as a DIFFERENT estimand.
        conv=(1*u.uJy).to_value(u.erg/u.s/u.cm**2/u.AA,equivalencies=u.spectral_density(d['wave']*u.um))
        fmeans=[];fmeds=[]
        for b in BANDS:
            w=weights(d['x'],b)
            fmeans.append(float(w@np.where(d['valid'],d['flux']*conv,0)))
            fmeds.append(float(np.median((d['flux']*conv)[(d['x']>=b[0])&(d['x']<=b[1])&d['valid']])))
        alternatives.append(dict(id=s['id'],variant='flambda_mean',ratio_at_means=fmeans[1]/fmeans[0],supported=True))
        alternatives.append(dict(id=s['id'],variant='flambda_median',ratio_at_means=fmeds[1]/fmeds[0],supported=True))
        for name,kw in variants:
            alternatives.append(dict(id=s['id'],variant=name,**measure(d,seed=s['srcid'],**kw)))
        # Post-acquisition diagnostic from the archive's ancillary redshift fit.
        # Its full_err is explicitly built in the same numerical flux units,
        # though its FITS unit metadata are incomplete. Never infer this from
        # the misleading unit on escale; verify arrays and the source formula.
        ancillary=d['path'].with_name(s['file'].replace('.spec.fits','.spec.zfit.fits'))
        if ancillary.exists():
            with fits.open(ancillary) as h:
                ft=h['SPEC1D'].data
                full=np.array(ft['full_err'])
                region=(d['x']>=3000)&(d['x']<=4600)
                assert np.allclose(ft['wave'],d['wave'])
                assert np.allclose(ft['flux'][region],d['flux'][region])
                assert np.allclose(ft['err'][region],d['err'][region])
                assert np.allclose(full[region]**2,
                    (ft['err'][region]*ft['escale'][region])**2+
                    (h['SPEC1D'].header['SYS_ERR']*np.maximum(ft['flux'][region],0))**2)
                dd=dict(d);dd['err']=full;dd['valid']=d['valid']&np.array(ft['valid'])&(full>0)
                r=measure(dd,seed=s['srcid'])
                r['full_err_over_raw_band_errors']=[r['blue_err_uJy']/baseline['blue_err_uJy'],r['red_err_uJy']/baseline['red_err_uJy']]
                alternatives.append(dict(id=s['id'],variant='archive_fit_full_error',**r))
                if s['id']=='RUBIES-UDS-40579':
                    alternatives.append(dict(id=s['id'],variant='wang_paper_z_archive_full_error',
                                             **measure(dd,z=3.1034,seed=s['srcid'])))
        print(s['id'],json.dumps(baseline))
    old=SAMPLES[0]['file'].replace('-v4','-v3')
    if (ROOT/'data/raw/spectra'/old).exists():
        d=load(SAMPLES[0],old);write_spectrum(d,'TheCliff_v3');metas.append(metadata(d))
        for name,z in [('v3_global_current_z',SAMPLES[0]['z']),('v3_global_paper_z',3.548)]:
            alternatives.append(dict(id=SAMPLES[0]['id'],variant=name,**measure(d,z=z)))
            print(name,alternatives[-1])
    nod=old.replace('uds31-v3','uds31-nod-v3')
    if (ROOT/'data/raw/spectra'/nod).exists():
        d=load(SAMPLES[0],nod);write_spectrum(d,'TheCliff_v3_nod');metas.append(metadata(d))
        for name,z in [('v3_nod_current_z',SAMPLES[0]['z']),('v3_nod_paper_z',3.548)]:
            alternatives.append(dict(id=SAMPLES[0]['id'],variant=name,**measure(d,z=z)))
            print(name,alternatives[-1])
    for name,value in [('measurements',results),('sensitivity',alternatives),('product-audit',metas)]:
        (OUT/(name+'.json')).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    rows=[]
    for r in results:
        rows.append({k:r[k] for k in ['id','z','blue_uJy','blue_err_uJy','blue_sn','red_uJy','red_err_uJy','red_sn','ratio_at_means','red_minus_blue_sigma']})
        rows[-1].update(dict(zip(['ratio_p16','ratio_p50','ratio_p84'],r['ratio_p16_p50_p84'])))
        rows[-1]['fieller95_kind']=r['fieller95']['kind']
    Table(rows=rows).write(OUT/'measurements.csv',format='ascii.csv',overwrite=True)
    simple=[]
    for r in alternatives:
        simple.append(dict(id=r['id'],variant=r['variant'],supported=r['supported'],
                           redshift_used=r.get('redshift_used'),
                           ratio=r.get('ratio_at_means'),p16=r.get('ratio_p16_p50_p84',[None]*3)[0],
                           p50=r.get('ratio_p16_p50_p84',[None]*3)[1],p84=r.get('ratio_p16_p50_p84',[None]*3)[2],
                           fieller95=json.dumps(r.get('fieller95'))))
    Table(rows=simple).write(OUT/'sensitivity.csv',format='ascii.csv',overwrite=True)


if __name__=='__main__':
    main()
