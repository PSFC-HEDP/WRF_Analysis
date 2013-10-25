# Functions for making plots of the rhoR model

import math

from numpy import arange, zeros
from NIF_WRF.Analysis.rhoR_Model import rhoR_Model
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis


__author__ = 'Alex Zylstra'

def plot_rhoR_v_Energy(analysis, filename, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, color='k', title=None, old_models=None, figsize=(4,3)):
    """Plot rhoR model's curve versus energy.

    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot
    :param E0: (optional) The initial proton energy in MeV [default=14.7]
    :param dE: (optional) The energy step size in MeV [default=14.7]
    :param Emin: (optional) minimum energy to plot in MeV [default=5]
    :param Emax: (optional) maximum energy to plot in MeV [default=14]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param old_models: (optional) functional forms of previous models to overplot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

    # lists of things to plot:
    EnergyList = []
    RhoRList = []
    RhoRListPlusErr = []
    RhoRListMinusErr = []

    # energies:
    for i in arange(Emin, Emax, dE):
        EnergyList.append(i)
        # get result, then add it to the appropriate lists:
        temp = analysis.Calc_rhoR(i)
        RhoRList.append(temp[0])
        RhoRListPlusErr.append(temp[0] + temp[2])
        RhoRListMinusErr.append(temp[0] - temp[2])

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
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
    ax.set_xlabel(r'$\rho$R (g/cm$^2$)', fontsize=12)
    ax.set_ylabel(r'Energy (MeV)', fontsize=12)
    if title is not None:
        ax.set_title(r'$\rho$R Model', fontsize=12)

    #plt.show()
    fig.savefig(filename, bbox_inches='tight')


def plot_Rcm_v_Energy(analysis, filename, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, Eerr=0.13, grid=False, color='k', title=None, figsize=(4,3)):
    """Plot rhoR model's curve of Rcm versus energy.

    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot to
    :param E0: (optional) The initial proton energy in MeV [default=14.7]
    :param dE: (optional) The energy step size in MeV [default=14.7]
    :param Emin: (optional) minimum energy to plot in MeV [default=5]
    :param Emax: (optional) maximum energy to plot in MeV [default=14]
    :param Eerr: (optional) the energy error bar in MeV [default=0.13]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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
        temp = analysis.Calc_Rcm(i, Eerr, ModelErr=False)
        RcmListPlusErrEnergy.append((temp[0] + temp[1]) * 1e4)
        RcmListMinusErrEnergy.append((temp[0] - temp[1]) * 1e4)


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.plot(RcmList, EnergyList, color+'-')
    ax.plot(RcmListPlusErr, EnergyList, color+'--')
    ax.plot(RcmListMinusErr, EnergyList, color+'--')
    ax.plot(RcmListPlusErrEnergy, EnergyList, color+':')
    ax.plot(RcmListMinusErrEnergy, EnergyList, color+':')

    # set some options:
    ax.set_ylim([0, math.ceil(E0)])
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'Energy (MeV)', fontsize=12)
    if title is not None:
        ax.set_title(title, fontsize=12)

    #plt.show()
    fig.savefig(filename, bbox_inches='tight')


def plot_rhoR_v_Rcm(analysis, filename, Rmin=150e-4, dr=10e-4, grid=False, color='k', title=None, figsize=(4,3)):
    """Plot rhoR model's curve versus center-of-mass radius.

    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot to
    :param Rmin: (optional) the minimum shell CM radius to plot in cm [default=0.015]
    :param dr: (optional) step size to use for Rcm in cm [default=0.001]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.plot(RcmList, RhoRList, color+'-')
    ax.plot(RcmList, RhoRListPlusErr, color+'--')
    ax.plot(RcmList, RhoRListMinusErr, color+'--')

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'$\rho$R (g/cm$^2$)', fontsize=12)
    if title is not None:
        ax.set_title(title, fontsize=12)

    #plt.show()
    fig.savefig(filename, bbox_inches='tight')


def plot_profile(analysis, Rcm, filename, xlim=None, ylim=None, figsize=(4,3)):
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

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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
    fig = plt.figure(figsize=figsize)
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
    ax.set_xlabel(r'Radius ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'$\rho$ (g/cm$^3$)', fontsize=12)

    #show the plot:
    #plt.show()
    fig.savefig(filename, bbox_inches='tight')

def plot_rhoR_fractions(analysis, filename, Rmin=150e-4, dr=10e-4, grid=False, title=None, normalize=False, figsize=(4,3)):
    """Plot rhoR model's fractional composition (fuel, shell, abl mass) vs Rcm

    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot to
    :param Rmin: (optional) the minimum shell CM radius to plot in cm [default=0.015]
    :param dr: (optional) step size for Rcm in cm [default=0.001]
    :param grid: (optional) whether to show a grid on the plot [default=False]
    :param color: (optional) matplotlib color character [default='k']
    :param title: (optional) Title to display over the plot [default=None]
    :param figsize: (optional) figsize parameter to pass to matplotlib [default=(4,3)]
    """
    #sanity check:
    if not isinstance(analysis, rhoR_Analysis):
        return

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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

    # optionally normalize the plot to the total rhoR
    if normalize:
        for i in range(len(RcmList)):
            total = FuelList[i] + MixList[i] + ShellList[i] + AblList[i]
            FuelList[i] = FuelList[i] / total
            MixList[i] = MixList[i] / total
            ShellList[i] = ShellList[i] / total
            AblList[i] = AblList[i] / total

    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.plot(RcmList, FuelList, 'r-')
    ax.plot(RcmList, MixList, 'r--')
    ax.plot(RcmList, ShellList, 'b-')
    ax.plot(RcmList, AblList, 'g-')

    # for normalized plots, set y limits, and move the legend:
    if normalize:
        ax.set_ylim([0,1])
        loc=9
    else:
        loc=1
    ax.legend(['Fuel','Mix','Shell','Ablated'], loc=loc, fontsize=10, ncol=2)

    # set some options:
    ax.grid(grid)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)', fontsize=12)
    ax.set_ylabel(r'$\rho$R (g/cm$^2$)', fontsize=12)
    if normalize:
        ax.set_ylabel(r'Fractional $\rho$R', fontsize=12)
    if title is not None:
        ax.set_title(title, fontsize=12)

    #plt.show()
    fig.savefig(filename, bbox_inches='tight')



def compare_rhoR_v_Energy(analyses, filename, names=None, styles=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, title=None, figsize=(4,3)):
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

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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
    fig = plt.figure(figsize=figsize)
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


def compare_Rcm_v_rhoR(analyses, filename, names=None, styles=None, Rmin=150e-4, dr=10e-4, grid=False, title=None, figsize=(4,3)):
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

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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
    fig = plt.figure(figsize=figsize)
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


def compare_Rcm_v_Energy(analyses, filename, names=None, styles=None, E0=14.7, dE=0.25, Emin=5.0, Emax=14.0, grid=False, title=None, figsize=(4,3)):
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

    # import matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
    if matplotlib.get_backend() != 'agg':
        plt.switch_backend('Agg')

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
    fig = plt.figure(figsize=figsize)
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