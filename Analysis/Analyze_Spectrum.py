# Implement a function which performs analysis of a NIF WRF spectrum
# to get rhoR, yield, and so on with error bars.

import os
from datetime import *
import csv
import math
from Analysis.rhoR_Analysis import *
from Analysis.rhoR_Model_plots import *
from util.GaussFit import *
from Analysis.Hohlraum import *
from Analysis.SlideGenerator import *

__author__ = 'Alex Zylstra'

def diff(a, b):
    """Calculate the difference between a and b.
    :param a: The first number
    :param b: The second number
    :returns: The difference between a and b as a positive number
    """
    return abs(max(a, b) - min(a, b))

def myprint(text, ProgressBar=None):
    """Handle output for the analysis. Either prints to command line (if ProgressBar is None) or updates the bar.
    :param text: The text to either display or print
    :param ProgressBar: The ProgressBar to use for GUI mode
    """
    # CLI mode:
    if ProgressBar is None:
        print(text)            
    # GUI mode:
    #else:
        #ProgressBar.set_text(text)
        
def mytime(time, inc, ProgressBar=None):
    """Display a time elapsed on CLI or update ProgressBar.
    :param inc: How much to increment the progress bar
    :param time: If in CLI mode, displays a time elapsed in seconds
    :param ProgressBar: The ProgressBar to use for GUI mode
    """
    # CLI:
    if ProgressBar is None:
        print('{:.1f}'.format(time) + "s elapsed")
    else:
        current = ProgressBar.counter.get()
        ProgressBar.counter.set(current+inc)

