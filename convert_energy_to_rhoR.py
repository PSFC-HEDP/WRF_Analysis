import argparse
from typing import Union

import numpy as np

from src.calculate_rhoR import calculate_rhoR, Quantity, perform_hohlraum_correction


def convert_energy_to_rhoR(
		final_energy: Union[Quantity, str], shell_material: str, shell_density: float,
		shell_temperature: float, secondary: bool,
		gold: float, tantalum: float, uranium: float, aluminum: float):
	""" print out the ρR that approximately corresponds to a given measured D3He-p energy, given some hohlraum parameters.
	    :param final_energy: the final energy of the D3He protons (MeV)
	    :param shell_material: the material of the capsule shell ("HDC", "SiO2", or "CH")
	    :param shell_density: the density of the imploded shell plasma (g/cm^3)
	    :param shell_temperature: the electron temperature of the imploded shell plasma (keV)
	    :param secondary: whether these are secondary D3He reactions (which have a higher average birth energy)
	    :param gold: the amount of gold the particles passed thru (μm)
	    :param tantalum: the amount of tantalum the particles passed thru (μm)
	    :param uranium: the amount of depleted uranium the particles passed thru (μm)
	    :param aluminum: the amount of aluminum the particles passed thru (μm)
	"""
	# if a filename is passd instead of a specific energy
	if type(final_energy) is str:
		final_energies = np.genfromtxt(final_energy)
		for row in final_energies:
			if len(row) == 1:
				final_energy = (row[0], 0, 0)
			elif len(row) == 2:
				final_energy = (row[0], row[1], row[1])
			elif len(row) == 3:
				final_energy = (row[0], row[1], row[2])
			else:
				raise ValueError(f"the table you pass should have 1, 2, or 3 collums, not {len(row)}")
			convert_energy_to_rhoR(final_energy, shell_material, shell_density, shell_temperature,
			                       secondary, gold, tantalum, uranium, aluminum)
	else:
		_, intermediate_energy, _ = perform_hohlraum_correction(
			[(gold, "Au"), (tantalum, "Ta"), (uranium, "U"), (aluminum, "Al")],
			((0, 0, 0), final_energy, (0, 0, 0)))
		if intermediate_energy[0] != final_energy[0]:
			print(f"Hohlraum-corrected energy is {intermediate_energy[0]:.2f} MeV")
		rhoR = calculate_rhoR(
			intermediate_energy, "O", {
				"ablator material": shell_material,
				"shell density": shell_density,
				"shell electron temperature": shell_temperature,
				"secondary": secondary,
			}
		)
		print(f"ρR = {rhoR[0]:.2f} ± {rhoR[1]:.2f} mg/cm^2")


def main():
	parser = argparse.ArgumentParser(
		prog="python convert_energy_to_rhoR.py",
		description = "return the ρR that approximately corresponds to a given measured D3He-p energy, given some hohlraum parameters.")
	parser.add_argument("energy", type=str,
	                    help="the final energy of the D3He protons, in MeV, or a file containing a list of such final energies")
	parser.add_argument("--shell_material", type=str,
	                    help="the material of the capsule shell (HDC, SiO2, or CH)")
	parser.add_argument("--shell_density", type=float,
	                    help="the density of the imploded shell plasma (g/cm³)")
	parser.add_argument("--shell_temperature", type=float,
	                    help="the electron temperature of the imploded shell plasma (keV)")
	parser.add_argument("--gold", type=float, default=0,
	                    help="the amount of gold the particles passed through, in μm")
	parser.add_argument("--tantalum", type=float, default=0,
	                    help="the amount of tantalum the particles passed through, in μm")
	parser.add_argument("--uranium", type=float, default=0,
	                    help="the amount of depleted uranium the particles passed through, in μm")
	parser.add_argument("--aluminum", type=float, default=0,
	                    help="the amount of tantalum the particles passed through, in μm")
	parser.add_argument("--secondary", action="store_true",
	                    help="to treat the protons as secondary reactions (in which case the assumed mean birth energy is 15.0 MeV instead of 14.7)")
	args = parser.parse_args()

	try:
		energy = (float(args.energy), 0, 0)
	except ValueError:
		energy = args.energy
	convert_energy_to_rhoR(energy, args.shell_material, args.shell_density,
	                       args.shell_temperature, args.secondary,
	                       args.gold, args.tantalum, args.uranium, args.aluminum)


if __name__ == "__main__":
	main()
