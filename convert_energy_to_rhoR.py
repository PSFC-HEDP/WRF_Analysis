import argparse

from src.calculate_rhoR import get_ein_from_eout
from src.rhoR_Analysis import rhoR_Analysis


def convert_energy_to_rhoR(
		final_energy: float, shell_material: str, fD: float, f3He: float, birth_energy: float,
		gold: float, tantalum: float, uranium: float, aluminum: float):
	""" print out the ρR that approximately corresponds to a given measured D3He-p energy, given some hohlraum parameters.
	    :param final_energy: the final energy of the D3He protons (MeV)
	    :param shell_material: the material of the capsule shell ("HDC", "SiO2", or "CH")
	    :param fD: the fraction of gas atoms that are deuterium
	    :param f3He: the fraction of gas atoms that are helium-3
	    :param birth_energy: the mean birth energy of the protons
	    :param gold: the amount of gold the particles passed thru (μm)
	    :param tantalum: the amount of tantalum the particles passed thru (μm)
	    :param uranium: the amount of depleted uranium the particles passed thru (μm)
	    :param aluminum: the amount of aluminum the particles passed thru (μm)
	"""
	mean_energy = get_ein_from_eout(final_energy, [
		(gold, "Au"), (tantalum, "Ta"), (uranium, "U"), (aluminum, "Al")])
	if mean_energy != final_energy:
		print(f"Hohlraum-corrected energy is {mean_energy:.2f} MeV")
	analysis_object = rhoR_Analysis(
		shell_mat=shell_material, Ri=1100e-4, Ro=1180e-4, t_Shell=15e-4,
		P0=25, fD=fD, f3He=f3He, E0=birth_energy)

	rhoR, Rcm_value, error = analysis_object.Calc_rhoR(E1=mean_energy)
	print(f"ρR = {rhoR*1e3:.3g} mg/cm^2")


def main():
	parser = argparse.ArgumentParser(
		prog="python convert_energy_to_rhoR.py",
		description = "return the ρR that approximately corresponds to a given measured D3He-p energy, given some hohlraum parameters.")
	parser.add_argument("energy", type=float,
	                    help="the final energy of the D3He protons, in MeV")
	parser.add_argument("shell_material", type=str,
	                    help="the material of the capsule shell (HDC, SiO2, or CH)")
	parser.add_argument("--gold", type=float, default=0,
	                    help="the amount of gold the particles passed through, in μm")
	parser.add_argument("--tantalum", type=float, default=0,
	                    help="the amount of tantalum the particles passed through, in μm")
	parser.add_argument("--uranium", type=float, default=0,
	                    help="the amount of depleted uranium the particles passed through, in μm")
	parser.add_argument("--aluminum", type=float, default=0,
	                    help="the amount of tantalum the particles passed through, in μm")
	parser.add_argument("--secondary", action="store_true",
	                    help="to treat the protons as secondary reactions (in which case the mean birth energy is 15.0 MeV instead of 14.7)")
	args = parser.parse_args()

	E0 = 15.0 if args.secondary else 14.7
	fD, f3He = (1.00, 0.) if args.secondary else (.67, .33)

	convert_energy_to_rhoR(args.energy, args.shell_material, fD, f3He, E0,
	                       args.gold, args.tantalum, args.uranium, args.aluminum)


if __name__ == "__main__":
	main()
