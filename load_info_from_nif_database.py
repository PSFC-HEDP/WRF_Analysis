import argparse
import os
import re
import string
import time
import webbrowser
from io import StringIO
from math import sqrt, atan, hypot, degrees, isnan, nan, pi
from typing import Optional

import numpy as np
import openpyxl
import pandas as pd

from src.reactivity import get_reactivity_ratio

# the collums and types of shot_info.csv
SHOT_INFO_HEADER = [
	("PI", str), ("DD-n yield", float), ("DD-n temperature", float),
	("ablator material", str), ("ablator thickness", float),
	("ablator radius", float), ("ablator density", float), ("hohlraum material", str),
	("fill gas", str), ("fill pressure", float),
	("deuterium fraction", float), ("helium-3 fraction", float),
	("shot name", str), ("campaign", str), ("subcampaign", str), ("platform", str),
]
# the collums and types of the aux_info.csv files
AUX_INFO_HEADER = [
	("type", str), ("DIM", str), ("position", int),
	("distance", float), ("theta", float), ("phi", float),
	("filter ID", int), ("bert ID", str), ("ernie ID", str),
	("snout configuration", str),
]
# the list of DIMs in the order they appear in the work order template
DIM_LIST = ["TC090-078", "TC090-124", "TC090-315", "TC000-000"]

FRAME_AREA = 1.36e-03  # cm^2
DOWNLOAD_WARN_TIME = 2  # the amount of time it usually takes to download a WebDAV file (s)
DOWNLOAD_QUIT_TIME = 30  # the timeout for downloading a file (s)


def load_info_from_nif_database(shot_number: str, shot_subfolder: str, DD_yield: float,
                                DD_temperature: float, downloads_folder: str):
	""" Load the information about a given shot number from WebDav and any traveler spreadsheets
	    placed in the relevant data/ subdirectory, store the top-level fields in the shot_info.csv
	    file, and generate a simple etch/scan request
	    :param shot_number: the complete 12-digit N number
	    :param shot_subfolder: the directory in which to put information relevant to this shot
	    :param DD_yield: the DD-n yield of this shot, or nan if you want me to get it from WebDav
	    :param DD_temperature: the DD-n ion temperature of this shot, or nan if you want me to get it from WebDav
	    :param downloads_folder: the default downloads folder for the default browser
	"""
	try:
		load_general_webdav_info(
			shot_number, shot_subfolder,
			DD_yield, DD_temperature,
			downloads_folder)
	except FileNotFoundError as e:
		print(f"Error! {e}")
		return

	found_any_travelers = False
	for directory, _, filenames in os.walk(shot_subfolder):
		for filename in filenames:
			if "Traveler" in filename and filename.endswith(".xlsx"):
				try:
					load_traveler_spreadsheet_info(
						shot_number, shot_subfolder,
						os.path.join(directory, filename),
						downloads_folder)
				except SpreadsheetFormatError as e:
					print(f"Error! Couldn't read the traveler spreadsheet at "
					      f"`{os.path.join(directory, filename)}` because {e}")
				except MissingSnoutError as e:
					print(f"Error! {e}")
				else:
					found_any_travelers = True

	if not found_any_travelers:
		print(f"there are no valid traveler spreadsheets in `{shot_subfolder}/`, "
		      f"so I can't get the WRF info or generate a scan request")
	else:
		try:
			generate_etch_scan_request(
				shot_number, shot_subfolder)
		except PermissionError:
			print(f"Error! I don't have permission to copy and edit the workorder template spreadsheet. "
			      f"please close Microsoft Excel.")

	print(f"done! see `{shot_subfolder}` for the etch and scan workorder.")


