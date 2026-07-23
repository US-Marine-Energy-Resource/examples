"""Runtime environment for the example notebooks: platform, paths, and caches.

Importing this module performs the platform bootstrap, so it must be imported
before numpy/pandas/mhkit -- on Kaggle it installs the notebook's dependencies,
which can move those versions, and an already-imported module would go stale.
On a developer machine the Kaggle branch is a no-op and only paths are set.

Exports:
    ON_KAGGLE     -- True inside a Kaggle kernel.
    WORK_DIR      -- root for everything the document writes.
    CACHE_DIR     -- derived-results cache (contour fits), seeded from the
                     companion Kaggle Dataset when present.
    KAGGLE_ASSETS -- the companion dataset's mount point, or None.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ON_KAGGLE = "KAGGLE_KERNEL_RUN_TYPE" in os.environ or Path("/kaggle/working").is_dir()

# Everything the document writes hangs off WORK_DIR. Locally `Path(".") / "figures"`
# is `figures`, so local behaviour is unchanged.
WORK_DIR = Path("/kaggle/working") if ON_KAGGLE else Path(".")

# The companion Kaggle Dataset ships `cache/` (derived results), `mer_wave_cache/`
# (the warmed us-marine-energy-resource download cache), and `h2o_examples/` (these
# helpers). Locate it by looking for the package. Kaggle mounts datasets a few
# levels deep (e.g. /kaggle/input/datasets/<user>/<slug>/), so search recursively
# rather than assuming a fixed */h2o_examples depth.
_pkg = next(Path("/kaggle/input").rglob("h2o_examples/__init__.py"), None) if ON_KAGGLE else None
KAGGLE_ASSETS = _pkg.parent.parent if _pkg else None

if ON_KAGGLE:
    # Select the existing `dynamic` preset -- live Folium map, interactive tables.
    # setdefault, never assignment: `make render-pdf` sets =png and must win.
    os.environ.setdefault("H2O_RENDER_CONTEXT", "dynamic")
    # No -U: Kaggle's numpy/pandas/scipy already satisfy mhkit's floors and
    # should be left alone.
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q",
         "mhkit[wave]==1.1.*", "itables", "folium",
         "us-marine-energy-resource>=0.5.0"],
        check=True,
    )
    # Without the companion dataset every sea-state record is fetched from S3,
    # which takes hours on Kaggle's network. Fail now, with the fix, rather
    # than crawl.
    if not (KAGGLE_ASSETS and (KAGGLE_ASSETS / "mer_wave_cache").is_dir()):
        raise RuntimeError(
            "Companion dataset not attached (expected mer_wave_cache/ under "
            "/kaggle/input/*/). Attach 'h2o-wave-hindcast-cache' under Notebook "
            "settings > Input."
        )
    # Seed the wave-download cache from the dataset. Copy rather than point at
    # it: /kaggle/input is read-only and fetches write back into the cache.
    _target = Path("/kaggle/working/.mer_wave_cache")
    shutil.copytree(KAGGLE_ASSETS / "mer_wave_cache", _target, dirs_exist_ok=True)
    os.environ["MER_WAVE_CACHE_DIR"] = str(_target)

# Derived results (contour fits) cache here. The raw sea-state downloads live in
# the package's own cache (~/.mer_wave_cache, or MER_WAVE_CACHE_DIR set above).
CACHE_DIR = WORK_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Seed from the companion Kaggle Dataset. Copy rather than read through it:
# derived results are written back, and /kaggle/input is read-only.
if KAGGLE_ASSETS and (KAGGLE_ASSETS / "cache").is_dir():
    shutil.copytree(KAGGLE_ASSETS / "cache", CACHE_DIR, dirs_exist_ok=True)
