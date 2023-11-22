from typing import Optional, Tuple, Union

import numpy as np
from matplotlib import pyplot as plt

from ..constants import PITCH_ID_TO_NAME
from .utils import pitch_padding

# -------------------------------------------- #
# Global and Customized Parameters
# -------------------------------------------- #

# color maps
NOTE_CMAP = "Greens"
CHROMA_CMAP = "magma"
SM_CMAP = "gray"
PR_CMAP = "gray"

# colors
WHITE_KEY_SATUR = 0.96
BLACK_KEY_SATUR = 0.78

# font size
XLABEL_FONT_SIZE = 2
YLABEL_FONT_SIZE = 5

# set middle C (midi note number 60)
#     ex: set C4 to 60(5th) means set 0(0th) to C-1
OFFSET_OCTAVE = -1


# -------------------------------------------- #
# Main Functions
# -------------------------------------------- #
def plot(
    pianoroll: np.ndarray,
    note_range: Tuple[int, int] = (0, 128),
    beat_resolution: int = 24,
    downbeats: Union[int, np.ndarray] = 4,
    background_layout: str = "pianoroll",
    grid_layout: str = "x",
    xtick: str = "downbeat",
    ytick: str = "number",
    ytick_interval: int = 12,
    xtick_interval: int = 1,
    x_range: Optional[Tuple[int, int]] = None,
    y_range: Optional[Tuple[int, int]] = None,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = 300,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot Pianoroll
    Parameters
    ----------
    pianoroll : np.ndarray
        a tensor with the shape of T(time) x P(pitch).
    note_range : tuple or list
        (start, end) or [start, end]. It indicates the pitch range of
        the input pianoroll. The default is [0, 128], which means there
        is no cropping.
    beat_resolution : int
        the resolution of one beat. It's equivalent to 'ticks per beat' in MIDI
    downbeats : np.ndarray or int
        np.array:
            bool: indicates that if the current beat is a downbeat or not
            int: indices of downbeat
        int:
            num of beats per downbeat
    background_layout : str
        'pianoroll', 'blank'
    grid_layout : str
        'x', 'y', 'both', None
    xtick : str
        'downbeat', 'beat', 'tick', None
    ytick : str
        'number', 'note', None
    ytick_interval : int
        interval between ticks of pitch axis
    xtick_interval : int
        interval between ticks of time axis
    x_range : tuple
        (start, end) or [start, end], None for all
    y_range : tuple
        (start, end) or [start, end], None for all
    figsize : tuple
        (h, w). Using it to customize the output image when the result
        is too large.
    dpi : int
        Dots per inch.
    """

    # init the figure
    if figsize is not None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig, ax = plt.subplots(dpi=dpi)

    # critical paras
    st, ed = note_range
    sz_time, sz_pitch = pianoroll.shape
    if (ed - st) != sz_pitch:
        raise ValueError("Invalid note_range")
    pianoroll = pitch_padding(pianoroll, note_range)

    # set display range
    if x_range is None:
        x_range = (0, sz_time)
    if y_range is None:
        y_range = note_range

    to_plot = pianoroll.T
    canvas = np.ones_like(to_plot)

    # plot background
    plot_background(ax, background_layout, canvas)

    # plot notes
    plot_note_entries(ax, to_plot)

    # plot and set ticks
    plot_xticks(ax, xtick, xtick_interval, sz_time, beat_resolution, downbeats)
    plot_yticks(ax, ytick, ytick_interval, sz_time, beat_resolution, downbeats)

    # plot grid
    plot_grid(ax, grid_layout)

    # set range
    plt.xlim(x_range)
    plt.ylim(y_range)

    return fig, ax


def plot_chroma(
    chroma: np.ndarray,
    beat_resolution: int = 24,
    downbeats: Union[int, np.ndarray] = 4,
    xtick: str = "downbeat",
    ytick: str = "note",
    x_range: Optional[Tuple[int, int]] = None,
    xtick_interval: int = 1,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = 300,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot Chromagram
    Parameters
    ----------
    chroma : np.ndarray
        a tensor with the shape of T(time) x 12.
    beat_resolution : int
        the resolution of one beat. It's equivalent to 'ticks per beat' in MIDI
    downbeats : np.array or int
        np.array:
            bool: indicates that if the current beat is a downbear or not
            int: indices of downbeat
        int:
            num of beats per downbeat
    xtick : str
        'downbeat', 'beat', 'tick', None
    ytick : str
        'number', 'note', None
    xtick_interval : int
        interval between ticks of time axis
    x_range : tuple
        (start, end) or [start, end], None for all
    figsize : tuple
        (h, w). Using it to customize the output image when the result
        is too large.
    dpi : int
        Dots per inch.
    """
    # init the figure
    if figsize is not None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig, ax = plt.subplots(dpi=dpi)

    # chroma
    sz_time, sz_pitch = chroma.shape
    to_plot = chroma.T
    if sz_pitch != 12:
        raise ValueError("Invalid Input: the dim of pitch should be 12")

    # set range
    if x_range is None:
        x_range = (0, sz_time)

    # plot xticks
    plot_xticks(ax, xtick, xtick_interval, sz_time, beat_resolution, downbeats)

    # plot yticks
    yticks = np.arange(0, 12)
    ax.set_yticks(yticks)
    if ytick == "number":
        ax.set_yticklabels(yticks, fontsize=YLABEL_FONT_SIZE)
    elif ytick == "note":
        yticks_name = [PITCH_ID_TO_NAME[k % 12] for k in yticks]
        ax.set_yticklabels(yticks_name, fontsize=YLABEL_FONT_SIZE)
    else:
        ax.tick_params(axis="y", width=0)
        ax.set_yticklabels([])

    # display
    ax.imshow(
        to_plot,
        aspect="auto",
        cmap=CHROMA_CMAP,
        vmin=np.min(to_plot),
        vmax=np.max(to_plot),
        origin="lower",
        interpolation="none",
    )
    # set range
    plt.xlim(x_range)

    return fig, ax


def plot_heatmap(
    to_plot: np.ndarray,
    tick_interval: Optional[int] = None,
    origin: str = "upper",
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = 300,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot Similarity Matrix
    Parameters
    ----------
    to_plot : np.ndarray
        an M x N heatmap matrix. If the input is the self-similarity one,
        the size would be M x M
    tick_interval : int
        interval between ticks of both axis. If the input is None, it will
        be automatically adjusted.
    origin : str
        'upper', 'lower'. Layout of the imshow
    figsize : tuple
        (h, w). Using it to customize the output image when the result
        is too large.
    dpi : int
        Dots per inch.
    """

    # init the figure
    if figsize is not None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig, ax = plt.subplots(dpi=dpi)

    # display
    plt.imshow(
        to_plot,
        cmap=SM_CMAP,
        vmin=np.min(to_plot),
        vmax=np.max(to_plot),
        origin=origin,
        interpolation="none",
    )

    # plot ticks
    sx, sy = to_plot.shape
    if tick_interval is None:
        tick_interval = min(sx, sy) // 20

    xticks = np.arange(0, sx)
    yticks = np.arange(0, sy)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, fontsize=XLABEL_FONT_SIZE, rotation=-90)
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks, fontsize=XLABEL_FONT_SIZE)

    ax.xaxis.set_tick_params(labeltop="on", top=True)  # show labs on top
    return fig, ax


# -------------------------------------------- #
# Auxiliary Tools
# -------------------------------------------- #


def plot_grid(ax: plt.Axes, layout: str, which: str = "minor", color="k"):
    # always using 'minor' tick to plot grid
    # argumens check
    if layout not in ["x", "y", "both", None]:
        raise ValueError("Unkown Grid layout: %s" % layout)

    # grid Show
    if layout in ["x", "both"]:
        ax.grid(
            axis="x", color=color, which=which, linestyle="-", linewidth=0.2, alpha=0.5
        )
    if layout in ["y", "both"]:
        ax.grid(
            axis="y", color=color, which=which, linestyle="-", linewidth=0.2, alpha=0.75
        )


def plot_yticks(
    ax: plt.Axes, ytick: str, ytick_interval: int, max_tick, beat_resolution, downbeats
):
    # tick arrangement
    # - ytick, minor for grid
    yticks = np.arange(0.5, 128.5)
    ax.set_yticks(yticks, minor=True)
    ax.tick_params(axis="y", which="minor", width=0)

    # - yticks & labels
    yticks_key = np.arange(0, 128, ytick_interval)
    ax.set_yticks(yticks_key)

    if ytick == "number":
        ax.set_yticklabels(yticks_key, fontsize=YLABEL_FONT_SIZE)
    elif ytick == "note":
        yticks_name = []
        for k in yticks_key:
            lab = ""
            if k % 12 in PITCH_ID_TO_NAME:
                lab = "%2s%s" % (
                    str(PITCH_ID_TO_NAME[k % 12]),
                    str(k // 12 + OFFSET_OCTAVE),
                )
            yticks_name.append(lab)
        ax.set_yticklabels(yticks_name, fontsize=YLABEL_FONT_SIZE)
    else:
        ax.tick_params(axis="y", which="major", width=0)
        ax.set_yticklabels([])


def plot_xticks(
    ax: plt.Axes,
    xtick: str,
    xtick_interval: int,
    max_tick: int,
    beat_resolution: int,
    downbeats: Optional[int] = None,
):
    # tick arrangement
    # - xtick, minor for beat
    xticks_beat = np.arange(0, max_tick, beat_resolution)
    ax.set_xticks(xticks_beat, minor=True)

    # - downbeats
    xticks_downbeats = None
    if downbeats is not None:
        xticks_downbeats = None
        if isinstance(downbeats, int):
            xticks_downbeats = np.arange(0, max_tick, beat_resolution * downbeats)
        else:
            downbeats = np.array(downbeats)
            if downbeats.dtype == int:
                xticks_downbeats = downbeats
            elif downbeats.dtype == bool:
                xticks_downbeats = np.where(downbeats == True)  # noqa: E712
            else:
                raise ValueError("Unkown downbeats type: %s" % downbeats)
        ax.set_xticks(xticks_downbeats)
        ax.grid(
            axis="x", color="k", which="major", linestyle="-", linewidth=0.5, alpha=1.0
        )
    else:
        ax.tick_params(axis="x", which="major", width=0)
    ax.set_xticklabels([])

    # - xticks & labels
    if xtick == "beat":
        xlabels_beat = np.array([str(tick // beat_resolution) for tick in xticks_beat])
        xlabels_beat = _label_selector(xlabels_beat, xtick_interval)
        ax.set_xticklabels(
            xlabels_beat, minor=True, fontsize=XLABEL_FONT_SIZE, rotation=-90
        )
    elif xtick == "tick":
        xlabels_tick = np.array([str(tick) for tick in xticks_beat])
        xlabels_tick = _label_selector(xlabels_tick, xtick_interval)
        ax.set_xticklabels(
            xlabels_tick, minor=True, fontsize=XLABEL_FONT_SIZE, rotation=-90
        )
    elif xtick == "downbeat":
        if xtick == "downbeat" and downbeats is None:
            raise ValueError("Invalid Input: downbeats is None!")
        xlabels_dwonbeats = np.array([str(idx) for idx in range(len(xticks_downbeats))])
        xlabels_dwonbeats = _label_selector(xlabels_dwonbeats, xtick_interval)
        ax.set_xticklabels(xlabels_dwonbeats, fontsize=XLABEL_FONT_SIZE, rotation=-90)
    elif xtick is None:
        ax.set_xticklabels([])
        ax.tick_params(axis="x", which="minor", width=0)
        ax.tick_params(axis="x", which="major", width=0)
    else:
        raise ValueError("Unkown xtick type: %s" % xtick)


def plot_background(ax: plt.Axes, layout: str, canvas):
    if layout == "pianoroll":
        all_black_index = []
        for n in range(11):
            all_black_index.extend(list(map(lambda x: x + 12 * n, [1, 3, 6, 8, 10])))

        pianoroll_bg = np.ones_like(canvas) * WHITE_KEY_SATUR
        pianoroll_bg[all_black_index[:-2]] = BLACK_KEY_SATUR

        ax.imshow(
            pianoroll_bg,
            aspect="auto",
            cmap=PR_CMAP,
            vmin=0,
            vmax=1,
            origin="lower",
            interpolation="none",
        )
    elif layout == "blank":
        pass
    else:
        raise ValueError("Unkown background layout: %s" % layout)


def plot_note_entries(ax: plt.Axes, to_plot):
    # for better color percetion
    color_shift = 80

    # plotting
    masked_data = np.ma.masked_where(to_plot <= 0, to_plot + color_shift)
    ax.imshow(
        masked_data,
        cmap=NOTE_CMAP,
        aspect="auto",
        vmin=0,
        vmax=127 + color_shift,
        origin="lower",
        interpolation="none",
    )


def _label_selector(labels, skip):
    if skip > 1:
        for idx in range(len(labels)):
            if idx % skip:
                labels[idx] = ""
    return labels
