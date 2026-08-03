# U.S. DOE H2O Wave Hindcast Resource Characterization

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/US-Marine-Energy-Resource/examples)

A worked example of wave energy resource characterization at U.S. marine energy
test sites, using the U.S. DOE WPTO High-Resolution Wave Hindcast. Data access
goes through the
[us-marine-energy-resource](https://pypi.org/project/us-marine-energy-resource/)
package. The analysis covers aggregate statistics, monthly climatology, joint
probability distributions, extreme sea state contours, and multi-site
comparison, using [MHKiT](https://mhkit-software.github.io/MHKiT/) for the wave
calculations.

The source of truth is the Quarto document
`us_doe_h2o_wave_hindcast_resource_characterization.qmd`. The rendered notebook
and PDF are committed alongside it. The notebook also runs on
[Kaggle](https://www.kaggle.com/code/andrewsimmsnlr/h2o-wave-hindcast-resource-characterization)
with a
[companion dataset](https://www.kaggle.com/datasets/andrewsimmsnlr/h2o-wave-hindcast-cache)
that provides pre-downloaded data.

## Getting started

Requires [uv](https://docs.astral.sh/uv/) and
[Quarto](https://quarto.org/docs/get-started/), or open the repository in
GitHub Codespaces, which installs both and runs `make sync` for you. The PDF is
produced by Typst, which ships inside Quarto, so no LaTeX install is needed
anywhere.

```sh
make sync            # build the environment and register the Jupyter kernel
make check-toolchain # confirm Quarto, Typst and the kernel are wired up
make render          # render the notebook and PDF
```

Run `make help` for the full list of targets. The first render downloads the sea
state records and caches them; renders after that read from disk. The cache
lives under `~/.mer_wave_cache`, or wherever `MER_WAVE_CACHE_DIR` points — in a
Codespace that is `/workspaces/.mer_wave_cache`, which survives a container
rebuild so the download happens once. The size depends on which points are
compared and over how many years, so the document measures it rather than
guessing: see "What the Records Cost", which reports the per-point download and
writes `.cache/download_statistics.json`. For the four default points over five
years it comes to roughly 585 MB, most of it raw S3 chunks under `s3_chunks/`
that distil into the much smaller per-point records (`US_*/`) later renders
read. Points in the Atlantic domain cost far more, because that domain bundles
about twenty times as many nodes into each chunk.

No account or API key is needed. The document reads the published hindcast
files on S3 anonymously. An API key from the
[NLR Developer Network](https://developer.nlr.gov/signup/) enables the API
backend for larger queries; see `.env.example`.

## Data

Source data is the WPTO U.S. Wave Hindcast, produced by the U.S. Department of
Energy Water Power Technologies Office and distributed through the AWS Open
Data registry at `s3://wpto-pds-us-wave`. It is a U.S. Government work in the
public domain.

## License

BSD 3-Clause License. Copyright (c) 2026, Alliance for Energy Innovation, LLC
under the terms of Contract DE-AC36-08GO28308. The U.S. Government retains
certain rights in this software. See [LICENSE](LICENSE).
