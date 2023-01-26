import csv
import os
import re
from collections import OrderedDict
from math import sqrt, pi, nan, inf
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter as xls
from matplotlib.ticker import ScalarFormatter
from scipy import integrate

from WRF_Analysis.Analysis.rhoR_Analysis import rhoR_Analysis

import matplotlib
matplotlib.use("qtagg")

# FOLDERS = ["N221128-001"]
FOLDERS = ["I_Stag_Sym_HyECpl"]

SHOW_PLOTS = False

ROOT = 'data'
σWRF = .159
δσWRF = .014
np.seterr(all="raise", under="warn")


class FixedOrderFormatter(ScalarFormatter):
	"""Formats axis ticks using scientifick notacion with a constant ordre of 
	magnitude"""
	def __init__(self, order_of_mag=0, use_offset=True, use_math_text=False):
		self._order_of_mag = order_of_mag
		ScalarFormatter.__init__(self, useOffset=use_offset,
		                         useMathText=use_math_text)
	def _set_orderOfMagnitude(self, _):
		"""Ovre-riding this to avoid having orderOfMagnitude reset elsewhere"""
		self.orderOfMagnitude = self._order_of_mag


def plt_set_locators() -> None:
	try:
		plt.locator_params(steps=[1, 2, 5, 10])
	except TypeError:
		pass


def get_ein_from_eout(eout: float, layers: list[tuple[float, str]]) -> float:
	""" do the reverse stopping power calculation """
	energy = eout # [MeV]
	for thickness, formula in layers[::-1]:
		data = np.loadtxt(f"res/tables/stopping_power_protons_{formula}.csv", delimiter=',')
		energy_axis = data[:, 0]/1e3 # [MeV]
		dEdx = data[:, 1]/1e3 # [MeV/μm]
		energy = integrate.odeint(
			func =lambda E, x: np.interp(E, energy_axis, dEdx),
			y0   =energy,
			t    =[0, thickness]
		)[-1, 0] # type: ignore
	return energy


def get_dein_from_deout(deout: float, eout: float, layers: list[tuple[float, str]]) -> float:
	""" do a derivative of the stopping power calculation """
	left = get_ein_from_eout(eout - deout, layers)
	rite = get_ein_from_eout(eout + deout, layers)
	return (rite - left)/2


def perform_correction(layers: list[tuple[float, str]],
                       mean_energy: float, mean_energy_error: float, sigma: float) -> tuple[float, float, float]:
	""" correct some spectral properties for a hohlraum """
	if len(layers) > 0:
		print(f"\tCorrecting for a {''.join(map(lambda t:t[1], layers))} hohlraum: {mean_energy:.2f} ± {sigma:.2f} becomes ", end='')
		mean_energy_error = get_dein_from_deout(mean_energy_error, mean_energy, layers)
		sigma = get_dein_from_deout(sigma, mean_energy, layers)
		mean_energy = get_ein_from_eout(mean_energy, layers)
		print(f"{mean_energy:.2f} ± {sigma:.2f} MeV")
	return mean_energy, mean_energy_error, sigma


