"""Figure and table output helpers for the example notebooks.

Import after `h2o_examples.environment` (this module imports it, so any import
order that starts with `environment` is safe).
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from h2o_examples.environment import WORK_DIR

sns.set_theme()

FIG_DIR = WORK_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Single source for figure width. Quarto's rendered page comfortably holds
# about 8 inches; wider figures get scaled down and their text with them.
# Height is free -- prefer separate figures over widening.
FIG_WIDTH = 8


def savefig(name):
    """Save the current figure to figures/<name>.png and render it inline.

    In a notebook plt.show() draws inline; as a script (Agg) show() does not
    execute but the PNG is still written.
    """
    plt.gcf().savefig(FIG_DIR / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.show()


def plot_wave_matrix(
    matrix,
    zlabel,
    figsize=None,
    fmt=".2f",
    buffer=1,
    suffix="%",
    annotate=True,
    annot_fontsize=9,
    blank_color=None,
    xtick_fmt="{:.0f}",
    ytick_fmt="{:.1f}",
):
    """Heatmap of a sea-state matrix (Te on columns, Hm0 on the index).

    `matrix` is indexed by bin *centers* -- mhkit's convention, since
    `performance.wave_energy_flux_matrix` converts the arrays it is handed from
    centers to edges internally. Ticks are therefore drawn on the bin edges,
    midway between consecutive centers, so a label marks a boundary instead of
    sitting in the middle of a cell. That means one more tick than cells.

    Empty bins are blanked and the axes are cropped to the populated bins plus
    a one-bin `buffer` on each side. Light gridlines fall on the labelled edges.
    Adapted from the EMEC/PacWave proficiency-testing capture-matrix plot.
    """
    m = matrix.replace(0, np.nan)

    # Crop to populated bins + a one-bin buffer, dropping the empty low-Te block.
    rows = np.where(m.notna().any(axis=1))[0]
    cols = np.where(m.notna().any(axis=0))[0]
    r0, r1 = max(rows.min() - buffer, 0), min(rows.max() + buffer, m.shape[0] - 1)
    c0, c1 = max(cols.min() - buffer, 0), min(cols.max() + buffer, m.shape[1] - 1)
    m = m.iloc[r0 : r1 + 1, c0 : c1 + 1].sort_index(ascending=False)  # Hm0 up

    # `annotate=False` leaves the cells bare, for a version that reads as a shape
    # rather than a table. None is seaborn's "no annotations" sentinel.
    annot = None
    if annotate:
        annot = m.apply(
            lambda col: col.map(
                lambda v: "" if pd.isna(v) else format(v, fmt) + suffix
            )
        )

    plt.figure(figsize=figsize or (FIG_WIDTH + 1, FIG_WIDTH - 2))
    ax = sns.heatmap(
        m,
        annot=annot,
        fmt="",
        cmap="viridis",
        annot_kws={"fontsize": annot_fontsize},
        cbar_kws={"label": zlabel},
    )
    # Blank cells are transparent, so the axes background is what shows through.
    # Set it explicitly to grey out bins with no value rather than relying on
    # whatever the active theme happens to use.
    if blank_color is not None:
        ax.set_facecolor(blank_color)

    # Cell j spans [j, j+1] in heatmap coordinates, so the bin edges are the
    # integers 0..n. Convert the centers to edges by stepping half a bin: the
    # index runs high -> low, so position i is that cell's upper edge.
    def edge_labels(values, descending=False):
        step = abs(values[1] - values[0]) if len(values) > 1 else 1.0
        half = step / 2
        if descending:
            return [v + half for v in values] + [values[-1] - half]
        return [v - half for v in values] + [values[-1] + half]

    ax.set_xticks(np.arange(len(m.columns) + 1))
    ax.set_xticklabels(
        [xtick_fmt.format(v) for v in edge_labels(list(m.columns))], rotation=0
    )
    ax.set_yticks(np.arange(len(m.index) + 1))
    ax.set_yticklabels(
        [ytick_fmt.format(v) for v in edge_labels(list(m.index), descending=True)],
        rotation=0,
    )

    # Gridlines now coincide with the labelled edges.
    ax.grid(False)
    ax.grid(which="major", color="#dddddd", linewidth=0.6)
    ax.set_xlabel("Energy Period, $T_e$ [s]")
    ax.set_ylabel("Significant Wave Height, $H_{m0}$ [m]")
    plt.tight_layout()
    return ax


# Interactive DataTables everywhere except the Typst/PDF path, which cannot
# show them: the Makefile sets H2O_RENDER_CONTEXT=png for the PDF and =dynamic
# for the HTML and notebook.
INTERACTIVE_TABLES = os.environ.get("H2O_RENDER_CONTEXT", "default") != "png"
if INTERACTIVE_TABLES:
    from itables import init_notebook_mode
    from itables import show as _show_interactive
    # itables defaults to connected=False, which embeds the DataTables JS
    # rather than fetching it from a CDN -- the right behaviour everywhere,
    # Kaggle included. Do not pass connected=True: it makes every render wait
    # on a CDN.
    init_notebook_mode(all_interactive=False)


def show_table(df, **kwargs):
    """Interactive itables view in HTML/notebook, static text in the PDF."""
    if INTERACTIVE_TABLES:
        _show_interactive(df, **kwargs)
    else:
        print(df.to_string())
