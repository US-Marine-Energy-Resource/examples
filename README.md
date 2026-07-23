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
GitHub Codespaces, which installs both.

```sh
make sync    # build the environment and register the Jupyter kernel
make render  # render the notebook and PDF
```

Run `make help` for the full list of targets. The first render downloads the
sea state records and caches them under `~/.mer_wave_cache`; renders after that
read from disk.

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
