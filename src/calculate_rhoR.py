# a file for top-level ρR calculation functions.  the reason this file is separate from rhoR_Analysis.py despite the
# passingly similar semantic scope is that Alex wrote his fancy calculations OOPly and the script onto which I grafted it
# is entirely procedural, so the interface is a little awkward.
from typing import Any

import numpy as np
from numpy import inf
from scipy import integrate

# if Alex's C stuff isn't working, catch the error here so the rest of the program can keep functioning
try:
	from src.Material import plasma_conditions
	from src.StopPow import StopPow_LP
	from src.rhoR_Analysis import rhoR_Analysis
except ImportError:
	LIBRARY_IMPORTED = False
	plasma_conditions = None
	StopPow_LP = None
	rhoR_Analysis = None
else:
	LIBRARY_IMPORTED = True

# a type that represents the thickness and material of a layer
Layer = tuple[float, str]
# a type that encodes a value with its error bars
Quantity = tuple[float, float, float]
np_Quantity = np.dtype([("value", float), ("lower_err", float), ("upper_err", float)])
# a type that fully describes a gaussian
Peak = tuple[Quantity, Quantity, Quantity]
np_Peak = np.dtype([("yield", np_Quantity), ("mean", np_Quantity), ("sigma", np_Quantity)])

rhoR_objects: dict[str, Any] = {}


def calculate_rhoR(mean_energy: Quantity, shot_name: str, params: dict[str, Any]) -> Quantity:
	""" calculate the rhoR using whatever tecneke makes most sense.
	    for a NIF shot, this will use Alex's fancy calculations.
	    for an OMEGA shot, this will simply interpolate off a table loaded from disk.
		return rhoR, error, hotspot_component, shell_component (mg/cm^2)
		:raise ValueError: if not enuff information is available to make an inference
	"""
	if not LIBRARY_IMPORTED:
		raise ValueError("the stopping power library couldn't be imported")

	elif shot_name.startswith("O"): # if it's an omega shot
		if shot_name not in rhoR_objects:
			if "ablator material" not in params:
				raise ValueError("to infer ρR on OMEGA shots, you need to specify the shell material with '--shell_material=_'.")
			if "shell density" not in params:
				raise ValueError("to infer ρR on OMEGA shots, you need to specify the shell density (in g/cm3) with '--shell_density=_'")
			if "shell electron temperature" not in params:
				raise ValueError("to infer ρR on OMEGA shots, you need to specify the shell material (in keV) with '--shell_temperature=_'")
			elif params["shell electron temperature"] > 50:
				raise ValueError("you clearly passed a shell temperature in eV.  read the instructions, baka; it should be in keV.  try again.")
			# do a simple stopping power calculation through a uniform plasma
			masses, charges, temperatures, densities = plasma_conditions(
				params["ablator material"], params["shell density"], params["shell electron temperature"])
			rhoR_objects[shot_name] = [
				(1., StopPow_LP(1, 1, masses, charges, temperatures, densities))]  # the 1, 1 at the beginning specifies that these are protons
			for density_factor in [0.5, 1.5]:
				for temperature_factor in [0.5, 1.5]:
					rhoR_objects[shot_name].append(
						(density_factor, StopPow_LP(1, 1, masses, charges,
						                            temperatures*temperature_factor,
						                            densities*density_factor)))

		birth_energy = 15.0 if params["secondary"] else 14.7
		guesses = []
		for energy in [mean_energy[0], mean_energy[0] - mean_energy[1], mean_energy[0] + mean_energy[2]]:
			if energy >= birth_energy:
				guesses.append(0)
			elif energy <= 0:
				guesses.append(inf)
			else:
				for density_factor, stopping_power in rhoR_objects[shot_name]: # then iterate thru all the other combinations of ρ and Te
					thickness = stopping_power.Thickness(birth_energy, energy)*1e-4  # (convert μm to cm)
					density = density_factor*params["shell density"]
					guesses.append(thickness*density/1e-3)  # convert
		best_gess = guesses[0]
		lower_error = guesses[0] - np.min(guesses)
		upper_error = np.max(guesses) - guesses[0]
		return best_gess, lower_error, upper_error

	elif shot_name.startswith("N"): # if it's a NIF shot
		# use Alex's fancy implosion stopping model
		if shot_name not in rhoR_objects:
			try:
				rhoR_objects[shot_name] = rhoR_Analysis(
					shell_mat   = params['ablator material'],
					Ri          = (params['ablator radius'] - params['ablator thickness'])*1e-4,  # convert to cm
					Ri_err      = 0.1e-4,
					Ro          = params['ablator radius']*1e-4,  # convert to cm
					Ro_err      = 0.1e-4,
					fD          = params['deuterium fraction'],
					fD_err      = min(params['deuterium fraction'], 1e-2),
					f3He        = params['helium-3 fraction'],
					f3He_err    = min(params['helium-3 fraction'], 1e-2),
					P0          = params['fill pressure']/760,  # convert to atm
					P0_err      = 0.1,
					t_Shell     = params['shell thickness']*1e-4,  # convert to cm
					t_Shell_err = params['shell thickness']/2*1e-4,
					E0          = 14.7 if params['helium-3 fraction'] > 0 else 15.0,  # MeV
				)
			except KeyError as e:
				raise ValueError(f"inferring ρR on NIF shots requires that the {e} be in the shot_info.csv table")

		# then calculate the ρR
		analysis_object = rhoR_objects[shot_name]
		rhoR, Rcm_value, error = analysis_object.Calc_rhoR(E1=mean_energy[0], dE=mean_energy[1])
		# hotspot_component, shell_component, ablated_component = analysis_object.rhoR_Parts(Rcm_value)
		return rhoR*1e3, error*1e3, error*1e3 # convert from g/cm2 to mg/cm2

	else:
		raise ValueError(f"I don't know what facility {shot_name} is supposed to be")