def load_general_webdav_info(shot_number: str, shot_subfolder: str,
                             DD_yield: float, DD_temperature: float, downloads_folder: str) -> None:
	""" load all of the information about shot_number on WebDav and store it in `shot_info.csv`
	    :param shot_number: the complete 12-digit N number
	    :param shot_subfolder: the directory in which to put information relevant to this shot
	    :param DD_yield: the DD-n yield of this shot, or nan if you want me to get it from WebDav
	    :param DD_temperature: the DD-n ion temperature of this shot, or nan if you want me to get it from WebDav
	    :param downloads_folder: the default downloads folder for the default browser
	    :raise FileNotFoundError: if you don’t specify DD_yield and DD_temperature of this shot but it’s not on WebDav either
	"""
	# start by downloading all of the shot info from WebDAV
	shot_info = download_webdav_file(shot_number, f"reports/SHOT-INPUTS_{shot_number}.csv", downloads_folder)
	shot_info = shot_info.iloc[0]  # simplify this from a DataFrame to a Series since we know there’s only one row
	print(f"loaded {shot_number} ({shot_info['EXPERIMENT_ID']}) inputs from WebDav")

	# extract the atomic fill percentages from the "HIGH_PRESSURE_GAS_FILL"
	gas_fill_name: Optional[str] = None
	for key in shot_info.keys():
		if "GAS_FILL" in key and len(shot_info[key]) > 0:
			gas_fill_name = shot_info[key]
	if gas_fill_name is None:
		gas_fill_name = ""
	atomic_fill_fractions: dict[str, float] = {}
	for component in ["H", "D", "T", "He3", "He4", "N", "O", "Ne", "Ar", "Kr"]:
		percentage = re.search(rf"([0-9.]+)% ?{component}\b", gas_fill_name)
		if percentage is not None:
			atomic_fill_fractions[component] = float(percentage.group(1))/100
		else:
			atomic_fill_fractions[component] = 0
	gas_fill_name = " + ".join(
		[f"{frac:.0%} {key}" for key, frac in atomic_fill_fractions.items() if frac > 0])

	# correct the pressure for temperature
	if shot_info["CAPSULE_FILL_PRESSURE"] != "":
		if shot_info["SHOT_TEMPERATURE"] != "":
			shot_info["CAPSULE_FILL_PRESSURE"] *= 293/shot_info["SHOT_TEMPERATURE"]
		else:
			print(f"Warning? there's no shot temperature given, so I hope {shot_info['CAPSULE_FILL_PRESSURE']:.3g}torr "
			      f"is measured at room temp.")

	# get the neutronics data from webdav as well
	if isnan(DD_yield):
		try:
			DD_yield = download_webdav_number(
				shot_number, f"reports/AUTH-INSTR-YN_{shot_number}.csv", "Yn", downloads_folder)
		except FileNotFoundError:
			raise FileNotFoundError("I couldn't find an official DD-n yield on WebDAV, so "
			                        "you need to supply it using `--DD_yield=...`.")
		print(f"found DD-n yield of {DD_yield:.3g}")
	else:
		print(f"using user-supplied DD-n yield of {DD_yield:.3g}")
	if isnan(DD_temperature):
		try:
			DD_temperature = download_webdav_number(
				shot_number, f"reports/AUTH-INSTR-TION_{shot_number}.csv", "Tion", downloads_folder)
		except FileNotFoundError:
			raise FileNotFoundError("I couldn't find an official DD ion temperature on WebDAV, so "
			                        "you need to supply it using `--DD_temperature=...`.")
		print(f"found DD-n temperature of {DD_temperature:.2f} keV")
	else:
		print(f"using user-supplied DD-n temperature of {DD_temperature:.2f} keV")

	# then load the existing CSV and add in the relevant stuff
	try:
		shot_table = pd.read_csv("shot_info.csv", skipinitialspace=True, index_col="shot number",
		                         dtype={key: dtype for key, dtype in SHOT_INFO_HEADER})
	except FileNotFoundError:
		shot_table = pd.DataFrame(columns=[key for key, dtype in SHOT_INFO_HEADER])
	if shot_number in shot_table.index:  # make sure to remove any previus iterations of this shot
		print(f"overwriting the previus entry for {shot_number} in shot_info.csv")
		shot_table = shot_table.drop(shot_number)
	shot_table = pd.concat([shot_table, pd.DataFrame(index=[shot_number], data={
		"shot name":          shot_info["EXPERIMENT_ID"],
		"PI":                 shot_info["SHOT_RI"],
		"campaign":           shot_info["CAMPAIGN"],
		"subcampaign":        shot_info["SUBCAMPAIGN"],
		"platform":           shot_info["PLATFORM"],
		"hohlraum material":  shot_info["HOHLRAUM_TYPE_RT"],
		"ablator material":   shot_info["ABLATOR_MATERIAL_RT"],
		"ablator thickness":  shot_info["ABLATOR_THICKNESS_CRYO"],
		"ablator radius":     shot_info["ABLATOR_OUTER_RADIUS_CRYO"],
		"ablator density":    shot_info["ABLATOR_AVG_MASS_DENSITY_CRYO"],
		"fill pressure":      shot_info["CAPSULE_FILL_PRESSURE"],
		"deuterium fraction": atomic_fill_fractions["D"],
		"helium-3 fraction":  atomic_fill_fractions["He3"],
		"fill gas":           gas_fill_name,
		"DD-n yield":         DD_yield,
		"DD-n temperature":   DD_temperature,
		})])
	shot_table = shot_table.sort_index()
	shot_table.to_csv("shot_info.csv", index_label="shot number", float_format="%.5g")

	# finally, create the aux_info.csv for this shot in its designated subfolder, replacing any previus ones
	if os.path.isfile(f"{shot_subfolder}/aux_info.csv"):
		print(f"overwriting the previus `{shot_subfolder}/aux_info.csv` file")
		os.remove(f"{shot_subfolder}/aux_info.csv")
	with open(f"{shot_subfolder}/aux_info.csv", "w") as f:
		f.write(", ".join([key for key, dtype in AUX_INFO_HEADER]) + "\n")


