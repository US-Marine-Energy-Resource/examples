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

# The newest file timestamp Kaggle currently serves for this slug. Used as a
# before/after marker: when it advances, the new version is the one being served.
#
# `datasets status` is NOT usable for this. It keeps reporting "ready" for the
# version already published while the new one is still processing, so polling it
# returns on the first call and tells you nothing.
dataset_stamp() {
  kaggle datasets files "$SLUG" --page-size 500 2>/dev/null \
    | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' \
    | sort | tail -1
}

# `datasets status` exits non-zero (or reports an error) for a slug that does not
# exist yet, which is how we tell a first upload from a refresh.
if kaggle datasets status "$SLUG" >/dev/null 2>&1; then
  BEFORE="$(dataset_stamp)"
  echo "==> versioning dataset $SLUG"
  kaggle datasets version -p "$DATASET" --dir-mode zip -m "$MESSAGE"
else
  BEFORE=""
  echo "==> creating dataset $SLUG"
  kaggle datasets create -p "$DATASET" --dir-mode zip
fi

# `datasets version` returns as soon as the upload lands; Kaggle then processes it
# asynchronously, and `kernels push` pins whatever version is current at push time.
# Pushing straight away therefore attaches the PREVIOUS version -- which is how the
# kernel came to run against a dataset with no h2o_examples/download_statistics.py
# and fail on ModuleNotFoundError. Wait for the served files to actually change.
echo "==> waiting for $SLUG to serve the new version"
ready=""
for _ in $(seq 60); do
  sleep 10
  now="$(dataset_stamp)"
  if [ -n "$now" ] && [ "$now" != "$BEFORE" ]; then
    ready=1
    echo "    now serving files stamped $now"
    break
  fi
done
if [ -z "$ready" ]; then
  echo "error: $SLUG still serves files stamped '$BEFORE' after 10 minutes --" >&2
  echo "       not pushing the notebook, it would attach the previous version." >&2
  echo "       Check https://www.kaggle.com/datasets/$SLUG and re-run." >&2
  exit 1
fi

echo "==> pushing notebook"
kaggle kernels push -p "$NBDIR"
