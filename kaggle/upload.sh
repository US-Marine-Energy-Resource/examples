#!/usr/bin/env bash
# Push the staged dataset and notebook to Kaggle.
#
# Uploads only -- run `make kaggle-render` first if the .qmd has changed. The dataset
# is created on the first run and versioned on every run after, so this script is
# safe to re-run.
#
# Usage: ./kaggle/upload.sh ["version message"]
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MESSAGE="${1:-refresh cache}"

DATASET="$HERE/dataset"
NBDIR="$HERE/notebook"

for d in "$DATASET" "$NBDIR"; do
  if [ ! -d "$d" ]; then
    echo "error: $d missing -- run 'make kaggle-render' first" >&2
    exit 1
  fi
done

# TLS: uploading crosses two hosts with opposite trust requirements --
# api.kaggle.com is intercepted by the corporate proxy and needs the internal root,
# while the storage leg (www.googleapis.com) is not intercepted and needs the public
# roots. A bundle holding both is the only thing that satisfies the pair; either one
# alone fails on the other host. Rebuild with:
#   cat "$(/opt/homebrew/bin/python3 -m certifi)" ~/nrel_root_ca.pem > ~/combined_ca.pem
if [ -z "${REQUESTS_CA_BUNDLE:-}" ] && [ -f "$HOME/combined_ca.pem" ]; then
  echo "note: using ~/combined_ca.pem (REQUESTS_CA_BUNDLE was unset)"
  export SSL_CERT_FILE="$HOME/combined_ca.pem"
  export REQUESTS_CA_BUNDLE="$HOME/combined_ca.pem"
  export CURL_CA_BUNDLE="$HOME/combined_ca.pem"
fi

SLUG="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' \
        "$DATASET/dataset-metadata.json")"

# `datasets status` exits non-zero (or reports an error) for a slug that does not
# exist yet, which is how we tell a first upload from a refresh.
if kaggle datasets status "$SLUG" >/dev/null 2>&1; then
  echo "==> versioning dataset $SLUG"
  kaggle datasets version -p "$DATASET" --dir-mode zip -m "$MESSAGE"
else
  echo "==> creating dataset $SLUG"
  kaggle datasets create -p "$DATASET" --dir-mode zip
fi

echo "==> pushing notebook"
kaggle kernels push -p "$NBDIR"
