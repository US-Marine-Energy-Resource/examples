"""Mapping render helpers for notebooks and GitHub-friendly outputs."""

from __future__ import annotations

import io
import math
import os
import ssl
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import matplotlib.image as mpimg
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np

WEB_MERCATOR_MAX_LAT = 85.05112878
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"


class MapTileFetchError(RuntimeError):
    """Raised when static map tiles cannot be retrieved."""


@dataclass(frozen=True)
class MapRenderContext:
    """Controls which map artifacts are saved and displayed."""

    outputs: tuple[str, ...] = ("png", "static_html")
    display: bool | str = "auto"
    png_dpi: int = 150
    tile_url: str = OSM_TILE_URL
    tile_timeout: int = 20
    tile_ssl_context: ssl.SSLContext | None = None


def map_render_context(
    context: str | Mapping[str, Any] | MapRenderContext | None = None,
) -> MapRenderContext:
    """Normalize string/dict contexts into a :class:`MapRenderContext`.

    Presets:
      - ``None``/``"default"``/``"github"``: save/display PNG and save static HTML.
      - ``"dynamic_html"``/``"dynamic"``: display the live Folium map in notebooks.
      - ``"static_html"``/``"html"``: save static HTML only.
      - ``"png"``: save/display PNG only.
    """

    if isinstance(context, MapRenderContext):
        return context

    if context is None:
        context = os.environ.get("H2O_RENDER_CONTEXT", "default")

    if isinstance(context, str):
        preset = context.lower().replace("-", "_")
        presets = {
            "default": MapRenderContext(),
            "github": MapRenderContext(),
            "notebook": MapRenderContext(),
            "dynamic": MapRenderContext(outputs=("dynamic_html",)),
            "dynamic_html": MapRenderContext(outputs=("dynamic_html",)),
            "static_html": MapRenderContext(outputs=("static_html",)),
            "html": MapRenderContext(outputs=("static_html",)),
            "png": MapRenderContext(outputs=("png",)),
        }
        if preset not in presets:
            expected = ", ".join(sorted(presets))
            raise ValueError(f"Unknown map render context {context!r}; expected one of: {expected}")
        return presets[preset]

    return MapRenderContext(**dict(context))


def is_notebook() -> bool:
    """Return True when running inside a Jupyter kernel."""

    try:
        from IPython import get_ipython
    except ImportError:
        return False

    shell = get_ipython()
    return shell is not None and "IPKernelApp" in shell.config


def render_map_outputs(
    folium_map: Any,
    *,
    output_dir: str | Path,
    stem: str,
    context: str | Mapping[str, Any] | MapRenderContext | None = None,
    png_renderer: Callable[[Path, MapRenderContext], None] | None = None,
) -> dict[str, Path]:
    """Save/display a Folium map as dynamic HTML, static HTML, and/or PNG.

    ``png_renderer`` is intentionally caller-provided so domain-specific vector
    data can be rendered as a true static Web Mercator figure instead of taking
    a browser screenshot of the dynamic HTML.
    """

    render_context = map_render_context(context)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, Path] = {}
    outputs = set(render_context.outputs)

    if outputs & {"static_html", "dynamic_html"}:
        html_path = output_path / f"{stem}.html"
        folium_map.save(html_path)
        artifacts["html"] = html_path

    if "png" in outputs:
        if png_renderer is None:
            raise ValueError("A png_renderer is required when the render context includes 'png'.")
        png_path = output_path / f"{stem}.png"
        png_renderer(png_path, render_context)
        artifacts["png"] = png_path

    should_display = render_context.display is True or (
        render_context.display == "auto" and is_notebook()
    )
    if should_display:
        _display_outputs(folium_map, artifacts, outputs)

    return artifacts


def render_sites_map_outputs(
    sites: Mapping[str, Mapping[str, Any]],
    folium_map_factory: Callable[[Mapping[str, Mapping[str, Any]]], Any],
    *,
    output_dir: str | Path,
    stem: str = "sites_map",
    context: str | Mapping[str, Any] | MapRenderContext | None = None,
    title: str = "US marine energy test sites",
) -> dict[str, Path]:
    """Render the examples' site map through the shared context interface."""

    folium_map = folium_map_factory(sites)

    def png_renderer(path: Path, render_context: MapRenderContext) -> None:
        render_sites_png(
            sites,
            path,
            title=title,
            dpi=render_context.png_dpi,
            tile_url=render_context.tile_url,
            timeout=render_context.tile_timeout,
            ssl_context=render_context.tile_ssl_context,
        )

    return render_map_outputs(
        folium_map,
        output_dir=output_dir,
        stem=stem,
        context=context,
        png_renderer=png_renderer,
    )


