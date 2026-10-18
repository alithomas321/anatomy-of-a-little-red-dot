"""Fetch explicitly listed public evidence; preserve bytes and append provenance.

Usage: python analysis/retrieve.py path/relative/to/project URL [URL ...]
The optional extra URLs are fallbacks for the SAME resource, not extra files.
Existing files are verified against the manifest and never overwritten.
"""
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/retrieval-manifest.json"


def retrieve(relative, urls):
    target = (ROOT / relative).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError("Output must stay inside this project")
    records = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    if target.exists():
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        assert any(r["path"] == relative and r["sha256"] == digest for r in records)
        print(f"Verified existing {relative}")
        return
    failures = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LRD-observational-pilot/1.0 (public research data)"})
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read(50_000_001)
                if len(data) > 50_000_000:
                    raise ValueError("Per-resource 50 MB limit exceeded")
                headers = dict(response.headers.items())
                final_url = response.url
            if relative.endswith(".fits") and not data.startswith(b"SIMPLE"):
                raise ValueError("Response is not a FITS file")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            records.append({"path": relative, "requested_url": url,
                            "resolved_url": final_url,
                            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                            "md5": hashlib.md5(data).hexdigest(),
                            "headers": {k: v for k, v in headers.items() if k.lower() in
                                        ["content-type", "last-modified", "etag", "content-length"]},
                            "failed_routes": failures})
            MANIFEST.write_text(json.dumps(records, indent=2) + "\n")
            print(f"Saved {relative}: {len(data)} bytes")
            return
        except (urllib.error.URLError, ValueError, TimeoutError) as exc:
            failures.append({"url": url, "error": str(exc)})
    raise RuntimeError(f"All public retrieval routes failed: {failures}")


if __name__ == "__main__":
    retrieve(sys.argv[1], sys.argv[2:])
