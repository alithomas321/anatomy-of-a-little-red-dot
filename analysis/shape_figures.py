"""Plot conditional shape fits and the loss of transition information."""
from figures import *

def main():
    fits=json.loads((ROOT/'data/derived/shape-fits.json').read_text())
    prof=json.loads((ROOT/'data/derived/shape-profiles.json').read_text())
    colors={'smooth':'#728d5b','continuous':BLUE,'jump':RED}
    fig,axs=plt.subplots(2,3,figsize=(14,8))
    fig.subplots_adjust(left=.07,right=.97,top=.85,bottom=.19,hspace=.35,wspace=.28)
    fig.suptitle('The contrast is measurable; the exact edge is not securely located',fontsize=17,y=.97)
    for j,s in enumerate(SAMPLES):
        d=load(s);ax=axs[0,j]
        region=(d['x']>=3000)&(d['x']<=4600)&d['valid'];keep,intervals=line_mask(d,.75)
        for lo,hi,name in intervals:ax.axvspan(lo,hi,color='#d6dadd',alpha=.55,lw=0)
        ax.errorbar(d['x'][region],d['flux'][region],yerr=d['err'][region],fmt='o',ms=2.6,color=GRAY,ecolor='#adb4ba',elinewidth=.5)
        ax.plot(d['x'][region&keep],d['flux'][region&keep],'o',color=INK,ms=3)
        these=[r for r in fits if r['id']==s['id'] and r['mask_fwhm']==.75 and r['R_multiplier']==1]
        for r in these:
            ax.plot(r['x_plot'],r['pred_plot_uJy'],color=colors[r['model']],lw=1.3,label=r['model'])
        ax.axvline(3646,ls='--',color='#766299',lw=1)
        ax.set_xlim(3000,4600);ax.set_ylim(bottom=-.015)
        ax.set_title(s['nickname'],fontsize=11)
        ax.set_xlabel('Rest wavelength (Å)')
        if j==0:ax.set_ylabel('Measured fν (µJy)');ax.legend(frameon=False,fontsize=8)
        ax=axs[1,j]
        for width,ls in [(.75,'-'),(1.,'--')]:
            for model in ['continuous','jump']:
                r=next(r for r in prof if r['id']==s['id'] and r['mask_fwhm']==width and r['R_multiplier']==1 and r['model']==model)
                chi=np.array(r['chi2']);ax.plot(r['transitions_A'],chi-chi.min(),color=colors[model],ls=ls,lw=1.3,label=f'{model}, mask {width:g} FWHM')
        ax.axhline(3.84,color=GRAY,lw=.8,ls=':');ax.axvline(3646,ls='--',color='#766299',lw=1)
        ax.set_xlim(3400,4100);ax.set_ylim(0,12)
        ax.set_xlabel('Assumed transition in the fit (Å)')
        if j==0:ax.set_ylabel('Fit penalty above its minimum (Δχ²)')
        if j==2:ax.legend(fontsize=7,frameon=False,loc='upper right')
    fig.text(.07,.055,'Upper panels: gray spans are excluded line regions; predictions within them are extrapolations of the chosen shape.\nLower panels: many transition locations fit similarly; some minima reach the allowed boundary. Changing the mask changes the answer.\nEach profile is relative to its own minimum. The dotted Δχ²=3.84 line is a descriptive reference, not a calibrated detection threshold.\nGaussian instrument model and independent supplied errors. These are mathematical descriptions, not models identifying the power source.',fontsize=10)
    save(fig,'shape-ambiguity')

    fig,axs=plt.subplots(1,3,figsize=(13,4.5),sharey=True)
    fig.subplots_adjust(left=.22,right=.96,top=.80,bottom=.25,wspace=.15)
    sens=json.loads((ROOT/'data/derived/sensitivity.json').read_text())
    names=['baseline','archive_fit_full_error','noise_rho_0.3','noise_rho_0.6','errors_times_2']
    labels=['Supplied errors','Archive rescaled errors','Correlation scenario ρ=0.3','Correlation scenario ρ=0.6','Error-amplitude scenario ×2']
    for i,s in enumerate(SAMPLES):
        ax=axs[i];rs={r['variant']:r for r in sens if r['id']==s['id']}
        for j,name in enumerate(names):
            r=rs[name];fs=r['fieller95'];v=r['ratio_at_means']
            if fs['kind']=='bounded':
                lo,hi=fs['intervals'][0]
                ax.plot([lo,hi],[j,j],color=INK,lw=2)
            else:
                lo=fs['intervals'][-1][0];hi=250
                ax.annotate('',xy=(hi,j),xytext=(lo,j),arrowprops=dict(arrowstyle='->',color=RED,lw=1.8))
                ax.text(lo*1.05,j-.12,'no finite upper bound',fontsize=8,color=RED)
            ax.plot(v,j,'o',color=RED,ms=5)
        ax.axvline(1,ls='--',lw=.8,color=BLUE)
        ax.set_xscale('log');ax.set_title(s['nickname'],fontsize=11)
        ax.set_xlim([2,.65,.6][i],[300,5,2.3][i]);ax.set_xlabel('Red / blue ratio')
        ax.set_xticks([[3,10,30,100],[1,2,3,4],[.7,1,1.5,2]][i]);ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.grid(axis='x',alpha=.15)
    axs[0].set_yticks(range(5),labels);axs[0].set_ylim(4.55,-.5)
    fig.suptitle('The Cliff’s upper bound depends on the noise assumptions',fontsize=17)
    fig.text(.05,.055,'Bars: positive branch of the 95% Fieller confidence set. Unbounded sets also have a negative branch, saved in the tables.\nArchive rescaling is an actual ancillary product; the correlation and ×2 rows are stated stress scenarios.\nThe observations do not supply a covariance matrix. Panel x-axis ranges differ.',fontsize=9)
    save(fig,'uncertainty-assumptions')

if __name__=='__main__':main()
