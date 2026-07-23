QMD    := us_doe_h2o_wave_hindcast_resource_characterization.qmd
HTML   := us_doe_h2o_wave_hindcast_resource_characterization.html
IPYNB  := us_doe_h2o_wave_hindcast_resource_characterization.ipynb
PDF    := us_doe_h2o_wave_hindcast_resource_characterization.pdf

# Quarto executes cells through the uv-managed virtual environment.
export QUARTO_PYTHON := .venv/bin/python

# TLS trust store: render targets read the wave hindcast from AWS S3 (via
# us-marine-energy-resource). S3 is a public endpoint and verifies against the
# certifi bundle, NOT the internal root CA. Exporting the internal CA replaces the
# public trust store rather than adding to it, so with it set, S3 reads fail.
#
#   Public endpoints (S3, OSM tiles off-network) -- the usual case here:
#     export SSL_CERT_FILE=$(.venv/bin/python -m certifi)
#     export REQUESTS_CA_BUNDLE=$(.venv/bin/python -m certifi)
#
#   Internal hosts that present the internal CA:
#     export SSL_CERT_FILE=~/nrel_root_ca.pem REQUESTS_CA_BUNDLE=~/nrel_root_ca.pem
#
# These are a per-situation swap, not a fixed setting; neither works for everything.
# A combined bundle (cat both into one file) serves both if you need it.

.DEFAULT_GOAL := help

.PHONY: help sync preview render-html render-notebook render-pdf render kaggle-render kaggle-upload clean

help: ## Show this help message.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z_%-]+:.*##/ {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync: ## Build the uv virtual environment and register the Jupyter kernel.
	uv sync
	uv run python -m ipykernel install --user --name python3 --display-name "H2O examples"

preview: ## Live HTML preview with hot reload (re-renders on save).
	H2O_RENDER_CONTEXT=dynamic quarto preview $(QMD) --to html

render-html: ## Render a standalone HTML page with the INTERACTIVE Folium map.
	H2O_RENDER_CONTEXT=dynamic quarto render $(QMD) --to html

render-notebook: ## Render the self-contained notebook with the INTERACTIVE Folium map.
	H2O_RENDER_CONTEXT=dynamic quarto render $(QMD) --to ipynb

render-pdf: ## Render the Typst PDF (no LaTeX) with the STATIC map PNG.
	# Also fetches OSM tiles over HTTPS -- see the TLS note at the top of this file.
	H2O_RENDER_CONTEXT=png quarto render $(QMD) --to typst

render: render-notebook render-pdf ## Render both committed deliverables (notebook + PDF).

kaggle-render: render-notebook ## Render and stage the Kaggle dataset and notebook.
	# Outputs land in kaggle/dataset and kaggle/notebook (both gitignored).
	./kaggle/build.sh

kaggle-upload: ## Push the staged dataset and notebook to Kaggle.
	# Deliberately does NOT render: uploading an unchanged notebook should not cost
	# a full Quarto run. Run `make kaggle-render` first when the .qmd has changed.
	# Creates the dataset on the first run, versions it thereafter.
	# Override the version message with M="...":  make kaggle-upload M="add 2011"
	./kaggle/upload.sh "$(M)"

clean: ## Remove Quarto caches and generated outputs.
	# `*.quarto_ipynb*` (not `*.quarto_ipynb`) also catches the numbered siblings
	# an interrupted render leaves behind, e.g. `*.quarto_ipynb_17`.
	rm -rf .quarto *_files *.quarto_ipynb* __pycache__ .ipynb_checkpoints
	rm -f $(HTML) $(IPYNB) $(PDF)