def calculate_rhoR(mean_energy: float, mean_energy_error: float,
                   shot_name: str, params: dict[str, Any],
                   rhoR_objects: dict[str, Any] = {}):
	""" calcualte the rhoR using whatever tecneke makes most sense.
		return rhoR, error, hotspot_component, shell_component (mg/cm^2)
	"""
	if shot_name.startswith("O"): # if it's an omega shot
		if shot_name not in rhoR_objects:
			rhoR_objects[shot_name] = []
			for ρ, Te in [(20, 500), (30, 500), (10, 500), (20, 250), (20, 750)]:
				try:
					data = np.loadtxt(f"res/tables/stopping_range_protons_D_plasma_{ρ}gcc_{Te}eV.txt", skiprows=4)
				except IOError:
					print(f"!\tDid not find res/tables/stopping_range_protons_D_plasma_{ρ}gcc_{Te}eV.txt.")
					rhoR_objects.pop(shot_name)
					break
				else:
					rhoR_objects[shot_name].append([data[::-1, 1], data[::-1, 0]*1000]) # load a table from Frederick's program

		if shot_name in rhoR_objects:
			energy_ref, rhoR_ref = rhoR_objects[shot_name][0]
			best_gess = np.interp(mean_energy, energy_ref, rhoR_ref) # calculate the best guess based on 20g/cc and 500eV
			error_bar = 0
			for energy in [mean_energy - mean_energy_error, mean_energy, mean_energy + mean_energy_error]:
				for energy_ref, rhoR_ref in rhoR_objects[shot_name]: # then iterate thru all the other combinations of ρ and Te
					perturbd_gess = np.interp(energy, energy_ref, rhoR_ref)
					if abs(perturbd_gess - best_gess) > error_bar:
						error_bar = abs(perturbd_gess - best_gess)
			return best_gess, error_bar, nan, nan

		else:
			return nan, nan, nan, nan

	elif shot_name.startswith("N"): # if it's a NIF shot
		if shot_name not in rhoR_objects: # try to load the rhoR analysis parameters
			rhoR_objects[shot_name] = rhoR_Analysis(
				shell_mat   = params['shell_material'],
				Ri          = float(params['Ri'])*1e-4,
				Ri_err      = 0.1e-4,
				Ro          = float(params['Ro'])*1e-4,
				Ro_err      = 0.1e-4,
				fD          = float(params['fD']),
				fD_err      = min(float(params['fD']), 1e-2),
				f3He        = float(params['f3He']),
				f3He_err    = min(float(params['f3He']), 1e-2),
				P0          = float(params['P']),
				P0_err      = 0.1,
				t_Shell     = float(params['shell_thickness'])*1e-4,
				t_Shell_err = float(params['shell_thickness'])/2*1e-4,
				E0          = 14.7 if float(params['f3He']) > 0 else 15.0,
			)

		if shot_name in rhoR_objects: # if you did or they were already there, calculate the rhoR
			analysis_object = rhoR_objects[shot_name]
			rhoR, Rcm_value, error = analysis_object.Calc_rhoR(E1=mean_energy, dE=mean_energy_error)
			hotspot_component, shell_component, ablated_component = analysis_object.rhoR_Parts(Rcm_value)
			return np.multiply(1000, [rhoR, error, hotspot_component, shell_component]) # convert from g/cm2 to mg/cm2
		else:
			return nan, nan, nan, nan

	else:
		raise NotImplementedError(shot_name)


def load_rhoR_parameters(folder: str) -> dict[str, Any]:
	params: dict[str, Any] = {}

	# load each line as an attribute
	with open(os.path.join(folder, 'rhoR_parameters.txt')) as f:
		for line in f.readlines():
			key, value = re.split(r"\s*=\s*", line.strip())
			value = re.sub(r" (um|μm|atm)", "", value)  # strip off units
			params[key] = value

	# parse the hohlraum layers
	hohlraum_codes = re.split(r",\s*", params["hohlraum"])
	keyed_layer_sets = OrderedDict()
	for hohlraum_code in hohlraum_codes:
		if ":" in hohlraum_code:
			key, layer_set_code = re.split(r"\s*:\s*", hohlraum_code, maxsplit=2)
		else:
			key, layer_set_code = "", hohlraum_code
		layer_set: list[tuple[float, str]] = []
		for layer_code in re.split(r"\s+", layer_set_code):
			thickness, _, material = re.fullmatch(r"([0-9.]+)([uμ]m)?([A-Za-z0-9-]+)", layer_code).groups()
			layer_set.append((float(thickness), material))
		keyed_layer_sets[key] = layer_set
	params["hohlraum"] = keyed_layer_sets

	# parse the comma-separated flags
	for key in ["clipping", "overlap"]:
		if key in params:
			params[key] = set(re.split(r",\s*", params[key]))
		else:
			params[key] = set()

	return params


def combine_measurements(*args):
	nume = 0
	deno = 0
	for value, unc in args:
		nume += value/unc**2
		deno += 1/unc**2
	return nume/deno, sqrt(1/deno)


