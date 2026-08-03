"""Measured download statistics for the wave hindcast.

The S3 backend never reads a single node. For each variable it takes
``width = ds.chunks[1]`` neighbouring nodes at a time and keeps that block under
``<cache>/s3_chunks/<domain>/<year>/<variable>_<start>.npy``, where
``start = (gid // width) * width``. So a point's first run costs exactly the
blocks its grid node rides in, and those blocks are still on disk afterwards --
which means these numbers are measured from the cache, never estimated.

Two consequences worth reporting rather than assuming:

- ``width`` varies by domain, and not slightly. It sets the whole cost.
- Points whose nodes land in the same block share it: the first pays, the rest
  are free.

Nothing here downloads. `describe_point` is an offline index lookup, and block
sizes come from files already on disk, so a point whose blocks were never
fetched is reported as unmeasured rather than guessed at.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from us_marine_energy_resource import wave_hindcast
from us_marine_energy_resource.wave_hindcast.config import CONFIG

from h2o_examples.points import point_coord


def chunk_root(cache_dir=None):
    """Return the cached-block root, honouring MER_WAVE_CACHE_DIR.

    Parameters
    ----------
    cache_dir : path-like, optional
        Cache root to read. Defaults to the package's own resolution, so this
        follows MER_WAVE_CACHE_DIR wherever the notebook is running.

    Returns
    -------
    Path
        The ``s3_chunks`` directory, which may not exist.
    """
    root = Path(cache_dir) if cache_dir else CONFIG.default_cache_dir()
    return root / CONFIG.chunks_dirname


def block_width(year_dir):
    """Return the chunk width (nodes per block) recorded in a year's blocks.

    Read from a block's own shape rather than assumed: ``(timestamps, width)``.

    Returns
    -------
    int or None
        None when the directory holds no blocks.
    """
    block = next(Path(year_dir).glob("*.npy"), None)
    if block is None:
        return None
    return int(np.load(block, mmap_mode="r").shape[1])


def point_blocks(domain, node_id, years, cache_dir=None):
    """Return the cached blocks one point's node rides in, per year.

    Globs on the block's ``start`` rather than composing variable names,
    so a domain-year that spells a variable differently is still counted.

    Returns
    -------
    dict
        ``{"blocks": [Path, ...], "starts": {year: start}, "widths": {year: width},
        "unmeasured": [year, ...]}``
    """
    root = chunk_root(cache_dir)
    blocks, starts, widths, unmeasured = [], {}, {}, []
    for year in years:
        year_dir = root / domain / str(year)
        width = block_width(year_dir) if year_dir.is_dir() else None
        if width is None:
            unmeasured.append(year)
            continue
        start = (node_id // width) * width
        starts[year], widths[year] = start, width
        found = sorted(year_dir.glob(f"*_{start}.npy"))
        if found:
            blocks.extend(found)
        else:
            unmeasured.append(year)
    return {
        "blocks": blocks, "starts": starts, "widths": widths,
        "unmeasured": unmeasured,
    }


def download_statistics(points, years, cache_dir=None):
    """Measure what each point's record cost to download.

    Parameters
    ----------
    points : mapping
        ``name -> {"lat", "lng", "label"}``, as built from POINTS.
    years : sequence of int
        The years of record the cost covers.
    cache_dir : path-like, optional
        Cache root; defaults to the package's resolution.

    Returns
    -------
    dict
        ``{"cache_dir", "years", "points": [...], "totals": {...}}``. Each point
        carries its domain, node id, chunk width, bytes and any unmeasured
        years. `shared_with` names points riding the same blocks, whose bytes
        are counted once in the totals.
    """
    years = sorted(years)
    rows, by_chunk = [], {}

    for name, point in points.items():
        described = wave_hindcast.describe_point(*point_coord(point))
        domain, node_id = described["domain"], described["location_id"]
        found = point_blocks(domain, node_id, years, cache_dir)
        blocks = found["blocks"]
        widths = sorted(set(found["widths"].values()))
        rows.append({
            "point": name,
            "label": point.get("label", name),
            "domain": domain,
            "node_id": node_id,
            # Nodes bundled into one block. This is what sets the cost, and it
            # differs by domain, so it is reported rather than assumed.
            "chunk_width": widths[0] if len(widths) == 1 else widths or None,
            "chunk_starts": sorted(set(found["starts"].values())),
            # Years actually measured, which is the requested span minus any
            # whose blocks are absent -- so bytes and n_years always agree.
            "n_years": len(years) - len(found["unmeasured"]),
            "blocks": len(blocks),
            "bytes": sum(p.stat().st_size for p in blocks) if blocks else None,
            "unmeasured_years": found["unmeasured"],
        })
        for block in blocks:
            by_chunk.setdefault(block, []).append(name)

    # A block fetched once serves every point in it, so the total counts each
    # file once even though each point reports the full cost of its own record.
    shared = {b: names for b, names in by_chunk.items() if len(names) > 1}
    for row in rows:
        row["shared_with"] = sorted(
            {n for names in shared.values() if row["point"] in names
             for n in names} - {row["point"]}
        )

    return {
        "cache_dir": str(chunk_root(cache_dir)),
        "years": years,
        "points": rows,
        "totals": {
            "unique_blocks": len(by_chunk),
            "bytes": sum(b.stat().st_size for b in by_chunk),
            "points_measured": sum(1 for r in rows if r["bytes"] is not None),
            "points_total": len(rows),
        },
    }


def write_json(statistics, path):
    """Write `statistics` to `path` as indented JSON and return the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n")
    return path