def load_traveler_spreadsheet_info(shot_number: str, shot_subfolder: str,
                                   filepath: str, downloads_folder: str) -> None:
	""" load all of the information in this traveler spreadsheet and some supplementary information
	    from WebDav and store it in {shot_subfolder}/aux_info.csv
	    :param shot_number: the complete 12-digit N number
	    :param shot_subfolder: the directory in which all of the information about this shot can be found
	    :param filepath: the location and name of the traveler spreadsheet, relative to the working directory
	    :param downloads_folder: the default downloads folder for the default browser
	    :raise SpreadsheetFormatError: if there’s anything wrong or confusing about the traveler spreadsheet
	    :raise MissingSnoutError: if snout_config is an unrecognized snout configuration
	"""
	# instantiate the wedges
	component_list_headers: dict[int, tuple[str, int]] = {}
	dim: Optional[str] = None
	snout_config: Optional[str] = None
	shot_name: Optional[str] = None

	# open the spreadsheet
	traveler = openpyxl.load_workbook(filename=filepath, read_only=True).active
	i_just_saw_the_word_snout_config = False
	# start by looking through each cell
	for row in range(1, 37):
		for col in string.ascii_uppercase[0:13]:
			cell = traveler[f"{col}{row}"].value
			if cell is None or type(cell) is not str:
				continue
			# if this looks like a position header, record it
			elif re.fullmatch(r"Position #([0-9])", cell):
				position = int(cell[-1])
				component_list_headers[position] = (col, row)
			# if it looks like a shot name, note it
			elif re.fullmatch(r"\s*\w+_\w+_\w+_\w+_[\w0-9]+\s*", cell):
				shot_name = normalize_shot_name(cell.strip())
			# if this looks like a DIM specifier, note it
			elif re.fullmatch(r"(TC)?(0*9?0)-([0-9]+)([- ][0-9A-Za-z-]+)?", cell):
				dim = normalize_dim_coordinates(cell)
			# if this says "Snout Config", look at the next nonempty cell
			elif re.fullmatch(r"Snout( Config.*)?( Name)?:?", cell):
				i_just_saw_the_word_snout_config = True
			# if this is the next nonempty cell after "Snout Config",
			elif i_just_saw_the_word_snout_config:
				# check if it's a KB swap
				if re.fullmatch(r".*SWAP.*", cell):
					snout_config = "KB swap"
				# or else read the snout config
				else:
					# cut out unnecessary qualifiers
					full_match = re.fullmatch(r"([\w0-9-]+-[0-9.X]+)(-DS(BOTH)?)?(-DIXI)?([ ,].*)?", cell)
					if not full_match:
						raise SpreadsheetFormatError(f"there's something incomprehensible about the snout config {cell!r}.")
					snout_config = full_match.group(1)
				i_just_saw_the_word_snout_config = False

	# make sure we found everything we need
	if shot_name is None:
		raise SpreadsheetFormatError("I couldn't find the shot name anywhere in this spreadsheet.")
	elif dim is None:
		raise SpreadsheetFormatError("I couldn't find the DIM anywhere in this spreadsheet.")
	elif snout_config is None:
		raise SpreadsheetFormatError("I couldn't find the snout configuration name anywhere in this spreadsheet.")
	elif shot_name != get_shot_name(shot_number):
		raise SpreadsheetFormatError(f"This traveler spreadsheet in the {get_shot_name(shot_number)} folder "
		                             f"says it's for {shot_name}.")

	print(f"reading traveler spreadsheet for DIM {dim}...")

	# if this is a KB swap, fill in information from the previus configuration on this DIM
	if snout_config == "KB swap":
		try:
			previus_snout_config = get_previous_snout_config(shot_number, dim)
		except ValueError as e:
			raise SpreadsheetFormatError(
				f"This DIM is a KB swap, so I tried to load the snout config from the last shot, but {e}")
		print(f"  setting snout config to {previus_snout_config}")
		snout_config = previus_snout_config

	# load any auxiliaries we already have for this shot
	found_anything = False
	aux_table = pd.read_csv(f"{shot_subfolder}/aux_info.csv", skipinitialspace=True, na_filter=False,
	                        dtype={key: dtype for key, dtype in AUX_INFO_HEADER})
	for position, (col, row) in component_list_headers.items():
		components = []
		for i in range(1, 5):
			cell = traveler[f"{col}{row + i}"].value
			if cell is None:
				break
			elif type(cell) is int:
				components.append(cell)
			elif type(cell) is str:
				parsing = re.fullmatch(r"([0-9]+)\s+.*", cell)
				if parsing is not None:
					components.append(int(parsing.group(1)))
				else:
					raise SpreadsheetFormatError(f"The list of component IDs on DIM {dim} position {position} contains "
					                             f"{cell!r}, which doesn't parse as an ID number")
			else:
				raise SpreadsheetFormatError(f"The list of component IDs on DIM {dim} position {position} contains "
				                             f"{cell!r}, which is not an ID number")

		if len(components) == 0:
			continue  # most of the time this part will be blank (nothing fielded)
		filter_id = components[0]
		bert_id = components[1] if len(components) > 1 else None
		ernie_id = components[2] if len(components) > 2 else None

		# if the first item is a WRF ID
		if 13425000 <= filter_id < 13426000:
			aux_type = "WRF"
		elif 14042000 <= filter_id < 14046000:
			aux_type = "SRF"
		else:
			continue  # ignore anything that looks like pTOF or SRC

		print(f"  found {aux_type} at position {position} ({filter_id})")
		found_anything = True

		# calculate the position’s absolute TC coordinates
		r, θ, ф = calculate_aux_coordinates(
			shot_number, dim, position,
			snout_config,
			downloads_folder)

		aux_table = pd.concat([aux_table, pd.DataFrame(index=[aux_table.index.max() + 1], data={
			"type": aux_type,
			"DIM": dim,
			"position": position,
			"distance": r, "theta": θ, "phi": ф,
			"filter ID": filter_id,
			"bert ID": bert_id,
			"ernie ID": ernie_id,
			"snout configuration": snout_config,
		})])

	if not found_anything:
		print("  There were no auxiliaries we support on this traveler spreadsheet.")

	# save it all
	aux_table.to_csv(f"{shot_subfolder}/aux_info.csv", index=False)


