## @package wrf_analysis
# A three-part rhoR model for NIF WRF analysis
# including fuel, shell, and ablated mass
#
# Author: Alex Zylstra
# Date: 2013/04/02

import math
import numpy
import scipy.interpolate
import scipy.integrate
import os
from Constants import *
from StopPow import *

## Class to encapsulate rhoR model calculations
#
class rhoR_Model(object):
	"""3-part (shell, fuel, ablated mass) rhoR model."""

	# initial shell conditions:
	# values below are defaults
	Ri = 900e-4 # initial inner radius [cm]
	Ro = 1100e-4 # initial outer radius [cm]
	P0 = 50 # initial pressure [atm]
	fD = 0.5 # deuterium fraction in fuel
	f3He = 0.5 # 3He fraction in fuel

	# a few densities and masses:
	rho_CH = 1.044
	rho_D2_STP = 2*0.08988e-3
	rho_3He_STP = (3/4)*0.1786e-3
	rho0_Gas = 0 # initial gas density
	Mass_CH_Total = 0
	Mass_Mix_Total = 0

	# ASSUMED CONDITIONS
	Te_Gas = 1 # keV
	Te_Shell = 0.2 # keV
	Te_Abl = 0.3 # keV
	Te_Mix = 0.3 # keV
	# ablated mass is modeled as an exponential profile
	# specified by max, min, and length scale:
	rho_Abl_Max = 1.5 # g/cc
	rho_Abl_Min = 0.1 # g/cc
	rho_Abl_Scale = 70e-4 # [cm]
	# Fraction of CH mixed into the hot spot
	MixF = 0.025

	# options for stop pow calculations:
	steps = 50 # steps in radius per region

	## initialize the rhoR model. Arguments taken here are primarily
	## shot-dependent initial conditions
	# @param Ri = inner radius [cm]
	# @param Ro = outer radius [cm]
	# @param fD = deuterium fraction
	# @param f3He = 3He fraction
	# @param P0 = initial fuel pressure [atm]
	def __init__(self, Ri=9e-2, Ro=11e-2, fD=0.5, f3He=0.5, P0=50, 
		Te_Gas=1, Te_Shell=0.2, Te_Abl=0.3, Te_Mix=0.3,
		rho_Abl_Max=1.5, rho_Abl_Min=0.1, rho_Abl_Scale=70e-4, MixF = 0.025):
		self.Ri = Ri
		self.Ro = Ro
		self.fD = fD
		self.f3He = f3He
		self.P0 = P0
		self.Te_Gas = Te_Gas
		self.Te_Shell = Te_Shell
		self.Te_Abl = Te_Abl
		self.Te_Mix = Te_Mix
		self.rho_Abl_Max = rho_Abl_Max
		self.rho_Abl_Min = rho_Abl_Min
		self.rho_Abl_Scale = rho_Abl_Scale
		self.MixF = MixF

		# calculate initial gas density
		self.rho0_Gas = P0*( (fD/2)*self.rho_D2_STP + f3He*self.rho_3He_STP )

		# calculate initial masses:
		self.Mass_CH_Total = (4*math.pi/3)*self.rho_CH*(Ro**3 - Ri**3)

	## Main function
	# Calculate the proton energy downshift
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @param E0 = initial proton energy [MeV]
	# @return Eout = final proton energy [MeV]
	def Eout(self, Rcm, Tshell, Mrem, E0=14.7):
		E = E0
		# range through gas:
		dr = (Rcm-Tshell/2) / self.steps # radial step
		for i in range(self.steps):
			E = E + dr*(self.dEdr_Gas(E,Rcm,Tshell,Mrem)
				        +self.dEdr_Mix(E,Rcm,Tshell,Mrem))
		
		#range through shell:
		dr = Tshell / self.steps # radial step
		for i in range(self.steps):
			E = E + dr*self.dEdr_Shell(E,Rcm,Tshell,Mrem)

		#range through ablated mass:
		r1,r2,r3 = self.get_Abl_radii(Rcm,Tshell,Mrem)
		dr = (r3-r1) / self.steps
		for i in range(self.steps):
			E = E + dr*self.dEdr_Abl(E,r1+dr*i,Rcm,Tshell,Mrem)

		return max(E,0)

	## Alternative analysis method: specify measured E and calc rhoR
	# @param Eout = Measured proton energy [MeV]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @param E0 = initial proton energy [MeV]
	# @return rhoR = modeled areal density to produce modeled E
	def Calc_rhoR(self, E1, Tshell, Mrem, E0=14.7):
		# this function sets up an interpolating function to solve
		# for an exact answer
		#E = []
		#rR = []
		#for i in numpy.arange(150e-4,400e-4,5e-4): # model from 150 to 400 um Rcm
		#	E.append( self.Eout( i, Tshell, Mrem, E0) )
		#	rR.append( self.rhoR_Total( i, Tshell, Mrem) )

		# set up interpolation:
		#interp = scipy.interpolate.interp1d( E , rR )
		#return interp(E1)

		# possibly faster:
		#E = E0
		#r = self.Ri
		#rhoR = self.rhoR_Total(r,Tshell,Mrem)

		#E_last = E
		#rhoR_last = rhoR

		#dr = 5e-4
		#while E > E1:
		#	r -= dr
		#	E_last = E
		#	rhoR_last = rhoR