def perform_hohlraum_correction(layers: list[Layer], after_wall: Peak) -> Peak:
	""" correct some spectral properties for a hohlraum """
	if not any(thickness > 0 for thickness, material in layers):
		return after_wall

	yeeld, after_wall_mean, after_wall_sigma = after_wall

	before_wall_mean = (
		get_ein_from_eout(after_wall_mean[0], layers),
		get_σin_from_σout(after_wall_mean[1], after_wall_mean[0], layers))
	before_wall_sigma = (get_σin_from_σout(after_wall_sigma[0], after_wall_mean[0], layers),
	                     get_σin_from_σout(after_wall_sigma[1], after_wall_mean[0], layers))
	before_wall = (yeeld,
	               (before_wall_mean[0], before_wall_mean[1], before_wall_mean[1]),
	               (before_wall_sigma[0], before_wall_sigma[1], before_wall_sigma[1]))

	hohlraum_material_name = ""
	for thickness, layer_material_name in layers:
		if thickness > 0:
			hohlraum_material_name += layer_material_name
	print(f"\tCorrecting for a {hohlraum_material_name} hohlraum: {after_wall_mean[0]:.3f} ± "
	      f"{after_wall_sigma[0]:.3f} becomes {before_wall_mean[0]:.3f}±{before_wall_sigma[0]:.3f} MeV")

	return before_wall


def get_ein_from_eout(eout: float, layers: list[Layer]) -> float:
	""" do the reverse cold matter stopping power calculation """
	energy = eout # [MeV]
	for thickness, formula in layers[::-1]:
		data = np.loadtxt(f"tables/stopping_power_protons_{formula}.csv", delimiter=',')
		energy_axis = data[:, 0]/1e3 # [MeV]
		dEdx = data[:, 1]/1e3 # [MeV/μm]
		energy = integrate.odeint(
			func =lambda E, x: np.interp(E, energy_axis, dEdx),
			y0   =energy,
			t    =[0, thickness]
		)[-1, 0]  # type: ignore
	return energy


def get_σin_from_σout(deout: float, eout: float, layers: list[Layer]) -> float:
	""" do a derivative of the cold matter stopping power calculation """
	left = get_ein_from_eout(max(0., eout - deout), layers)
	rite = get_ein_from_eout(max(0., eout + deout), layers)
	return (rite - left)/2
