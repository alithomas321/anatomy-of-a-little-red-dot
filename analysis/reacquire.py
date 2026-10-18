"""Reacquire missing public evidence only if it matches the original SHA-256.

Never execute downloaded code. Existing resources are verified, not replaced.
This is a separate, network-using step; run.sh performs no downloads.
"""
from pathlib import Path
import json,hashlib,urllib.request
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def main():
    records=json.loads((ROOT/'data/retrieval-manifest.json').read_text())
    for r in records:
        p=(ROOT/r['path']).resolve()
        if not p.is_relative_to(ROOT/'data/raw') and not p.is_relative_to(ROOT/'research/evidence'):
            raise ValueError('Manifest destination outside evidence directories')
        if p.exists():
            assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
            continue
        assert r['requested_url'].startswith('https://')
        req=urllib.request.Request(r['requested_url'],headers={'User-Agent':'LRD-observational-pilot/1.0'})
        with urllib.request.urlopen(req,timeout=45) as response:
            data=response.read(r['bytes']+1)
        if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:
            raise RuntimeError(f"Upstream resource changed; original version not reacquired: {r['path']}")
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        event={'path':r['path'],'utc':datetime.now(timezone.utc).isoformat(),'sha256':r['sha256']}
        with (ROOT/'data/reacquisition-events.jsonl').open('a') as stream:
            stream.write(json.dumps(event)+'\n')
        print('Reacquired and hash verified:',r['path'])
    print('All resources match the original acquisition manifest.')

if __name__=='__main__':main()