def calculate_aux_coordinates(shot_number: str, dim: str, position: int,
                              snout_config: str, downloads_folder: str
                              ) -> tuple[float, float, float]:
	""" in general, the distances of "cling-on" auxiliary diagnostics is not well-known on NIF shots. this function
	    will attempt to use WebDAV information to calculate it, along with its angular position.

	    as a prerequisite, the distance from the pinhole plane to the first auxiliary bracket mounting pin must be
	    determined from the snout assembly drawing and entered into the `tables/snout_configs.csv` table. luckily, most
	    snout configurations are used many times, so only infrequently does that need to be updated.
	    :param shot_number: the complete 12-digit N number
	    :param dim: the complete six-digit name of the line-of-sight on which the aux is clinging
	    :param position: the position number on the aux bracket (1, 2, 3, or 4)
	    :param snout_config: the name of the DIM’s snout configuration
	    :param downloads_folder: the default downloads folder for the default browser
	    :return: the spherical coordinates of the auxiliary diagnostic: r (cm), θ (°), and ф (°)
	    :raise MissingSnoutError: if snout_config is an unrecognized snout configuration
	"""
	snout_config_table = pd.read_csv("tables/snout_configs.csv", index_col="Configuration name",
	                                 skipinitialspace=True)
	try:
		snout_config_details = snout_config_table.loc[snout_config]
	except KeyError:
		raise MissingSnoutError(f"The snout {snout_config!r} does not exist in tables/snout_config.csv yet. "
		                        f"please consult the drawings and fill it in.")
	try:
		pinhole_to_pin_distance = snout_config_details["Pinhole-to-small-pin distance"]
	except KeyError:
		raise SpreadsheetFormatError(f"The tables/snout_config.csv is missing its "
		                             f"'Pinhole-to-small-pin' distance column")
	pinhole_to_pin_distance /= 10  # the table is in mm, so convert to cm
	theta, phi = float(dim[2:5]), float(dim[6:9])
	content = download_webdav_file(
		shot_number, f"setup/csv/MS.MODE_PLAN/{dim}/SETUP_{dim}_PRIMARY_AIMPOINT-TO-PINHOLE-PLANE_SHOT_MODE-PLAN_{shot_number}.csv",
		downloads_folder)
	tcc_to_pinhole_distance = content.iloc[0]["MODE_VALUE"]/10
	x = 3.00095702294918
	y = 11.6654233681113
	z = -7.12729253292641 + tcc_to_pinhole_distance + pinhole_to_pin_distance
	r = sqrt(x**2 + y**2 + z**2)
	if theta == 90:
		delta_theta = degrees(atan(y/z))
		delta_phi = degrees(atan(x/z))
		if position == 1:
			return r, theta - delta_theta, phi + delta_phi
		if position == 2:
			return r, theta - delta_theta, phi - delta_phi
		if position == 3:
			return r, theta + delta_theta, phi - delta_phi
		if position == 4:
			return r, theta + delta_theta, phi + delta_phi
		raise ValueError(f"Unknown position '{position}'")
	elif theta == 0:
		delta_theta = degrees(atan(hypot(x, y)/z))
		delta_phi = degrees(atan(x/y))
		if position == 1:
			return r, delta_theta, 180 - delta_phi
		if position == 2:
			return r, delta_theta, 180 + delta_phi
		if position == 3:
			return r, delta_theta, 360 - delta_phi
		if position == 4:
			return r, delta_theta, delta_phi
		raise ValueError(f"Unknown position '{position}'")
	else:
		raise ValueError(f"this calculation doesn't work with theta={theta}°")


