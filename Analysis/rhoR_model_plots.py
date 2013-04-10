## @package wrf_analysis
# Functions for making plots of the rhoR model
#
# Author: Alex Zylstra
# Date: 2013/03/13

from rhoR_Analysis import *
from numpy import arange
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

## Plot a model's curve for rhoR versus energy
# @param analysis the rhoR analysis model to plot
def plot_rhoR_v_Energy(analysis):
	"""Plot rhoR model's curve versus energy."""

	#sanity check:
	if not isinstance( analysis , rhoR_Analysis):
		return

	# lists of things to plot:
	EnergyList = []
	RhoRList = []
	RhoRListPlusErr = []
	RhoRListMinusErr = []
	# start at the inner radius of the shell:
	Rcm = analysis.Ri[1]

	# energies:
	dE = 0.5 #step for plot points
	E0 = 14.7 #initial protons
	Emax = 14.0 # Max plot energy
	Emin= 5.0 # min plot energy
	for i in arange(Emin,Emax,dE):
		EnergyList.append(i)
		# get result, then add it to the appropriate lists:
		temp = analysis.Calc_rhoR(i,E0)
		RhoRList.append( temp[0] )
		RhoRListPlusErr.append( temp[0]+temp[2] )
		RhoRListMinusErr.append( temp[0]-temp[2] )


	# make a plot, and add curves for the rhoR model
	# and its error bars:
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(RhoRList,EnergyList,'b-')
	ax.plot(RhoRListPlusErr,EnergyList,'b--')
	ax.plot(RhoRListMinusErr,EnergyList,'b--')

	# set some options:
	ax.set_ylim([0,15])
	ax.grid(True)
	# add labels:
	ax.set_xlabel(r'$\rho$R (g/cm$^2$)')
	ax.set_ylabel('Energy (MeV)')
	#ax.set_title(r'$\rho$R Model')

	#plt.show()
	fig.savefig('rhoR_vs_energy.eps')






## Plot a model's curve for Rcm versus energy
# @param analysis the rhoR analysis model to plot
def plot_Rcm_v_Energy(analysis):
	"""Plot rhoR model's curve of Rcm versus energy."""

	#sanity check:
	if not isinstance( analysis , rhoR_Analysis):
		return

	# lists of things to plot:
	EnergyList = []
	RcmList = []
	RcmListPlusErr = []
	RcmListMinusErr = []
	RcmListPlusErrEnergy = []
	RcmListMinusErrEnergy = []
	# start at the inner radius of the shell:
	Rcm = analysis.Ri[1]

	# energies:
	dE = 0.5 #step for plot points
	E0 = 14.7 #initial protons
	Emax = 14.0 # Max plot energy
	Emin= 5.0 # min plot energy
	Eerr = 0.13
	for i in arange(Emin,Emax,dE):
		EnergyList.append(i)
		# get result, then add it to the appropriate lists:
		temp = analysis.Calc_Rcm(i,Eerr,E0,ModelErr=True)
		RcmList.append( temp[0]*1e4 )
		RcmListPlusErr.append( (temp[0]+temp[1])*1e4 )
		RcmListMinusErr.append( (temp[0]-temp[1])*1e4 )

		# recalculate using only energy error bar:
		temp = analysis.Calc_Rcm(i,Eerr,E0,ModelErr=False)
		RcmListPlusErrEnergy.append( (temp[0]+temp[1])*1e4 )
		RcmListMinusErrEnergy.append( (temp[0]-temp[1])*1e4 )


	# make a plot, and add curves for the rhoR model
	# and its error bars:
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(RcmList,EnergyList,'b-')
	ax.plot(RcmListPlusErr,EnergyList,'b--')
	ax.plot(RcmListMinusErr,EnergyList,'b--')
	ax.plot(RcmListPlusErrEnergy,EnergyList,'b:')
	ax.plot(RcmListMinusErrEnergy,EnergyList,'b:')

	# set some options:
	ax.set_ylim([0,15])
	ax.grid(True)
	# add labels:
	ax.set_xlabel(r'$R_{cm}$ ($\mu$m)')
	ax.set_ylabel('Energy (MeV)')
	#ax.set_title(r'$\rho$R Model')

	#plt.show()
	fig.savefig('Rcm_vs_energy.eps')








