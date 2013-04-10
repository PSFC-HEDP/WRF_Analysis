## @package wrf_analysis
# A three-part rhoR model for NIF WRF analysis
# including fuel, shell, and ablated mass.
# This class encapsulates the model itself, adding in
# error bars and sensitivity analysis.
#
# Author: Alex Zylstra
# Date: 2013/03/20

from rhoR_Model import *
from Constants import *

## Encapsulate analysis of energy -> rhoR using various error bars for assumed parameters.
#
class rhoR_Analysis(object):
	"""Encapsulate analysis of energy -> rhoR using various error bars for assumed parameters."""

	# set verbosity for console output:
	verbose = False

	# Error bars for various things:
	Ri_Err = 5e-4
	Ro_Err = 5e-4 # initial outer radius [cm]
	P0_Err = 5 # initial pressure [atm]
	fD_Err = 0. # deuterium fraction in fuel
	f3He_Err = 0. # 3He fraction in fuel
	Te_Gas_Err = 2 # keV
	Te_Shell_Err = 0.1 # keV
	Te_Abl_Err = 0.1 # keV
	Te_Mix_Err = 0.2 # keV
	# ablated mass is modeled as an exponential profile
	# specified by max, min, and length scale:
	rho_Abl_Max_Err = 0.5 # g/cc
	rho_Abl_Min_Err = 0.05 # g/cc
	rho_Abl_Scale_Err = 30e-4 # [cm]
	# Fraction of CH mixed into the hot spot
	MixF_Err = 0.05
	# thickness and mass remaining:
	Tshell_Err = 20e-4
	Mrem_Err = 0.05

	# the rhoR model itself:
	model = 0

	# a list of all parameters
	AllParam = []

	## initialize the rhoR model. Arguments taken here are primarily
	## shot-dependent initial conditions
	# @param Ri = inner radius [cm]
	# @param Ro = outer radius [cm]
	# @param fD = deuterium fraction
	# @param f3He = 3He fraction
	# @param P0 = initial fuel pressure [atm]
	def __init__(self, Ri=9e-2, Ro=11e-2, fD=0.3, f3He=0.7, P0=50, 
		Te_Gas=3, Te_Shell=0.2, Te_Abl=0.3, Te_Mix=0.5,
		rho_Abl_Max=1.5, rho_Abl_Min=0.1, rho_Abl_Scale=70e-4, MixF = 0.05,
		Tshell = 40e-4 , Mrem = 0.175):
		self.Ri = [ Ri-self.Ri_Err , Ri , Ri + self.Ri_Err ]
		self.Ro = [ Ro-self.Ro_Err , Ro , Ro + self.Ro_Err ]
		self.fD = [ fD-self.fD_Err, fD , fD+self.fD_Err]
		self.f3He = [ f3He-self.f3He_Err , f3He , f3He+self.f3He_Err ]
		self.P0 = [ P0-self.P0_Err , P0 , P0+self.P0_Err ]
		self.Te_Gas = [ Te_Gas-self.Te_Gas_Err , Te_Gas , Te_Gas+self.Te_Gas_Err ]
		self.Te_Shell = [ Te_Shell-self.Te_Shell_Err , Te_Shell , Te_Shell+self.Te_Shell_Err ]
		self.Te_Abl = [ Te_Abl-self.Te_Abl_Err , Te_Abl , Te_Abl+self.Te_Abl_Err ]
		self.Te_Mix = [ Te_Mix-self.Te_Mix_Err , Te_Mix , Te_Mix+self.Te_Mix_Err ]
		self.rho_Abl_Max = [ rho_Abl_Max-self.rho_Abl_Max_Err, rho_Abl_Max, rho_Abl_Max+self.rho_Abl_Max_Err]
		self.rho_Abl_Min = [ rho_Abl_Min-self.rho_Abl_Min_Err , rho_Abl_Min , rho_Abl_Min+self.rho_Abl_Min_Err ]
		self.rho_Abl_Scale = [ rho_Abl_Scale-self.rho_Abl_Scale_Err , rho_Abl_Scale , rho_Abl_Scale+self.rho_Abl_Scale_Err]
		self.MixF = [ MixF-self.MixF_Err , MixF , MixF+self.MixF_Err ]
		self.Tshell = [ Tshell-self.Tshell_Err , Tshell , Tshell+self.Tshell_Err ]
		self.Mrem = [ Mrem-self.Mrem_Err , Mrem , Mrem+self.Mrem_Err ]

		# start the rhoR model itself:
		self.model = rhoR_Model(Ri,Ro,fD,f3He,P0,Te_Gas,Te_Shell,Te_Abl,Te_Mix,rho_Abl_Max,rho_Abl_Min,rho_Abl_Scale,MixF)

	## Main function
	# Calculate the proton energy downshift
	# @param Rcm = shell radius at shock BT [cm]
	# @param E0 = initial proton energy [MeV]
	# @return Eout = final proton energy [MeV]
	def Eout(self, Rcm, E0=14.7):
		TotalError = self.__calc_error__("Eout",Rcm,E0)
		return self.model.Eout(Rcm, self.Tshell[1], self.Mrem[1], E0) , TotalError

	## Alternative analysis method: specify measured E and calc rhoR
	# @param E1 = Measured proton energy [MeV]
	# @param E0 = initial proton energy [MeV]
	# @return rhoR , Rcm , rhoR error = modeled areal density to produce modeled E
	def Calc_rhoR(self, E1, E0=14.7):
		TotalError = self.__calc_error__("Calc_rhoR",0,E0,E1)
		rhoR , Rcm = self.model.Calc_rhoR(E1, self.Tshell[1], self.Mrem[1], E0)
		return rhoR , Rcm , TotalError

	## Calculate total rhoR
	# @param Rcm = shell radius at shock BT [cm]
	def rhoR_Total(self, Rcm):
		TotalError = self.__calc_error__("rhoR_Total",Rcm)
		return self.model.rhoR_Total(Rcm, self.Tshell[1], self.Mrem[1]) , TotalError

	## Calculate the three components of rhoR
	# @param Rcm shell radius at shock BT [cm]
	def rhoR_Parts(self,Rcm):
		#TotalError = self.__calc_error__("rhoR_Parts",Rcm)
		return self.model.rhoR_Parts(Rcm, self.Tshell[1], self.Mrem[1]) #, TotalError


	## Calculate the shell Rcm
	# @param E1 the measured energy (MeV)
	# @param dE the energy uncertainty (MeV)
	# @param E0 initial proton energy
	# @return Rcm , Rcm unc
	def Calc_Rcm(self, E1, dE, E0=14.7, ModelErr=True):
		"""Calculate the shell Rcm"""
		rhoR , Rcm = self.model.Calc_rhoR(E1, self.Tshell[1], self.Mrem[1], E0)

		# error due to the rhoR model:
		if ModelErr:
			RcmModelErr = self.__calc_error__("Calc_rhoR_Rcm",0,E0,E1)
		else:
			RcmModelErr = 0

		# error due to dE, on low energy side:
		Rcm_Emin = Rcm
		Emin = E1
		while Emin > (E1-dE):
			Rcm_Emin -= 1e-4
			Emin = self.Eout(Rcm_Emin,E0)[0]

		# error due to dE, on high energy side:
		Rcm_Emax = Rcm
		Emax = E1
		while Emax < (E1+dE):
			Rcm_Emax += 1e-4
			Emax = self.Eout(Rcm_Emax,E0)[0]

		# Calculate a quadrature sum total error:
		TotalError = math.sqrt( RcmModelErr**2 + ((Rcm_Emax-Rcm_Emin)/2)**2 )

		return Rcm , TotalError


	## Helper function for calculating errors. Calls an appropriate function
	# of model.
	def __call_func__(self, model, func, Rcm, Tshell, Mrem, E0=0, E1=0):
		if func == "Eout":
			return model.Eout(Rcm,Tshell,Mrem,E0)
		if func == "Calc_rhoR":
			return model.Calc_rhoR(E1, Tshell, Mrem, E0)[0]
		if func == "Calc_rhoR_Rcm":
			return model.Calc_rhoR(E1, Tshell, Mrem, E0)[1]
		if func == "rhoR_Total":
			return model.rhoR_Total(Rcm, Tshell, Mrem)
		if func == "rhoR_Parts":
			return model.rhoR_Parts(Rcm, Tshell, Mrem)

	def __calc_error__(self, func, Rcm=0, E0=0, E1=0):

		# list of error bars for various parameters:
		Errors = []
		new_model = 0

		# Vary the inner radius:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max
		for Ri in self.Ri: # vary inner radius:
			new_model = rhoR_Model(Ri,self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the outer radius:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Ro in self.Ro: # vary Ro:
			new_model = rhoR_Model(self.Ri[1],Ro,self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the deuterium fraction:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for fD in self.fD: # vary fD:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],fD,self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the 3He fraction::
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for f3He in self.f3He: # vary f3He:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],f3He,self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the initial pressure:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for P0 in self.P0: # vary P0:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],P0,
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the gas electron temperature:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Te_Gas in self.Te_Gas: # vary Te_Gas:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				Te_Gas,self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the shell electron temperature:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Te_Shell in self.Te_Shell: # vary Te_Shell:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],Te_Shell,self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the ablated material electron temp:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Te_Abl in self.Te_Abl: # vary Te_Abl:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],Te_Abl,self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the Te_Mix:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Te_Mix in self.Te_Mix: # vary Te_Mix:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],Te_Mix,
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the maximum ablated material density:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for rho_Abl_Max in self.rho_Abl_Max: # vary rho_Abl_Max:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				rho_Abl_Max,self.rho_Abl_Min[1],self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the minimum ablated mass density:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for rho_Abl_Min in self.rho_Abl_Min: # vary rho_Abl_Min:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],rho_Abl_Min,self.rho_Abl_Scale[1],self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the ablated mass scale length:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for rho_Abl_Scale in self.rho_Abl_Scale: # vary rho_Abl_Scale:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],rho_Abl_Scale,self.MixF[1])
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the mix fraction:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for MixF in self.MixF: # vary MixF:
			new_model = rhoR_Model(self.Ri[1],self.Ro[1],self.fD[1],self.f3He[1],self.P0[1],
				self.Te_Gas[1],self.Te_Shell[1],self.Te_Abl[1],self.Te_Mix[1],
				self.rho_Abl_Max[1],self.rho_Abl_Min[1],self.rho_Abl_Scale[1],MixF)
			new_val = self.__call_func__( new_model , func, Rcm, self.Tshell[1], self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the shell thickness:
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Tshell in self.Tshell: # vary Tshell:
			new_val = self.__call_func__( self.model , func, Rcm, Tshell, self.Mrem[1], E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		# Vary the mass remaining::
		Max = self.__call_func__( self.model , func , Rcm, self.Tshell[1], self.Mrem[1], E0, E1) # nominal value
		Min = Max # nominal value
		for Mrem in self.Mrem: # vary Mrem:
			new_val = self.__call_func__( self.model , func, Rcm, self.Tshell[1], Mrem, E0, E1)
			if new_val > Max:
				Max = new_val
			elif new_val < Min:
				Min = new_val
		Errors.append( (Max-Min)/2.0 )
		if self.verbose:
			print( (Max-Min)/2.0 )

		#Calculate quadrature sum of Errors, i.e. total error bar:
		TotalError = 0
		for i in Errors:
			TotalError += i**2.0
		TotalError = math.sqrt(TotalError)

		return TotalError