def generate_etch_scan_request(shot_number: str, shot_subfolder: str) -> None:
	""" estimate a reasonable etch time and fill in a generic etch/scan request spreadsheet for the
	    given shot, using the info in {shot_subfolder}/wrf_info.csv and shot_info.csv
	    :param shot_number: the complete 12-digit N number
	    :param shot_subfolder: the directory in which all of the information about this shot can be found
	    :raise PermissionError: if I don’t have permission to create and edit the workorder spreadsheet
	"""
	# load the tables
	shot_info = pd.read_csv("shot_info.csv", index_col="shot number",
	                        skipinitialspace=True,
	                        dtype={key: dtype for key, dtype in SHOT_INFO_HEADER}
	                        ).loc[shot_number]
	full_aux_table = pd.read_csv(f"{shot_subfolder}/aux_info.csv",
	                             skipinitialspace=True, na_filter=False,
	                             dtype={key: dtype for key, dtype in AUX_INFO_HEADER})
	# make a work order for each type of aux present
	for aux_type in full_aux_table["type"].unique():
		aux_table = full_aux_table[full_aux_table["type"] == aux_type]
		# make a work order for each CR39 level
		any_berts = any(aux_table["bert ID"])
		any_ernies = any(aux_table["ernie ID"])
		if not any_berts and not any_ernies:
			raise ValueError("no detectors were found on any of these pieces")
		for detector in ["bert"]*any_berts + ["ernie"]*any_ernies:
			print(f"generating etch and scan request for {aux_type} {detector}s...")

			# set some strings and estimate the yield
			if aux_type == "SRF":
				filter_name = "Ta step range filter ID"
				material = "SRF:CR-39"
				scan_type = "5 cm round"
				overlap_limit = 20  # tracks per frame
				proton_yield = shot_info["DD-n yield"]
			elif aux_type == "WRF":
				filter_name = "Al WRF ID: wedge ID"
				material = "WRF:CR-39"
				scan_type = "Al WRF"
				overlap_limit = 40  # tracks per frame
				reactivity_ratio = get_reactivity_ratio(
					"D3He-p", "DD-n", shot_info["DD-n temperature"])
				number_ratio = 2*shot_info["helium-3 fraction"]/shot_info["deuterium fraction"]
				primary_yield = shot_info["DD-n yield"]*reactivity_ratio*number_ratio
				secondary_yield = shot_info["DD-n yield"]*2e-3  # 2×10^-3 is the max possible yield ratio for Te ~= 3keV
				if primary_yield > secondary_yield:
					proton_yield = primary_yield
					print(f"  estimating a primary D3He proton yield of {proton_yield:.2g}")
				else:
					proton_yield = secondary_yield
					print(f"  estimating a secondary D3He proton yield of <{proton_yield:.2g}")
			else:
				raise ValueError(f"I don't know how to calculate the relevant yield for {aux_type!r}.")

			# copy and open the new workorder spreadsheet
			workorder_workbook = openpyxl.load_workbook("templates/workorder.xlsx")
			workorder = workorder_workbook.active
			# fill in the generic boxen
			workorder["B121"] = shot_number
			workorder["B122"] = shot_info["shot name"]
			workorder["B123"] = shot_info["fill gas"]
			workorder["B124"] = shot_info["ablator material"]

			# iterate thru the WRFs
			rows_with_auxs = []
			for _, aux in full_aux_table.iterrows():
				# calculate the recommended etch time
				fluence = proton_yield/(4*pi*aux["distance"]**2)*FRAME_AREA
				etch_time = max(1.5, min(5.0, 5*sqrt(overlap_limit/fluence)))
				print(f"  the {aux_type} on {aux['DIM']}:{aux['position']} will see ~{fluence:.2g} track/frame; "
				      f"I suggest a {etch_time:.1f} hour etch.")

				# fill in the relevant boxen
				top_row = -4 + (DIM_LIST.index(aux["DIM"])*4 + aux["position"])*4
				workorder[f"A{1 + top_row}"] = aux[f"{detector} ID"]
				workorder[f"E{4 + top_row}"] = scan_type
				workorder[f"F{3 + top_row}"] = round(etch_time*2)/2  # round etch time to the nearest half hour
				bottom_row = 62 + DIM_LIST.index(aux["DIM"])*14 + aux["position"]*3
				workorder[f"A{1 + bottom_row}"] = filter_name
				workorder[f"B{1 + bottom_row}"] = aux["filter ID"]
				workorder[f"D{2 + bottom_row}"] = aux[f"{detector} ID"]
				workorder[f"E{2 + bottom_row}"] = aux["DIM"]
				workorder[f"F{2 + bottom_row}"] = material
				workorder[f"G{2 + bottom_row}"] = round(aux["distance"], 2)  # round distance to the nearest 100μm
				rows_with_auxs.append((top_row, bottom_row))

			# do the priorities as well, so that they go top-to-bottom
			for i, (top_row, bottom_row) in enumerate(sorted(rows_with_auxs)):
				workorder[f"A{2 + top_row}"] = i + 1
				workorder[f"B{2 + bottom_row}"] = i + 1

			# finally, save it in the new location
			detector_str = f"{detector} " if any_berts and any_ernies else ""
			workorder_workbook.save(
				f"{shot_subfolder}/{shot_number} {shot_info['shot name']} {aux_type} {detector_str}WO #1.xlsx")


