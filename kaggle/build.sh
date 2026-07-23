#!/usr/bin/env bash
# Stage everything Kaggle needs into kaggle/dataset/ and kaggle/notebook/.
#
# Both output directories are generated and gitignored -- they are copies of repo
# content, not sources. Re-run this after warming the cache or re-rendering.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"

NOTEBOOK="us_doe_h2o_wave_hindcast_resource_characterization.ipynb"
DATASET="$HERE/dataset"
NBDIR="$HERE/notebook"

rm -rf "$DATASET" "$NBDIR"
mkdir -p "$DATASET" "$NBDIR"

# --- dataset ------------------------------------------------------------------
# Copy with an explicit allowlist. Never stage the repo wholesale: renders, .venv
# and local config files must not ride along into a public dataset.
#
# `.cache` -> `cache` and `.mer_wave_cache` -> `mer_wave_cache`: Kaggle's uploader
# and the /kaggle/input browser silently drop dot-prefixed entries. The notebook
# copies them back to writable dot-dirs at runtime.
if [ ! -d "$REPO/.cache" ]; then
  echo "error: $REPO/.cache does not exist -- render the notebook once to warm it" >&2
  exit 1
fi
# The us-marine-energy-resource download cache: the sea-state records themselves.
MER_CACHE="${MER_WAVE_CACHE_DIR:-$HOME/.mer_wave_cache}"
if [ ! -d "$MER_CACHE" ]; then
  echo "error: $MER_CACHE does not exist -- render the notebook once to warm it" >&2
  exit 1
fi
rsync -a --exclude '__pycache__' "$REPO/.cache/"       "$DATASET/cache/"
# Ship only the notebook's organized site records (US_*), not raw download
# intermediates (archives/, s3_chunks/), the manifest, or unrelated cached points.
rsync -a --include='/US_*/' --include='/US_*/**' --exclude='*' \
  "$MER_CACHE/" "$DATASET/mer_wave_cache/"
rsync -a --exclude '__pycache__' "$REPO/h2o_examples/" "$DATASET/h2o_examples/"
cp "$HERE/dataset-metadata.json" "$DATASET/dataset-metadata.json"

# --- notebook -----------------------------------------------------------------
# Strip outputs (the rendered notebook is ~7.6 MB of embedded tables and figures;
# on Kaggle the point is that the reader runs it) and normalize the kernelspec,
# which otherwise publishes the local home-directory path and "H2O examples".
if [ ! -f "$REPO/$NOTEBOOK" ]; then
  echo "error: $REPO/$NOTEBOOK not found -- run 'make render-notebook' first" >&2
  exit 1
fi
jupyter nbconvert \
  --ClearOutputPreprocessor.enabled=True \
  --to notebook \
  --output-dir "$NBDIR" \
  --output "$NOTEBOOK" \
  "$REPO/$NOTEBOOK" >/dev/null

# kernel-metadata.json rides alongside the notebook: `kaggle kernels push` reads it
# for the dataset attachment and the internet toggle, so neither is a manual click.
cp "$HERE/kernel-metadata.json" "$NBDIR/kernel-metadata.json"

python3 - "$NBDIR/$NOTEBOOK" <<'PY'
import json, sys
path = sys.argv[1]
nb = json.load(open(path))
nb["metadata"]["kernelspec"] = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}
json.dump(nb, open(path, "w"), indent=1)
open(path, "a").write("\n")
PY

echo "staged:"
echo "  $DATASET  ($(du -sh "$DATASET" | cut -f1))"
echo "  $NBDIR/$NOTEBOOK  ($(du -h "$NBDIR/$NOTEBOOK" | cut -f1))"