def main():
	shot_days = []
	shot_numbers = []
	lines_of_site = []
	positions = []
	flags = []
	overlapd = []
	clipd = []
	means = []
	sigmas = []
	yields = []
	rhoRs = []
	compression_yields = []
	spectra = []
	for i, folder in enumerate(FOLDERS):
		if i > 0 and len(folder) < 7: # allow user to only specify the last few digits when most of the foldername is the same
			FOLDERS[i] = FOLDERS[i-1][:-len(folder)] + folder

	# first, load the analyzed data
	for i, folder_name in enumerate(FOLDERS): # for each specified folder
		folder = os.path.join(ROOT, folder_name)
		assert os.path.isdir(folder), f"El sistema no puede encontrar la ruta espificada: '{folder}'"

		for subfolder, _, _ in os.walk(folder): # and any subfolders inside it
			for filename in os.listdir(subfolder): # scan all files inside that folder
				if re.fullmatch(r'(A|N|Om?)\d{6}-?\d{3}.csv', filename): # if it is a shot summary file

					with open(os.path.join(subfolder, filename), encoding="utf8") as f:
						shot_day, shot_number = filename[:-4].split('-')

						for row in f.readlines(): # read all the wrf summaries out of it
							print(re.sub(r"[|:±]", " ", row).split())
							line_of_site, position, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error\
								= re.sub(r"[|:±]", " ", row).split()

							shot_days.append(shot_day)
							shot_numbers.append(shot_number)
							lines_of_site.append(line_of_site)
							positions.append(position)
							flags.append('')
							overlapd.append(False)
							clipd.append(False)
							means.append([float(mean_value), float(mean_error), float(mean_error)])
							sigmas.append([0, 0, 0])
							yields.append([float(yield_value), float(yield_error), float(yield_error)])
							rhoRs.append([float(rhoR_value), float(rhoR_error), float(rhoR_error), 0, 0])

				elif re.fullmatch(r'.*ANALYSIS.*\.csv', filename): # if it is an analysis file

					parameters = load_rhoR_parameters(folder)

					shot_day, shot_number, line_of_site, position, wrf_number = None, None, None, None, None
					flag = ''
					identifiers = [folder_name] + filename[:-4].split('_') # figure out what wrf this is
					for identifier in reversed(identifiers):
						if re.fullmatch(r'N\d{6}-?\d{3}-?999', identifier):
							shot_day, shot_number, _ = identifier.split('-')
						elif re.fullmatch(r'O[mM]?2\d{5}', identifier):
							shot_day = identifier
						elif re.fullmatch(r'O?1?\d{5}', identifier):
							shot_number = identifier
						elif re.fullmatch(r'(DIM-?)?(0+-0+|0?90-(0?78|124|315))|TIM[1-6]', identifier):
							line_of_site = identifier
						elif re.fullmatch(r'(Pos-?)?[1-4]', identifier):
							position = identifier[-1]
						elif re.fullmatch(r'134\d{5}|[gG][0-2]\d{2}', identifier):
							wrf_number = identifier
						elif re.fullmatch(r'(left|right|top|bottom|full)', identifier):
							flag = identifier

					assert None not in [shot_number, line_of_site] is not None, identifiers
					if len(line_of_site) > 6: # standardize the DIM names if they're too long
						line_of_site = "{:02d}-{:03d}".format(*(
							int(angle) for angle in re.fullmatch(r"\D*(\d+)-(\d+)", line_of_site).group(1, 2)))

					print(f"{wrf_number} – {shot_day}-{shot_number} {line_of_site}:{position} {flag}")

					with open(os.path.join(subfolder, filename), newline='') as f: # read thru its contents

						mean_value, sigma_value, yield_value = None, None, None
						mean_variance, sigma_variance, yield_variance = 0, 0, 0
						gaussian_fit = True
						we_have_reachd_the_spectrum_part = False
						spectrum = []

						for row in csv.reader(f):
							if len(row) == 0:
								continue

							if not we_have_reachd_the_spectrum_part:
								if row[0] == 'Value (gaussian fit):':
									try:
										mean_value = float(row[1])
										sigma_value = float(row[2])
										yield_value = float(row[3])
									except ValueError:
										gaussian_fit = False

								elif row[0] == 'Value (raw stats):' and mean_value is None:
									mean_value = float(row[1])
									sigma_value = float(row[2])
									yield_value = float(row[3])

								elif row[0] == '    Random:' or row[0] == '    Systematic calib:':
									mean_variance += float(row[1])**2
									sigma_variance += float(row[2])**2
									yield_variance += (float(row[3][:-1])*yield_value/100)**2

								elif row[0] == 'Energy 	 Yield/MeV 	Stat. Error':
									we_have_reachd_the_spectrum_part = True

							else:
								values = row[0].split()
								spectrum.append([float(v) for v in values])

					spectrum = np.array(spectrum)

					spectrum = spectrum[spectrum[:, 2] != 0, :] # remove any points with sus error bars
					spectrum = spectrum[1:, :] # remove the lowest bin

					spectra.append(spectrum)

					any_hohlraum = any(parameters["hohlraum"].values())
					any_clipping_here = any(indicator in filename for indicator in parameters["clipping"])
					any_overlap_here = any(indicator in filename for indicator in parameters["overlap"])

					plt.figure(figsize=(10, 4)) # plot its spectrum
					plt.plot([0, 20], [0, 0], 'k', linewidth=1)
					if gaussian_fit:
						x = np.linspace(0, 20, 1000)
						μ, σ, Σ = mean_value, sigma_value, yield_value
						plt.plot(x, Σ*np.exp(-(x - μ)**2/(2*σ**2))/np.sqrt(2*pi*σ**2),
						         color='#C00000')
					plt.errorbar(x=spectrum[:, 0],
					             y=spectrum[:, 1],
					             yerr=spectrum[:, 2],
					             fmt='.', color='#000000', elinewidth=1, markersize=6)
					plt.axis([4, 18, min(0, np.min(spectrum[:, 1] + spectrum[:, 2])), None])
					plt.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
					plt.xlabel("Energy after hohlraum wall (MeV)" if any_hohlraum else "Energy (MeV)")
					plt.ylabel("Yield (MeV⁻¹)")
					if flag != '':
						plt.title(f"{line_of_site}, position {position} ({flag})")
					elif position is not None:
						plt.title(f"{line_of_site}, position {position}")
					else:
						plt.title(f"{shot_number}, {line_of_site}")
					plt_set_locators()
					plt.tight_layout()
					plt.savefig(os.path.join(subfolder, filename+'_spectrum.png'), dpi=300)
					plt.savefig(os.path.join(subfolder, filename+'_spectrum.eps'))
					if SHOW_PLOTS:
						plt.show()
					plt.close()

					if yield_value != 0: # summarize it
						shot_days.append(shot_day)
						shot_numbers.append(shot_number)
						lines_of_site.append(line_of_site)
						positions.append(position)
						flags.append(flag)
						overlapd.append(any_overlap_here)
						clipd.append(any_clipping_here)

						mean_error = sqrt(mean_variance)
						sigma_error = sqrt(sigma_variance)
						yield_error = sqrt(yield_variance)

						# correct for the hohlraum
						if '90' in line_of_site and any(parameters["hohlraum"].values()) > 0:
							if position in parameters["hohlraum"]:
								layers = parameters["hohlraum"][position]
							else:
								layers = parameters["hohlraum"][""]
						else:
							layers = []

						mean_value, mean_error, sigma_value = perform_correction(
								layers, mean_value, mean_error, sigma_value)
						rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR = calculate_rhoR(
							mean_value, mean_error, shot_day+shot_number, parameters) # calculate ρR if you can

						# test_mean, _, _ = perform_correction(layers, 5, 0, 0)
						# test_rhoR, _, _, _ = calculate_rhoR(test_mean, 0, shot_day+shot_number, parameters)
						# print(f"\tthe maximum measurable ρR is {test_rhoR:.1f} mg/cm^2")

						means.append([mean_value, mean_error, mean_error]) # and add the info to the list
						sigmas.append([sigma_value, sigma_error, sigma_error])
						yields.append([yield_value, yield_error, yield_error])
						rhoRs.append([rhoR_value, rhoR_error, rhoR_error, hotspot_rhoR, shell_rhoR]) # tho the hotspot and shell components are probably not reliable...

						compression_value = np.sum(spectrum[:, 1], where=spectrum[:, 0] < 11)
						compression_error = yield_error/yield_value*abs(compression_value)
						compression_yields.append([compression_value, compression_error, compression_error])

					else:
						print("!\tthis one had an invalid analysis.")

	assert len(means) > 0, "No datum were found."
	means = np.array(means)
	sigmas = np.array(sigmas)
	yields = np.array(yields)
	rhoRs = np.array(rhoRs)
	compression_yields = np.array(compression_yields)
	shot_days = np.array(shot_days)
	shot_numbers = np.array(shot_numbers)
	lines_of_site = np.array(lines_of_site)
	positions = np.array(positions)

	# compose labels of the appropirate specificity
	shots = []
	labels = []
	for i in range(len(shot_days)):
		shot_day = shot_days[i]
		shot_number = shot_numbers[i]

		if positions[i] is None:
			location = lines_of_site[i]
		else:
			location = f"{lines_of_site[i]}:{positions[i]}"
		if len(set(shot_days)) > 1 and len(shot_number) < 4:
			shots.append(f"{shot_day}-{shot_number}")
		else:
			shots.append(shot_number)

		if len(set(shot_days)) > 1 or len(set(shot_numbers)) > 1:
			labels.append(f"{shots[-1]}\n{location}")
		else:
			labels.append(f"{location}")
		if len(set(flags)) > 1:
			labels[-1] += f" ({flags[i]})"
		if len(labels[-1]) < 13:
			labels[-1] = labels[-1].replace('\n', ' ')

	shots = np.array(shots)

	# convert sigmas to widths and temperatures
	widths = sigmas*2.355e3
	temps = np.empty(sigmas.shape)
	temps[:, 0] = (np.sqrt(np.maximum(0, sigmas[:, 0]**2 - σWRF**2))/76.68115805e-3)**2
	temps[:, 1] = np.sqrt((2*sigmas[:, 0]*sigmas[:, 1])**2 + (2*σWRF*δσWRF)**2)/76.68115805e-3**2
	temps[:, 2] = temps[:, 1]

	base_directory = os.path.join(ROOT, FOLDERS[0])

	# load any results we got from Patrick's secondary analysis
	try:
		secondary_stuff = np.atleast_2d(np.loadtxt(os.path.join(base_directory, f'Te.txt')))
	except IOError:
		secondary_stuff = None # but it's okey if there is none
	if secondary_stuff is None or np.all(np.isnan(secondary_stuff)):
		secondary_stuff = np.full((means.shape[0], 6), nan)
		np.savetxt(os.path.join(base_directory, f'Te.txt'), secondary_stuff) # type: ignore
	assert secondary_stuff.shape[0] == means.shape[0], "This secondary analysis file has the rong number of entries"
	secondary_rhoRs = secondary_stuff[:, 0:3]
	secondary_temps = secondary_stuff[:, 3:6]

	# save the spectra to a csv file
	for i in range(len(spectra)):
		sanitized_label = re.sub(r"[:\s]", "_", labels[i])
		filename = os.path.join(base_directory, f"spectrum_{sanitized_label}.csv")
		np.savetxt(filename, spectra[i],
		           header="Energy after passing through hohlraum (MeV),Spectrum (MeV^-1),Uncertainty (MeV^-1)",
		           delimiter=",", comments="")

	# save the spectra in a spreadsheet
	workbook = xls.Workbook(os.path.join(base_directory, f"{shot_days[0]} WRF spectra.xlsx"))
	worksheet = workbook.add_worksheet()
	for i in range(len(spectra)):
		worksheet.merge_range(0, 4*i, 0, 4*i+2, labels[i].replace("\n", " "))
		worksheet.write(1, 4*i,   "Energy (MeV)")
		worksheet.write(1, 4*i+1, "Spectrum (MeV^-1)")
		worksheet.write(1, 4*i+2, "Error bar (MeV^-1)")
		spectrum = spectra[i]
		for j in range(spectrum.shape[0]):
			for k in range(3):
				worksheet.write(2+j, 4*i+k, spectrum[j, k])
	workbook.close()

	# print out a table, and also save the condensed results in a csv file
	print()
	with open(os.path.join(base_directory, 'wrf_analysis.csv'), 'w') as f:
		print("|  WRF              |  Yield              |Mean energy (MeV)| ρR (mg/cm^2)  |")
		print("|-------------------|---------------------|----------------|----------------|")
		f.write(
			"WRF, Yield, Yield unc., Mean energy (MeV), Mean energy unc. (MeV), " +
			"Sigma (MeV), Sigma unc. (MeV), Rho-R (mg/cm^2), Rho-R unc. (mg/cm^2), " +
			"Hot-spot rho-R (mg/cm^2), Shell rho-R (mg/cm^2)\n")
		for i in range(len(labels)):
			label = labels[i]
			yield_value, yield_error, _ = yields[i]
			mean_value, mean_error, _ = means[i]
			rhoR_value, rhoR_error, _, hotspot_rhoR, shell_rhoR = rhoRs[i]
			sigma_value, sigma_error, _ = sigmas[i]
			width_value, width_error, _ = widths[i]
			temp_value, temp_error, _ = temps[i]
			label = label.replace('\n', ' ')
			print("|  {:15.15s}  |  {:#.2g} ± {:#.2g}  |  {:5.2f} ± {:4.2f}  |  {:5.1f} ± {:4.1f}  |".format(
				label, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error))
			if i + 1 < len(labels) and shots[i+1] != shots[i]:
				print()
			f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
				label, yield_value, yield_error, mean_value, mean_error, sigma_value, sigma_error,
				rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR))
	print()

	# make the error bars asymmetrick if there are issues with the data
	if np.any(overlapd):
		for affected_values in [yields, compression_yields, secondary_rhoRs, secondary_temps]:
			affected_values[overlapd, 1] = 2e20
	if np.any(clipd):
		for affected_values in [yields, compression_yields, secondary_rhoRs, secondary_temps, rhoRs]:
			affected_values[clipd, 1] = 2e20
		means[clipd, 2] = 2e20

	# for shot in sorted(shots):
	# 	matching_shot = [shot in label for label in loong_labels]
	# 	print(f"{shot} ρR breakdown:")
	# 	print(f"  Total: {np.average(rhoRs[:,0], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")
	# 	print(f"  Fuel: {np.average(rhoRs[:,2], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")
	# 	print(f"  Shell: {np.average(rhoRs[:,3], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")

	# choose label spacing based on number of shots
	if len(shot_numbers) <= 6:
		rotation = 0
		alignment = 'center'
		spacing = 1
	else:
		rotation = 45
		alignment = 'right'
		if len(shot_numbers) <= 15 or len(set(shot_days)) > 1:
			spacing = 0.55
		else:
			spacing = 0.40

	# create the comparison plots
	for label, filetag, values in [
			("Yield", 'yield', yields),
			("Compression yield", 'yield_compression', compression_yields),
			("Mean energy (MeV)", 'mean', means),
			("Total ρR (mg/cm^2)", 'rhoR_total', rhoRs),
			("Fuel ρR (mg/cm^2)", 'rhoR_fuel', secondary_rhoRs),
			("Electron temperature (keV)", 'temperature_electron', secondary_temps),
			("Width (keV)", 'width', widths),
			("Ion temperature (keV)", 'temperature_ion', temps),
			]:
		if values.size == 0 or np.all(np.isnan(values[:, 0])): # skip if there's noting here
			continue

		plt.figure(figsize=(1.5+values.shape[0]*spacing, 4.5)) # then plot it!
		plt.errorbar(x=np.arange(values.shape[0]),
		             y=values[:, 0],
		             yerr=[values[:, 2], values[:, 1]],
		             fmt='.k', elinewidth=2, markersize=12)

		plt.xlim(-1/2, values.shape[0]-1/2)
		plt.xticks(ticks=np.arange(values.shape[0]),
		           labels=labels,
		           rotation=rotation,
		           ha=alignment) # set the tick stuff
		plt.ylabel(label)
		plt.grid()

		max_value = np.max(values[:, 0]) # figure out the scale and limits
		min_value = np.min(values[:, 0], where=values[:, 0] != 0, initial=inf)
		tops = values[:, 0] + values[:, 1]
		bottoms = values[:, 0] - values[:, 2]
		measurable = values[:, 0] - np.minimum(values[:, 1], values[:, 2]) >= 0

		if np.any(measurable & (tops < 1e20)):
			plot_top = np.max(tops[measurable & (tops < 1e20)])
		elif np.any(tops < 1e20):
			plot_top = np.max(tops[tops < 1e20])
		else:
			plot_top = max_value
		if np.any(measurable & (bottoms > 0)):
			plot_bottom = np.min(bottoms[measurable & (bottoms > 0)])
		elif np.any(bottoms > -1e20):
			plot_bottom = np.min(bottoms[bottoms > -1e20])
		else:
			plot_bottom = min_value
		if "MeV" in label and np.all(values < 14.7):
			plot_top = min(15, plot_top)

		if min_value > 0 and max_value/min_value > 10 and plot_bottom > 0:
			plt.yscale('log')
			plt.grid(axis='y', which='minor')
			rainge = plot_top/plot_bottom
			plt.ylim(plot_bottom/rainge**0.15, plot_top*rainge**0.15)
		else:
			rainge = plot_top - plot_bottom
			plt.ylim(plot_bottom - 0.15*rainge, plot_top + 0.15*rainge)

		# if filetag == "yield":
		# 	plt.ylim(-.1e11, 2e11)
		if filetag == "temperature_electron":
			plt.ylim(None, 4)
		plt_set_locators()
		
		plt.tight_layout()
		plt.savefig(os.path.join(base_directory, f'summary_{filetag}.png'), dpi=300)
		plt.savefig(os.path.join(base_directory, f'summary_{filetag}.eps'))

	# now create a line-of-site comparison plot
	compared_lines_of_site = sorted(set(lines_of_site))
	if len(compared_lines_of_site) >= 2:
		compared_shots = sorted(set(shots))
		los_rhoRs = np.empty((len(compared_shots), 2, 3))
		for i, shot in enumerate(compared_shots):
			for j, line_of_site in enumerate(compared_lines_of_site[:2]):
				here = (lines_of_site == line_of_site) & (shots == shot)
				if np.sum(here) > 0 and not np.any(rhoRs[here, 2] == 0):
					los_rhoRs[i, j, 0] = np.average(rhoRs[here, 0], weights=rhoRs[here, 2]**(-2))
					los_rhoRs[i, j, 1] = np.min(rhoRs[here, 1])
					los_rhoRs[i, j, 2] = np.min(rhoRs[here, 2])
				else:
					los_rhoRs[i, j, :] = nan

		plt.figure(figsize=(4.5, 4.5))
		plt.errorbar(y=los_rhoRs[:, 0, 0],
		             yerr=los_rhoRs[:, 0, [2, 1]].T,
		             x=los_rhoRs[:, 1, 0],
		             xerr=los_rhoRs[:, 1, [2, 1]].T,
		             fmt='.', color='#000000', markersize=12)
		plt.axline((0, 0), slope=1, color='k', linewidth=1)
		plt.ylabel(f"ρR on {compared_lines_of_site[0]}")
		plt.xlabel(f"ρR on {compared_lines_of_site[1]}")
		plt.axis('square')
		plt.xlim(0, 220)
		plt.ylim(0, 220)
		plt.grid('on')
		plt.tight_layout()
		plt.savefig(os.path.join(base_directory, f'summary_asymmetry.png'), dpi=300)
		plt.savefig(os.path.join(base_directory, f'summary_asymmetry.eps'))

	# show plots
	if SHOW_PLOTS:
		plt.show()
	plt.close('all')


if __name__ == "__main__":
	main()
