# Functions for making plots of the rhoR model

import math
import matplotlib
import matplotlib.pyplot
import numpy
from numpy import arange, zeros
from NIF_WRF.Analysis.rhoR_Model import rhoR_Model
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis
from NIF_WRF.util.StopPow import StopPow, StopPow_LP, DoubleVector


__author__ = 'Alex Zylstra'

def plot_rhoR_v_Energy(analysis, filename=None, ax=None, backend=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, color='k', title=None, old_models=None, figsize=(3.,2.5), units='mg/cm2', rmin=None, rmax=None):
    """Plot rhoR model's curve versus energy.

    :param analysis: the rhoR analysis model to plot
    :param filename: (optional) where to save the plot
    :param ax: (optional) existing matplotlib axes to plot into
    :param backend: (optional) matplotlib backend to use
    :param E0: (optional) The initial proton energy in MeV [default=14.7]
    :param dE: (optional) The energy step size in MeV [default=14.7]
    :param Emin: (optional) minimum energy to plot in MeV [default=5]
    :param Emax: (optional) maximum energy to plot in MeV [default=14]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param old_models: (optional) functional forms of previous models to overplot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    :param units: (optional) either 'mg/cm2' or 'g/cm2'
    :param rmin: (optional) Minimum radius to plot [cm]
    :param rmax: (optional) Maximum radius to plot [cm]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    #if matplotlib.get_backend() != 'agg':
    if backend is not None:
        matplotlib.pyplot.switch_backend(backend)

    # lists of things to plot:
    EnergyList = []
    RhoRList = []
    RhoRListPlusErr = []
    RhoRListMinusErr = []

    # energies:
    for i in arange(Emin, Emax, dE):
        # get result:
        temp = analysis.Calc_rhoR(i)
        # If r limits are specified:
        if rmin is not None and rmax is not None:
            add = (temp[1] >= rmin and temp[1] <= rmax)
        else:
            add = True
        # Add to appropriate lists:
        if add:
            EnergyList.append(i)
            RhoRList.append(temp[0])
            RhoRListPlusErr.append(temp[0] + temp[2])
            RhoRListMinusErr.append(temp[0] - temp[2])

    # do correction for units
    if units == 'mg/cm2':
        RhoRList = 1e3*numpy.asarray(RhoRList)
        RhoRListPlusErr = 1e3*numpy.asarray(RhoRListPlusErr)
        RhoRListMinusErr = 1e3*numpy.asarray(RhoRListMinusErr)

    # make a plot if necessary:
    if ax is None:
        fig = matplotlib.pyplot.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    
    # temp:
    ax.axhline(5, c='k', ls='dotted')
    ax.axhline(7, c='k', ls='dotted')
    ax.text(75, 5.5, 'Pole', ha='center', va='center', fontsize=8)
    ax.text(75, 7.5, 'Equator', ha='center', va='center', fontsize=8)

    # actual plot:
    p0, = ax.plot(RhoRList, EnergyList, color+'-')
    ax.plot(RhoRListPlusErr, EnergyList, color+'--')
    ax.plot(RhoRListMinusErr, EnergyList, color+'--')

    if old_models is not None:
        plots = [p0]
        names = ['This Model']

        for i in range(len(old_models)):
            name = old_models[i][1]
            model = old_models[i][0]

            # calculate list to plot
            x = []
            y = []
            for j in arange(Emin, Emax, dE):
                y.append(j)
                x.append(model(j))

            p1, = ax.plot(x,y)
            plots.append( p1 )
            names.append( name )

        # make the legend:
        ax.legend(plots, names, fontsize=10, loc=3, ncol=2)

    # set some options:
    ax.set_ylim([0, math.ceil(E0)])
    ax.grid(grid)
    # add labels:
    if units == 'g/cm2':
        ax.set_xlabel(r'$\rho$R (g/cm$^2$)', fontsize=10)
    else:
        ax.set_xlabel(r'$\rho$R (mg/cm$^2$)', fontsize=10)
    ax.set_ylabel(r'Energy (MeV)', fontsize=10)
    if title is not None:
        ax.set_title(r'$\rho$R Model', fontsize=10)

    ax.tick_params(axis='both', labelsize=8)

    #plt.show()
    if filename is not None:
        matplotlib.pyplot.savefig(filename, bbox_inches='tight')


def plot_Rcm_v_Energy(analysis, filename=None, ax=None, backend=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, Eerr=0.13, grid=False, color='k', title=None, figsize=(3.,2.5), rmin=None, rmax=None):
    """Plot rhoR model's curve of Rcm versus energy.

    :param analysis: the rhoR analysis model to plot
    :param filename: (optional) where to save the plot
    :param ax: (optional) existing matplotlib axes to plot into
    :param backend: (optional) matplotlib backend to use
    :param E0: (optional) The initial proton energy in MeV [default=14.7]
    :param dE: (optional) The energy step size in MeV [default=14.7]
    :param Emin: (optional) minimum energy to plot in MeV [default=5]
    :param Emax: (optional) maximum energy to plot in MeV [default=14]
    :param Eerr: (optional) the energy error bar in MeV [default=0.13]. Set to 0 to disable.
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    :param rmin: (optional) Minimum radius to plot [cm]
    :param rmax: (optional) Maximum radius to plot [cm]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    if backend is not None:
        matplotlib.pyplot.switch_backend(backend)

    # lists of things to plot:
    EnergyList = []
    RcmList = []
    RcmListPlusErr = []
    RcmListMinusErr = []
    RcmListPlusErrEnergy = []
    RcmListMinusErrEnergy = []

    # energies:
    for i in arange(Emin, Emax, dE):
        EnergyList.append(i)
        # get result, then add it to the appropriate lists:
        temp = analysis.Calc_Rcm(i, Eerr, ModelErr=True)
        RcmList.append(temp[0] * 1e4)
        RcmListPlusErr.append((temp[0] + temp[1]) * 1e4)
        RcmListMinusErr.append((temp[0] - temp[1]) * 1e4)

        # recalculate using only energy error bar:
        if Eerr != 0:
            temp = analysis.Calc_Rcm(i, Eerr, ModelErr=False)
            RcmListPlusErrEnergy.append((temp[0] + temp[1]) * 1e4)
            RcmListMinusErrEnergy.append((temp[0] - temp[1]) * 1e4)


    # make a plot if necessary, and add curves for the rhoR model
    # and its error bars:
    if ax is None:
        fig = matplotlib.pyplot.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    ax.plot(RcmList, EnergyList, color+'-')
    ax.plot(RcmListPlusErr, EnergyList, color+'--')
    ax.plot(RcmListMinusErr, EnergyList, color+'--')
    if Eerr != 0:
        ax.plot(RcmListPlusErrEnergy, EnergyList, color+':')
        ax.plot(RcmListMinusErrEnergy, EnergyList, color+':')

    # set some options:
    ax.set_ylim([0, math.ceil(E0)])
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=10)
    ax.set_ylabel(r'Energy (MeV)', fontsize=10)
    ax.set_xlim(100,900)
    if title is not None:
        ax.set_title(title, fontsize=10)

    ax.tick_params(axis='both', labelsize=8)
    if rmin is not None and rmax is not None:
        ax.set_xlim(rmin*1e4, rmax*1e4)

    # save if requested
    if filename is not None:
        matplotlib.pyplot.savefig(filename, bbox_inches='tight')


