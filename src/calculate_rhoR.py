# a file for top-level ρR calculation functions.  the reason this file is separate from rhoR_Analysis.py despite the
# passingly similar topic scope is that Alex wrote his fancy calculations OOPly and the script onto which I grafted it
# is entirely procedural, so the interface is a little awkward semanticly.
from math import nan
from typing import Any

import numpy as np
from scipy import integrate

from src.rhoR_Analysis import rhoR_Analysis

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
		return rhoR, error, hotspot_component, shell_component (mg/cm^2)
	"""
	if shot_name.startswith("O"): # if it's an omega shot
		if shot_name not in rhoR_objects:
			rhoR_objects[shot_name] = []
			for ρ, Te in [(20, 500), (30, 500), (10, 500), (20, 250), (20, 750)]:
				table_filename = f"tables/stopping_range_protons_{params['ablator material']}_plasma_{ρ}gcc_{Te}eV.txt"
				try:
					data = np.loadtxt(table_filename, skiprows=4)
				except IOError:
					print(f"!\tDid not find '{table_filename}'.")
					rhoR_objects.pop(shot_name)
					break
				else:
					rhoR_objects[shot_name].append([data[::-1, 1], data[::-1, 0]*1000]) # load a table from Frederick's program

		if shot_name in rhoR_objects:
			energy_ref, rhoR_ref = rhoR_objects[shot_name][0]
			best_gess = np.interp(mean_energy[0], energy_ref, rhoR_ref) # calculate the best guess based on 20g/cc and 500eV
			error_bar = 0
			for energy in [mean_energy[0] - mean_energy[1], mean_energy[0], mean_energy[0] + mean_energy[2]]:
				for energy_ref, rhoR_ref in rhoR_objects[shot_name]: # then iterate thru all the other combinations of ρ and Te
					perturbd_gess = np.interp(energy, energy_ref, rhoR_ref)
					if abs(perturbd_gess - best_gess) > error_bar:
						error_bar = abs(perturbd_gess - best_gess)
			return best_gess, error_bar, error_bar

		else:
			return nan, nan, nan

	elif shot_name.startswith("N"): # if it's a NIF shot
		if shot_name not in rhoR_objects: # try to load the rhoR analysis parameters
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

		if shot_name in rhoR_objects: # if you did or they were already there, calculate the rhoR
			analysis_object = rhoR_objects[shot_name]
			rhoR, Rcm_value, error = analysis_object.Calc_rhoR(E1=mean_energy[0], dE=mean_energy[1])
			# hotspot_component, shell_component, ablated_component = analysis_object.rhoR_Parts(Rcm_value)
			return rhoR*1e3, error*1e3, error*1e3 # convert from g/cm2 to mg/cm2
		else:
			return nan, nan, nan

	else:
		raise NotImplementedError(shot_name)


def perform_hohlraum_correction(layers: list[Layer], after_wall: Peak) -> Peak:
	""" correct some spectral properties for a hohlraum """
	if len(layers) == 0:
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
	print(f"\tCorrecting for a {''.join(map(lambda t:t[1], layers))} hohlraum: {after_wall_mean[0]:.3f} ± "
	      f"{after_wall_sigma[0]:.3f} becomes {before_wall_mean[0]:.3f}±{before_wall_sigma[0]:.3f} MeV")

	return before_wall


def get_ein_from_eout(eout: float, layers: list[Layer]) -> float:
	""" do the reverse stopping power calculation """
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
	""" do a derivative of the stopping power calculation """
	left = get_ein_from_eout(max(0., eout - deout), layers)
	rite = get_ein_from_eout(max(0., eout + deout), layers)
	return (rite - left)/2
