"""Verify scientific arithmetic and exact artifact state; never human sign-off."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ.setdefault(key,'1')
import hashlib
import importlib.metadata as md
import json
import platform
import re
import sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from measure import ROOT,SAMPLES,load,weights,BANDS,fieller
from amended_v2_lines import matrix,solve,full_errors
from amended_v2_extraction import band_result,native_sum,image_extract

OUT=ROOT/'data/derived/amended-v2'
MANIFEST=OUT/'final-state-manifest.json'
REPORT=OUT/'verification.json'
EXCLUDED_PARTS={'.venv','.cache','__pycache__','.git'}
EXCLUDED_FILES={MANIFEST,REPORT}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def inventory():
    return {str(p.relative_to(ROOT)):p for p in ROOT.rglob('*') if p.is_file()
            and not any(x in EXCLUDED_PARTS for x in p.relative_to(ROOT).parts)
            and p not in EXCLUDED_FILES and p.suffix!='.log'}


def check_snapshot():
    recorded=json.loads(MANIFEST.read_text())
    current=inventory();stored={r['path']:r for r in recorded['files']}
    assert set(current)==set(stored),'Artifact set changed since verification'
    for name,p in current.items():assert sha(p)==stored[name]['sha256'],name
    report=json.loads(REPORT.read_text())
    assert report['status']=='passed' and report['manifest_sha256']==sha(MANIFEST)
    print(json.dumps({'status':'passed','mode':'exact_delivered_snapshot','artifact_count':len(current),
                      'manifest_sha256':sha(MANIFEST),'human_science_review':'pending'},indent=2))


def write_assets():
    info={
      'central-evidence':('primary','The Cliff: observed spectrum with a bending continuous continuum plus emission; blue-band estimates under four same-exposure extractions/reductions, with the box-sum uncertainty crossing zero.'),
      'line-diagnostics':('technical','Spectra, residuals and conditional jump-ratio profiles for the three objects. The weak object retains substantial residuals; diagnostic profile thresholds are not calibrated confidence.'),
      'extraction-sensitivity':('technical','Blue-band flux under fixed extraction alternatives for each object, above explicitly hypothetical common-offset effects on the ratios. The offset is not measured sky error.')}
    assets=[]
    for stem,(role,alt) in info.items():
        for suffix in ['png','svg','pdf']:
            p=ROOT/f'figures/amended-v2/{stem}.{suffix}'
            if not p.exists():continue
            record=dict(role=role,path=str(p.relative_to(ROOT)),absolute_path=str(p),sha256=sha(p),
                        bytes=p.stat().st_size,alt=alt,human_review_pending=True)
            if suffix=='png':
                with Image.open(p) as im:record['width_px'],record['height_px']=im.size
            assets.append(record)
    doc=ROOT/'research/amended-v2/website-copy.md'
    payload={'status':'Prepared for private draft integration; human understanding/science/contribution/release review pending',
        'website_modified':False,'published':False,'project_root':str(ROOT),
        'text':{'path':str(doc.relative_to(ROOT)),'absolute_path':str(doc),'sha256':sha(doc)},
        'credit':'NASA/ESA/CSA JWST; RUBIES GO-4233 (Anna de Graaff, Gabriel Brammer); DAWN JWST Archive / msaexp. Original analysis and figures prepared with Codex under Alison’s direction.',
        'reuse_scope':'Original project text and figures only; no third-party paper figures or raw FITS redistribution license granted.',
        'assets':assets}
    (ROOT/'research/amended-v2/website-assets.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')


def main():
    checks={}
    before=json.loads((ROOT/'research/amended-v2/pre-work-inventory.json').read_text())['files']
    allowed={'README.md','CASE_STUDY.md'}
    for r in before:
        p=ROOT/r['path'];assert p.exists(),r['path']
        if r['path'] in allowed:
            name='README-v1-preserved.md' if r['path']=='README.md' else 'CASE_STUDY-v1-preserved.md'
            assert sha(ROOT/'research/amended-v2'/name)==r['sha256']
        else:assert sha(p)==r['sha256'],r['path']
    checks['preexisting_files_unchanged']=len(before)-len(allowed)
    checks['updated_reader_pages_with_byte_exact_archival_copies']=sorted(allowed)
    manifests=[(ROOT/'data/retrieval-manifest.json',None),(ROOT/'research/amended-v2/source-manifest.json','resources')]
    count=0
    for p,key in manifests:
        contents=json.loads(p.read_text());records=contents if key is None else contents[key]
        for r in records:
            assert sha(ROOT/r['path'])==r['sha256'];assert (ROOT/r['path']).stat().st_size==r['bytes'];count+=1
    checks['retrieved_resource_hashes']=count
    frozen=json.loads((ROOT/'research/protocol-freeze.json').read_text())
    assert sha(ROOT/'analysis/sample.json')==frozen['sample_sha256']
    assert sha(ROOT/'research/protocol-v1.md')==frozen['protocol_sha256']
    checks['frozen_protocol_and_three_object_sample']='unchanged'
    original=json.loads((ROOT/'data/derived/measurements.json').read_text())
    spectra={}
    for s in SAMPLES:
        d=load(s);spectra[s['id']]=d;r=next(x for x in original if x['id']==s['id'])
        m=band_result(d['x'],d['flux'],d['err'],d['valid'])
        for new,old in [('blue_uJy','blue_uJy'),('red_uJy','red_uJy'),('ratio','ratio_at_means')]:
            assert np.isclose(m[new],r[old],rtol=1e-12,atol=1e-14)
    checks['original_observed_band_measurements_reproduced']=3
    extraction=json.loads((OUT/'extraction-results.json').read_text())['results']
    for r in extraction:
        d=spectra[r['id']]
        if r['product']!='v4':
            filename=SAMPLES[0]['file'].replace('uds31-v4','uds31-nod-v3' if r['product']=='v3_local_nod' else 'uds31-v3')
            d=load(SAMPLES[0],filename)
        if r['variant']=='native_profile_normalized_sum':
            t=d['table'];f,e,v=native_sum(np.array(t['flux_sum']),np.array(t['profile_sum']),np.array(t['var_sum']))
        elif r['variant'].startswith('image_'):
            match=re.fullmatch(r'image_r(\d)_shift(-?\d)',r['variant']);radius,shift=map(int,match.groups())
            f,e,v,_=image_extract(d['images']['SCI'],d['images']['WHT'],d['images']['PROFILE'],int(d['header']['YTRACE']),radius,shift)
        else:f,e,v=d['flux'],d['err'],d['valid']
        m=band_result(d['x'],f,e,v)
        for key in ['blue_uJy','red_uJy','blue_formal_error_uJy','red_formal_error_uJy','ratio']:
            assert np.isclose(m[key],r[key],rtol=1e-12,atol=1e-14)
        assert m['fieller95_diagonal']==r['fieller95_diagonal']
    assert json.loads((OUT/'extraction-validation.json').read_text())['all_passed']
    for r in json.loads((OUT/'extraction-provenance.json').read_text())['inputs']:
        assert sha(ROOT/r['path'])==r['sha256'],r['path']
    checks['fresh_extraction_rows_and_confidence_sets']=len(extraction)
    fits=json.loads((OUT/'line-fits.json').read_text());assert len(fits)==36
    lc=json.loads((OUT/'line-checks.json').read_text())
    assert lc['script_sha256']==sha(ROOT/'analysis/amended_v2_lines.py') and lc['status']=='passed'
    assert len(lc['checks'])==18
    for r in fits:
        d=spectra[r['id']];s=next(s for s in SAMPLES if s['id']==r['id'])
        use=d['valid']&(d['x']>=3000)&(d['x']<=4600);y=d['flux'][use]
        e=full_errors(s,d)[use] if r['error_model']=='archive_full_err' else d['err'][use]
        A,_=matrix(d,use,r['intrinsic_fwhm_kms'],r['R_multiplier'])
        p,c,k=solve(A,y,e);p0,c0,k0=solve(A,y,e,1.)
        assert np.allclose(A@p,r['best_total_uJy'],rtol=1e-10,atol=1e-12)
        assert np.allclose(A@p0,r['nojump_total_uJy'],rtol=1e-10,atol=1e-12)
        assert np.isclose(c,r['chi2'],rtol=1e-10,atol=1e-10)
        assert np.isclose(c0-c,r['nojump_delta_chi2'],rtol=1e-8,atol=1e-10)
        assert np.allclose(r['err_uJy'],e) and np.allclose(r['flux_uJy'],y)
        profile=np.array(r['profile_chi2']);q=np.array(r['ratio_grid'])
        assert np.all(profile>=c-1e-7)
        assert np.array_equal(q[profile<=c+3.84],np.array(r['nominal_support_grid']))
        # Independently rerun a boundary, no-jump, and last scan point.
        for j in [0,20,len(q)-1]:
            _,cc,_=solve(A,y,e,q[j]);assert np.isclose(cc,profile[j],rtol=1e-10,atol=1e-10)
    checks['fresh_joint_fit_minima_and_profile_spot_checks']=len(fits)
    checks['largest_half_grid_change_in_archive_error_units']=max(r['finer_grid_max_change_sigma'] for r in lc['checks'])
    versions={}
    for line in (ROOT/'analysis/requirements.lock').read_text().splitlines():
        match=re.fullmatch(r'([A-Za-z0-9_.-]+)==([^ ]+)',line)
        if match:
            name,version=match.groups();actual=md.version(name);assert actual==version,(name,actual,version);versions[name]=actual
    checks['locked_package_versions_verified']=len(versions)
    image_count=0
    for p in sorted((ROOT/'figures/amended-v2').glob('*')):
        if p.suffix=='.png':
            with Image.open(p) as im:
                im.load();a=np.asarray(im.convert('RGB'));assert min(im.size)>600;assert np.std(a)>10
            image_count+=1
        elif p.suffix=='.svg':ET.parse(p)
        elif p.suffix=='.pdf':assert p.read_bytes().startswith(b'%PDF-')
    checks['nonblank_readable_pngs_and_vector_containers']=image_count
    write_assets()
    docs=[ROOT/'README.md',ROOT/'CASE_STUDY.md',ROOT/'PORTFOLIO_HANDOFF.md',ROOT/'research/observational-report-v2.md',
          ROOT/'research/owner-walkthrough-v2.md',ROOT/'analysis/AMENDED_V2.md']
    docs+=list((ROOT/'research/amended-v2').glob('*.md'))
    docs+=list((ROOT/'research/sessions').glob('2026-09-18*.md'))
    checked_links=0
    for p in docs:
        if p.name in ['CASE_STUDY-v1-preserved.md','README-v1-preserved.md']:continue
        assert p.exists(),p
        for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',dest) or dest.startswith('#'):continue
            target=(p.parent/unquote(dest.split('#')[0].strip('<>'))).resolve()
            assert target.exists() or target in EXCLUDED_FILES,(p,dest)
            checked_links+=1
    checks['local_document_links']=checked_links
    current=inventory()
    state={'scope':'Exact final project artifact state; environment/caches/logs and self-hashing verification records excluded.',
           'human_science_review':'pending','files':[{'path':name,'bytes':p.stat().st_size,'sha256':sha(p)} for name,p in sorted(current.items())]}
    MANIFEST.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
    report={'status':'passed','utc':datetime.now(timezone.utc).isoformat(),'checks':checks,
        'environment':{'python':sys.version,'platform':platform.platform(),'packages':versions},
        'manifest_sha256':sha(MANIFEST),'artifact_count':len(current),
        'limits':'Software, arithmetic, preservation and artifact verification; not human science/contribution/release approval.',
        'human_science_review':'pending'}
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    check_snapshot()
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':
    if '--check-snapshot' in sys.argv:check_snapshot()
    else:main()