#
#			E = self.Eout(r,Tshell,Mrem,E0)
#			rhoR = self.rhoR_Total(r,Tshell,Mrem)
#
#		return rhoR - (E1 - E) * (rhoR-rhoR_last)/(E_last-E)

		# fastest implementation: binary search
		min_r = self.Ri/20
		max_r = self.Ri
		dE = 0.01 # accuracy goal
		
		r = (max_r + min_r)/2.0
		E = self.Eout(r,Tshell,Mrem,E0)
		rhoR = self.rhoR_Total(r,Tshell,Mrem)
		i = 0
		while math.fabs(E1-E) > dE:
			if( E1 > E ): # need lower rhoR to explain E1
				min_r = r
			elif( E1 < E ): # need higher rhoR to explain E1:
				max_r = r

			r = (max_r + min_r)/2.0
			E = self.Eout(r,Tshell,Mrem,E0)
			rhoR = self.rhoR_Total(r,Tshell,Mrem)

		return rhoR , r

	# ----------------------------------------------------------------
	#         Calculators for rho, rhoR, n
	# ----------------------------------------------------------------
	## Calculate gas density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	def rho_Gas(self, Rcm, Tshell):
		Rgas = Rcm - Tshell/2
		return self.rho0_Gas * (self.Ri/Rgas)**3

	## Calculate gas areal density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	def rhoR_Gas(self, Rcm, Tshell):
		Rgas = Rcm - Tshell/2
		return self.rho0_Gas * Rgas * (self.Ri/Rgas)**3

	## Calculate gas number density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @return ni , ne
	def n_Gas(self, Rcm, Tshell):
		A = self.fD*2 + self.f3He*3
		ni = self.rho_Gas(Rcm,Tshell) / (A*mp)
		Z = self.fD + self.f3He*2
		ne = Z*ni
		return (ni , ne)

	## Calculate mix density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rho_Mix(self, Rcm, Tshell, Mrem):
		V = (4*math.pi/3) * (Rcm-Tshell/2)**3
		return self.Mass_Mix_Total / V

	## Calculate mix areal density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rhoR_Mix(self, Rcm, Tshell, Mrem):
		V = (4*math.pi/3) * (Rcm-Tshell/2)**3
		return (Rcm-Tshell/2) * self.Mass_Mix_Total / V

	## Calculate mix number density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return ni , ne
	def n_Mix(self, Rcm, Tshell,Mrem):
		ni = self.rho_Mix(Rcm,Tshell,Mrem) / (6.5*mp)
		ne = 3.5*ni
		return ni , ne

	## Calculate shell density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rho_Shell(self, Rcm, Tshell, Mrem):
		m = self.Mass_CH_Total * Mrem
		V = (4*math.pi/3)*( (Rcm+Tshell/2)**3 - (Rcm-Tshell/2)**3 )
		return m/V

	## Calculate shell areal density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rhoR_Shell(self, Rcm, Tshell, Mrem):
		m = self.Mass_CH_Total * Mrem
		V = (4*math.pi/3)*( (Rcm+Tshell/2)**3 - (Rcm-Tshell/2)**3 )
		return Tshell*m/V

	## Calculate shell number density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return ni , ne
	def n_Shell(self, Rcm, Tshell, Mrem):
		ni = self.rho_Shell(Rcm,Tshell,Mrem) / (6.5*mp)
		ne = 3.5*ni
		return ni , ne

	## Helper function for the ablated mass profile
	# Calculates the beginning, end of exp ramp, and final r
	# of the profile
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return r1 , r2 , r3
	def get_Abl_radii(self, Rcm, Tshell, Mrem):
		# density has an exponential ramp from max to min rho, then flat tail
		# as far out as necessary to conserve mass.
		m = self.Mass_CH_Total * (1-Mrem-self.MixF)
		r1 = Rcm + Tshell/2; # start of ablated mass
		# end of exponential ramp:
		r2 = r1 + self.rho_Abl_Scale * math.log(self.rho_Abl_Max/self.rho_Abl_Min)
		# mass left in the "tail""
		scale = self.rho_Abl_Scale # shorthand
		m23 = m - 4*math.pi*scale*(2*scale**2 + 2*r1*scale
			      -math.exp((r1-r2)/scale)*(2*scale**2+2*scale*r2+r2**2))
		r3 = (math.pow(3*m23+4*math.pi*r2**3*scale , 1/3) 
			  / (math.pow(4*math.pi*self.rho_Abl_Min,1/3)) )
		return r1,r2,r3

	## Calculate ablated mass density as a function of r
	# @param r [cm]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rho_Abl(self, r, Rcm, Tshell, Mrem):
		r1,r2,r3 = self.get_Abl_radii(Rcm,Tshell,Mrem)

		# density is constructed piecewise, depending on where we are:
		if r > r1 and r < r2:
			return self.rho_Abl_Max*math.exp(-(r-r1)/self.rho_Abl_Scale)
		if r > r2 and r < r3:
			return self.rho_Abl_Min
		return 0

	## Calculate ablated mass areal density
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def rhoR_Abl(self, Rcm, Tshell, Mrem):
		r1,r2,r3 = self.get_Abl_radii(Rcm,Tshell,Mrem)
		# integrate from origin to 1cm since rho profile handles bounds
		return scipy.integrate.quad( self.rho_Abl , r1, r3, args=(Rcm,Tshell,Mrem))[0]

	## Calculate ablated mass number density
	# @param r [cm]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return ni , ne
	def n_Abl(self, r, Rcm, Tshell, Mrem):
		ni = self.rho_Abl(r, Rcm,Tshell,Mrem) / (6.5*mp)
		ne = 3.5*ni
		return ni , ne

	## Calculate total rhoR
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return total rhoR [g/cm2]
	def rhoR_Total(self, Rcm, Tshell, Mrem):
		ret = self.rhoR_Gas(Rcm,Tshell)
		ret += self.rhoR_Mix(Rcm,Tshell,Mrem)
		ret += self.rhoR_Shell(Rcm,Tshell,Mrem)
		ret += self.rhoR_Abl(Rcm,Tshell,Mrem)
		return ret

	## Return all three components of rhoR
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	# @return (fuel,shell,ablated) rhoR [g/cm2]
	def rhoR_Parts(self, Rcm, Tshell, Mrem):
		gas = self.rhoR_Gas(Rcm,Tshell)
		gas += self.rhoR_Mix(Rcm,Tshell,Mrem)
		shell = self.rhoR_Shell(Rcm,Tshell,Mrem)
		abl = self.rhoR_Abl(Rcm,Tshell,Mrem)
		return gas, shell, abl



		
	# ----------------------------------------------------------------
	#         Calculators for stopping power
	# ----------------------------------------------------------------
	## Calculate gas stopping power for protons
	# @param Ep = proton energy [MeV]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def dEdr_Gas(self, Ep, Rcm, Tshell, Mrem):
	    mt = 1
	    Zt = 1

	    # Set up FloatVectors for stopping power
	    mf = FloatVector(3)
	    mf[0] = 2
	    mf[1] = 3
	    mf[2] = me/mp
	    Zf = FloatVector(3)
	    Zf[0] = 1
	    Zf[1] = 2
	    Zf[2] = -1
	    Tf = FloatVector(3)
	    Tf[0] = self.Te_Gas
	    Tf[1] = self.Te_Gas
	    Tf[2] = self.Te_Gas
	    nf = FloatVector(3)
	    ni , ne = self.n_Gas(Rcm,Tshell)
	    nf[0] = ni*self.fD
	    nf[1] = ni*self.f3He
	    nf[2] = ne
	    # Use Li-Petrasso:
	    if ne>0:
	    	model = StopPow_LP(mt,Zt,mf,Zf,Tf,nf)
	    	return 1e4*model.dEdx(Ep)
	    return 0

	## Calculate mix stopping power for protons
	# @param Ep = proton energy [MeV]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def dEdr_Mix(self, Ep, Rcm, Tshell, Mrem):
	    mt = 1
	    Zt = 1
	    # Set up FloatVectors for stopping power
	    mf = FloatVector(3)
	    mf[0] = 1
	    mf[1] = 12
	    mf[2] = me/mp
	    Zf = FloatVector(3)
	    Zf[0] = 1
	    Zf[1] = 6
	    Zf[2] = -1
	    Tf = FloatVector(3)
	    Tf[0] = self.Te_Mix
	    Tf[1] = self.Te_Mix
	    Tf[2] = self.Te_Mix
	    nf = FloatVector(3)
	    ni , ne = self.n_Mix(Rcm,Tshell,Mrem)
	    nf[0] = ni/2
	    nf[1] = ni/2
	    nf[2] = ne
	    # Use Li-Petrasso:
	    if ne>0:
	    	model = StopPow_LP(mt,Zt,mf,Zf,Tf,nf)
	    	return 1e4*model.dEdx(Ep)
	    return 0

	## Calculate shell stopping power for protons
	# @param Ep = proton energy [MeV]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def dEdr_Shell(self, Ep, Rcm, Tshell, Mrem):
	    mt = 1
	    Zt = 1
	    mf = FloatVector(3)
	    mf[0] = 1
	    mf[1] = 12
	    mf[2] = me/mp
	    Zf = FloatVector(3)
	    Zf[0] = 1
	    Zf[1] = 6
	    Zf[2] = -1
	    Tf = FloatVector(3)
	    Tf[0] = self.Te_Shell
	    Tf[1] = self.Te_Shell
	    Tf[2] = self.Te_Shell
	    nf = FloatVector(3)
	    ni , ne = self.n_Shell(Rcm,Tshell,Mrem)
	    nf[0] = ni/2
	    nf[1] = ni/2
	    nf[2] = ne
	    # Use Li-Petrasso:
	    if ne>0:
	    	model = StopPow_LP(mt,Zt,mf,Zf,Tf,nf)
	    	return 1e4*model.dEdx(Ep)
	    return 0


	## Calculate ablated mass stopping power for protons
	# @param Ep = proton energy [MeV]
	# @param r = radius [cm]
	# @param Rcm = shell radius at shock BT [cm]
	# @param Tshell = shell thickness at shock BT [cm]
	# @param Mrem = fraction of shell mass remaining
	def dEdr_Abl(self, Ep, r, Rcm, Tshell, Mrem):
	    mt = 1
	    Zt = 1
	    
	    mf = FloatVector(3)
	    mf[0] = 1
	    mf[1] = 12
	    mf[2] = me/mp
	    Zf = FloatVector(3)
	    Zf[0] = 1
	    Zf[1] = 6
	    Zf[2] = -1
	    Tf = FloatVector(3)
	    Tf[0] = self.Te_Abl
	    Tf[1] = self.Te_Abl
	    Tf[2] = self.Te_Abl
	    nf = FloatVector(3)
	    ni , ne = self.n_Abl(r,Rcm,Tshell,Mrem)
	    nf[0] = ni/2
	    nf[1] = ni/2
	    nf[2] = ne
	    # Use Li-Petrasso:
	    if ne>0:
	    	model = StopPow_LP(mt,Zt,mf,Zf,Tf,nf)
	    	return 1e4*model.dEdx(Ep)
	    return 0