def download_webdav_number(shot_number: str, path: str, key: str, downloads_folder: str, timeout=DOWNLOAD_QUIT_TIME) -> float:
	""" download a WebDAV file for the given shot number and return the average value of a single column
	    :param shot_number: the complete 12-digit N number
	    :param path: the WebDav filepath, relative to shotdata/shots/YY/MM/NYYMMDD-XXX-999/
	    :param key: the name of the desired number
	    :param downloads_folder: the default downloads folder for the default browser
	    :param timeout: the number of seconds to wait for the file to appear before giving up
	    :raise TimeoutError: if the file doesn’t appear after timeout seconds
	    :raise FileNotFoundError: if the file does not exist in WebDav
	"""
	data = download_webdav_file(shot_number, path, downloads_folder, timeout)
	uncertainty_key: Optional[str] = None
	for possible_uncertainty_key in ["+/-", "+/- %"]:
		if possible_uncertainty_key in data.columns:
			uncertainty_key = possible_uncertainty_key
	if uncertainty_key is None:
		raise ValueError(f"which of these column names represents the uncertainty?: {data.columns}")
	return np.average(data[key], weights=1/data[uncertainty_key]**2)


def download_webdav_file(shot_number: str, path: str,
                         downloads_folder: str, timeout=DOWNLOAD_QUIT_TIME) -> pd.DataFrame:
	""" download a WebDAV file for the given shot number at the given address and return it as a DataFrame
	    :param shot_number: the complete 12-digit N number
	    :param path: the WebDav filepath, relative to shotdata/shots/YY/MM/NYYMMDD-XXX-999/
	    :param downloads_folder: the default downloads folder, whither we expect it to
	    :param timeout: the number of seconds to wait for the file to appear before giving up
	    :raise TimeoutError: if the file doesn’t appear after timeout seconds
	    :raise FileNotFoundError: if the file does not exist in WebDav
	"""
	year, month = "20" + shot_number[1:3], shot_number[3:5]
	url = f"https://nifit.llnl.gov/ArchiveWebDav/export/shotdata/shots/{year}/{month}/{shot_number}/{path}"

	# in order to authenticate properly, we have to download this file from a browser that supports JS
	webbrowser.open(url, autoraise=True)  # always autoraise in case it prompts the user for a password
	downloaded_filepath = os.path.join(downloads_folder, os.path.basename(path))

	# wait for our downloaded file to appear
	start_time = time.time()
	user_has_been_warned = False
	while True:
		current_time = time.time()
		if os.path.isfile(downloaded_filepath):
			break
		elif not user_has_been_warned and current_time - start_time > DOWNLOAD_WARN_TIME:
			print(f"downloading `{path}`...")
			user_has_been_warned = True
		elif current_time - start_time > timeout:
			raise TimeoutError(f"I couldn't get `{url}`. this may be because `{downloads_folder}` is not your "
			                   f"default downloads directory, or because you're not on the LLNL VPN.")
		else:
			time.sleep(0.2)
	time.sleep(0.2)  # give it a sec after it appears, to ensure it's populated

	# go find it wherever it ended up
	try:
		with open(downloaded_filepath, "r") as f:
			content = f.read()
	except FileNotFoundError:
		raise RuntimeError(f"I lost the file `{url}`. something must have deleted it from "
		                   f"`{downloads_folder}` when I wasn't looking.")
	# and delete it after you’ve read it
	os.remove(downloaded_filepath)

	# sometimes they put an extra comma at the end for no reason? so fix that??
	if content.count(",") % (content.count("\n") + 1) == 1 and content.endswith(","):
		content = content[:-1]

	try:
		return pd.read_csv(filepath_or_buffer=StringIO(content), na_filter=False)  # type: ignore
	except pd.errors.EmptyDataError:
		raise FileNotFoundError(f"the file `{url}` does not exist in WebDav "
		                        f"(or it does but it's just empty)")