def render_sites_png(
    sites: Mapping[str, Mapping[str, Any]],
    output_path: str | Path,
    *,
    title: str = "US marine energy test sites",
    tile_url: str = OSM_TILE_URL,
    timeout: int = 20,
    ssl_context: ssl.SSLContext | None = None,
    dpi: int = 150,
    figsize: tuple[float, float] = (11, 6.5),
    zoom: int | None = None,
) -> Path:
    """Render site points and boundaries to a static Web Mercator PNG.

    Tiles are fetched from the configured URL at render time. SSL/network errors
    are surfaced as ``MapTileFetchError`` so they are visible instead of silently
    producing a misleading blank basemap.
    """

    output_path = Path(output_path)
    west, south, east, north = _site_lonlat_bounds(sites)
    west, south, east, north = _pad_lonlat_bounds(west, south, east, north)
    zoom = zoom or _choose_zoom(west, south, east, north, figsize, dpi)

    fig, ax = plt.subplots(figsize=figsize)
    _draw_tiles(
        ax,
        west=west,
        south=south,
        east=east,
        north=north,
        zoom=zoom,
        tile_url=tile_url,
        timeout=timeout,
        ssl_context=ssl_context,
    )
    _draw_site_vectors(ax, sites)

    left, bottom = lonlat_to_web_mercator(west, south)
    right, top = lonlat_to_web_mercator(east, north)
    ax.set_xlim(left, right)
    ax.set_ylim(bottom, top)
    ax.set_axis_off()
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold")
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return output_path


def lonlat_to_web_mercator(lon: float, lat: float) -> tuple[float, float]:
    """Project lon/lat coordinates to EPSG:3857 meters."""

    lat = max(min(lat, WEB_MERCATOR_MAX_LAT), -WEB_MERCATOR_MAX_LAT)
    radius = 6378137.0
    x = radius * math.radians(lon)
    y = radius * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
    return x, y


def _display_outputs(folium_map: Any, artifacts: Mapping[str, Path], outputs: set[str]) -> None:
    try:
        from IPython.display import Image, display
    except ImportError:
        return

    if "png" in outputs and "png" in artifacts:
        display(Image(filename=str(artifacts["png"])))
    elif "dynamic_html" in outputs:
        display(folium_map)


def _site_lonlat_bounds(sites: Mapping[str, Mapping[str, Any]]) -> tuple[float, float, float, float]:
    lats: list[float] = []
    lons: list[float] = []
    for site in sites.values():
        lats.append(float(site["lat"]))
        lons.append(float(site["lng"]))
        for corner in site.get("corners", {}).values():
            lats.append(float(corner["lat"]))
            lons.append(float(corner["lng"]))
    return min(lons), min(lats), max(lons), max(lats)


def _pad_lonlat_bounds(
    west: float,
    south: float,
    east: float,
    north: float,
    pad_fraction: float = 0.08,
) -> tuple[float, float, float, float]:
    lon_pad = max((east - west) * pad_fraction, 0.1)
    lat_pad = max((north - south) * pad_fraction, 0.1)
    return west - lon_pad, south - lat_pad, east + lon_pad, north + lat_pad


def _choose_zoom(
    west: float,
    south: float,
    east: float,
    north: float,
    figsize: tuple[float, float],
    dpi: int,
    min_zoom: int = 2,
    max_zoom: int = 12,
) -> int:
    width_px = figsize[0] * dpi
    height_px = figsize[1] * dpi

    west_x = _lon_to_tile_float(west, max_zoom)
    east_x = _lon_to_tile_float(east, max_zoom)
    north_y = _lat_to_tile_float(north, max_zoom)
    south_y = _lat_to_tile_float(south, max_zoom)

    x_fraction_at_max = abs(east_x - west_x) / (2**max_zoom)
    y_fraction_at_max = abs(south_y - north_y) / (2**max_zoom)

    for zoom in range(max_zoom, min_zoom - 1, -1):
        scale = 256 * (2**zoom)
        if x_fraction_at_max * scale <= width_px and y_fraction_at_max * scale <= height_px:
            return zoom
    return min_zoom


