# Anatomy of a Little Red Dot

What can three JWST spectra tell us about the light from distant little red dots?

## What JWST measures

Little red dots are compact, distant objects seen in JWST images. Their light can include stars and gas around growing black holes. Understanding which sources produce the light is part of understanding these objects.

JWST measures their light at different wavelengths. This produces a spectrum: a record of how much light is present at each wavelength. Because the objects are distant, light originally emitted at shorter wavelengths reaches JWST stretched into the infrared. This analysis accounts for that shift before comparing the spectra.

## Why the shape of the light matters

Stars and gas can leave different patterns in a spectrum. Measuring those patterns helps test explanations of what produces an object's light. That matters for estimates of how many stars it contains and for understanding black hole growth in the early universe.

This project examines a strong change in brightness near a wavelength associated with light absorption by hydrogen, called the Balmer limit. A large difference between two wavelength ranges is a useful measurement, but it does not by itself identify the physical cause.

## What this project actually does

This version analyzes real public JWST spectra of three objects. It compares light in two wavelength ranges, then checks how uncertainty, the way light is measured from the telescope data, and overlapping emission affect the interpretation.

Two objects have substantially more light in the longer-wavelength range. The third does not require a strong difference. In the most extreme case, The Cliff, the shorter-wavelength light is so faint that some measurement choices leave the size of the ratio without a finite upper bound.

The analysis also demonstrates that a model without a sharp jump can describe the contrast under its stated assumptions. A striking brightness difference therefore does not uniquely establish a sharp edge or reveal what powers the object.

The outcome is a clearer account of what these three spectra support. It does not settle whether stars or a black hole supply their light, or establish a result for every little red dot.

![The Cliff's observed JWST spectrum compared with a continuous model, alongside measurements of its faint shorter-wavelength light](figures/little-red-dot.png)

[Read the case study](https://alisonthomasportfolio.com/projects/little-red-dot) · [Explore the code](https://github.com/alithomas321/anatomy-of-a-little-red-dot/tree/main/analysis) · [Methods](research/observational-report-v2.md)

<details>
<summary>Run the code</summary>

The recorded environment uses Python 3.12.13.

```sh
python3.12 -m venv analysis/.venv
analysis/.venv/bin/python -m pip install -r analysis/requirements.lock
analysis/.venv/bin/python analysis/reacquire.py
analysis/.venv/bin/python analysis/measure.py
analysis/.venv/bin/python analysis/shapes.py
analysis/.venv/bin/python analysis/amended_v2_extraction.py
analysis/.venv/bin/python analysis/amended_v2_lines.py
```

The reacquisition step downloads missing public evidence and checks its original hashes. Saved measurements are in data/derived. [Data and sources](SOURCES.md) describe their origins.

</details>

Background: [The original study of The Cliff](https://arxiv.org/abs/2503.16600). Its physical interpretation uses evidence beyond this project's limited measurements. Observations: NASA/ESA/CSA JWST, RUBIES GO-4233; reduced spectra: DAWN JWST Archive / msaexp.