def get_shot_name(shot_number: str) -> str:
	""" convert a shot number to a shot *name* using the shot_info.csv table
	    :param shot_number: the complete 12-digit N number
	    :return: the full shot name, including the series number
	"""
	shot_table = pd.read_csv("shot_info.csv", index_col="shot number", skipinitialspace=True,
	                         dtype={key: dtype for key, dtype in SHOT_INFO_HEADER})
	return shot_table.loc[normalize_shot_number(shot_number)]["shot name"]


def get_previous_snout_config(shot_number: str, dim: str) -> str:
	""" look up what snout configuration was used on this DIM on the shot before this
	    :param shot_number: the N number of this shot
	    :param dim: the complete six-digit name of the line-of-sight
	    :return: the name of the snout configuration on this line-of-sight last shot
	    :raise ValueError: if the previus shot was obviusly unrelated or didn’t use the given DIM
	"""
	# look at all the shots from oldest to newest
	for other_shot_subfolder in reversed(os.listdir("data")):
		# skip any that are after or equal to the one in question or not NIF shots
		try:
			other_shot_number = normalize_shot_number(other_shot_subfolder)
		except ValueError:
			continue
		if other_shot_number >= shot_number:
			continue
		# as soon as you find an earlier one, return its snout configuration
		campaign = get_shot_name(shot_number)[:-4]
		other_campaign = get_shot_name(other_shot_number)[:-4]
		if campaign != other_campaign:
			raise ValueError(f"the previous shot is from a different campaign ({other_campaign}), "
			                 f"whereas I was looking for {campaign}")
		aux_table = pd.read_csv(f"data/{other_shot_subfolder}/aux_info.csv",
		                        skipinitialspace=True, na_filter=False,
		                        dtype={key: dtype for key, dtype in AUX_INFO_HEADER})
		if not any(aux_table["DIM"] == dim):
			raise ValueError(f"the previous shot ({other_shot_number}) did not use the DIM in question ({dim})")
		return aux_table[aux_table["DIM"] == dim].iloc[0]["snout configuration"]


def locate_subfolder_for(shot_number: str) -> str:
	""" look at all subfolders of data/ for one whose name matches the given shot number
	    :param shot_number: the complete 12-digit N number
	    :return: the path to the folder that most closely matches this shot, relative to the working directory
	    :raise IOError: if you can’t find any subfolder that seems to go with this shot
	"""
	# start by trying to find a shot that matches the YYMMDD-00N part of it
	for item in os.listdir("data"):
		if os.path.isdir(os.path.join("data", item)) and shot_number[1:11] in item:
			return f"data/{item}"
	# if you can’t, see if there’s one that just matches the YYMMDD part
	for item in os.listdir("data"):
		if os.path.isdir(os.path.join("data", item)) and shot_number[1:7] in item:
			return f"data/{item}"
	# otherwise, give up
	raise IOError(f"you need to create the subdirectory for shot {shot_number}")


