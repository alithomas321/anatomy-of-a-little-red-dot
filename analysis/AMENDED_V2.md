# Reproduce the bounded exploratory extension

From the project directory, with the preserved inputs and existing isolated environment:

```bash
cd /Users/alisont/astronomy-portfolio/current-projects/anatomy-of-a-little-red-dot
bash analysis/run_amended_v2.sh
```

This runs the extraction checks, finite joint line/continuum grid, original scientific figures and final verification **offline**, using the unchanged Python 3.12.13 environment and [requirements.lock](requirements.lock). It overwrites only v2 generated products. It does not invoke the September 10 runner, rewrite its products, download data, execute retrieved upstream code, expand the sample, or publish. The existing [v1 environment instructions](README.md) also apply to recreating this environment; recreating it may need package downloads.

| Script | Purpose |
| --- | --- |
| [amended_v2_extraction.py](amended_v2_extraction.py) | Native sum and 2D aperture/center alternatives, same-z reduction comparison, explicitly hypothetical offsets, numerical controls and provenance |
| [amended_v2_lines.py](amended_v2_lines.py) | 36 fits: three objects × three line widths × two resolutions × two error choices; fixed-ratio profiles and numerical controls |
| [amended_v2_figures.py](amended_v2_figures.py) | Central owner figure and technical spectra/residual/profile figure |
| [verify_amended_v2.py](verify_amended_v2.py) | Preservation, original-band agreement, fresh fit checks, source hashes, links, asset manifest and exact final-state manifest |
| [run_amended_v2.sh](run_amended_v2.sh) | Reproduction driver with project-scoped outputs/logs |

To verify the delivered artifact bytes without regenerating them:

```bash
analysis/.venv/bin/python analysis/verify_amended_v2.py --check-snapshot
```

The manifest covers project artifacts and source/data evidence, excluding the environment, caches, logs and the manifest/verification records themselves. This explicit exclusion avoids recursive self-hashing. Its separate verification report records the manifest's SHA-256. Regenerated numerical results are deterministic in the pinned environment; timestamps and figure container metadata can change. The runner validates results afresh and updates the manifest to the regenerated state.

Methods and output meanings are in [the amended protocol](../research/amended-v2/protocol.md), [extraction record](../research/amended-v2/extraction-methods.md), [line report](../research/amended-v2/line-results.md) and [technical extension](../research/observational-report-v2.md). New data outputs live in `data/derived/amended-v2/`; figures in `figures/amended-v2/`. No physical line decomposition, calibrated edge confidence or human science approval is implied by a passing script.
