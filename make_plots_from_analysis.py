from __future__ import annotations

import argparse
import csv
import os
import re
from collections import OrderedDict
from math import sqrt, pi, nan, inf
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from numpy.typing import NDArray
from scipy import optimize

from load_info_from_nif_database import normalize_shot_number
from src.calculate_rhoR import perform_hohlraum_correction, calculate_rhoR, Layer
from src.gaussian import Quantity, Peak

# matplotlib.use("qtagg")
np.seterr(all="raise", under="warn")

ROOT = 'data'
σWRF = .159
δσWRF = .014


def make_plots_from_analysis(folders: list[str], show_plots: bool):
	""" take the analysis .csv files created by AnalyzeCR39 in a given series of folders, and
	    generate a bunch of plots and tables summarizing the information therein.
	    :param folders: a list of subdirectories in data/ to search for analysis results
	    :param show_plots: whether to show the plots as they’re generated in addition to saving them to disk
	"""
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
	compression_means = []
	compression_rhoRs = []
	spectra = []
	for i, folder in enumerate(folders):
		if i > 0 and len(folder) < 7: # allow user to only specify the last few digits when most of the foldername is the same
			folders[i] = folders[i-1][:-len(folder)] + folder

	# first, load the analyzed data
	for i, folder_name in enumerate(folders): # for each specified folder
		folder = os.path.join(ROOT, folder_name)
		assert os.path.isdir(folder), f"El sistema no puede encontrar la ruta espificada: '{folder}'"

		for subfolder, _, _ in os.walk(folder): # and any subfolders inside it
			for filename in os.listdir(subfolder): # scan all files inside that folder
				if re.fullmatch(r'(A|N|Om?)\d{6}-?\d{3}.csv', filename): # if it is a shot summary file

					with open(os.path.join(subfolder, filename), encoding="utf8") as f:
						shot_day, shot_number = filename[:-4].split('-')

						for row in f.readlines(): # read all the wrf summaries out of it
							print(re.sub(r"[|:±]", " ", row).split())
							line_of_site, position, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error \
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
							rhoRs.append([float(rhoR_value), float(rhoR_error), float(rhoR_error)])
							compression_yields.append([0, 0, 0])
							compression_means.append([nan, inf, inf])
							compression_rhoRs.append([nan, inf, inf])

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
						elif re.fullmatch(r'(DIM-?)?(0+-0+|0?90-(0?78|124|315))|TIM[1-6](-(4|8|12))?|(NDI-)?P2', identifier):
							line_of_site = identifier
						elif re.fullmatch(r'(Pos-?)?[1-4]|(4|8|12):00', identifier):
							position = identifier[-1]
						elif re.fullmatch(r'134\d{5}|[gG][0-2]\d{2}', identifier):
							wrf_number = identifier
						elif re.fullmatch(r'(left|right|top|bottom|full)', identifier):
							flag = identifier

					if shot_number is None:
						raise ValueError(f"no shot number found in {identifiers}")
					if line_of_site is None:
						raise ValueError(f"no line of sight found in {identifiers}")
					if re.fullmatch(r"TIM[1-6]-(4|8|12)", line_of_site):
						line_of_site, position = re.fullmatch(r"(TIM[1-6])-(4|8|12)", line_of_site).group(1, 2)
					elif re.fullmatch(r"\D*\d+-\d+", line_of_site): # standardize the DIM names if they're too long
						theta, phi = re.fullmatch(r"\D*(\d+)-(\d+)", line_of_site).group(1, 2)
						line_of_site = f"{int(theta):02d}-{int(phi):03d}"

					print(f"{wrf_number} – {shot_day}-{shot_number} {line_of_site}:{position} {flag}")

					# read thru the analysis file
					with open(os.path.join(subfolder, filename), newline='') as f:

						shock: Optional[Peak] = None
						gaussian_fit = True
						we_have_reachd_the_spectrum_part = False
						spectrum = []

						for row in csv.reader(f):
							if len(row) == 0:
								continue

							if not we_have_reachd_the_spectrum_part:
								if row[0] == 'Value (gaussian fit):':
									try:
										shock = Peak(
											mean=Quantity(float(row[1]), 0),
											sigma=Quantity(float(row[2]), 0),
											yeeld=Quantity(float(row[3]), 0))
									except ValueError:
										gaussian_fit = False

								elif row[0] == 'Value (raw stats):' and shock is None:
									shock = Peak(
										mean=Quantity(float(row[1]), 0),
										sigma=Quantity(float(row[2]), 0),
										yeeld=Quantity(float(row[3]), 0))

								elif row[0] == '    Random:' or row[0] == '    Systematic calib:':
									shock.mean.error += float(row[1])**2  # start by summing the errors as variances
									shock.sigma.error += float(row[2])**2
									shock.yeeld.error += (float(row[3][:-1])*shock.yeeld.value/100)**2

								elif row[0] == 'Energy 	 Yield/MeV 	Stat. Error':
									we_have_reachd_the_spectrum_part = True

							else:
								values = row[0].split()
								spectrum.append([float(v) for v in values])

					# convert variances to sigmas
					shock.mean.error = sqrt(shock.mean.error)
					shock.sigma.error = sqrt(shock.sigma.error)
					shock.yeeld.error = sqrt(shock.yeeld.error)

					# clean up the extracted spectrum
					spectrum = np.array(spectrum)
					spectrum = spectrum[spectrum[:, 2] != 0, :] # remove any points with sus error bars
					spectrum = spectrum[2:, :] # remove the two lowest bins because Fredrick’s program calculates them incorrectly

					# try to fit the compression peak
					if gaussian_fit:
						compression = fit_skew_gaussian(spectrum, 0, shock.mean.value - 2*shock.sigma.value)
					else:
						compression = Peak(Quantity(0, 0), Quantity(nan, inf), Quantity(nan, inf))
					good_compression_fit = compression.yeeld.value > shock.yeeld.value and compression.mean.value > spectrum[0, 0]
					if not good_compression_fit:
						compression = Peak(Quantity(nan, inf), Quantity(nan, inf), Quantity(nan, inf))

					# think about some flags
					any_hohlraum = any(parameters["hohlraum"].values())
					any_clipping_here = any(indicator in filename for indicator in parameters["clipping"])
					any_overlap_here = any(indicator in filename for indicator in parameters["overlap"])

					# plot its spectrum
					plt.figure(figsize=(10, 4))
					plt.grid()
					plt.axhline(0, color='k', linewidth=1)
					if gaussian_fit:
						x = np.linspace(0, 20, 1000)
						plt.plot(x, gaussian(
							x, shock.yeeld.value, shock.mean.value, shock.sigma.value),
						         color='#C00000')
						if compression.yeeld.value > 0:
							plt.plot(x, skew_gaussian(
								x, compression.yeeld.value, compression.mean.value, compression.sigma.value),
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
					if show_plots:
						plt.show()
					plt.close()

					# do the ρR analysis for both the shock and compression peak
					if '90' in line_of_site and any(parameters["hohlraum"].values()) > 0:
						if position in parameters["hohlraum"]:
							hohlraum_layers = parameters["hohlraum"][position]
						else:
							hohlraum_layers = parameters["hohlraum"][""]
					else:
						hohlraum_layers = []
					shock = perform_hohlraum_correction(hohlraum_layers, shock)
					shock_rhoR = calculate_rhoR(
						shock.mean, shot_day+shot_number, parameters)
					if good_compression_fit:
						compression = perform_hohlraum_correction(hohlraum_layers, compression)
						compression_rhoR = calculate_rhoR(
							compression.mean, shot_day+shot_number, parameters)
					else:
						compression_rhoR = Quantity(nan, nan)

					# test_mean, _, _ = perform_correction(layers, 5, 0, 0)
					# test_rhoR, _, _, _ = calculate_rhoR(test_mean, 0, shot_day+shot_number, parameters)
					# print(f"\tthe maximum measurable ρR is {test_rhoR:.1f} mg/cm^2")

					# summarize it
					shot_days.append(shot_day)
					shot_numbers.append(shot_number)
					lines_of_site.append(line_of_site)
					positions.append(position)
					flags.append(flag)
					overlapd.append(any_overlap_here)
					clipd.append(any_clipping_here)
					spectra.append(spectrum)

					means.append([shock.mean.value, shock.mean.error, shock.mean.error]) # and add the info to the list
					sigmas.append([shock.sigma.value, shock.sigma.error, shock.sigma.error])
					yields.append([shock.yeeld.value, shock.yeeld.error, shock.yeeld.error])
					rhoRs.append([shock_rhoR.value, shock_rhoR.error, shock_rhoR.error]) # tho the hotspot and shell components are probably not reliable...
					compression_yields.append([compression.yeeld.value, compression.yeeld.error, compression.yeeld.error])
					compression_means.append([compression.mean.value, compression.mean.error, compression.mean.error])
					compression_rhoRs.append([compression_rhoR.value, compression_rhoR.error, compression_rhoR.error])

	assert len(means) > 0, "No datum were found."
	means = np.array(means)
	sigmas = np.array(sigmas)
	yields = np.array(yields)
	rhoRs = np.array(rhoRs)
	compression_yields = np.array(compression_yields)
	compression_means = np.array(compression_means)
	compression_rhoRs = np.array(compression_rhoRs)
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

	base_directory = os.path.join(ROOT, folders[0])

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
	workbook = openpyxl.Workbook()
	worksheet = workbook.active
	for i in range(len(spectra)):
		worksheet.cell(1, 4*i + 1).value = labels[i].replace("\n", " ")
		worksheet.merge_cells(start_row=1, end_row=1, start_column=4*i + 1, end_column=4*i + 3)
		worksheet.cell(2, 4*i + 1).value = "Energy (MeV)"
		worksheet.cell(2, 4*i + 2).value = "Spectrum (MeV^-1)"
		worksheet.cell(2, 4*i + 3).value = "Error bar (MeV^-1)"
		spectrum = spectra[i]
		for j in range(spectrum.shape[0]):
			for k in range(spectrum.shape[1]):
				worksheet.cell(3 + j, 4*i + 1 + k).value = spectrum[j, k]
	workbook.save(os.path.join(base_directory, f"{shot_days[0]} WRF spectra.xlsx"))

	# print out a table, and also save the condensed results in a csv file
	print()
	with open(os.path.join(base_directory, 'wrf_analysis.csv'), 'w') as f:
		print("|  WRF              |  Yield              |Mean energy (MeV)| ρR (mg/cm^2)  |")
		print("|-------------------|---------------------|----------------|----------------|")
		f.write(
			"WRF, Yield, Yield unc., Mean energy (MeV), Mean energy unc. (MeV), "
			"Sigma (MeV), Sigma unc. (MeV), Width (keV), Width unc. (keV), "
			"Rho-R (mg/cm^2), Rho-R unc. (mg/cm^2), "
			"Compres. yield, Compres. yield unc., Compres. mean (MeV), Compres. mean unc. (MeV), "
			"Compres. rho-R (mg/cm^2), Compres. rho-R unc. (mg/cm^2)"
			"\n")
		for i in range(len(labels)):
			label = labels[i]
			yield_value, yield_error, _ = yields[i]
			mean_value, mean_error, _ = means[i]
			rhoR_value, rhoR_error, _ = rhoRs[i]
			sigma_value, sigma_error, _ = sigmas[i]
			width_value, width_error, _ = widths[i]
			temp_value, temp_error, _ = temps[i]
			compression_yield_value, compression_yield_error, _ = compression_yields[i]
			compression_mean_value, compression_mean_error, _ = compression_means[i]
			compression_rhoR_value, compression_rhoR_error, _ = compression_rhoRs[i]
			label = label.replace('\n', ' ')
			print("|  {:15.15s}  |  {:#.2g} ± {:#.2g}  |  {:5.2f} ± {:4.2f}  |  {:5.1f} ± {:4.1f}  |".format(
				label, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error))
			if i + 1 < len(labels) and shots[i+1] != shots[i]:
				print()
			f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
				label, yield_value, yield_error, mean_value, mean_error,
				sigma_value, sigma_error, width_value, width_error,
				rhoR_value, rhoR_error,
				compression_yield_value, compression_yield_error,
				compression_mean_value, compression_mean_error,
				compression_rhoR_value, compression_rhoR_error))
	print()

	# make the error bars asymmetrick if there are issues with the data
	if np.any(overlapd):
		for affected_values in [yields, compression_yields, secondary_rhoRs, secondary_temps]:
			affected_values[overlapd, 1] = 2e20
		for affected_values in [sigmas, widths, temps]:
			affected_values[overlapd, 0] = nan
	if np.any(clipd):
		for affected_values in [yields, compression_yields, compression_rhoRs, secondary_rhoRs, secondary_temps, rhoRs]:
			affected_values[clipd, 1] = 2e20
		means[clipd, 2] = 2e20

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
	if np.any(np.isfinite(compression_yields[:, 0])):
		yield_descriptor = "Shock yield"
		mean_descriptor = "Shock peak energy"
		rhoR_descriptor = "Shock ρR"
	else:
		yield_descriptor = "Yield"
		mean_descriptor = "Mean energy"
		rhoR_descriptor = "Total ρR"
	for label, filetag, values in [
		(f"{yield_descriptor}", 'yield', yields),
		(f"{mean_descriptor} (MeV)", 'mean', means),
		(f"{rhoR_descriptor} (mg/cm^2)", 'rhoR_total', rhoRs),
		("Fuel ρR (mg/cm^2)", 'rhoR_fuel', secondary_rhoRs),
		("Compression yield", 'yield_compression', compression_yields),
		("Compression ρR (mg/cm^2)", 'rhoR_compression', compression_rhoRs),
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

		if np.all(values[:, 0] == 0):
			continue
		max_value = np.max(values[:, 0]) # figure out the scale and limits
		min_value = np.min(values[:, 0], where=values[:, 0] != 0, initial=inf)
		tops = values[:, 0] + values[:, 1]
		bottoms = values[:, 0] - values[:, 2]
		points = np.stack([bottoms, values[:, 0], tops])
		measurable = values[:, 0] - np.minimum(values[:, 1], values[:, 2]) >= 0

		if np.any(measurable):
			valid = (points > -1e20) & (points < 1e20) & \
			        np.stack([measurable, np.full(measurable.shape, True), measurable])
		else:
			valid = (points > -1e20) & (points < 1e20)
		plot_top = np.max(points, where=valid, initial=-inf)
		plot_bottom = np.min(points, where=valid, initial=inf)
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
		plt_set_locators()
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
		plt.grid()
		plt.tight_layout()
		plt.savefig(os.path.join(base_directory, f'summary_asymmetry.png'), dpi=300)
		plt.savefig(os.path.join(base_directory, f'summary_asymmetry.eps'))

	# show plots
	if show_plots:
		plt.show()
	plt.close('all')


def load_rhoR_parameters(folder: str) -> dict[str, Any]:
	""" load the analysis parameters given in the rhoR_parameters.txt file
	    :param folder: the absolute or relative path to the directory with the data we're considering
	    :return: a dictionary containing values for 'ablator thickness', 'hohlraum', and a bunch of other stuff.
	    :raise FileNotFoundError: if the hohlraum.txt file hasn't been created
	"""
	# start by taking information from shot_info.csv
	shot_table = pd.read_csv("shot_info.csv", skipinitialspace=True, index_col="shot number",
	                         dtype={})
	shot_info = shot_table.loc[normalize_shot_number(os.path.basename(folder))]
	params: dict[str, Any] = {}
	for key in ["ablator radius", "ablator thickness", "ablator material", "fill pressure", "deuterium fraction", "helium-3 fraction"]:
		params[key] = shot_info[key]

	# calculate the converged shell thickness
	params["shell thickness"] = params["ablator thickness"]*40.0/200.0  # from "Alex's paper" (idk which)

	# parse the hohlraum layers and booleans
	with open(os.path.join(folder, "hohlraum.txt")) as f:
		hohlraum_codes = re.split(r",\s*", f.read().strip())
	params["hohlraum"] = OrderedDict()
	params["clipping"] = set()
	params["overlap"] = set()
	for hohlraum_code in hohlraum_codes:
		# separate out all of the line of sight keys
		if ":" in hohlraum_code:
			key, layer_set_code = re.split(r"\s*:\s*", hohlraum_code, maxsplit=2)
		else:
			key, layer_set_code = "", hohlraum_code
		# check for clipped spectrum flags
		if "clip" in layer_set_code:
			params["clipping"].add(key)
			layer_set_code = re.sub(r"\s*\(?clip(ping)?\)?\s*", "", layer_set_code)
		# check for track overlap flags
		if "overlap" in layer_set_code:
			params["overlap"].add(key)
			layer_set_code = re.sub(r"\s*\(?(track[ -]?)?overlap(ping)?\)?\s*", "", layer_set_code)
		# parse the material thicknesses
		layers: list[Layer] = []
		for layer_code in re.split(r"\s+", layer_set_code):
			if len(layer_code) == 0:
				continue
			thickness, _, material = re.fullmatch(r"([0-9.]+)([uμ]m)?([A-Za-z0-9-]+)", layer_code).groups()
			layers.append((float(thickness), material))
		params["hohlraum"][key] = layers

	return params


def gaussian(E, yeeld, mean, sigma):
	""" it’s just a gaussian. """
	return yeeld*np.exp(-(E - mean)**2/(2*sigma**2))/np.sqrt(2*pi*sigma**2)


def skew_gaussian(E_out, yeeld, median, birth_sigma, birth_energy=14.7):
	""" a spectrum that could result from a gaussian D3He peak getting ranged down thru some
	    material, approximately speaking (assume dE/dx \\propto E)
	"""
	valid = E_out**2 + (birth_energy**2 - median**2) > 0
	result = np.empty(E_out.shape)
	E_in = np.sqrt(E_out[valid]**2 + (birth_energy**2 - median**2))
	dEdE = E_out[valid]/E_in
	result[valid] = dEdE*gaussian(E_in, yeeld, birth_energy, birth_sigma)
	result[~valid] = 0
	return result


def fit_skew_gaussian(spectrum: NDArray[float], lower_bound: float, upper_bound: float) -> Peak:
	""" do a gaussian fit, accounting for how the shape changes and the peak shifts when the
	    spectrum has been ranged down to where σ !<< E (Fredrick and Alex don’t account for this in
	    their fitting, but I don’t think it’s significant above 7 MeV)
	"""
	spectrum = spectrum[(spectrum[:, 0] > lower_bound) & (spectrum[:, 0] < upper_bound), :]
	rainge = np.ptp(spectrum[:, 0])
	center = np.mean(spectrum[:, 0])
	values, covariances = optimize.curve_fit(
		skew_gaussian, xdata=spectrum[:, 0], ydata=spectrum[:, 1], sigma=spectrum[:, 2],
		p0=(abs(np.max(spectrum[:, 1]))*rainge, center, rainge/4),
		bounds=(0, inf), absolute_sigma=True)
	return Peak(yeeld=Quantity(values[0], sqrt(covariances[0, 0])),
	            mean=Quantity(values[1], sqrt(covariances[1, 1])),
	            sigma=Quantity(values[2], sqrt(covariances[2, 2])))


def plt_set_locators() -> None:
	try:
		plt.locator_params(steps=[1, 2, 5, 10])
	except TypeError:
		pass


def main():
	parser = argparse.ArgumentParser(
		prog="make_plots_from_analysis",
		description = "take the analysis .csv files created by AnalyzeCR39 in a given series of folders, and "
		              "generate a bunch of plots and tables summarizing the information therein.")
	parser.add_argument(
		"folders", type=str,
		help="A list of subdirectories in data/ to search for analysis results. If you have multiple folders, separate "
		     "them with commas. If you're doing multiple shots from the same day, you don't have to include the day "
		     "part of the shot number after the first one (for example, 'N220420-001,-002,-003').")
	parser.add_argument(
		"--show", action="store_true",
		help="to show the plots as they're generated in addition to saving them in the subdirectory."
	)
	args = parser.parse_args()

	make_plots_from_analysis(args.folders.split(","), args.show)


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


if __name__ == "__main__":
	main()