# noinspection PyListCreation,PyListCreation,PyUnusedLocal
def Analyze_Spectrum(data, spectrum_random, spectrum_systematic, LOS, hohl_wall=None, name="", summary="", plots=True,
                     verbose=True, rhoR_plots=False, OutputDir=None, Nxy=None, ProgressBar=None, ShowSlide=False):
    """Analyze a NIF WRF spectrum.
    :param data: The raw spectral data, n x 3 array where first column is energy (MeV), second column is yield/MeV, and third column is uncertainty in yield/MeV
    :param spectrum_random: Random 1 sigma error bars in spectrum as [dY,dE,dsigma]
    :param spectrum_systematic: Systematic total error bars in spectrum as [dY,dE,dsigma]
    :param LOS: The line of sight of this wedge, and [theta,phi]
    :param hohl_wall: Hohlraum wall info, requires a 2-D list with columns [ Drawing , Name , Layer # , Material , r (cm) , z (cm) ]
    :param name: (optional) Name of this wedge [default=""]
    :param summary: (optional) Any summary info to display [default=""]
    :param plots: (optional) Whether to make plots [default=True]
    :param verbose: (optional) Whether to print out summary info [default=True]
    :param rhoR_plots: (optional) Whether to generate rhoR model plots as well [default=False]
    :param OutputDir: (optional) Where to put the output files [default = pwd + 'AnalysisOutputs']
    :param Nxy: (optional) image data to display as N(x,y) {default=None}
    :param ProgressBar: (optional) a progress bar of type WRF_Progress_Dialog to use for updates [default=None, uses CLI]
    :param ShowSlide: (optional) set to True to display the summary slide after this method completes [default=False]
    :author: Alex Zylstra
    :date: 2013/08/06
    """
    # sanity checking on the inputs:
    assert isinstance(data, list) or isinstance(data, numpy.ndarray)
    assert isinstance(spectrum_random, list) or isinstance(spectrum_random, numpy.ndarray)
    assert isinstance(spectrum_systematic, list) or isinstance(spectrum_systematic, numpy.ndarray)
    assert isinstance(LOS, list) or isinstance(LOS, numpy.ndarray)

    # for the progress bar:
    if ProgressBar is not None:
        from GUI.WRF_Progress_Dialog import WRF_Progress_Dialog
        assert isinstance(ProgressBar, WRF_Progress_Dialog)

    # set up the output directory:
    if OutputDir is None:  # default case
        path = os.path.dirname(__file__)
        OutputDir = os.path.join(path, 'AnalysisOutputs')
    # check to see if OutputDir exists:
    if not os.path.isdir(OutputDir):
        # create it:
        os.makedirs(OutputDir, exist_ok=True)

    # set up a return dict
    results = dict({})

    # if we are in verbose mode, then we spit out data to a file:
    log_file = csv.writer(open(os.path.join(OutputDir, name + '_Analysis.csv'), 'w'))

    # ----------------------------
    # 		Hohlraum Correction
    # ----------------------------
    # if no wall info is passed, assume the correction
    # is not needed:
    if hohl_wall is not None:
        t1 = datetime.now()
        myprint(name + ' hohlraum correction...', ProgressBar=ProgressBar)

        hohl = Hohlraum(data,
                        wall=hohl_wall,
                        angles=LOS)

        # get corrected spectrum:
        corr_data = hohl.get_data_corr()
        # get hohlraum uncertainty:
        unc_hohl = hohl.get_unc()

        if verbose:
            log_file.writerow(['=== Hohlraum Analysis ==='])
            log_file.writerow(['Raw Energy (MeV)', hohl.get_fit_raw()[1]])
            log_file.writerow(['Corr Energy (MeV)', hohl.get_fit_corr()[1]])
            log_file.writerow(['Au Thickness (um)', hohl.Au, '+/-', hohl.d_Au])
            log_file.writerow(['DU Thickness (um)', hohl.DU, '+/-', hohl.d_DU])
            log_file.writerow(['Al Thickness (um)', hohl.Al, '+/-', hohl.d_Al])
            log_file.writerow(['Uncertainties due to hohlraum correction:'])
            log_file.writerow(['Qty', '- err', '+ err'])
            log_file.writerow(['Yield', unc_hohl[0][0], unc_hohl[0][1]])
            log_file.writerow(['Energy (MeV)', unc_hohl[1][0], unc_hohl[1][1]])
            log_file.writerow(['Sigma (MeV)', unc_hohl[2][0], unc_hohl[2][1]])

        if plots:
            # make plot of raw and corrected spectra:
            hohl_plot1_fname = os.path.join(OutputDir, name + '_HohlCorr.eps')
            hohl.plot_file(hohl_plot1_fname)
            # make figure showing hohlraum profile:
            hohl_plot2_fname = os.path.join(OutputDir, name + '_HohlProfile.eps')
            hohl.plot_hohlraum_file(hohl_plot2_fname)

        t2 = datetime.now()
        mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)
    else:
        corr_data = data

    # add info to the return dict
    results['Au'] = hohl.Au
    results['Au_unc'] = hohl.d_Au
    results['DU'] = hohl.DU
    results['DU_unc'] = hohl.d_DU
    results['Al'] = hohl.Al
    results['Al_unc'] = hohl.d_Al

    results['Hohl_Y_posunc'] = unc_hohl[0][0]
    results['Hohl_Y_negunc'] = unc_hohl[0][1]
    results['Hohl_E_posunc'] = unc_hohl[1][0]
    results['Hohl_E_negunc'] = unc_hohl[1][1]
    results['Hohl_sigma_posunc'] = unc_hohl[2][0]
    results['Hohl_sigma_negunc'] = unc_hohl[2][1]


    # -----------------------------
    # 		Energy analysis
    # -----------------------------
    t1 = datetime.now()
    myprint(name + ' energy analysis...', ProgressBar=ProgressBar)
    # First, we need to perform a Gaussian fit to both raw and corrected data:
    FitObjRaw = GaussFit(data, name=name)
    FitObj = GaussFit(corr_data, name=name)
    # get the fit and uncertainty:
    fit = FitObj.get_fit()
    fit_raw = FitObjRaw.get_fit()
    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    t1 = datetime.now()
    myprint(name + ' energy error analysis...', ProgressBar=ProgressBar)
    unc_fit = FitObj.chi2_fit_unc()
    unc_fit_raw = FitObjRaw.chi2_fit_unc()

    # make a plot of the fit:
    if plots:
        fit_plot_fname = os.path.join(OutputDir, name + '_GaussFit.eps')
        FitObj.plot_file(fit_plot_fname)

    # calculate total error bars for yield, energy, sigma:
    yield_random = math.sqrt(spectrum_random[0] ** 2 + 0.25 * diff(unc_fit[0][0], unc_fit[0][1]) ** 2)
    yield_systematic = spectrum_systematic[0]
    energy_random = math.sqrt(spectrum_random[1] ** 2 + 0.25 * diff(unc_fit[1][0], unc_fit[1][1]) ** 2)
    energy_systematic = spectrum_systematic[1]
    sigma_random = math.sqrt(spectrum_random[2] ** 2 + 0.25 * diff(unc_fit[2][0], unc_fit[2][1]) ** 2)
    sigma_systematic = spectrum_systematic[2]

    if verbose:
        log_file.writerow(['=== Spectrum Analysis ==='])
        log_file.writerow(['Quantity', 'Value', 'Random Unc', 'Sys Unc'])
        log_file.writerow(['Yield', fit[0], yield_random, yield_systematic])
        log_file.writerow(['Energy (MeV)', fit[1], energy_random, energy_systematic])
        log_file.writerow(['Sigma (MeV)', fit[2], sigma_random, sigma_systematic])

    # add to the return dict:
    results['E_raw'] = fit_raw[1]
    results['E_raw_ran_unc'] = spectrum_random[1]
    results['E_raw_sys_unc'] = spectrum_systematic[1]
    results['Yield'] = fit[0]
    results['Yield_ran_unc'] = yield_random
    results['Yield_sys_unc'] = yield_systematic
    results['Energy'] = fit[1]
    results['Energy_ran_unc'] = energy_random
    results['Energy_sys_unc'] = energy_systematic
    results['Sigma'] = fit[2]
    results['Sigma_ran_unc'] = sigma_random
    results['Sigma_sys_unc'] = sigma_systematic

    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    # -----------------------------
    # 		rhoR analysis
    # -----------------------------
    t1 = datetime.now()
    myprint(name + ' rhoR analysis...', ProgressBar=ProgressBar)
    # set up the rhoR analysis:
    model = rhoR_Analysis()
    temp = model.Calc_rhoR(fit[1], breakout=True)
    rhoR = temp[0]
    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    # error analysis for rR:
    t1 = datetime.now()
    myprint(name + ' rhoR error analysis...', ProgressBar=ProgressBar)
    rhoR_model_random = 0
    rhoR_model_systematic = temp[2][0]

    # error bars propagated from energy:
    temp_plus = model.Calc_rhoR(fit[1] + energy_random)
    temp_minus = model.Calc_rhoR(fit[1] - energy_random)
    rhoR_energy_random = diff(temp_plus[0], temp_minus[0]) / 2
    temp_plus = model.Calc_rhoR(fit[1] + energy_systematic)
    temp_minus = model.Calc_rhoR(fit[1] - energy_systematic)
    rhoR_energy_systematic = diff(temp_plus[0], temp_minus[0]) / 2

    # calculate total rhoR error bar:
    rhoR_random = math.sqrt(rhoR_model_random ** 2 + rhoR_energy_random ** 2)
    rhoR_systematic = math.sqrt(rhoR_model_systematic ** 2 + rhoR_energy_systematic ** 2)

    # convert all rR to mg/cm2:
    rhoR *= 1e3
    rhoR_random *= 1e3
    rhoR_systematic *= 1e3
    rhoR_model_systematic *= 1e3

    if verbose:
        log_file.writerow(['=== rhoR Analysis ==='])
        log_file.writerow(['Quantity', 'Value', 'Random Unc', 'Sys Unc', 'Sys Model Unc (inc in previous)'])
        log_file.writerow(['rhoR (mg/cm2)', rhoR, rhoR_random, rhoR_systematic, rhoR_model_systematic])
        log_file.writerow(['rhoR model error due to:'])
        for row in temp[2][1]:
            log_file.writerow([row[0], row[1]*1e3, 'mg/cm2'])

    if rhoR_plots:
        plot_rhoR_v_Energy(model, os.path.join(OutputDir, name + '_rR_v_E.eps'))
        plot_Rcm_v_Energy(model, os.path.join(OutputDir, name + '_Rcm_v_E.eps'))
        plot_rhoR_v_Rcm(model, os.path.join(OutputDir, name + '_rR_v_Rcm.eps'))

    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    # add info to the return dict:
    results['rhoR'] = rhoR
    results['rhoR_ran_unc'] = rhoR_random
    results['rhoR_sys_unc'] = rhoR_systematic
    results['rhoR_model_unc'] = rhoR_model_systematic

    # -----------------------------
    # 		Rcm analysis
    # -----------------------------
    t1 = datetime.now()
    myprint(name + ' Rcm analysis...', ProgressBar=ProgressBar)
    E0 = 14.7  # initial proton energy from D3He
    temp = model.Calc_Rcm(fit[1], 0)
    Rcm = temp[0]
    Rcm_model_random = 0
    Rcm_model_systematic = temp[1]

    # error bars propagated from energy errors:
    temp_plus = model.Calc_Rcm(fit[1] + energy_random, 0)
    temp_minus = model.Calc_Rcm(fit[1] - energy_random, 0)
    Rcm_energy_random = diff(temp_plus[0], temp_minus[0]) / 2

    temp_plus = model.Calc_Rcm(fit[1] + energy_systematic, 0)
    temp_minus = model.Calc_Rcm(fit[1] - energy_systematic, 0)
    Rcm_energy_systematic = diff(temp_plus[0], temp_minus[0]) / 2

    # Calculate Rcm error bars:
    Rcm_random = math.sqrt(Rcm_model_random ** 2 + Rcm_energy_random ** 2)
    Rcm_systematic = math.sqrt(Rcm_model_systematic ** 2 + Rcm_energy_systematic ** 2)

    # Convert to um:
    Rcm *= 1e4
    Rcm_random *= 1e4
    Rcm_systematic *= 1e4
    Rcm_model_systematic *= 1e4

    if verbose:
        log_file.writerow(['Rcm (um)', Rcm, Rcm_random, Rcm_systematic, Rcm_model_systematic])

    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    # add info to the return dict:
    results['Rcm'] = Rcm[()]
    results['Rcm_ran_unc'] = Rcm_random
    results['Rcm_sys_unc'] = Rcm_systematic
    results['Rcm_model_unc'] = Rcm_model_systematic

    # -----------------------------
    # 		Make summary Figs
    # -----------------------------
    t1 = datetime.now()
    myprint(name + ' generate summary...', ProgressBar=ProgressBar)
    result_text = [r'$Y_p$ = ' + r'{:.2e}'.format(float(fit[0]))
                + r' $\pm$ ' + r'{:.1e}'.format(float(yield_random)) + r'$_{(ran)}$ $\pm$ '
                + r'{:.1e}'.format(float(yield_systematic)) + r'$_{(sys)}$'
                , r'$E_p$ (MeV) = ' + r'{:.2f}'.format(float(fit[1]))
                + r' $\pm$ ' + r'{:.2f}'.format(float(energy_random))
                + r'$_{(ran)}$ $\pm$ '
                + r'{:.2f}'.format(float(energy_systematic))
                + r'$_{(sys)}$'
                , r'$\sigma_p$ (MeV) = '
                + r'{:.2f}'.format(float(fit[2]))
                + r' $\pm$ ' + r'{:.2f}'.format(float(sigma_random)) + r'$_{(ran)}$ $\pm$ '
                + r'{:.2f}'.format(float(sigma_systematic)) + r'$_{(sys)}$'
                ,
                r'$\rho R$ (mg/cm$^2$) = ' + r'{:.0f}'.format(float(rhoR))
                + r' $\pm$ ' + r'{:.0f}'.format(float(rhoR_random)) + r'$_{(ran)}$ $\pm$ '
                + r'{:.0f}'.format(float(rhoR_systematic)) + r'$_{(sys)}$'
                , r'$R_{cm}$ ($\mu$m) = ' + r'{:.0f}'.format(float(Rcm))
                + r' $\pm$ ' + '{:.0f}'.format(float(Rcm_random))
                + r'$_{(ran)}$ $\pm$ '
                + '{:.0f}'.format(float(Rcm_systematic)) + r'$_{(sys)}$']

    fname = os.path.join(OutputDir, name + '_Summary.eps')
    # noinspection PyUnboundLocalVariable
    save_slide(fname, Fit=FitObj, Hohl=hohl, name=name, summary=summary, results=result_text, Nxy=Nxy)
    if ShowSlide:
        show_slide(Fit=FitObj, Hohl=hohl, name=name, summary=summary, results=result_text, Nxy=Nxy, interactive=True)

    t2 = datetime.now()
    mytime((t2-t1).total_seconds(), 10, ProgressBar=ProgressBar)

    return results