## Make a plot of rhoR vs center-of-mass radius
## Plot a model's curve for rhoR versus energy
# @param analysis the rhoR analysis model to plot
def plot_rhoR_v_Rcm(analysis):
	"""Plot rhoR model's curve versus center-of-mass radius."""

	#sanity check:
	if not isinstance( analysis , rhoR_Analysis):
		return

	# lists of things to plot:
	RcmList = []
	RhoRList = []
	RhoRListPlusErr = []
	RhoRListMinusErr = []
	# start at the inner radius of the shell:
	Rcm = analysis.Ri[1]

	# energies:
	dr = 10e-4 #step for plot points
	Rmin = 100e-4 # Minimum radius to plot
	for i in arange(Rmin,Rcm,dr):
		RcmList.append(i*1e4)
		# get result, then add it to the appropriate lists, for total error bar:
		temp = analysis.rhoR_Total(i)
		RhoRList.append( temp[0] )
		RhoRListPlusErr.append( temp[0]+temp[1] )
		RhoRListMinusErr.append( temp[0]-temp[1] )


	# make a plot, and add curves for the rhoR model
	# and its error bars:
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(RcmList,RhoRList,'b-')
	ax.plot(RcmList,RhoRListPlusErr,'b--')
	ax.plot(RcmList,RhoRListMinusErr,'b--')

	# set some options:
	#ax.set_ylim([0,Rcm])
	ax.grid(True)
	# add labels:
	ax.set_xlabel(r'$R_{cm}$ ($\mu$m)')
	ax.set_ylabel(r'$\rho$R (g/cm$^2$)')
	#ax.set_title(r'$\rho$R Model')

	#plt.show()
	fig.savefig('rhoR_vs_Rcm.eps')










## Plot the mass profile for a given center-of-mass radius
# @param analysis the model to use for the plot
# @param Rcm the CM radius in cm
def plot_profile(analysis, Rcm):
	"""Plot the mass profile for a given center-of-mass radius"""

	#sanity check:
	if not isinstance( analysis , rhoR_Analysis):
		return

	# get modeled shell thickness:
	Tshell = analysis.Tshell[1]
	Mrem = analysis.Mrem[1]
	Rgas = Rcm - Tshell/2
	rho_Gas = analysis.model.rho_Gas(Rcm,Tshell)
	Rshell = Rcm + Tshell/2
	rho_Shell = analysis.model.rho_Shell(Rcm,Tshell,Mrem)

	# data for plotting gas profile:
	Gas_x = [0 , Rgas*1e4 ]
	Gas_y = [rho_Gas , rho_Gas]
	# data for plotting shell profile:
	Shell_x = [ Rgas*1e4 , Rshell*1e4 ]
	Shell_y = [ rho_Shell , rho_Shell ]
	# calculate ablated mass profile:
	Abl_r1 , Abl_r2 , Abl_r3 = analysis.model.get_Abl_radii(Rcm,Tshell,Mrem)
	Abl_x = []
	Abl_y = []
	for x in numpy.arange( Abl_r1+1e-5 , Abl_r3 , 5e-4):
		Abl_y.append( analysis.model.rho_Abl(x,Rcm,Tshell,Mrem) )
		Abl_x.append( x*1e4 )

	# make a plot window:
	fig = plt.figure()
	ax = fig.add_subplot(111)
	# add plots for three regions:
	ax.plot(Gas_x,Gas_y,'r-')
	ax.fill_between(Gas_x,Gas_y,[0,0],color='r')
	ax.plot(Shell_x,Shell_y,'b-')
	ax.fill_between(Shell_x,Shell_y,[0,0],color='b')
	ax.plot(Abl_x,Abl_y,'g-')
	ax.fill_between(Abl_x,Abl_y,numpy.zeros(len(Abl_x)),color='g')

	ax.set_ylim([0, int(1.1*rho_Shell) ])
	ax.set_ylim([0,25])
	#plt.yscale('log')
	ax.set_xlabel(r'Radius ($\mu$m)')
	ax.set_ylabel(r'$\rho$ (g/cm$^3$)')

	#show the plot:
	#plt.show()
	fig.savefig('rhoR_model_profile.eps')