def evaluate_directory(directory: str) -> str:
	""" look for and fill in references to environment variables in the given str
	    :param directory: an absolute path with some %VARIABLE%s and/or $VARIBALEs in it
	    :return: the same path, but with actual values filled in for all the variables
	    :raise ValueError: if one of the variables invoked in the path isn’t set
	"""
	for variable_syntax in [r"%(\w+)%", r"\$(\w+)"]:
		while re.search(variable_syntax, directory):
			key = re.search(variable_syntax, directory).group(1)
			value = os.getenv(key)
			if value is None:
				raise ValueError(f"could not find environment variable {key!r}")
			directory = re.sub(variable_syntax.replace(r"(\w+)", key), re.escape(value), directory)
	return directory


def normalize_shot_number(shot_number: str) -> str:
	""" take a NIF shot number in a variety of formats and return an equivalent NXXXXXX-00X-999 version
	    :param shot_number: the N number of this shot, possibly incomplete
	    :return: the complete 12-digit N number
	    :raise ValueError: if shot_number isn’t formatted like any kind of shot number
	"""
	parsing = re.fullmatch(r"N?([0-9]{6})(-([0-9]{3}))?(-999)?( [A-Za-z0-9_-]+)?", shot_number)
	if parsing is None:
		raise ValueError(f"I could not parse the shot number {shot_number!r}. "
		                 f"It should follow the N210808-001(-999) format.")
	date, index = parsing.group(1, 3)
	if index is None:
		index = "001"
	return f"N{date}-{index}-999"


def normalize_shot_name(shot_name: str) -> str:
	""" take a DIM name in a variety of formats and return an equivalent TC0XX-XXX version
	    :param shot_name: the name of the shot (e.g. "I_Stag_Sym_HohlScan_S01a"),
	                      possibly missing part or all of the S01a
	    :return: the complete shot name as it appears in WebDav
	"""
	if re.search(r"_S[0-9]{2}[a-z]$", shot_name):
		return shot_name
	elif re.search(r"_S[0-9]{2}$", shot_name):
		return shot_name + "a"
	else:
		return shot_name + "S01a"


def normalize_dim_coordinates(dim_coordinates: str) -> str:
	""" take a DIM name in a variety of formats and return an equivalent TC0XX-XXX version
	    :param dim_coordinates: the hyphenated DIM name, possibly with some 0s removed
	    :return: the complete six-digit name of the line-of-sight on which the aux is clinging
	    :raise ValueError: if dim_coordinates isn’t formatted like any kind of DIM name
	"""
	full_match = re.fullmatch(r"(TC)?(0*9?0)-([0-9]+)([- ][0-9A-Za-z-]+)?", dim_coordinates)
	if full_match is None:
		raise ValueError(f"{dim_coordinates!r} does not appear to be a DIM")
	theta, phi = full_match.group(2, 3)
	return f"TC{int(theta):03d}-{int(phi):03d}"


def main():
	parser = argparse.ArgumentParser(
		prog="load_info_from_nif_database",
		description = "Load the information about a given shot number from WebDav and any traveler spreadsheets placed "
		              "in the relevant `data/` subdirectory, store the top-level fields in the `shot_info.csv` file, "
		              "and generate a simple etch and scan request.")
	parser.add_argument("shot_number", type=str,
	                    help="the shot's 9- or 12-digit N number (e.g. N210808-001)")
	parser.add_argument("--DD_yield", type=float, default=nan,
	                    help="the approximate DD yield of the implosion in keV, if it's not on WebDav yet")
	parser.add_argument("--DD_temperature", type=float, default=nan,
	                    help="the approximate nTOF-measured ion temperature of the implosion, if it's not on WebDav yet")
	parser.add_argument("--downloads", type=str, default="%USERPROFILE%\\Downloads\\" if os.name == "nt" else "~/Downloads/",
	                    help="the default directory where files downloaded from your default browser go")
	args = parser.parse_args()

	shot_number = normalize_shot_number(args.shot_number)
	shot_subfolder = locate_subfolder_for(shot_number)
	downloads_folder = evaluate_directory(args.downloads)

	load_info_from_nif_database(shot_number, shot_subfolder, args.DD_yield, args.DD_temperature, downloads_folder)


class SpreadsheetFormatError(ValueError):
	pass

class MissingSnoutError(ValueError):
	pass


if __name__ == "__main__":
	main()
