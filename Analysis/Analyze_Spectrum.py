## Implement a function which performs analysis of a NIF WRF spectrum
# to get rhoR, yield, and so on with error bars.

import os
from datetime import *
import csv
import math
import matplotlib
matplotlib.use('Agg')

from rhoR_Analysis import *
from rhoR_Model_plots import *
from GaussFit import *
from CSV import *
from Hohlraum import *
from SlideGenerator import *

def diff(a,b):
	return max(a,b) - min(a,b)

def Analyze_Spectrum(data,spectrum_random,spectrum_systematic,hohl_wall,LOS,name="",summary=True,plots=True,verbose=True,rhoR_plots=False):
	OutputDir = 'AnalysisOutputs'
	# check to see if OutputDir exists:
	if not os.path.isdir(OutputDir):
		# create it:
		os.makedirs(OutputDir)
	# if we are in verbose mode, then we spit out data to a file:
	if verbose:
		log_file = csv.writer(open(os.path.join(OutputDir,name+'_Analysis.csv'),'w'))
	
	# ----------------------------
	# 		Hohlraum Correction
	# ----------------------------
	t1 = datetime.now()
	print(name + ' hohlraum correction...')

	hohl = Hohlraum(data,
		wall=hohl_wall,
		angles=LOS)

	# get corrected spectrum:
	corr_data = hohl.get_data_corr()

	if verbose:
		log_file.writerow( ['=== Hohlraum Analysis ==='] )
		log_file.writerow( ['Raw Energy (MeV)', hohl.get_fit_raw()[1] ] )
		log_file.writerow( ['Corr Energy (MeV)', hohl.get_fit_corr()[1] ] )
		log_file.writerow( ['Au Thickness (um)', hohl.Au ] )
		log_file.writerow( ['DU Thickness (um)', hohl.DU ] )
		log_file.writerow( ['Al Thickness (um)', hohl.Al ] )

	if plots:
		# make plot of raw and corrected spectra:
		hohl_plot1_fname = os.path.join(OutputDir,name+'_HohlCorr.eps')
		hohl.plot_file( hohl_plot1_fname )
		# make figure showing hohlraum profile:
		hohl_plot2_fname = os.path.join(OutputDir,name+'_HohlProfile.eps')
		hohl.plot_hohlraum_file( hohl_plot2_fname )

	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")

	# -----------------------------
	# 		Energy analysis
	# -----------------------------
	t1 = datetime.now()
	print(name + ' energy analysis...')
	# First, we need to perform a Gaussian fit:
	FitObj = GaussFit(corr_data,name=name)
	# get the fit and uncertainty:
	fit = FitObj.get_fit()
	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")

	t1 = datetime.now()
	print(name + ' energy error analysis...')
	fit_unc = FitObj.chi2_fit_unc()
	print(fit_unc)
	# average + and - error bars:
	for i in range(len(fit_unc)):
		fit_unc[i] = ( math.fabs(fit_unc[i][0])
			+ math.fabs(fit_unc[i][1]) ) /2
	# make a plot of the fit:
	if plots:
		fit_plot_fname = os.path.join(OutputDir,name+'_GaussFit.eps')
		FitObj.plot_file( fit_plot_fname )

	# calculate total error bars:
	yield_random = math.sqrt( spectrum_random[0]**2 + fit_unc[0]**2 )
	yield_systematic = spectrum_systematic[0]
	energy_random = math.sqrt( spectrum_random[1]**2 + fit_unc[1]**2 )
	energy_systematic = spectrum_systematic[1]
	sigma_random = math.sqrt( spectrum_random[2]**2 + fit_unc[2]**2 )
	sigma_systematic = spectrum_systematic[2]

	if verbose:
		log_file.writerow( ['=== Spectrum Analysis ==='] )
		log_file.writerow( ['Quantity','Value','Random Unc','Sys Unc'] )
		log_file.writerow( ['Yield',fit[0],yield_random,yield_systematic] )
		log_file.writerow( ['Energy (MeV)',fit[1],energy_random,energy_systematic] )
		log_file.writerow( ['Sigma (MeV)',fit[2],sigma_random,sigma_systematic] )

	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")

	# -----------------------------
	# 		rhoR analysis
	# -----------------------------
	t1 = datetime.now()
	print(name + ' rhoR analysis...')
	# set up the rhoR analysis:
	model = rhoR_Analysis()
	E0 = 14.7 # initial proton energy from D3He
	temp = model.Calc_rhoR(fit[1],E0)
	rhoR = temp[0]
	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")

	# error analysis for rR:
	t1 = datetime.now()
	print(name + ' rhoR error analysis...')
	rhoR_model_random = 0
	rhoR_model_systematic = (temp[1]+temp[2])/2
	# error bars propagated from energy:
	temp_plus = model.Calc_rhoR(fit[1]+energy_random,E0)
	temp_minus = model.Calc_rhoR(fit[1]-energy_random,E0)
	rhoR_energy_random = diff(temp_plus[0],temp_minus[0])/2
	temp_plus = model.Calc_rhoR(fit[1]+energy_systematic,E0)
	temp_minus = model.Calc_rhoR(fit[1]-energy_systematic,E0)
	rhoR_energy_systematic = diff(temp_plus[0],temp_minus[0])/2

	# calculate total rhoR error bar:
	rhoR_random = math.sqrt( rhoR_model_random**2 + rhoR_energy_random**2 )
	rhoR_systematic = math.sqrt( rhoR_model_systematic**2 + rhoR_energy_systematic**2 )

	# convert all rR to mg/cm2:
	rhoR = rhoR * 1e3
	rhoR_random = rhoR_random * 1e3
	rhoR_systematic = rhoR_systematic * 1e3

	if verbose:
		log_file.writerow( ['=== rhoR Analysis ==='] )
		log_file.writerow( ['Quantity','Value','Random Unc','Sys Unc'] )
		log_file.writerow( ['rhoR (mg/cm2)',rhoR,rhoR_random,rhoR_systematic] ) 

	if rhoR_plots:
		plot_rhoR_v_Energy(model, os.path.join(OutputDir,name + '_rR_v_E.eps'))
		plot_Rcm_v_Energy(model, os.path.join(OutputDir,name + '_Rcm_v_E.eps'))
		plot_rhoR_v_Rcm(model, os.path.join(OutputDir,name + '_rR_v_Rcm.eps'))

	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")


	# -----------------------------
	# 		Rcm analysis
	# -----------------------------
	t1 = datetime.now()
	print(name + ' Rcm analysis...')
	E0 = 14.7 # initial proton energy from D3He
	temp = model.Calc_Rcm(fit[1],0,E0=E0)
	Rcm = temp[0]
	print(temp)
	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")

	# -----------------------------
	# 		Make summary Figs
	# -----------------------------
	t1 = datetime.now()
	print(name + ' generate summary...')
	summary = r'foo'
	results = []
	results.append(r'$Y_p$ = ' + r'{:.2e}'.format(fit[0]) + r' $\pm$ ' + r'{:.1e}'.format(yield_random) + r'$_{(ran)}$ $\pm$ ' + r'{:.1e}'.format(yield_systematic) + r'$_{(sys)}$')
	results.append(r'$E_p$ (MeV) = ' + r'{:.2f}'.format(fit[1]) + r' $\pm$ ' + r'{:.2f}'.format(energy_random) + r'$_{(ran)}$ $\pm$ ' + r'{:.2f}'.format(energy_systematic) + r'$_{(sys)}$')
	results.append(r'$\sigma_p$ (MeV) = ' + r'{:.2f}'.format(fit[2]) + r' $\pm$ ' + r'{:.2f}'.format(sigma_random) + r'$_{(ran)}$ $\pm$ ' + r'{:.2f}'.format(sigma_systematic) + r'$_{(sys)}$')
	results.append(r'$\rho R$ (mg/cm$^2$) = ' + r'{:.0f}'.format(rhoR) + r' $\pm$ ' + r'{:.0f}'.format(rhoR_random) + r'$_{(ran)}$ $\pm$ ' + r'{:.0f}'.format(rhoR_systematic) + r'$_{(sys)}$')
	fname = os.path.join(OutputDir,name+'_Summary.eps')
	save_slide(fname,Fit=FitObj,Hohl=hohl,name=name,summary=summary,results=results)

	t2 = datetime.now()
	print( '{:.1f}'.format((t2-t1).total_seconds()) + "s elapsed")
