QMD    := us_doe_h2o_wave_hindcast_resource_characterization.qmd
HTML   := us_doe_h2o_wave_hindcast_resource_characterization.html
IPYNB  := us_doe_h2o_wave_hindcast_resource_characterization.ipynb
PDF    := us_doe_h2o_wave_hindcast_resource_characterization.pdf

# Quarto executes cells through the uv-managed virtual environment.
export QUARTO_PYTHON := .venv/bin/python

.DEFAULT_GOAL := help

.PHONY: help sync preview render-html render-notebook render-pdf render clean

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
	# The static map fetches OSM tiles over HTTPS. On the NREL network, point the
	# TLS trust store at the root CA first, e.g.:
	#   export SSL_CERT_FILE=~/nrel_root_ca.pem REQUESTS_CA_BUNDLE=~/nrel_root_ca.pem
	H2O_RENDER_CONTEXT=png quarto render $(QMD) --to typst

render: render-notebook render-pdf ## Render both committed deliverables (notebook + PDF).

clean: ## Remove Quarto caches and generated outputs.
	rm -rf .quarto *_files *.quarto_ipynb __pycache__ .ipynb_checkpoints
	rm -f $(HTML) $(IPYNB) $(PDF)
