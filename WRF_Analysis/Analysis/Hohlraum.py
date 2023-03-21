# Implement functionality for hohlraum corrections

import os
import sys
from math import inf, tan, radians
from typing import Optional

import matplotlib
import numpy
from numpy.typing import NDArray

import WRF_Analysis.util.StopPow
from WRF_Analysis.util.GaussFit import GaussFit

__author__ = 'Alex Zylstra'

def LOS_r(z, theta) -> float:
    """Calculate radius along LOS given z.

    :param z: the axial position in cm
    :param theta: theta the LOS polar angle
    :returns: r the radial position in cm
    """
    theta2 = radians(90 - theta)
    return z / tan(theta2)


def LOS_z(r, theta) -> float:
    """Calculate z along LOS given r.

    :param r: the radial position in cm
    :param theta: the LOS polar angle
    :returns: z the axial position in cm
    """
    theta2 = radians(90 - theta)
    return r * tan(theta2)


def double_list_sort(list1, list2) -> tuple:
    """Sort two lists simultaneously, using first as key.

    :param list1: first list (will be sorted by this one)
    :param list2: second list
    :returns: tuple (list1,list2) sorted
    """
    list1, list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
    return list1, list2


def flatten(l) -> list:
    """Flatten a list, i.e. [[1,2],[3,4]] -> [1,2,3,4]

    :param l: the list to flatten
    :returns: the flattened list
    """
    return [item for sublist in l for item in sublist]