def plot_rhoR_v_Rcm(analysis, filename=None, ax=None, backend=None, Rmin=150e-4, dr=10e-4, grid=False, color='k', title=None, figsize=(3.,2.5), units='mg/cm2', rmin=None, rmax=None):
    """Plot rhoR model's curve versus center-of-mass radius.

    :param analysis: the rhoR analysis model to plot
    :param filename: (optional) where to save the plot
    :param ax: (optional) existing matplotlib axes to plot into
    :param backend: (optional) matplotlib backend to use
    :param Rmin: (optional) the minimum shell CM radius to plot in cm [default=0.015]
    :param dr: (optional) step size to use for Rcm in cm [default=0.001]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    :param units: (optional) either 'mg/cm2' or 'g/cm2'
    :param rmin: (optional) Minimum radius to plot [cm]
    :param rmax: (optional) Maximum radius to plot [cm]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    if backend is not None:
        matplotlib.pyplot.switch_backend(backend)

    # lists of things to plot:
    RcmList = []
    RhoRList = []
    RhoRListPlusErr = []
    RhoRListMinusErr = []
    # start at the inner radius of the shell:
    Rcm = analysis.Ri[1]

    # energies:
    for i in arange(Rmin, Rcm, dr):
        RcmList.append(i * 1e4)
        # get result, then add it to the appropriate lists, for total error bar:
        temp = analysis.rhoR_Total(i)
        RhoRList.append(temp[0])
        RhoRListPlusErr.append(temp[0] + temp[1])
        RhoRListMinusErr.append(temp[0] - temp[1])

    # do correction for units
    if units == 'mg/cm2':
        RhoRList = 1e3*numpy.asarray(RhoRList)
        RhoRListPlusErr = 1e3*numpy.asarray(RhoRListPlusErr)
        RhoRListMinusErr = 1e3*numpy.asarray(RhoRListMinusErr)


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    if ax is None:
        fig = matplotlib.pyplot.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    ax.plot(RcmList, RhoRList, color+'-')
    ax.plot(RcmList, RhoRListPlusErr, color+'--')
    ax.plot(RcmList, RhoRListMinusErr, color+'--')

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=10)
    if units == 'g/cm2':
        ax.set_ylabel(r'$\rho$R (g/cm$^2$)', fontsize=10)
    else:
        ax.set_ylabel(r'$\rho$R (mg/cm$^2$)', fontsize=10)
    if title is not None:
        ax.set_title(title, fontsize=10)

    ax.tick_params(axis='both', labelsize=8)
    if rmin is not None and rmax is not None:
        ax.set_xlim(rmin*1e4, rmax*1e4)

    # save if requested
    if filename is not None:
        matplotlib.pyplot.savefig(filename, bbox_inches='tight')


def plot_profile(analysis, Rcm, filename, xlim=None, ylim=None, figsize=(3.,2.5)):
    """Plot the mass profile for a given center-of-mass radius

    :param analysis: the rhoR analysis model to plot
    :param Rcm: the center of mass radius to use for the plot [cm]
    :param dr: (optional) step size for Rcm in cm [default=0.001]
    :param filename: where to save the plot to
    :param xlim: (optional) Tuple or list with x limits, passed directly to matplotlib [default=None]
    :param ylim: (optional) Tuple or list with x limits, passed directly to matplotlib [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """

    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')

    # get modeled shell thickness:
    Tshell = analysis.Tshell[1]
    Mrem = analysis.Mrem[1]
    Rgas = Rcm - Tshell / 2
    rho_Gas = analysis.model.rho_Gas(Rcm)
    Rshell = Rcm + Tshell / 2
    rho_Shell = analysis.model.rho_Shell(Rcm)

    # data for plotting gas profile:
    Gas_x = [0, Rgas * 1e4]
    Gas_y = [rho_Gas, rho_Gas]
    # data for plotting shell profile:
    Shell_x = [Rgas * 1e4, Rshell * 1e4]
    Shell_y = [rho_Shell, rho_Shell]
    # calculate ablated mass profile:
    Abl_r1, Abl_r2, Abl_r3 = analysis.model.get_Abl_radii(Rcm)
    Abl_x = []
    Abl_y = []
    for x in arange(Abl_r1 + 1e-5, Abl_r3, 5e-4):
        Abl_y.append(analysis.model.rho_Abl(x, Rcm))
        Abl_x.append(x * 1e4)

    # make a plot window:
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    # add plots for three regions:
    ax.plot(Gas_x, Gas_y, 'r-')
    ax.fill_between(Gas_x, Gas_y, [0, 0], color='r')
    ax.plot(Shell_x, Shell_y, 'b-')
    ax.fill_between(Shell_x, Shell_y, [0, 0], color='b')
    ax.plot(Abl_x, Abl_y, 'g-')
    ax.fill_between(Abl_x, Abl_y, zeros(len(Abl_x)), color='g')

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_xlabel(r'Radius ($\mu$m)', fontsize=10)
    ax.set_ylabel(r'$\rho$ (g/cm$^3$)', fontsize=10)
    ax.tick_params(axis='both', labelsize=8)

    #show the plot:
    #plt.show()
    fig.savefig(filename, bbox_inches='tight')

def plot_rhoR_fractions(analysis, filename=None, ax=None, backend=None, Rmin=150e-4, dr=10e-4, grid=False, title=None, legend=True, normalize=False, figsize=(3.,2.5), mix=True, units='mg/cm2', rmin=None, rmax=None):
    """Plot rhoR model's fractional composition (fuel, shell, abl mass) vs Rcm

    :param analysis: the rhoR analysis model to plot
    :param filename: (optional) where to save the plot
    :param ax: (optional) existing matplotlib axes to plot into
    :param backend: (optional) matplotlib backend to use
    :param Rmin: (optional) the minimum shell CM radius to plot in cm [default=0.015]
    :param dr: (optional) step size for Rcm in cm [default=0.001]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param legend: (optional) Whether to add a legend to the plot [default=True]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    :param mix: (optional) Whether to plot the mix [default=True]
    :param units: (optional) either 'mg/cm2' or 'g/cm2' [default=mg/cm2]
    :param rmin: (optional) Minimum radius to plot [cm]
    :param rmax: (optional) Maximum radius to plot [cm]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    if backend is not None:
        matplotlib.pyplot.switch_backend(backend)

    # lists of things to plot:
    RcmList = []
    FuelList = []
    MixList = []
    ShellList = []
    AblList = []
    # start at the inner radius of the shell:
    Rcm = analysis.Ri[1]

    # energies:
    for i in arange(Rmin, Rcm, dr):
        RcmList.append(i * 1e4)
        # get the components at this CM radius:
        FuelList.append(analysis.model.rhoR_Gas(i))
        MixList.append(analysis.model.rhoR_Mix(i))
        ShellList.append(analysis.model.rhoR_Shell(i))
        AblList.append(analysis.model.rhoR_Abl(i))

    # convert to numpy:
    RcmList = numpy.asarray(RcmList)
    FuelList = numpy.asarray(FuelList)
    MixList = numpy.asarray(MixList)
    ShellList = numpy.asarray(ShellList)
    AblList = numpy.asarray(AblList)

    if units == 'mg/cm2':
        FuelList *= 1e3
        MixList *= 1e3
        ShellList *= 1e3
        AblList *= 1e3

    # optionally normalize the plot to the total rhoR
    if normalize:
        total = FuelList + MixList + ShellList + AblList
        FuelList = FuelList / total
        MixList = MixList / total
        ShellList = ShellList / total
        AblList = AblList / total

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    if ax is None:
        fig = matplotlib.pyplot.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    ax.plot(RcmList, FuelList, 'r-', label='Gas')
    if mix:
        ax.plot(RcmList, MixList, 'r--', label='Mix')
    ax.plot(RcmList, ShellList, 'b-', label='Shell')
    ax.plot(RcmList, AblList, 'g-', label='Ablated')
    if not normalize:
        ax.plot(RcmList, (FuelList+MixList+ShellList+AblList), 'k-', label='Total')

    # for normalized plots, set y limits, and move the legend:
    if normalize:
        ax.set_ylim([0,1])
        loc=9
    else:
        loc=1
    if legend:
        if normalize and not mix:
            ax.legend(loc=loc, fontsize=8, ncol=3)
        else:
            ax.legend(loc=loc, fontsize=8, ncol=2)

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=10)
    if units == 'g/cm2':
        ax.set_ylabel(r'$\rho$R (g/cm$^2$)', fontsize=10)
    else:
        ax.set_ylabel(r'$\rho$R (mg/cm$^2$)', fontsize=10)
    if normalize:
        ax.set_ylabel(r'Fractional $\rho$R', fontsize=10)
    if title is not None:
        ax.set_title(title, fontsize=10)
    if rmin is not None and rmax is not None:
        ax.set_xlim(rmin*1e4, rmax*1e4)

    # save if requested:
    if filename is not None:
        matplotlib.pyplot.savefig(filename, bbox_inches='tight')



