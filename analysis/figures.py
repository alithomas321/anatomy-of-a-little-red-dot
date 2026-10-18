"""Generate standalone scientific figures from the observed spectra and results."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(__file__).resolve().parent/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, NullFormatter
import numpy as np
import json
from measure import ROOT,SAMPLES,load,edges,BANDS,weights,line_mask

DEST=ROOT/'figures'
BLUE='#2670aa'; RED='#b54b3e'; INK='#203244'; GRAY='#77818a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,
                     'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,
                     'figure.facecolor':'white','savefig.facecolor':'white','svg.fonttype':'none'})


def save(fig,name):
    DEST.mkdir(exist_ok=True)
    for ax in fig.axes:
        if ax.get_xscale()=='log':ax.xaxis.set_minor_formatter(NullFormatter())
    for ext in ['png','svg']:
        fig.savefig(DEST/(name+'.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)


def observed_axis(ax,z):
    sec=ax.secondary_xaxis('top',functions=(lambda x:x*(1+z)/1e4,lambda x:x*1e4/(1+z)))
    sec.set_xlabel('Wavelength reaching JWST (µm)',fontsize=9,labelpad=5)
    sec.tick_params(labelsize=8)


def spectrum(ax,d,limits=(3100,4500),bands=True):
    x=d['x']; good=d['valid']&(x>=limits[0])&(x<=limits[1])
    ax.errorbar(x[good],d['flux'][good],yerr=d['err'][good],fmt='o',ms=3,
                color=INK,ecolor='#a7afb6',elinewidth=.8,capsize=0,zorder=3)
    ax.plot(x[good],d['flux'][good],color=INK,lw=.8,alpha=.7)
    ax.axhline(0,color=GRAY,lw=.7)
    ax.axvline(3646,color='#766299',ls='--',lw=1.1)
    if bands:
        for i,(a,b) in enumerate(BANDS):
            color=[BLUE,RED][i]
            ax.axvspan(a,b,color=color,alpha=.15)
            w=weights(x,(a,b)); f=w@np.where(d['valid'],d['flux'],0)
            ax.plot([a,b],[f,f],color=color,lw=3,zorder=5)
    for l in [3727,4102,4341,4862,5008,6564]:
        if limits[0]<l<limits[1]: ax.axvline(l,color=GRAY,ls=':',alpha=.6,lw=.8)
    ax.set_xlim(*limits)
    yl=min(0,np.min(d['flux'][good]-d['err'][good]))
    yh=np.max(d['flux'][good]+d['err'][good])
    ax.set_ylim(yl-.08*(yh-yl),yh+.16*(yh-yl))
    ax.set_ylabel('Brightness, fν (µJy)')
    ax.set_xlabel('Wavelength in the object’s frame (Å)')
    ax.grid(axis='y',alpha=.15)


def twod(ax,d,limits=(3100,4500),sn=False):
    im=d['images']['SCI'].copy(); wht=d['images']['WHT']
    if sn: im=im*np.sqrt(np.maximum(wht,0))
    im[(wht<=0)|~np.isfinite(im)]=np.nan
    use=(d['x']>limits[0])&(d['x']<limits[1])
    if sn: vmax=7.
    else: vmax=np.nanpercentile(np.abs(im[:,use]),98)
    ny=im.shape[0];yc=d['header'].get('YTRACE',(ny-1)/2)
    pm=ax.pcolormesh(edges(d['x']),np.arange(ny+1)-.5-yc,im,cmap='RdBu_r',
                     vmin=-vmax,vmax=vmax,rasterized=True)
    ax.set_xlim(*limits);ax.set_ylim(-8,8)
    ax.axhline(0,color='black',lw=.55,ls='--',alpha=.5)
    for a,b in BANDS:
        ax.axvline(a,color='black',lw=.6,alpha=.5);ax.axvline(b,color='black',lw=.6,alpha=.5)
    ax.axvline(3646,color='#503179',ls='--',lw=1.1)
    ax.set_ylabel('Rows from source trace');ax.set_xlabel('Rest wavelength (Å)')
    return pm


def main():
    result=json.loads((ROOT/'data/derived/measurements.json').read_text())
    sens=json.loads((ROOT/'data/derived/sensitivity.json').read_text())
    data=[load(s) for s in SAMPLES]
    fig,axs=plt.subplots(3,2,figsize=(13,13),gridspec_kw={'width_ratios':[1.35,1]})
    fig.subplots_adjust(hspace=.80,wspace=.3,top=.83,bottom=.15)
    fig.suptitle('Three observed little red dots — three different measurement problems',fontsize=17,y=.975)
    fig.text(.08,.935,'Blue band: 3620–3720 Å  •  Red band: 4000–4100 Å  •  Dashed purple: hydrogen’s Balmer limit',fontsize=10)
    for j,(s,d,r) in enumerate(zip(SAMPLES,data,result)):
        ax=axs[j,0];spectrum(ax,d);observed_axis(ax,s['z'])
        ax.set_title(s['nickname']+f"   |   z = {s['z']:.4f}",loc='left',pad=48)
        axs[j,1].set_title('2D spectrum: the source runs along row 0',loc='left',pad=12)
        pm=twod(axs[j,1],d,sn=True)
        cb=fig.colorbar(pm,ax=axs[j,1],fraction=.035,pad=.025)
        cb.set_label('SCI × √WHT (display only)',fontsize=8)
        label=['Large contrast; faint blue denominator','Stable contrast in the original bands','Original bands allow equal brightness'][j]
        ax.text(.02,.95,label,transform=ax.transAxes,va='top',fontsize=9,
                bbox=dict(facecolor='white',alpha=.9,edgecolor='none',pad=2))
    fig.text(.08,.025,'Dots and gray bars: extracted measurements ±1 supplied error. Solid colored segments: measured band means.\n2D negative traces near ±5 rows arise from nodded background subtraction. Blank areas have no valid weight.\nJWST GO-4233 / RUBIES; DJA v4 extractions. New local calculations, 10 September 2026.',fontsize=9)
    save(fig,'annotated-spectra')

    for s,d in zip(SAMPLES,data):
        fig,ax=plt.subplots(3,1,figsize=(10,11),gridspec_kw={'height_ratios':[1.1,1.3,.8]})
        fig.subplots_adjust(hspace=.5,top=.9,bottom=.09)
        fig.suptitle(s['nickname']+' — inspect the observation',fontsize=18,y=.97)
        spectrum(ax[0],d,(2500,7000)); observed_axis(ax[0],s['z'])
        spectrum(ax[1],d)
        for a in ax[:2]:a.yaxis.set_label_coords(-.065,.5)
        ax[1].text(.02,.95,'The colored bands define a contrast; they do not isolate an uncontaminated edge.',
                   transform=ax[1].transAxes,fontsize=9,va='top')
        pm=twod(ax[2],d,sn=False)
        cb=fig.colorbar(pm,ax=ax[2],fraction=.025,pad=.02);cb.set_label('SCI (µJy per spatial pixel)',fontsize=9)
        fig.text(.1,.025,f"{s['file']}\nSame data in all panels. Dotted lines mark potential emission-line locations, not detections.\nPurple dashed line: 3646 Å. Gray error bars are conditional on the archive’s supplied errors.",fontsize=8)
        save(fig,s['id']+'-spectrum')

    fig,ax=plt.subplots(figsize=(9.5,5.1))
    fig.subplots_adjust(left=.26,bottom=.25,top=.84)
    for j,r in enumerate(result):
        q=r['ratio_p16_p50_p84'];v=r['ratio_at_means'];low,high=r['fieller95']['intervals'][0]
        ax.plot([low,high],[j,j],color=GRAY,lw=1.4)
        ax.plot([q[0],q[2]],[j,j],color=INK,lw=5)
        ax.plot(v,j,'o',color=RED,ms=7,zorder=5)
        arc=next(a for a in sens if a['id']==r['id'] and a['variant']=='archive_fit_full_error')
        al,ah=arc['fieller95']['intervals'][0]
        ax.plot([al,ah],[j+.12,j+.12],color=BLUE,lw=1.5)
        ax.text(v,j-.23,f'{v:.2f}',ha='center',fontsize=10)
    ax.axvline(1,color=BLUE,ls='--',lw=1)
    ax.set_xscale('log');ax.set_xlim(.7,80);ax.set_ylim(2.5,-.6)
    ax.set_xticks([1,2,3,5,10,20,40]);ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks(range(3),['The Cliff','RUBIES-BLAGN-1','RUBIES-UDS-182791'])
    ax.set_xlabel('Red-band brightness ÷ blue-band brightness (fν ratio)')
    ax.grid(axis='x',alpha=.15)
    fig.suptitle('A strong contrast can still have an uncertain size',fontsize=17)
    fig.text(.10,.06,'Dots: ratio at measured means. Thick bars: 16–84% interval from supplied extraction errors.\nThin gray: 95% Fieller interval. Thin blue below each row: 95% with archive rescaled errors.\nDashed line: equal brightness. These intervals still assume independent errors; calibration and\nextraction uncertainty are incomplete. See uncertainty-assumptions for unbounded cases.',fontsize=9)
    save(fig,'band-ratios')

    names=['baseline','linear_interpolation','inverse_variance','bands_minus_50A','bands_plus_50A','line_avoiding_bands','tilt_minus_5pct','tilt_plus_5pct']
    labels=['Original bands','Linear interpolation','Noise-weighted mean','Both bands −50 Å','Both bands +50 Å','3500–3600 / 4150–4250 Å','Calibration tilt −5%','Calibration tilt +5%']
    fig,axs=plt.subplots(1,3,figsize=(12,6),sharey=True)
    fig.subplots_adjust(left=.24,right=.97,bottom=.24,top=.80,wspace=.17)
    fig.suptitle('Band placement matters more than small numerical choices',fontsize=16,y=.97)
    for i,s in enumerate(SAMPLES):
        ax=axs[i];rows={r['variant']:r for r in sens if r['id']==s['id']}
        for j,n in enumerate(names):
            r=rows[n];q=r['ratio_p16_p50_p84'];color=RED if j in [3,4,5] else INK
            ax.plot([q[0],q[2]],[j,j],color=color,lw=2)
            ax.plot(r['ratio_at_means'],j,'o',color=color,ms=5)
        ax.axvline(1,ls='--',color=BLUE,lw=.8)
        ax.axvline(rows['baseline']['ratio_at_means'],color=GRAY,ls=':',lw=.8)
        ax.set_title(s['nickname'],fontsize=11)
        ax.set_xscale('log');ax.set_xlim([3,.7,.65][i],[30,5.5,2.3][i])
        ticks=[[3,5,10,20,30],[1,2,3,4,5],[.7,1,1.5,2]][i]
        ax.set_xticks(ticks);ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.set_xlabel('Red / blue ratio');ax.grid(axis='x',alpha=.15)
    axs[0].set_yticks(range(len(names)),labels);axs[0].set_ylim(7.7,-.7)
    fig.text(.06,.065,'Bars: 16–84% intervals under the same supplied-error model; rows reuse the same observations.\nRed rows change the wavelength bands and therefore the quantity measured. A changed ratio need not mean\na wrong calculation: it can expose a steep slope or blended lines. Panel x-axis ranges differ.',fontsize=10)
    save(fig,'analysis-sensitivity')

    fig,ax=plt.subplots(2,1,figsize=(10,7.2),sharex=True)
    fig.subplots_adjust(hspace=.12,top=.9,bottom=.17)
    old=load(SAMPLES[0],SAMPLES[0]['file'].replace('-v4','-v3'));cur=data[0]
    nod=load(SAMPLES[0],SAMPLES[0]['file'].replace('uds31-v4','uds31-nod-v3'))
    for d,label,c in [(old,'v3 global background',BLUE),(nod,'v3 local nod background','#69916e'),(cur,'v4 local nod background',RED)]:
        good=d['valid']&(d['x']>3100)&(d['x']<4500)
        ax[0].errorbar(d['x'][good],d['flux'][good],yerr=d['err'][good],fmt='o-',ms=3,lw=.8,color=c,alpha=.8,label=label)
        ax[1].plot(d['x'][good],d['err'][good],color=c,lw=1.2,label=label)
    for a in ax:
        a.axvline(3646,ls='--',color='#766299',lw=1)
        for i,(lo,hi) in enumerate(BANDS):a.axvspan(lo,hi,color=[BLUE,RED][i],alpha=.09)
        a.grid(axis='y',alpha=.15)
    ax[0].axhline(0,color=GRAY,lw=.7);ax[0].legend(frameon=False)
    ax[0].set_ylabel('Measured fν (µJy)');ax[1].set_ylabel('Supplied 1σ error (µJy)')
    ax[1].set_xlabel('Rest wavelength (Å)');ax[1].set_xlim(3100,4500)
    fig.suptitle('The Cliff: reduction choices affect the uncertainty',fontsize=17)
    fig.text(.12,.035,'All three files contain the same July 2024 exposures. They are not independent measurements.\nThe 2025 paper used v3 with local nod background subtraction. The alternate global-background\nproduct is retained as a check. Raw bytes, calibration headers and variant labels are retained in data/.',fontsize=9)
    save(fig,'cliff-reduction-comparison')


if __name__=='__main__':main()