class Hohlraum:
    """Wrapper class for hohlraum corrections, and associated metrics.

    :param raw: the raw spectrum
    :param layers: list of material names and corresponding thicknesses (um) that particles pass through.
                   it should be ordered from inside to outside. the supported material names are whatever
                   materials have proton stopping power tables in the res/tables directory (for example, "Au", "U", "Al")
    :param fit_guess: (optional) an input to the fitting routine, guess as (Y, E, σ)
    :param limits: (optional) Energy limits (of raw spectrum) to use for fitting. Default uses entire spectrum.

    :author: Alex Zylstra
    """
    OutputDir = 'AnalysisOutputs'

    mode_wall = 'Wall'
    mode_thick = 'Thick'

    def __init__(self, layers: list[tuple[float, str]],
                 raw: Optional[NDArray[float]] = None,
                 fit_guess: Optional[tuple[float, float, float]] = None,
                 limits: tuple[float, float] = (0, inf)):
        """Constructor for the hohlraum. """
        # initializations:
        self.raw: Optional[NDArray[float]] = None  # raw spectrum
        self.raw_fit: Optional[GaussFit] = None  # Gaussian fit to the raw spectrum
        self.fit_guess = fit_guess
        self.corr: Optional[NDArray[float]] = None  # corrected spectrum
        self.corr_fit: Optional[GaussFit] = None  # Gaussian fit to the corrected spectrum
        self.limits = limits
        self.corr_limits: tuple[float, float] = (0, inf)
        self.stop_pow_calculators: dict[str, WRF_Analysis.util.StopPow.StopPow_SRIM] = {}

        # hohlraum thickness and material
        self.layers = layers

        # do spectral stuff only if not none:
        if raw is not None:
            # copy the raw data to a class variable:
            self.raw = numpy.copy(raw)

            # correct the spectrum:
            self.__correct_spectrum__(self.layers)

            # calculate corrected spectrum limits:
            self.corr_limits = [self.shift_energy(self.limits[0], self.layers),
                                self.shift_energy(self.limits[1], self.layers)]

            # fit to the data:
            self.__fit_data__()

    def __correct_spectrum__(self, layers: list[tuple[float, str]]) -> None:
        """ Calculate the corrected spectrum. """
        self.corr = numpy.zeros([len(self.raw), len(self.raw[0])], numpy.float32)  # array of corrected data

        # loop over all data:
        for i in range(len(self.raw)):
            # calculate new energy:
            new_E = self.shift_energy(self.raw[i][0], layers)

            # infer the bin_size size:
            # make sure we don't cause problems with array indices:
            if i > 0:
                bin_size = self.raw[i][0] - self.raw[i - 1][0]
            else:
                bin_size = self.raw[i + 1][0] - self.raw[i][0]

            # calculate a corrected bin_size size:
            new_bin = (self.shift_energy(self.raw[i][0] + bin_size / 2, layers)
                       - self.shift_energy(self.raw[i][0] - bin_size / 2, layers))

            # correct for accordian effect due to bin_size width:
            new_Y = self.raw[i][1] * bin_size / new_bin

            # error bar is statistical. Sqrt(n) is unchanged, but the
            # Y value is changed due to accordion effect, which we must
            # correct for:
            if self.raw[i][1] != 0:  # sanity check to prevent divide by 0
                new_err = self.raw[i][2] * new_Y / self.raw[i][1]
            else:
                new_err = self.raw[i][2]

            # Add this data point to the corrected array:
            self.corr[i][0] = new_E
            self.corr[i][1] = new_Y
            self.corr[i][2] = new_err

    def shift_energy(self, E: float, layers: list[tuple[float, str]]) -> float:
        """Calculate the energy shift for a given incident energy.

        :param E: the incident energy for a proton (MeV)
        :param layers: the materials and thicknesses (um) the proton must traverse
        :returns: the energy out in MeV
        """
        if E <= 0:
            return 0

        new_E = E
        for thickness, material in reversed(layers):
            # load the stopping power for this material if you haven’t
            if material not in self.stop_pow_calculators:
                self.stop_pow_calculators[material] = WRF_Analysis.util.StopPow.StopPow_SRIM(
                    os.path.join(f"res/tables/Hydrogen in {material}.txt"))
            # then correct for this layer
            new_E = self.stop_pow_calculators[material].Ein(new_E, thickness)

        return new_E

    def __fit_data__(self):
        """Calculate fits to the raw and shifted spectra."""
        # fit to the raw data:
        if self.fit_guess is not None:
            self.raw_fit = GaussFit(self.raw, guess=self.fit_guess, limits=self.limits)
        else:
            self.raw_fit = GaussFit(self.raw, limits=self.limits)

        # fit corrected data:
        g = [self.get_fit_raw()[0],
             self.shift_energy(self.get_fit_raw()[1], self.layers),
             self.get_fit_raw()[2]]

        self.corr_fit = GaussFit(self.corr, guess=g, limits=self.corr_limits)

    def get_fit_raw(self) -> NDArray[float]:
        """Get the fit to the raw data.

        :returns: an list containing [Yp,Ep,sigma]
        """
        return self.raw_fit.get_fit()

    def get_fit_corr(self) -> NDArray[float]:
        """Get the fit to the corrected data.

        :returns: a list containing [Yp,Ep,sigma]
        """
        return self.corr_fit.get_fit()

    def get_data_raw(self) -> NDArray[float]:
        """Get the raw data.

        :returns: a list containing the raw data
        """
        return self.raw

    def get_data_corr(self):
        """Get the hohlraum-corrected data.

        :returns: a list containing the corrected data.
        """
        return self.corr

    def get_limits(self):
        """Get the limits used for fitting the raw data.

        :returns: a list containing [min,max]
        """
        return self.limits

    def get_limits_corr(self):
        """Get the limits used for fitting the corrected data.

        :returns: a list containing [min,max]
        """
        return self.corr_limits

    def get_E_shift(self):
        """Get the peak's energy shift due to the hohlraum.

        :returns: the peak shift in MeV
        """
        raw = self.raw_fit.get_fit()[1]
        corr = self.corr_fit.get_fit()[1]
        return corr - raw

    def get_unc(self):
        """Get the uncertainty due to the hohlraum correction with given thickness uncertainties.

        :returns: the uncertainties as [ [-dY,+dy] , [-dE,+dE] , [-ds,+ds] ]
        """
        # nominal raw and corrected energies:
        fit_nominal = self.corr_fit.get_fit()

        # minimum thicknesses:
        minimal_layers = []
        for thickness, material in self.layers:
            minimal_layers.append((thickness*0.98, material))

        # calculate new spectrum and fits with these thicknesses:
        self.__correct_spectrum__(minimal_layers)
        self.__fit_data__()

        # fit to corrected spectrum with minimum thickness:
        fit_min = self.get_fit_corr()

        # maximum thicknesses:
        maximal_layers = []
        for thickness, material in self.layers:
            maximal_layers.append((thickness*1.02, material))

        # calculate new spectrum and fits with these thicknesses:
        self.__correct_spectrum__(maximal_layers)
        self.__fit_data__()

        # fit to corrected spectrum with minimum thickness:
        fit_max = self.get_fit_corr()

        # put things back to nominal:
        self.__correct_spectrum__(self.layers)
        self.__fit_data__()

        # we want to return uncertainties and not absolute values,
        # so reference to nominal fit:
        fit_min = numpy.absolute(fit_min - fit_nominal)
        fit_max = numpy.absolute(fit_max - fit_nominal)

        # return:
        dY = [fit_min[0], fit_max[0]]
        dE = [fit_min[1], fit_max[1]]
        ds = [fit_min[2], fit_max[2]]
        return [dY, dE, ds]

    def plot_file(self, fname):
        """Generate a plot and save it to a file.

        :param fname: the file to save to
        """
        if matplotlib.get_backend() != 'agg':
            matplotlib.pyplot.switch_backend('Agg')
        # get the figure:
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        self.plot(ax)

        # save to file:
        fig.savefig(fname)

    def plot_window(self, interactive=False):
        """Make a plot in a new UI window.

        :param interactive: (optional) whether to use the interactive mode {default=False}
        """
        # os detection
        if sys.platform.startswith('linux'):  # generic *nix
            matplotlib.pyplot.switch_backend('TkAgg')
        elif sys.platform.startswith('darwin'):  # Mac OS X
            if matplotlib.get_backend() != 'MacOSX':
                matplotlib.pyplot.switch_backend('MacOSX')
        # use interactive mode if requested:
        matplotlib.pyplot.interactive(interactive)

        # get the figure:
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        self.plot(ax)

        matplotlib.pyplot.show()

    def plot(self, ax=None):
        """Make a plot of the spectrum data (raw & corrected) and fit.

        :param ax: matplotlib Axes instance to plot into
        """
        # sanity check:
        if ax is None:
            ax = matplotlib.pyplot.gca()

        # split up raw data into columns:
        raw_x = numpy.zeros(len(self.raw))
        raw_y = numpy.zeros(len(self.raw))
        raw_err = numpy.zeros(len(self.raw))
        for i in range(len(self.raw)):
            raw_x[i] = self.raw[i][0]
            raw_y[i] = self.raw[i][1]
            raw_err[i] = self.raw[i][2]

        # plot the data with error bars
        ax.errorbar(
            raw_x,  # x values
            raw_y,  # y values
            yerr=raw_err,  # y error bars
            marker='s',  # square markers
            lw=0,  # no lines connecting points
            elinewidth=1,  # error bar line width
            mfc='red',  # marker color
            mec='red',  # marker line color
            ecolor='red')  # error bar color

        # split up corrected data into columns:
        corr_x = numpy.zeros(len(self.corr))
        corr_y = numpy.zeros(len(self.corr))
        corr_err = numpy.zeros(len(self.corr))
        for i in range(len(self.corr)):
            corr_x[i] = self.corr[i][0]
            corr_y[i] = self.corr[i][1]
            corr_err[i] = self.corr[i][2]

        # plot the data with error bars
        ax.errorbar(
            corr_x,  # x values
            corr_y,  # y values
            yerr=corr_err,  # y error bars
            marker='s',  # square markers
            lw=0,  # no lines connecting points
            elinewidth=1,  # error bar line width
            mfc='blue',  # marker color
            mec='blue',  # marker line color
            ecolor='blue')  # error bar color

        # make an evaluted fit dataset for plotting
        fit_x = []
        fit_y = []
        x = raw_x[0]
        dx = (raw_x[1] - x) / 10
        while x < raw_x[-1]:
            fit_x.append(x)
            fit_y.append(self.raw_fit.eval_fit(x))
            x += dx

        ax.plot(fit_x, fit_y, 'r--')

        # make an evaluted fit dataset for plotting
        fit_x = []
        fit_y = []
        x = corr_x[0]
        dx = (corr_x[1] - x) / 10
        while x < corr_x[-1]:
            fit_x.append(x)
            fit_y.append(self.corr_fit.eval_fit(x))
            x += dx

        ax.plot(fit_x, fit_y, 'b--')

        # add text with fit parameters
        # location for the text: (based on line position)
        x = self.get_fit_corr()[1] + 3 * self.get_fit_corr()[2]
        y = numpy.max(corr_y) * 3 / 4
        # construct a text string to display:
        text = r'$E_{raw}$ = ' + '{:.2f}'.format(self.get_fit_raw()[1]) + ' MeV'
        # write text to the plot:
        ax.text(x, y,  # data
                text,  # text to display
                color='red',
                backgroundcolor='white')  # fill background
                #bbox=dict(ec='red', fc='white', alpha=1.0, pad=1.1))  # add boundary
        x = self.get_fit_corr()[1] + 3 * self.get_fit_corr()[2]
        y = y * 5/6
        text = r'$E_{corr}$ = ' + '{:.2f}'.format(self.get_fit_corr()[1]) + ' MeV'
        # write text to the plot:
        ax.text(x, y,  # data
                text,  # text to display
                color='blue',
                backgroundcolor='white')  # fill background
                #bbox=dict(ec='blue', fc='white', alpha=1.0, pad=1.1))  # add boundary

        ax.grid(True)
        ax.set_xlabel(r'Energy (MeV)')
        ax.set_ylabel(r'Yield/MeV')
        ax.set_title(r'Hohlraum Correction')
