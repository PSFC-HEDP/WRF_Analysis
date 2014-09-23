# Implement functionality for hohlraum corrections

import os
import sys
import numpy
import math
import scipy
import scipy.interpolate
import scipy.optimize
import scipy.stats
#try:
#    import scipy.interpolate
#    import scipy.optimize
#    import scipy.stats
#except:
#    import syslog
#    syslog.syslog(syslog.LOG_ALERT, 'Error loading scipy submodule(s)')
import matplotlib
from NIF_WRF.util.GaussFit import GaussFit
import NIF_WRF.util.StopPow


__author__ = 'Alex Zylstra'

def LOS_r(z, theta) -> float:
    """Calculate radius along LOS given z.

    :param z: the axial position in cm
    :param theta: theta the LOS polar angle
    :returns: r the radial position in cm
    """
    theta2 = math.radians(90 - theta)
    return z / math.tan(theta2)


def LOS_z(r, theta) -> float:
    """Calculate z along LOS given r.

    :param r: the radial position in cm
    :param theta: the LOS polar angle
    :returns: z the axial position in cm
    """
    theta2 = math.radians(90 - theta)
    return r * math.tan(theta2)


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


class Hohlraum(object):
    """Wrapper class for hohlraum corrections, and associated metrics.
    You must supply either the thickness array or an array containing wall data plus view angles.

    :param raw: the raw spectrum
    :param wall: python array of [ Drawing , Name , Layer # , Material , r (cm) , z (cm) ]
    :param angles: python array of [theta_min, theta_max] range in polar angle
    :param Thickness: the [Au,DU,Al] thickness in um
    :param d_Thickness: the uncertainty in wall thickness for [Au,DU,Al] in um
    :param fit_guess: (optional) an input to the fitting routine, guess as Y,E,sigma [default=None]
    :param limits: (optional) Energy limits (of raw spectrum) to use for fitting. Default uses entire spectrum.
    :param use_bump_corr: (optional) Boolean flag to use a correction for the hohlraum thickness because of the 'bump' [default=False]
    :param bump_corr: (optional) The change in thickness for the bump correction, which is added to the t=0 thickness [default=0]

    :author: Alex Zylstra
    """
    OutputDir = 'AnalysisOutputs'

    mode_wall = 'Wall'
    mode_thick = 'Thick'

    # set up SRIM calculators:
    Al_SRIM = NIF_WRF.util.StopPow.StopPow_SRIM(
        os.path.join(os.environ['SRIM_data'], "Hydrogen in Aluminum.txt"))  # SRIM stopping power for Al
    Au_SRIM = NIF_WRF.util.StopPow.StopPow_SRIM(
        os.path.join(os.environ['SRIM_data'], "Hydrogen in Gold.txt"))  # SRIM stopping power for Au
    DU_SRIM = NIF_WRF.util.StopPow.StopPow_SRIM(
        os.path.join(os.environ['SRIM_data'], "Hydrogen in Uranium.txt"))  # SRIM stopping power for DU

    def __init__(self, raw=None, wall=None, angles=None, Thickness=None, d_Thickness=(1, 1, 3), fit_guess=None, limits=None, use_bump_corr=False, bump_corr=0):
        """Constructor for the hohlraum. """
        super(Hohlraum, self).__init__() # super constructor

        # initializations:
        self.raw = []  # raw spectrum
        self.raw_fit = []  # Gaussian fit to the raw spectrum
        self.fit_guess = fit_guess
        self.corr = []  # corrected spectrum
        self.corr_fit = []  # Gaussian fit to the corrected spectrum
        self.limits = limits
        self.corr_limits = []

        # thickness in um of three hohlraum components:
        self.Au = 0  # Calculated or given thickness of Au
        self.DU = 0  # Calculated or given thickness of DU
        self.Al = 0  # Calculated or given thickness of Al
        # uncertainties in thickness:
        self.d_Au = 0  # Calculated or given uncertainty in thickness of Au
        self.d_DU = 0  # Calculated or given uncertainty in thickness of DU
        self.d_Al = 0  # Calculated or given uncertainty in thickness of Al

        # Bump correction if requested:
        self.use_bump_corr = use_bump_corr
        self.bump_corr = bump_corr

        #  r and z arrays for all wall layers:
        self.all_r = []
        self.all_z = []
        self.layer_mat = []
        self.angles = []

        # if the wall is specified:
        if wall is not None and len(wall) != 0 and angles is not None:
            self.__calc_from_wall__(wall, angles)
            self.mode = Hohlraum.mode_wall
        # thickness is specified:
        elif Thickness is not None and len(Thickness) is 3:
            self.Au = Thickness[0]
            self.DU = Thickness[1]
            self.Al = Thickness[2]
            self.mode = Hohlraum.mode_thick
        # if neither is supplied, default to 0 thickness to be safe:
        else:
            self.Au = 0
            self.DU = 0
            self.Al = 0
            self.mode = Hohlraum.mode_thick

        # Correct for the bump:
        if use_bump_corr:
            self.Au = max(self.Au + bump_corr, 0)  # make sure this stays positive

        # set the uncertainties:
        self.d_Au = d_Thickness[0]
        self.d_DU = d_Thickness[1]
        self.d_Al = d_Thickness[2]

        # do spectral stuff only if not none:
        if raw is not None:
            # copy the raw data to a class variable:
            self.raw = numpy.copy(raw)

            # correct the spectrum:
            self.__correct_spectrum__()

            # calculate corrected spectrum limits:
            if limits is not None:
                self.corr_limits = [self.shift_energy(self.limits[0], Au=self.Au, DU=self.DU, Al=self.Al),
                                    self.shift_energy(self.limits[1], Au=self.Au, DU=self.DU, Al=self.Al)]
            else:
                self.corr_limits = None

            # fit to the data:
            self.__fit_data__()

    def __calc_from_wall__(self, wall, angles):
        """Calculate the material thicknesses from a wall definition. Sets the class variables Au, DU, and Al.

        :param wall: python list of [ Drawing , Name , Layer # , Material , r (cm) , z (cm) ]
        :param angles: python list of [theta_min, theta_max] range in polar angle
        """
        self.Au = 0
        self.DU = 0
        self.Al = 0

        # ------------------------------------------------
        # Split the incoming wall data into layers:
        # ------------------------------------------------
        # figure out how many layers there are:
        num_layers = 0
        for i in wall:
            num_layers = max(num_layers, i[2])
        num_layers += 1  # correct for zero-index data

        # construct r and z arrays for all layers:
        self.all_r = []
        self.all_z = []
        self.layer_mat = []
        # create arrays of correct length for each layer:
        for _ in numpy.arange(num_layers):
            self.all_r.append([])
            self.all_z.append([])
            self.layer_mat.append([])

        # now read data into the new arrays:
        for i in wall:
            self.all_r[int(i[2])].append(i[4])
            self.all_z[int(i[2])].append(i[5])
            if len(self.layer_mat[int(i[2])]) is 0:
                self.layer_mat[int(i[2])] = i[3]

        # we need to have the wall data sorted:
        # iterate over each layer
        for i in range(int(num_layers)):
            # sort r values and z values together:
            self.all_z[i], self.all_r[i] = double_list_sort(self.all_z[i], self.all_r[i])

        # ------------------------------------------------
        # Incorporate layer data into the class info:
        # ------------------------------------------------
        # iterate over layers
        # each layer has two walls, thus factor of 2:
        for i in range(int(num_layers / 2)):
            thickness = self.__calc_layer_thickness__(self.all_r[2 * i], self.all_z[2 * i], self.all_r[2 * i + 1],
                                                  self.all_z[2 * i + 1], angles)
            # check material:
            if self.layer_mat[2 * i] == 'Au':
                self.Au += thickness[0] * 1e4  # also convert -> um
            elif self.layer_mat[2 * i] == 'DU' or self.layer_mat[2 * i] == 'U':
                self.DU += thickness[0] * 1e4  # also convert -> um
            elif self.layer_mat[2 * i] == 'Al':
                self.Al += thickness[0] * 1e4  # also convert -> um

        self.angles = angles

    def __calc_layer_thickness__(self, inner_r, inner_z, outer_r, outer_z, angles, n=50) -> tuple:
        """Calculate the average thickness of a wall layer

        :param inner_r: list of r values for points defining the inner wall
        :param inner_z: list of z values for points defining the inner wall
        :param outer_r: list of r values for points defining the outer wall
        :param outer_z: list of z values for points defining the outer wall
        :param angles: [min,max] polar angles for the line of sight
        :param n: (optional) number of angle points to sample (default = 50)
        :returns: a tuple containing (mean , stdev) of the thickness
        """
        values = []
        dtheta = (angles[1] - angles[0]) / n
        #iterate over angles:
        for theta in numpy.arange(angles[0], angles[1], dtheta):
            # set up interpolation:
            inner_int = scipy.interpolate.interp1d(
                inner_z,
                inner_r,
                kind='linear', bounds_error=False, fill_value=1e10)
            outer_int = scipy.interpolate.interp1d(
                outer_z,
                outer_r,
                kind='linear', bounds_error=False, fill_value=1e10)

            # calculate the intersection points:
            z1 = scipy.optimize.fminbound(
                func=(lambda x: math.fabs(inner_int(x) - LOS_r(x, theta))),
                x1=min(inner_z),
                x2=max(inner_z),
                xtol=1e-7)
            r1 = LOS_r(z1, theta)
            z2 = scipy.optimize.fminbound(
                func=(lambda x: math.fabs(outer_int(x) - LOS_r(x, theta))),
                x1=min(outer_z),
                x2=max(outer_z),
                xtol=1e-7)
            r2 = LOS_r(z2, theta)

            # calculate thickness:
            values.append(math.sqrt((z2 - z1) ** 2 + (r2 - r1) ** 2))

        return scipy.stats.tmean(values), scipy.stats.tstd(values)

    def __correct_spectrum__(self, Al=None, DU=None, Au=None):
        """Calculate the corrected spectrum.

        :param Al: (optional) the aluminum thickness in um
        :param DU: (optional) the uranium thickness in um
        :param Au: (optional) the gold thickness in um
        """
        self.corr = numpy.zeros([len(self.raw), len(self.raw[0])], numpy.float32)  # array of corrected data

        # if no thicknesses are input, use default class variables:
        if Al is None:
            Al = self.Al
        if DU is None:
            DU = self.DU
        if Au is None:
            Au = self.Au

        # loop over all data:
        for i in range(len(self.raw)):
            # calculate new energy:
            new_E = self.shift_energy(self.raw[i][0], Al=Al, DU=DU, Au=Au)

            # infer the bin_size size:
            # make sure we don't cause problems with array indices:
            if i > 0:
                bin_size = self.raw[i][0] - self.raw[i - 1][0]
            else:
                bin_size = self.raw[i + 1][0] - self.raw[i][0]

            # calculate a corrected bin_size size:
            new_bin = (self.shift_energy(self.raw[i][0] + bin_size / 2, Al=Al, DU=DU, Au=Au)
                       - self.shift_energy(self.raw[i][0] - bin_size / 2, Al=Al, DU=DU, Au=Au))

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

    def shift_energy(self, E, Al=None, DU=None, Au=None):
        """Calculate the energy shift for a given incident energy.

        :param E: the incident energy for a proton in MeV
        :param Al: (optional) the aluminum thickness in um
        :param DU: (optional) the uranium thickness in um
        :param Au: (optional) the gold thickness in um
        :returns: the energy out in MeV
        """
        # if no thicknesses are input, use default class variables:
        if Al is None:
            Al = self.Al
        if DU is None:
            DU = self.DU
        if Au is None:
            Au = self.Au

        new_E = E
        # correct for Al:
        new_E = self.Al_SRIM.Ein(new_E, Al)
        # correct for DU:
        new_E = self.DU_SRIM.Ein(new_E, DU)
        # correct for Au:
        new_E = self.Au_SRIM.Ein(new_E, Au)

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
             self.shift_energy(self.get_fit_raw()[1]),
             self.get_fit_raw()[2]]

        self.corr_fit = GaussFit(self.corr, guess=g, limits=self.corr_limits)

    def get_fit_raw(self) -> list:
        """Get the fit to the raw data.

        :returns: an list containing [Yp,Ep,sigma]
        """
        return self.raw_fit.get_fit()

    def get_fit_corr(self) -> list:
        """Get the fit to the corrected data.

        :returns: a list containing [Yp,Ep,sigma]
        """
        return self.corr_fit.get_fit()

    def get_data_raw(self) -> list:
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
        Au = self.Au
        if Au > 0:
            Au -= self.d_Au
        DU = self.DU
        if DU > 0:
            DU -= self.d_DU
        Al = self.Al
        if Al > 0:
            Al -= self.d_Al

        # calculate new spectrum and fits with these thicknesses:
        self.__correct_spectrum__(Al=Al, DU=DU, Au=Au)
        self.__fit_data__()

        # fit to corrected spectrum with minimum thickness:
        fit_min = self.get_fit_corr()

        # minimum thicknesses:
        Au = self.Au
        if Au > 0:
            Au += self.d_Au
        DU = self.DU
        if DU > 0:
            DU += self.d_DU
        Al = self.Al
        if Al > 0:
            Al += self.d_Al

        # calculate new spectrum and fits with these thicknesses:
        self.__correct_spectrum__(Al=Al, DU=DU, Au=Au)
        self.__fit_data__()

        # fit to corrected spectrum with minimum thickness:
        fit_max = self.get_fit_corr()

        # put things back to nominal:
        self.__correct_spectrum__()
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

    def plot_hohlraum_file(self, fname):
        """Save a hohlraum profile plot to file.

        :param fname: the file to save to
        """
        # sanity check, in thickness mode we cannot plot anything:
        if self.mode == Hohlraum.mode_thick:
            return

        if matplotlib.get_backend() != 'agg':
            matplotlib.pyplot.switch_backend('Agg')
        # get the figure:
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        self.plot_hohlraum(ax)

        # save to file:
        fig.savefig(fname)

    def plot_hohlraum_window(self, interactive=False):
        """Make a new hohlraum profile plot in a UI window.

        :param interactive: (optional) whether to use the interactive mode {default=False}
        """
        # sanity check, in thickness mode we cannot plot anything:
        if self.mode == Hohlraum.mode_thick:
            return

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
        self.plot_hohlraum(ax)

        matplotlib.pyplot.show()

    def plot_hohlraum(self, ax=None, text=True):
        """ Make a plot of the hohlraum wall and LOS into given Axes.

        :param ax: matplotlib Axes instance to plot into
        :param text: show text labels of various things
        """
        # sanity check:
        if ax is None:
            ax = matplotlib.pyplot.gca()

        # iterate over all layers:
        # noinspection PyTypeChecker
        for i in numpy.arange(len(self.all_z) / 2 - 1, -1, -1, dtype=numpy.int):
            # choose a color based on material type:
            c = 'black'
            if self.layer_mat[2 * i] == 'Au':
                c = 'orange'
            if self.layer_mat[2 * i] == 'DU' or self.layer_mat[2 * i] == 'U':
                c = '#555555'
            if self.layer_mat[2 * i] == 'Al':
                c = '#aaaaaa'

            # plot this layer:
            ax.fill_between(  # use fill_between type plot
                              self.all_z[2 * i],  # z points
                              self.all_r[2 * i],  # inner wall
                              self.all_r[2 * i + 1],  # outer wall
                              color=c)  # options

        # now plot the LOS:
        # find the max/min r we should plot:
        r_max = max(flatten(self.all_r)) * 1.1
        r_min = min(flatten(self.all_r)) * 0.9
        for theta in self.angles:
            r = numpy.linspace(r_min, r_max, 100)
            z = LOS_z(r, theta)

            ax.plot(z, r, 'b--')

        if text:
            # add a WRF text annotation for blue lines:
            text = 'WRF LOS'
            theta = scipy.stats.tmean(self.angles)
            ax.text(LOS_z(r_max, theta), r_max,  # where to put it
                    text,  #  text to display
                    color='blue', horizontalalignment='center')
            #backgroundcolor='blue') # fill background
            #bbox=dict(ec='black', fc='blue', alpha=1.0)) # add black boundary

            # Some coordinates for displaying text
            z_min = min(flatten(self.all_z))
            z_max = max(flatten(self.all_z))
            if math.fabs(z_min) < 1e-3:
                z_text = (z_max-z_min)/3.
            else:
                z_text = 0.
            dr = (r_max-r_min)/15.

            # add some text annotation with thicknesses:
            text = '{:.1f}'.format(self.Au) + r' $\mu$m Au'
            ax.text(z_text, r_min+2*dr, text, horizontalalignment='center')

            text = '{:.1f}'.format(self.DU) + r' $\mu$m DU'
            ax.text(z_text, r_min+dr, text, horizontalalignment='center')

            text = '{:.1f}'.format(self.Al) + r' $\mu$m Al'
            ax.text(z_text, r_min, text, horizontalalignment='center')


            # add an indicator showing where N pole is in this plot
            ax.arrow(z_max, r_min, z_max / 8, 0, fc='k', ec='k', head_width=z_max / 30, head_length=z_max / 30)
            ax.text(z_max, r_min * 1.02, 'N pole', ha='left', va='bottom')

        ax.set_xlabel('z (cm)')
        ax.set_ylabel('r (cm)')

        ax.set_title('Hohlraum Profile')
