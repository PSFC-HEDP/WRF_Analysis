## Implement a function which performs analysis of a NIF WRF spectrum
# to get rhoR, yield, and so on with error bars.

from rhoR_Analysis import *
from rhoR_Model_plots import *
from GaussFit import *
import os
import csv
import math

def diff(a,b):
	return max(a,b) - min(a,b)

def Analyze_Spectrum(data,spectrum_random,spectrum_systematic,name="",plots=True,verbose=True):
	OutputDir = 'SpectrumAnalysis'
	# check to see if OutputDir exists:
	if not os.path.isdir(OutputDir):
		# TODO
		print("directory problem!")

	# if we are in verbose mode, then we spit out data to a file:
	if verbose:
		log_file = csv.writer(open(os.path.join(OutputDir,name+'_Analysis.csv'),'w'))

	# -----------------------------
	# 		Energy analysis
	# -----------------------------
	# First, we need to perform a Gaussian fit:
	FitObj = GaussFit(data,name=name)

	# get the fit and uncertainty:
	fit = FitObj.get_fit()

	fit_unc = FitObj.chi2_fit_unc()
	# average + and - error bars:
	for i in range(len(fit_unc)):
		fit_unc[i] = ( math.fabs(fit_unc[i][0])
			+ math.fabs(fit_unc[i][1]) ) /2
	print(fit_unc)
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

	# -----------------------------
	# 		rhoR analysis
	# -----------------------------
	# set up the rhoR analysis:
	model = rhoR_Analysis()
	E0 = 14.7 # initial proton energy from D3He
	temp = model.Calc_rhoR(fit[1],E0)
	rhoR = temp[0]
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

	if verbose:
		log_file.writerow( ['=== rhoR Analysis ==='] )
		log_file.writerow( ['Quantity','Value','Random Unc','Sys Unc'] )
		log_file.writerow( ['rhoR',rhoR,rhoR_random,rhoR_systematic] ) 

	if plots:
		plot_rhoR_v_Energy(model, os.path.join(OutputDir,name))
