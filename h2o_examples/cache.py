"""Tiny disk memoisation for derived results."""

from pathlib import Path

import pandas as pd


def memoize_pickle(path, compute, force=False):
    """Return the pickled value at `path`, computing and saving it when absent.

    `compute` is a zero-argument callable. Pass `force=True` to ignore an
    existing file and recompute.
    """
    path = Path(path)
    if path.exists() and not force:
        return pd.read_pickle(path)
    value = compute()
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(value, path)
    return value
