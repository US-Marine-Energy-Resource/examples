"""Figure and table output helpers for the example notebooks.

Import after `h2o_examples.environment` (this module imports it, so any import
order that starts with `environment` is safe).
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from matplotlib.ticker import MultipleLocator

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


def plot_wave_matrix(matrix, zlabel, figsize=None, fmt=".2f", buffer=1):
    """Heatmap of a sea-state matrix (Te on columns, Hm0 on the index).

    Empty bins are blanked and the axes are cropped to the populated bins plus
    a one-bin `buffer` on each side. Light minor gridlines fall on the bin
    edges. Adapted from the EMEC/PacWave proficiency-testing capture-matrix
    plot.
    """
    m = matrix.replace(0, np.nan)

    # Crop to populated bins + a one-bin buffer, dropping the empty low-Te block.
    rows = np.where(m.notna().any(axis=1))[0]
    cols = np.where(m.notna().any(axis=0))[0]
    r0, r1 = max(rows.min() - buffer, 0), min(rows.max() + buffer, m.shape[0] - 1)
    c0, c1 = max(cols.min() - buffer, 0), min(cols.max() + buffer, m.shape[1] - 1)
    m = m.iloc[r0 : r1 + 1, c0 : c1 + 1].sort_index(ascending=False)  # Hm0 up

    plt.figure(figsize=figsize or (FIG_WIDTH, FIG_WIDTH))
    ax = sns.heatmap(
        m, annot=True, fmt=fmt, cmap="viridis", cbar_kws={"label": zlabel}
    )
    # Minor ticks sit on the bin edges (between the centered cells) -> grid there.
    ax.grid(False)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(1.0))
    ax.grid(which="minor", color="#dddddd", linewidth=0.6)
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
