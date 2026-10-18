"""Original scientific figures for the bounded extension, from saved outputs."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from measure import ROOT,SAMPLES,BANDS

OUT=ROOT/'figures/amended-v2'
INK='#21384a';BLUE='#286dad';RED='#b64b45';ORANGE='#c7771f';GREEN='#238576'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
    'axes.spines.right':False,'text.color':INK,'axes.labelcolor':INK,
    'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','savefig.facecolor':'white'})


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg','pdf']:
        fig.savefig(OUT/f'{name}.{ext}',dpi=190,bbox_inches='tight',metadata={'Creator':'Anatomy of a Little Red Dot / Codex-assisted analysis'})
    plt.close(fig)


def main():
    fits=json.loads((ROOT/'data/derived/amended-v2/line-fits.json').read_text())
    ex=json.loads((ROOT/'data/derived/amended-v2/extraction-results.json').read_text())['results']
    def selected(s):
        return next(r for r in fits if r['id']==s['id'] and r['error_model']=='archive_full_err'
                    and r['intrinsic_fwhm_kms']==0 and r['R_multiplier']==1)
    r=selected(SAMPLES[0]);x=np.array(r['x_A']);y=np.array(r['flux_uJy']);e=np.array(r['err_uJy'])
    fig=plt.figure(figsize=(12.8,7.1));gs=fig.add_gridspec(1,2,width_ratios=[1.7,1],left=.065,right=.975,bottom=.32,top=.76,wspace=.40)
    ax=fig.add_subplot(gs[0,0]);bx=fig.add_subplot(gs[0,1])
    fig.text(.065,.94,'A large contrast can have an uncertain explanation',fontsize=20,weight='bold')
    fig.text(.065,.887,'THE CLIFF  ·  The same JWST observations, examined two ways',fontsize=11,color='#556a79')
    fig.text(.065,.845,'Frozen band ratio: 8.65  ·  Allowing a jump improves the illustrative fit’s χ² by only 0.065*',fontsize=10)
    ax.errorbar(x,y,yerr=e,fmt='o',ms=3,color=INK,ecolor='#aebac2',elinewidth=.8,label='Observed spectrum',zorder=4)
    ax.plot(x,r['nojump_total_uJy'],color=ORANGE,lw=2,label='Continuous continuum + lines')
    ax.plot(x,r['nojump_continuum_uJy'],color=GREEN,lw=1.7,ls='--',label='Continuum part of that model')
    base=next(t for t in ex if t['id']==SAMPLES[0]['id'] and t['product']=='v4' and t['variant']=='spec1d_optimal')
    for (a,b),color,f in zip(BANDS,[BLUE,RED],[base['blue_uJy'],base['red_uJy']]):
        ax.axvspan(a,b,color=color,alpha=.12);ax.plot([a,b],[f,f],color=color,lw=3,zorder=6)
    ax.axvline(3646,color='#80729a',ls=':',lw=1.1)
    ax.axhline(0,color='#aebac2',lw=.7)
    ax.set(xlim=(3100,4500),ylim=(-.035,.35),xlabel='Wavelength in the object’s frame (Å)',ylabel='Brightness, fν (µJy)')
    ax.set_title('A  ·  A continuous alternative can fit the contrast',loc='left',fontsize=11,pad=12)
    ax.legend(loc='upper left',fontsize=8.5,frameon=False)
    keys=[('v4','spec1d_optimal','Current optimal'),('v4','native_profile_normalized_sum','Current box sum'),
          ('v3_local_nod','spec1d_optimal','Earlier local / nod'),('v3_global','spec1d_optimal','Earlier global')]
    for i,(prod,var,label) in enumerate(keys):
        row=next(t for t in ex if t['id']==SAMPLES[0]['id'] and t['product']==prod and t['variant']==var)
        bx.errorbar(row['blue_uJy'],3-i,xerr=row['blue_formal_error_uJy'],fmt='o',color=BLUE,
                    capsize=3,ms=6)
    bx.axvline(0,color='#899ba7',ls=':',lw=1.2)
    bx.set(yticks=range(4),yticklabels=[k[2] for k in keys][::-1],ylim=(-.55,3.55),
           xlim=(-.012,.046),xlabel='Blue-band brightness (µJy)')
    bx.set_title('B  ·  Faint blue light limits the ratio',loc='left',fontsize=11,pad=12)
    bx.grid(axis='x',alpha=.15)
    fig.text(.065,.22,'The blue band is faint. The box extraction allows zero blue light within its uncertainty, so its ratio has no finite upper 95% bound.',fontsize=10,weight='bold')
    fig.text(.065,.157,'A: archive-rescaled 1σ errors; frozen bands and means shaded / colored. Dotted purple: hydrogen’s limit, 3646 Å.\n'
             '*The continuous model may bend at 3646 Å; it is an illustrative assumption, not a physical identification or proof that no edge exists.',fontsize=9,color='#556a79',linespacing=1.5)
    fig.text(.065,.068,'B: bars are supplied diagonal 1σ errors for each estimator. All points reuse the same exposures; their spread is not a confidence interval.\n'
             'JWST / RUBIES GO-4233 · DAWN JWST Archive / msaexp · Original analysis with Codex · Exploratory v2 · Human review pending',fontsize=8.5,color='#556a79',linespacing=1.5)
    save(fig,'central-evidence')

    fig=plt.figure(figsize=(13.2,11.5));outer=fig.add_gridspec(3,2,width_ratios=[1.35,1],left=.07,right=.97,bottom=.13,top=.91,hspace=.47,wspace=.28)
    fig.text(.07,.958,'Conditional line + continuum diagnostics',fontsize=20,weight='bold')
    fig.text(.07,.931,'Actual spectra and explicit model failures · None of these curves is a physical decomposition',fontsize=10,color='#556a79')
    for i,s in enumerate(SAMPLES):
        r=selected(s);x=np.array(r['x_A']);y=np.array(r['flux_uJy']);e=np.array(r['err_uJy'])
        inner=outer[i,0].subgridspec(2,1,height_ratios=[3,1],hspace=.07)
        ax=fig.add_subplot(inner[0]);rx=fig.add_subplot(inner[1],sharex=ax);px=fig.add_subplot(outer[i,1])
        ax.errorbar(x,y,yerr=e,fmt='o',ms=2.4,color=INK,ecolor='#b4bfc6',elinewidth=.7)
        ax.plot(x,r['best_total_uJy'],color=ORANGE,lw=1.5,label='Free jump + lines')
        ax.plot(x,r['nojump_total_uJy'],color=GREEN,ls='--',lw=1.5,label='Continuous + lines')
        ax.axvline(3646,color='#8e80a5',ls=':',lw=1)
        ax.set_title(s['nickname']+ ('  ·  model residuals remain substantial' if i==2 else ''),loc='left',fontsize=11)
        ax.set_ylabel('fν (µJy)');ax.tick_params(labelbottom=False);ax.set_xlim(3000,4600)
        if i==0:ax.legend(fontsize=8,frameon=False,loc='upper left')
        rx.axhspan(-2,2,color='#edf2f5');rx.axhline(0,color='#9aaab5',lw=.6)
        rx.plot(x,r['best_residual_sigma'],'o',ms=2.5,color=ORANGE)
        rx.plot(x,(y-np.array(r['nojump_total_uJy']))/e,'.',ms=4,color=GREEN)
        rx.set_ylim(-5.5,5.5);rx.set_yticks([-4,0,4]);rx.set_ylabel('Δ / err',fontsize=8);rx.tick_params(labelsize=8)
        rx.set_xlabel('Rest wavelength (Å)',fontsize=9)
        subset=[t for t in fits if t['id']==s['id'] and t['error_model']=='archive_full_err']
        colors=[ORANGE,'#834f9f',GREEN]
        for t in subset:
            wi=[0.,1500.,3000.].index(t['intrinsic_fwhm_kms'])
            q=np.array(t['ratio_grid']);chi=np.array(t['profile_chi2'])-t['chi2']
            px.plot(q,chi,color=colors[wi],ls='-' if t['R_multiplier']==1 else '--',lw=1.2,
                    label=f"{t['intrinsic_fwhm_kms']:g} km/s" if t['R_multiplier']==1 else None)
        px.axhline(3.84,color='#9c9c9c',ls=':',lw=1);px.axvline(1,color='#667b88',ls=':',lw=1)
        px.set(xlim=(0,7 if i==0 else 2.5),ylim=(0,15),xlabel='Imposed latent jump ratio q (1 = continuous)',ylabel='Δχ² relative to each free-jump fit')
        px.set_title('Profile sensitivity; solid R, dashed 1.3R',fontsize=10,loc='left')
        if i==0:px.legend(fontsize=8,frameon=False,loc='upper right')
    fig.text(.07,.039,'All panels use archive-rescaled independent errors; smaller raw errors give worse residual scores (especially BLAGN-1).\n'
             'Δχ² = 3.84 is a diagnostic, not calibrated confidence. Widths, continuum family and Gaussian resolution are assumptions.\n'
             'Full q grid extends to 200 in the tables. Human science / release review pending.',fontsize=9,color='#556a79',linespacing=1.5)
    save(fig,'line-diagnostics')


if __name__=='__main__':main()