def compare_rhoR_v_Energy(analyses, filename, names=None, styles=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, title=None, figsize=(3.,2.5)):
    """Compare several rhoR models by plotting rhoR vs energy for them.

    :param analysis: the rhoR model to plot, several rhoR_Model objects in a list
    :param filename: where to save the plot
    :param names: Labels for the models, legend is only generated if names is not None
    :param styles: Particlar styles to use for each analysis, optional
    :param E0: (optional) The initial proton energy in MeV [default=14.7]
    :param dE: (optional) The energy step size in MeV [default=14.7]
    :param Emin: (optional) minimum energy to plot in MeV [default=5]
    :param Emax: (optional) maximum energy to plot in MeV [default=14]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    assert isinstance(analyses, list)
    for x in analyses:
        assert isinstance(x, rhoR_Model)

    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')

    plot_x = []
    plot_y = []

    # iterate over models:
    for analysis in analyses:
        # lists of things to plot:
        EnergyList = []
        RhoRList = []

        # energies:
        for i in arange(Emin, Emax, dE):
            EnergyList.append(i)
            # get result, then add it to the appropriate lists:
            temp = analysis.Calc_rhoR(i)
            RhoRList.append(temp[0])

        plot_x.append(RhoRList)
        plot_y.append(EnergyList)

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    for i in range(len(plot_x)):
        opts = []
        if styles is not None:
            opts.append(styles[i])
        ax.plot(plot_x[i], plot_y[i], *opts)
    if names is not None:
        ax.legend(names, fontsize=10)

    # set some options:
    ax.set_ylim([0, math.ceil(E0)])
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$\rho$R (g/cm$^2$)', fontsize=12)
    ax.set_ylabel(r'Energy (MeV)', fontsize=12)
    if title is not None:
        ax.set_title(title)

    fig.savefig(filename, bbox_inches='tight')


def compare_Rcm_v_rhoR(analyses, filename, names=None, styles=None, Rmin=150e-4, dr=10e-4, grid=False, title=None, figsize=(3.,2.5)):
    """Compare several rhoR models by plotting Rcm vs rhoR for them.

    :param analysis: the rhoR model to plot, several rhoR_Model objects in a list
    :param filename: where to save the plot
    :param names: Labels for the models, legend is only generated if names is not None
    :param styles: Particlar styles to use for each analysis, optional
    :param Rmin: (optional) the minimum shell CM radius to plot in cm [default=0.015]
    :param dr: (optional) step size to use for Rcm in cm [default=0.001]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    assert isinstance(analyses, list)
    for x in analyses:
        assert isinstance(x, rhoR_Model)

    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')

    plot_x = []
    plot_y = []

    # iterate over models:
    for analysis in analyses:
        # lists of things to plot:
        RcmList = []
        RhoRList = []

        # iterate over Rcm
        for i in arange(Rmin, analysis.Ri, dr):
            RcmList.append(i * 1e4)
            # get result, then add it to the appropriate lists, for total error bar:
            temp = analysis.rhoR_Total(i)
            RhoRList.append(temp)

        plot_x.append(RcmList)
        plot_y.append(RhoRList)

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    for i in range(len(plot_x)):
        opts = []
        if styles is not None:
            opts.append(styles[i])
        ax.plot(plot_x[i], plot_y[i], *opts)
    if names is not None:
        ax.legend(names, fontsize=10)

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'R$_{cm}$ ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'$\rho$R (g/cm$^2$)', fontsize=12)
    if title is not None:
        ax.set_title(title, fontsize=12)

    fig.savefig(filename, bbox_inches='tight')


