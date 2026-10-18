# Data and sources

This project uses public JWST/NIRSpec reductions from the DAWN JWST Archive (DJA) and the RUBIES releases. The three objects are The Cliff, RUBIES-BLAGN-1 and RUBIES-UDS-182791. These are already reduced spectra, not detector counts.

The original URLs, retrieval dates and checksums are in data/retrieval-manifest.json and research/amended-v2/source-manifest.json. The analysis/sample.json file records the object identities and adopted redshifts. Original reductions and scientific interpretations belong to their cited providers and authors.

Downloaded papers and archive-page snapshots are not bundled. analysis/reacquire.py fetches the original v1 evidence only if it matches the recorded checksums. Licensed msaexp source excerpts and their original MIT notices accompany the extraction-method audit.

The saved measurements and figures support an exploratory reanalysis of this finite sample. Read research/observational-report-v2.md for its assumptions and limits.
