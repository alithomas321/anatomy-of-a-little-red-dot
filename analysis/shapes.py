"""Conditional continuum descriptions; no physical identity inference.

All fits use raw extracted flux, supplied independent errors, and frozen masks.
The transition is profiled instead of fixed at hydrogen's Balmer limit.
"""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ.setdefault(k,'1')
import json
import numpy as np
from scipy.optimize import least_squares
from numpy.polynomial.legendre import leggauss
from measure import ROOT,SAMPLES,OUT,load,edges,line_mask

TRANSITIONS=np.arange(3400.,4100.1,10.)
GRID=np.arange(2500.,5100.1,2.)


def kernel(d,select,rscale=1.,grid=GRID):
    """Approximate Gaussian LSF, convolving f_lambda before f_nu conversion.

    Integrate each output pixel with 5-point Gaussian quadrature. R is a
    wavelength-dependent reference, not a measured source-specific LSF.
    """
    ed=edges(d['x']);lo=ed[:-1][select];hi=ed[1:][select]
    nodes,qweights=leggauss(5)
    q=(hi[:,None]+lo[:,None])/2+(hi-lo)[:,None]*nodes[None,:]/2
    sig=q/np.interp(q,d['x'],d['R'])/rscale/2.354820045
    dt=np.gradient(grid)
    # q weight /2 is the average over a pixel, rather than integrated flux.
    K=np.zeros((len(lo),len(grid)))
    for j in range(len(nodes)):
        qq=q[:,j,None];ss=sig[:,j,None]
        density=np.exp(-.5*((qq-grid)/ss)**2)/(np.sqrt(2*np.pi)*ss)
        K+=qweights[j]/2*density*(qq/grid)**2*dt
    return K


def design(model,transition=None,grid=GRID):
    if model=='smooth':
        x=np.log(grid/4000.)
        return np.array([np.ones(len(x)),x,x*x]).T
    x=np.log(grid/transition);left=grid<transition
    cols=[np.ones(len(x)),x*left,x*(~left)]
    if model=='jump':cols.append((~left).astype(float))
    return np.array(cols).T


def fit_fixed(K,y,e,model,transition,starts,grid=GRID):
    D=design(model,transition,grid)
    if model=='smooth':bounds=([-12,-20,-100],[8,30,100])
    elif model=='continuous':bounds=([-12,-20,-20],[8,30,30])
    else:bounds=([-12,-20,-20,-5],[8,30,30,5])
    lower,upper=np.array(bounds[0]),np.array(bounds[1])
    def fun(p):
        v=np.exp(D@p)
        return (K@v-y)/e
    def jac(p):
        v=np.exp(D@p)
        return (K@(v[:,None]*D))/e[:,None]
    best=None
    for start in starts:
        r=least_squares(fun,np.clip(start,lower+1e-7,upper-1e-7),jac=jac,bounds=(lower,upper),
                        ftol=1e-9,xtol=1e-9,gtol=1e-9,max_nfev=700)
        chi=float(r.fun@r.fun)
        if best is None or chi<best['chi2']:
            best=dict(p=r.x.tolist(),chi2=chi,success=bool(r.success),nfev=int(r.nfev),
                      active_bounds=[int(i) for i in np.flatnonzero((r.x-lower<1e-4)|(upper-r.x<1e-4))],
                      pred=(K@np.exp(D@r.x)).tolist(),residual=r.fun.tolist())
    return best


def runs_for_object(s):
    d=load(s);results=[];profiles=[]
    for mask_width in [.75,1.]:
        mask,intervals=line_mask(d,mask_width)
        use=d['valid']&mask&(d['x']>=3000)&(d['x']<=4600)
        n=int(use.sum());scale=float(np.median(d['flux'][use]))
        assert scale>0 and n>7
        y=d['flux'][use]/scale;e=d['err'][use]/scale
        for rscale in [1.,1.3]:
            K=kernel(d,use,rscale)
            group=[]
            smooth=fit_fixed(K,y,e,'smooth',None,[[0,3,0],[0,8,15],[0,0,0]])
            group.append(dict(model='smooth',transition_A=None,**smooth))
            cont=[]
            for j,tr in enumerate(TRANSITIONS):
                starts=[[0,0,3]]
                if j:starts.append(cont[-1]['p'])
                r=fit_fixed(K,y,e,'continuous',tr,starts)
                cont.append(dict(model='continuous',transition_A=tr,**r))
            best=min(cont,key=lambda r:r['chi2']);group.append(best.copy())
            jumps=[]
            for j,tr in enumerate(TRANSITIONS):
                starts=[cont[j]['p']+[0.], [0,0,3,0]]
                if j:starts.append(jumps[-1]['p'])
                else:starts.extend([[0,0,3,-2],[0,0,3,2]])
                r=fit_fixed(K,y,e,'jump',tr,starts)
                jumps.append(dict(model='jump',transition_A=tr,**r))
            best=min(jumps,key=lambda r:r['chi2']);group.append(best.copy())
            for arr in [cont,jumps]:
                chi=np.array([r['chi2'] for r in arr]);accepted=TRANSITIONS[chi<=chi.min()+3.84]
                profiles.append(dict(id=s['id'],mask_fwhm=mask_width,R_multiplier=rscale,model=arr[0]['model'],
                                     transitions_A=TRANSITIONS.tolist(),chi2=chi.tolist(),
                                     support_A=accepted.tolist(),best_transition_A=float(TRANSITIONS[np.argmin(chi)])))
            for r in group:
                k={'smooth':3,'continuous':4,'jump':5}[r['model']]
                r.update(id=s['id'],mask_fwhm=mask_width,R_multiplier=rscale,n=n,k=k,
                         chi2_dof=r['chi2']/(n-k),
                         aicc=r['chi2']+2*k+2*k*(k+1)/(n-k-1),
                         flux_scale_uJy=scale,x_used=d['x'][use].tolist(),
                         flux_used_uJy=d['flux'][use].tolist(),err_used_uJy=d['err'][use].tolist(),
                         transition_at_boundary=r['transition_A'] in [3400.,4100.])
                D=design(r['model'],r['transition_A'])
                # Also render the model at masked pixels, as prediction only.
                region=(d['x']>=3000)&(d['x']<=4600)
                KK=kernel(d,region,rscale)
                r['x_plot']=d['x'][region].tolist()
                r['pred_plot_uJy']=(KK@np.exp(D@np.array(r['p']))*scale).tolist()
                r['mask_plot']=use[region].tolist()
                if r['model']=='jump':r['jump_factor']=float(np.exp(r['p'][3]))
            best_aic=min(r['aicc'] for r in group)
            for r in group:r['delta_aicc']=r['aicc']-best_aic
            results.extend(group)
            print(s['id'],mask_width,rscale,[(r['model'],round(r['chi2'],2),round(r['delta_aicc'],2),r['transition_A'],r['active_bounds']) for r in group],flush=True)
    return results,profiles


def main():
    results=[];profiles=[]
    for s in SAMPLES:
        r,p=runs_for_object(s);results.extend(r);profiles.extend(p)
        (OUT/'shape-fits.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
        (OUT/'shape-profiles.json').write_text(json.dumps(profiles,indent=2,allow_nan=False)+'\n')
    from astropy.table import Table
    cols=['id','mask_fwhm','R_multiplier','model','n','k','chi2','chi2_dof','aicc','delta_aicc','transition_A','transition_at_boundary']
    Table(rows=[{k:r[k] for k in cols} for r in results]).write(OUT/'shape-summary.csv',format='ascii.csv',overwrite=True)


if __name__=='__main__':main()