def compare_Rcm_v_Energy(analyses, filename, names=None, styles=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, title=None, figsize=(3.,2.5)):
    """Compare several rhoR models by plotting Rcm vs energy for them.

    :param analysis: the rhoR model to plot, several rhoR_Model objects in a list
    :param filename: where to save the plot
    :param names: Labels for the models, legend is only generated if names is not None
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    assert isinstance(analyses, list)
    for x in analyses:
        assert isinstance(x, rhoR_Model)

    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')

    plot_x = []
    plot_y = []

    # iterate over models:
    for analysis in analyses:
        # lists of things to plot:
        EnergyList = []
        RcmList = []

        # energies:
        for i in arange(Emin, Emax, dE):
            # get result, then add it to the appropriate lists:
            temp = analysis.Calc_rhoR(i)
            RcmList.append(temp[1]*1.e4)
            EnergyList.append(i)

        plot_x.append(RcmList)
        plot_y.append(EnergyList)

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    for i in range(len(plot_x)):
        opts = []
        if styles is not None:
            opts.append(styles[i])
        ax.plot(plot_x[i], plot_y[i], *opts)
    if names is not None:
        ax.legend(names, loc=4, fontsize=10)

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'R$_{cm}$ ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'E (MeV)', fontsize=12)
    if title is not None:
        ax.set_title(title, fontsize=12)

    fig.savefig(filename, bbox_inches='tight')


def plot_stoppow(analysis, Rcm, filename, grid=False, legend=True, title=None, figsize=(3.,2.5), mix=True, units='mg/cm2'):
    """Plot rhoR model's stopping power in the various components vs proton energy for a given Rcm

    :param analysis: the rhoR model to plot
    :param Rcm: the center-of-mass radius to use [cm]
    :param filename: where to save the plot to
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param legend: (optional) Whether to display a legend [default=True]
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    :param mix: (optional) Whether to plot the mix [default=True]
    :param units: (optional) either 'mg/cm2' or 'g/cm2' [default=mg/cm2]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    if matplotlib.get_backend() != 'agg':
        matplotlib.pyplot.switch_backend('Agg')

    # Set up gas/mix stopping power:
    ni_gas, ne_gas = analysis.model.n_Gas(Rcm)
    ni_mix, ne_mix = analysis.model.n_Mix(Rcm)
    if mix:
        nf = DoubleVector(3+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
        mf = DoubleVector(3+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
        Zf = DoubleVector(3+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
        Tf = DoubleVector(3+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
        nf[0] = ne_gas + ne_mix
        nf[1] = ni_gas * analysis.model.fD
        nf[2] = ni_gas * analysis.model.f3He
        for i in range(len(analysis.model.__shell_F__[analysis.model.shell_mat])):
            nf[3+i] = ni_mix * analysis.model.__shell_F__[analysis.model.shell_mat][i]
        mf[0] = 1 / 1836.
        mf[1] = 2.
        mf[2] = 3.
        for i in range(len(analysis.model.__shell_F__[analysis.model.shell_mat])):
            mf[3+i] = analysis.model.__shell_A__[analysis.model.shell_mat][i]
        Zf[0] = -1
        Zf[1] = 1
        Zf[2] = 2
        for i in range(len(Zf)-3):
            Zf[3+i] = analysis.model.__shell_Z__[analysis.model.shell_mat][i]
        Tf[0] = analysis.model.Te_Gas
        Tf[1] = analysis.model.Te_Gas
        Tf[2] = analysis.model.Te_Gas
        for i in range(len(Tf)-3):
            Tf[3+i] = analysis.model.Te_Mix
    else:
        nf = DoubleVector(3)
        mf = DoubleVector(3)
        Zf = DoubleVector(3)
        Tf = DoubleVector(3)
        nf[0] = ne_gas
        nf[1] = ni_gas * analysis.model.fD
        nf[2] = ni_gas * analysis.model.f3He
        mf[0] = 1 / 1836.
        mf[1] = 2.
        mf[2] = 3.
        Zf[0] = -1
        Zf[1] = 1
        Zf[2] = 2
        Tf[0] = analysis.model.Te_Gas
        Tf[1] = analysis.model.Te_Gas
        Tf[2] = analysis.model.Te_Gas
    # if any densities are zero, it is problematic (no mix does this)
    # add 1 particle per cc minimum:
    for i in range(len(nf)):
        if nf[i] <= 0:
            nf[i] = 1
    dEdx_gasmix = StopPow_LP(1.008, 1, mf, Zf, Tf, nf)
    dEdx_gasmix.set_mode(StopPow.MODE_RHOR)

    # Set up stopping power in the shell:
    nf = DoubleVector(1+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
    mf = DoubleVector(1+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
    Zf = DoubleVector(1+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
    Tf = DoubleVector(1+len(analysis.model.__shell_A__[analysis.model.shell_mat]))
    ni, ne = analysis.model.n_Shell(Rcm)
    nf[0] = ne
    for i in range(len(analysis.model.__shell_F__[analysis.model.shell_mat])):
        nf[1+i] = ni * analysis.model.__shell_F__[analysis.model.shell_mat][i]
    mf[0] = 1/1836.
    for i in range(len(analysis.model.__shell_A__[analysis.model.shell_mat])):
        mf[1+i] = analysis.model.__shell_A__[analysis.model.shell_mat][i]
    Zf[0] = -1
    for i in range(len(analysis.model.__shell_Z__[analysis.model.shell_mat])):
        Zf[1+i] = analysis.model.__shell_Z__[analysis.model.shell_mat][i]
    Tf[0] = analysis.model.Te_Shell
    for i in range(len(analysis.model.__shell_Z__[analysis.model.shell_mat])+1):
        Tf[i] = analysis.model.Te_Shell
    dEdx_shell = StopPow_LP(1.008, 1, mf, Zf, Tf, nf)
    dEdx_shell.set_mode(StopPow.MODE_RHOR)

    # lists of things to plot:
    EList = numpy.arange(0.1, 15., 0.1)
    FuelMixList = []
    ShellList = []
    AblList = []

    # energies:
    for Ei in EList:
        FuelMixList.append(dEdx_gasmix.dEdx(Ei))
        ShellList.append(dEdx_shell.dEdx(Ei))
        AblList.append(analysis.model.dEdr_Abl(Ei, 3*Rcm, Rcm)/(1e3*analysis.model.rho_Abl(3*Rcm,Rcm)))

    # convert to numpy:
    FuelMixList = numpy.asarray(FuelMixList)
    ShellList = numpy.asarray(ShellList)
    AblList = numpy.asarray(AblList)

    if units == 'g/cm2':
        FuelMixList *= 1e3
        ShellList *= 1e3
        AblList *= 1e3

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    ax.plot(EList, FuelMixList, 'r-', label='Fuel')
    ax.plot(EList, ShellList, 'b-', label='Shell')
    ax.plot(EList, AblList, 'g-', label='Ablated')

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$E_{p}$ (MeV)', fontsize=10)
    if units == 'g/cm2':
        ax.set_ylabel(r'$dE/d\rho$R [MeV/(g/cm$^2$)]', fontsize=10)
    else:
        ax.set_ylabel(r'$dE/d\rho$R [MeV/(mg/cm$^2$)]', fontsize=10)
    if title is not None:
        ax.set_title(title, fontsize=10)
    if legend:
        ax.legend(loc=4, fontsize=8)
    # Set limits for plot:
    minY = numpy.min([numpy.min(ShellList), numpy.min(AblList)])
    ax.set_ylim(minY*1.05, 0)

    #plt.show()
    fig.savefig(filename, bbox_inches='tight')