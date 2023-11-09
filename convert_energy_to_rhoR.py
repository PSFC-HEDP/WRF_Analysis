import argparse

from src.calculate_rhoR import calculate_rhoR, Quantity, perform_hohlraum_correction


def convert_energy_to_rhoR(
		final_energy: Quantity, shell_material: str, shell_density: float,
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
	_, intermediate_energy, _ = perform_hohlraum_correction(
		[(gold, "Au"), (tantalum, "Ta"), (uranium, "U"), (aluminum, "Al")],
		((0, 0, 0), final_energy, (0, 0, 0)))
	if intermediate_energy != final_energy:
		print(f"Hohlraum-corrected energy is {intermediate_energy:.2f} MeV")
	rhoR = calculate_rhoR(
		intermediate_energy, "O", {
			"ablator material": shell_material,
			"shell density": shell_density,
			"shell electron temperature": shell_temperature,
			"secondary": secondary,
		}
	)
	print(f"ρR = {rhoR[0]:.3g} ± {rhoR[1]:.3g} mg/cm^2")


def main():
	parser = argparse.ArgumentParser(
		prog="python convert_energy_to_rhoR.py",
		description = "return the ρR that approximately corresponds to a given measured D3He-p energy, given some hohlraum parameters.")
	parser.add_argument("energy", type=float,
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

	convert_energy_to_rhoR((args.energy, 0, 0), args.shell_material, args.shell_density,
	                       args.shell_temperature, args.secondary,
	                       args.gold, args.tantalum, args.uranium, args.aluminum)


if __name__ == "__main__":
	main()
