# Functions for making plots of the rhoR model

from Analysis.rhoR_Analysis import *
from numpy import arange, zeros
import os
import matplotlib

__author__ = 'Alex Zylstra'

def plot_rhoR_v_Energy(analysis, filename):
    """Plot rhoR model's curve versus energy.
    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot
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
    dE = 0.5 #step for plot points
    E0 = 14.7 #initial protons
    Emax = 14.0 # Max plot energy
    Emin = 5.0 # min plot energy
    for i in arange(Emin, Emax, dE):
        EnergyList.append(i)
        # get result, then add it to the appropriate lists:
        temp = analysis.Calc_rhoR(i)
        RhoRList.append(temp[0])
        RhoRListPlusErr.append(temp[0] + temp[2])
        RhoRListMinusErr.append(temp[0] - temp[2])


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(RhoRList, EnergyList, 'b-')
    ax.plot(RhoRListPlusErr, EnergyList, 'b--')
    ax.plot(RhoRListMinusErr, EnergyList, 'b--')

    # set some options:
    ax.set_ylim([0, 15])
    ax.grid(True)
    # add labels:
    ax.set_xlabel(r'$\rho$R (g/cm$^2$)')
    ax.set_ylabel(r'Energy (MeV)')
    #ax.set_title(r'$\rho$R Model')

    #plt.show()
    fig.savefig(filename)


def plot_Rcm_v_Energy(analysis, filename):
    """Plot rhoR model's curve of Rcm versus energy.
    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot to
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
    dE = 0.5 #step for plot points
    E0 = 14.7 #initial protons
    Emax = 14.0 # Max plot energy
    Emin = 5.0 # min plot energy
    Eerr = 0.13
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
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(RcmList, EnergyList, 'b-')
    ax.plot(RcmListPlusErr, EnergyList, 'b--')
    ax.plot(RcmListMinusErr, EnergyList, 'b--')
    ax.plot(RcmListPlusErrEnergy, EnergyList, 'b:')
    ax.plot(RcmListMinusErrEnergy, EnergyList, 'b:')

    # set some options:
    ax.set_ylim([0, 15])
    ax.grid(True)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)')
    ax.set_ylabel(r'Energy (MeV)')
    #ax.set_title(r'$\rho$R Model')

    #plt.show()
    fig.savefig(filename)


def plot_rhoR_v_Rcm(analysis, filename):
    """Plot rhoR model's curve versus center-of-mass radius.
    :param analysis: the rhoR analysis model to plot
    :param filename: where to save the plot to
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
    dr = 10e-4 #step for plot points
    Rmin = 150e-4 # Minimum radius to plot
    for i in arange(Rmin, Rcm, dr):
        RcmList.append(i * 1e4)
        # get result, then add it to the appropriate lists, for total error bar:
        temp = analysis.rhoR_Total(i)
        RhoRList.append(temp[0])
        RhoRListPlusErr.append(temp[0] + temp[1])
        RhoRListMinusErr.append(temp[0] - temp[1])


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(RcmList, RhoRList, 'b-')
    ax.plot(RcmList, RhoRListPlusErr, 'b--')
    ax.plot(RcmList, RhoRListMinusErr, 'b--')

    # set some options:
    #ax.set_ylim([0,Rcm])
    ax.grid(True)
    # add labels:
    ax.set_xlabel(r'$R_{cm}$ ($\mu$m)')
    ax.set_ylabel(r'$\rho$R (g/cm$^2$)')
    #ax.set_title(r'$\rho$R Model')

    #plt.show()
    fig.savefig(filename)


def plot_profile(analysis, Rcm, filename):
    """Plot the mass profile for a given center-of-mass radius
    :param analysis: the rhoR analysis model to plot
    :param Rcm: the center of mass radius to use for the plot [cm]
    :param filename: where to save the plot to
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
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # add plots for three regions:
    ax.plot(Gas_x, Gas_y, 'r-')
    ax.fill_between(Gas_x, Gas_y, [0, 0], color='r')
    ax.plot(Shell_x, Shell_y, 'b-')
    ax.fill_between(Shell_x, Shell_y, [0, 0], color='b')
    ax.plot(Abl_x, Abl_y, 'g-')
    ax.fill_between(Abl_x, Abl_y, zeros(len(Abl_x)), color='g')

    ax.set_ylim([0, int(1.1 * rho_Shell)])
    ax.set_ylim([0, 25])
    #plt.yscale('log')
    ax.set_xlabel(r'Radius ($\mu$m)')
    ax.set_ylabel(r'$\rho$ (g/cm$^3$)')

    #show the plot:
    #plt.show()
    fig.savefig(filename)


def compare_rhoR_v_Energy(analyses, filename, names=None):
    """Compare several rhoR models by plotting rhoR vs energy for them.
    :param analysis: the rhoR model to plot, several rhoR_Model objects in a list
    :param filename: where to save the plot
    :param names: Labels for the models, legend is only generated if names is not None
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
        dE = 0.2 #step for plot points
        E0 = 14.7 #initial protons
        Emax = 14.0 # Max plot energy
        Emin = 5.0 # min plot energy
        for i in arange(Emin, Emax, dE):
            EnergyList.append(i)
            # get result, then add it to the appropriate lists:
            temp = analysis.Calc_rhoR(i)
            RhoRList.append(temp[0])

        plot_x.append(RhoRList)
        plot_y.append(EnergyList)


    # make a plot, and add curves for the rhoR model
    # and its error bars:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in range(len(plot_x)):
        ax.plot(plot_x[i], plot_y[i])
    if names is not None:
        ax.legend(names)

    # set some options:
    ax.set_ylim([0, 15])
    ax.grid(True)
    # add labels:
    ax.set_xlabel(r'$\rho$R (g/cm$^2$)')
    ax.set_ylabel(r'Energy (MeV)')
    #ax.set_title(r'$\rho$R Model')

    #plt.show()
    fig.savefig(filename)