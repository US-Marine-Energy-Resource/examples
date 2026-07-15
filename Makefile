SCRIPT := us_doe_h2o_wave_hindcast_resource_characterization.py
NOTEBOOK := us_doe_h2o_wave_hindcast_resource_characterization.ipynb

.DEFAULT_GOAL := help

.PHONY: help compile run analysis render execute clean

help: ## Show this help message.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z_%-]+:.*##/ {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

compile: ## Convert the Jupytext Python script to a Jupyter notebook.
	uv run --with jupytext jupytext --to notebook $(SCRIPT)

run: compile ## Compile and open the Jupyter notebook.
	uv run --with notebook jupyter notebook $(NOTEBOOK)

analysis: ## Run the Python analysis script directly.
	uv run $(SCRIPT)

render: compile ## Compile and execute the notebook in place so committed cells include outputs.
	uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace $(NOTEBOOK)

execute: render ## Alias for render.

clean: ## Remove generated notebook checkpoints and Python caches.
	rm -rf .ipynb_checkpoints __pycache__
