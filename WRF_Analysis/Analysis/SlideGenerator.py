# Make a single slide summarizing the analysis

import sys
import numpy
import matplotlib
import matplotlib.pyplot

__author__ = 'Alex Zylstra'


def show_slide(Fit=None, Hohl=None, Nxy=None, name='', summary='', results='', interactive=False):
    """Make a summary slide and show it on the screen.

    :param Fit: the GaussFit object which describes the fit to the data
    :param Hohl: (optional) the Hohlraum object describing hohlraum correction (if applicable) {default=None}
    :param Nxy: (optional) image data to display as N(x,y) {default=None}
    :param name: (optional) a short identifier for the data (EG 'N123456 90-78 Pos 1') {default=''}
    :param summary: (optional) a text description {default=''}
    :param results: (optional) a text description of the final results {default=''}
    :param interactive: (optional) whether to use the interactive mode {default=False}
    """
    # os detection
    if sys.platform.startswith('linux'):  # generic *nix
        matplotlib.pyplot.switch_backend('TkAgg')
    elif sys.platform.startswith('darwin'):  # Mac OS X
        if matplotlib.get_backend() != 'MacOSX':
            matplotlib.pyplot.switch_backend('MacOSX')
    else:
        matplotlib.pyplot.switch_backend('TkAgg')
    # use interactive mode if requested:
    matplotlib.pyplot.interactive(interactive)

    # make the figure:
    make_slide(Fit, Hohl, Nxy, name, summary, results)
    matplotlib.pyplot.show()


def save_slide(fname, Fit=None, Hohl=None, Nxy=None, name='', summary='', results=''):
    """Make a summary slide and save it to a file.

    :param Fit: the GaussFit object which describes the fit to the data
    :param Hohl: (optional) the Hohlraum object describing hohlraum correction (if applicable) {default=None}
    :param Nxy: (optional) image data to display as N(x,y) {default=None}
    :param name: (optional) a short identifier for the data (EG 'N123456 90-78 Pos 1') {default=''}
    :param summary: (optional) a text description {default=''}
    :param results: (optional) a text description of the final results {default=''}
    """
    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')
    make_slide(Fit, Hohl, Nxy, name, summary, results)
    matplotlib.pyplot.savefig(fname)


def make_slide(Fit=None, Hohl=None, Nxy=None, name='', summary='', results=''):
    """Make a summary slide.

    :param Fit: the GaussFit object which describes the fit to the data
    :param Hohl: (optional) the Hohlraum object describing hohlraum correction (if applicable) {default=None}
    :param Nxy: (optional) image data to display as N(x,y) {default=None}
    :param name: (optional) a short identifier for the data (EG 'N123456 90-78 Pos 1') {default=''}
    :param summary: (optional) a text description {default=''}
    :param results: (optional) a text description of the final results {default=''}
    """

    fig = matplotlib.pyplot.figure(figsize=(11, 8.5))
    gs = matplotlib.gridspec.GridSpec(2, 2,
                           width_ratios=[2, 3],
                           height_ratios=[2, 3])
    ax1 = matplotlib.pyplot.subplot(gs[0, 0])
    ax2 = matplotlib.pyplot.subplot(gs[0, 1])
    ax3 = matplotlib.pyplot.subplot(gs[1, 0])
    ax4 = matplotlib.pyplot.subplot(gs[1, 1])

    # top right box for text info:
    ax2.set_ylim([-1, 1])
    ax2.set_xlim([-1, 1])
    dy = 2. / (2+len(results))
    # display summary results:
    y = 1-dy
    ax2.text(0, y, summary, ha='center', va='center')
    for substr in results:
        y -= dy
        ax2.text(0, y, substr, ha='center', va='center')
    ax2.get_xaxis().set_visible(False)
    ax2.get_yaxis().set_visible(False)

    # top left box for N(x,y):
    if Nxy is not None:
        ax1.imshow(Nxy, interpolation='nearest')
        ax1.set_title(r'N(x,y)')
        ax1.get_xaxis().set_visible(False)
        ax1.get_yaxis().set_visible(False)

    # plot hohlraum correction:
    if Hohl is not None:
        Hohl.plot(ax3)
    # or state none:
    else:
        ax3.set_ylim([-1, 1])
        ax3.set_xlim([-1, 1])
        ax3.text(0, 0, 'No hohlraum correction', ha='center', va='center')
        ax3.get_xaxis().set_visible(False)
        ax3.get_yaxis().set_visible(False)

    # plot final spectrum:
    if Fit is not None:
       Fit.plot(ax4)

    matplotlib.rcParams.update({'font.size': 12})
    # if we are using TeX for rendering, then fix underscores:
    if matplotlib.rcParams['text.usetex'] == True:
        name = name.replace('_', r'$\textunderscore$')
    fig.suptitle(name, fontsize=24)
    return fig