def _draw_tiles(
    ax: plt.Axes,
    *,
    west: float,
    south: float,
    east: float,
    north: float,
    zoom: int,
    tile_url: str,
    timeout: int,
    ssl_context: ssl.SSLContext | None,
) -> None:
    x_min = math.floor(_lon_to_tile_float(west, zoom))
    x_max = math.floor(_lon_to_tile_float(east, zoom))
    y_min = math.floor(_lat_to_tile_float(north, zoom))
    y_max = math.floor(_lat_to_tile_float(south, zoom))
    max_index = (2**zoom) - 1

    for x in range(x_min, x_max + 1):
        wrapped_x = x % (2**zoom)
        for y in range(max(0, y_min), min(max_index, y_max) + 1):
            image = _fetch_tile(tile_url, zoom, wrapped_x, y, timeout, ssl_context)
            left, bottom, right, top = _tile_bounds_web_mercator(x, y, zoom)
            ax.imshow(image, extent=(left, right, bottom, top), origin="upper", zorder=0)


def _draw_site_vectors(ax: plt.Axes, sites: Mapping[str, Mapping[str, Any]]) -> None:
    for site in sites.values():
        color = site.get("color", "#2563eb")
        if "corners" in site:
            polygon = [_project_corner(corner) for corner in _ordered_corners(site["corners"])]
            polygon.append(polygon[0])
            xs, ys = zip(*polygon)
            ax.fill(xs, ys, color=color, alpha=0.18, zorder=4)
            ax.plot(xs, ys, color=color, linewidth=2.0, zorder=5)

    for site in sites.values():
        x, y = lonlat_to_web_mercator(float(site["lng"]), float(site["lat"]))
        ax.scatter(
            [x],
            [y],
            s=52,
            marker="o",
            facecolor="#ffffff",
            edgecolor="#111827",
            linewidth=1.2,
            zorder=6,
        )
        label = str(site["label"])
        text = ax.annotate(
            label,
            (x, y),
            xytext=(8, 7),
            textcoords="offset points",
            fontsize=8,
            fontweight="semibold",
            color="#111827",
            zorder=7,
        )
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground="white")])


def _ordered_corners(corners: Mapping[str, Mapping[str, float]]) -> list[Mapping[str, float]]:
    ordered = sorted(corners.values(), key=lambda corner: float(corner["lat"]), reverse=True)
    north = sorted(ordered[:2], key=lambda corner: float(corner["lng"]))
    south = sorted(ordered[2:], key=lambda corner: float(corner["lng"]), reverse=True)
    return [*north, *south]


def _project_corner(corner: Mapping[str, float]) -> tuple[float, float]:
    return lonlat_to_web_mercator(float(corner["lng"]), float(corner["lat"]))


def _fetch_tile(
    tile_url: str,
    zoom: int,
    x: int,
    y: int,
    timeout: int,
    ssl_context: ssl.SSLContext | None,
) -> np.ndarray:
    url = tile_url.format(z=zoom, x=x, y=y)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "us-marine-energy-resource-examples/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            return mpimg.imread(io.BytesIO(response.read()), format="png")
    except Exception as exc:
        raise MapTileFetchError(
            f"Could not fetch OSM tile {zoom}/{x}/{y} from {url}. "
            "If this is an SSL/certificate issue, fix the local certificate store "
            "or pass a custom tile_url/tile_ssl_context in the map render context."
        ) from exc


def _lon_to_tile_float(lon: float, zoom: int) -> float:
    return (lon + 180.0) / 360.0 * (2**zoom)


def _lat_to_tile_float(lat: float, zoom: int) -> float:
    lat = max(min(lat, WEB_MERCATOR_MAX_LAT), -WEB_MERCATOR_MAX_LAT)
    lat_rad = math.radians(lat)
    return (
        (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)
        / 2.0
        * (2**zoom)
    )


def _tile_bounds_web_mercator(x: int, y: int, zoom: int) -> tuple[float, float, float, float]:
    west = _tile_x_to_lon(x, zoom)
    east = _tile_x_to_lon(x + 1, zoom)
    north = _tile_y_to_lat(y, zoom)
    south = _tile_y_to_lat(y + 1, zoom)
    left, bottom = lonlat_to_web_mercator(west, south)
    right, top = lonlat_to_web_mercator(east, north)
    return left, bottom, right, top


def _tile_x_to_lon(x: int, zoom: int) -> float:
    return x / (2**zoom) * 360.0 - 180.0


def _tile_y_to_lat(y: int, zoom: int) -> float:
    n = math.pi - (2.0 * math.pi * y) / (2**zoom)
    return math.degrees(math.atan(math.sinh(n)))
