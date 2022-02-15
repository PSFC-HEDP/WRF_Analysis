import csv
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, MaxNLocator
import re
from scipy import integrate
import xlsxwriter as xls

from WRF_Analysis.Analysis.rhoR_Analysis import rhoR_Analysis


FOLDERS = ['Om211201']
# FOLDERS = ['I_MJDD_PDD_DDExpPush']
OVERLAP = []

# HOHLRAUM_LAYERS = []
# HOHLRAUM_LAYERS = [(8, 'Au')]
HOHLRAUM_LAYERS = [(30, 'Au')]
# HOHLRAUM_LAYERS = [(10, 'U'), (20, 'Au')]
# HOHLRAUM_LAYERS = [(14, 'U'), (27, 'Au'), (2, 'Al'), (594, 'accura60'), (5, 'parylene')]
# HOHLRAUM_LAYERS = [(14, 'U'), (27, 'Au'), (205, 'Al'), (2, 'Al'), (445, 'accura60'), (5, 'parylene')]
# HOHLRAUM_LAYERS = [(15, 'Au2Ta8'), (126, 'epoxy'), (116, 'kapton'), (403, 'Cu'), (116, 'kapton'), (462, 'microfine'), (2, 'Al'), (302, 'accura60'), (5, 'parylene')]
# HOHLRAUM_LAYERS = [(15, 'Au2Ta8'), (126, 'epoxy'), (230, 'kapton'), (462, 'microfine'), (2, 'Al'), (302, 'accura60'), (5, 'parylene')]
# HOHLRAUM_LAYERS = [(15, 'Au2Ta8'), (126, 'epoxy'), (462, 'microfine'), (2, 'Al'), (302, 'accura60'), (5, 'parylene')]

WEIRD_FILTERS = {
	# '': [(3000, 'In')],
	'top': [(10, 'Ti'), (5, 'Ta')],
}

SHOW_PLOTS = False

ROOT = 'data'
σWRF = .159
δσWRF = .014


class FixedOrderFormatter(ScalarFormatter):
	"""Formats axis ticks using scientifick notacion with a constant ordre of 
	magnitude"""
	def __init__(self, order_of_mag=0, useOffset=True, useMathText=False):
		self._order_of_mag = order_of_mag
		ScalarFormatter.__init__(self, useOffset=useOffset, 
								 useMathText=useMathText)
	def _set_orderOfMagnitude(self, range):
		"""Ovre-riding this to avoid having orderOfMagnitude reset elsewhere"""
		self.orderOfMagnitude = self._order_of_mag


def locator():
	return MaxNLocator(nbins='auto', steps=[1, 2, 5])
def plt_set_locators():
	ax = plt.gca()
	ax.xaxis.set_major_locator(locator())
	ax.yaxis.set_major_locator(locator())


def get_ein_from_eout(eout, layers):
	""" do the reverse stopping power calculation """
	energy = eout # [MeV]
	for thickness, formula in layers[::-1]:
		data = np.loadtxt(f"res/tables/stopping_power_protons_{formula}.csv", delimiter=',')
		energy_axis = data[:,0]/1e3 # [MeV]
		dEdx = data[:,1]/1e3 # [MeV/μm]
		energy = integrate.odeint(
			func = lambda E,x: np.interp(E, energy_axis, dEdx),
			y0   = energy,
			t    = [0, thickness]
		)[-1,0]
	return energy

def get_dein_from_deout(deout, eout, layers):
	""" do a derivative of the stopping power calculation """
	left = get_ein_from_eout(eout - deout, layers)
	rite = get_ein_from_eout(eout + deout, layers)
	return (rite - left)/2


def perform_correction(noun, layers, mean_value, mean_error, sigma_value):
	print(f"Correcting for a {''.join(map(lambda t:t[1], layers))} {noun}: {mean_value:.2f} ± {sigma_value:.2f} becomes ", end='')
	mean_error = get_dein_from_deout(mean_error, mean_value, layers)
	sigma_value = get_dein_from_deout(sigma_value, mean_value, layers)
	mean_value = get_ein_from_eout(mean_value, layers)
	print(f"{mean_value:.2f} ± {sigma_value:.2f}")
	return mean_value, mean_error, sigma_value


def calculate_rhoR(mean_energy, mean_energy_error, shot_name, rhoR_objects={}):
	""" calcualte the rhoR using whatever tecneke makes most sense.
		return rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR (mg/cm^2)
	"""
	if shot_name.startswith("O"): # if it's an omega shot
		if shot_name not in rhoR_objects:
			rhoR_objects[shot_name] = []
			for ρ, Te in [(20, 500), (30, 500), (10, 500), (20, 250), (20, 750)]:
				try:
					with open(f"res/tables/stopping_range_protons_D_plasma_{ρ}gcc_{Te}eV.txt") as f:
						data = np.loadtxt(f, skiprows=4)
				except IOError:
					print(f"Did not find res/tables/stopping_range_protons_D_plasma_{ρ}gcc_{Te}eV.txt.")
					rhoR_objects.pop(shot_name)
					break
				else:
					rhoR_objects[shot_name].append([data[::-1,1], data[::-1,0]*1000]) # load a table from Frederick's program

		if shot_name in rhoR_objects:
			energy_ref, rhoR_ref = rhoR_objects[shot_name][0]
			best_gess = np.interp(mean_energy, energy_ref, rhoR_ref) # calculate the best guess based on 20g/cc and 500eV
			error_bar = 0
			for energy in [mean_energy - mean_energy_error, mean_energy, mean_energy + mean_energy_error]:
				for energy_ref, rhoR_ref in rhoR_objects[shot_name]: # then iterate thru all the other combinations of ρ and Te
					perturbd_gess = np.interp(energy, energy_ref, rhoR_ref)
					if abs(perturbd_gess - best_gess) > error_bar:
						error_bar = abs(perturbd_gess - best_gess)
			return best_gess, error_bar, 0, 0

		else:
			return 0, 0, 0, 0

	elif shot_name.startswith("N"): # if it's a NIF shot
		if shot_name not in rhoR_objects: # try to load the rhoR analysis parameters
			try:
				params = {}
				with open(os.path.join(folder, 'rhoR_parameters.txt')) as f:
					for line in f.readlines():
						params[line.split()[0]] = line.split()[2]
			except IOError:
				print(f"Did not find {os.path.join(folder, 'rhoR_parameters.txt')}.")
			else:
				rhoR_objects[shot_name] = rhoR_Analysis(
					shell_mat = params['Shell'],
					Ri        = float(params['Ri'])*1e-4,
					Ri_err    = 0.1e-4,
					Ro        = float(params['Ro'])*1e-4,
					Ro_err    = 0.1e-4,
					fD        = float(params['fD']),
					fD_err    = 1e-2,
					f3He      = float(params['f3He']),
					f3He_err  = 1e-2,
					P0        = float(params['P']),
					P0_err    = 0.1,
					Tshell    = float(params['Tshell'])*1e-4,
					E0        = 14.7 if float(params['f3He']) > 0 else 15.0)

		if shot_name in rhoR_objects: # if you did or they were already there, calculate the rhoR
			analysis_object = rhoR_objects[shot_day+shot_number]
			rhoR_value, Rcm_value, rhoR_error = analysis_object.Calc_rhoR(E1=mean_energy, dE=mean_energy_error)
			hotspot_rhoR, shell_rhoR, ablated_rhoR = analysis_object.rhoR_Parts(Rcm_value)
			return 1000*rhoR_value, 1000*rhoR_error, 1000*hotspot_rhoR, 1000*shell_rhoR # convert from g/cm2 to mg/cm2
		else:
			return 0, 0, 0, 0

	else:
		raise NotImplementedError(shot_name)


def combine_measurements(*args):
	nume = 0
	deno = 0
	for value, unc in args:
		nume += value/unc**2
		deno += 1/unc**2
	return nume/deno, np.sqrt(1/deno)


if __name__ == '__main__':
	shot_days = []
	shot_numbers = []
	locacions = []
	flags = []
	overlapd = []
	means = []
	sigmas = []
	yields = []
	rhoRs = []
	compression_yields = []
	spectra = []
	for i, folder in enumerate(FOLDERS):
		if i > 0 and len(folder) == 3:
			FOLDERS[i] = FOLDERS[i-1][:-3] + folder

	for i, folder_name in enumerate(FOLDERS): # for each specified folder
		folder = os.path.join(ROOT, folder_name)
		assert os.path.isdir(folder), f"El sistema no puede encontrar la ruta espificada: '{folder}'"

		for subfolder, _, _ in os.walk(folder): # and any subfolders inside it
			for filename in os.listdir(subfolder): # scan all files inside that folder
				if re.fullmatch(r'(A|N|Om?)\d{6}-?\d{3}.csv', filename): # if it is a campaign summary file

					with open(os.path.join(subfolder, filename)) as f:
						shot_day, shot_number = filename[:-4].split('-')

						for row in f.readlines(): # read all the wrf summaries out of it
							line_of_site, posicion, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error = row.split()
							locacion = ':'.join((line_of_site, posicion))

							shot_days.append(shot_day)
							shot_numbers.append(shot_number)
							locacions.append(locacion)
							flags.append('')
							overlapd.append(False)
							means.append([float(mean_value), float(mean_error)])
							sigmas.append([0, 0])
							yields.append([float(yield_value), float(yield_error)])
							rhoRs.append([float(rhoR_value), float(rhoR_error), 0, 0])

				elif re.fullmatch(r'.*ANALYSIS.*\.csv', filename): # if it is an analysis file

					shot_day, shot_number, line_of_site, posicion, wrf_number = None, None, None, None, None
					flag = ''
					identifiers = filename[:-4].split('_') # figure out what wrf this is
					identifiers.append(folder_name)
					for identifier in reversed(identifiers):
						if re.fullmatch(r'N\d{6}-?\d{3}-?999', identifier):
							shot_day, shot_number, _ = identifier.split('-')
						elif re.fullmatch(r'O[mM]?\d{6}', identifier):
							shot_day = identifier
						elif re.fullmatch(r'9\d{4}|1\d{5}', identifier):
							shot_number = identifier
						elif re.fullmatch(r'0+-0+|0?90-(0?78|124|315)|TIM[1-6]', identifier):
							line_of_site = identifier
						elif re.fullmatch(r'[1-4]', identifier):
							posicion = identifier
						elif re.fullmatch(r'134\d{5}|[gG][0-2]\d{2}', identifier):
							wrf_number = identifier
						elif re.fullmatch(r'(left|right|top|bottom|full)', identifier):
							flag = identifier
					locacion = line_of_site
					if posicion is not None:
						locacion += f":{posicion}"

					assert shot_day is not None and shot_number is not None, identifiers

					print(f"{wrf_number} – {shot_day}-{shot_number} {locacion} {flag}")

					with open(os.path.join(subfolder, filename), newline='') as f: # read thru its contents

						mean_value, sigma_value, yield_value = None, None, None
						mean_variance, sigma_variance, yield_variance = 0, 0, 0
						gaussian_fit = True
						we_have_reachd_the_spectrum_part = False
						spectrum = []

						for row in csv.reader(f):
							if len(row) == 0: continue

							if not we_have_reachd_the_spectrum_part:
								if row[0] == 'Value (gaussian fit):':
									try:
										mean_value = float(row[1])
										sigma_value = float(row[2])
										yield_value = float(row[3])
									except:
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

					spectrum = spectrum[spectrum[:,2] != 0]
					spectrum = spectrum[1:]

					spectra.append(spectrum)

					plt.figure(figsize=(10, 4)) # plot its spectrum
					plt.plot([0, 20], [0, 0], 'k', linewidth=1)
					if gaussian_fit:
						x = np.linspace(0, 20, 1000)
						μ, σ, Σ = mean_value, sigma_value, yield_value
						plt.plot(x, Σ*np.exp(-(x - μ)**2/(2*σ**2))/np.sqrt(2*np.pi*σ**2), color='#C00000')
					plt.errorbar(x=spectrum[:,0], y=spectrum[:,1], yerr=spectrum[:,2], fmt='.', color='#000000', elinewidth=1, markersize=6)
					plt.axis([4, 18, min(0, np.min(spectrum[:,1]+spectrum[:,2])), None])
					plt.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))
					plt.xlabel("Energy after hohlraum wall (MeV)" if len(HOHLRAUM_LAYERS) >= 1 else "Energy (MeV)")
					plt.ylabel("Yield (MeV^-1)")
					if flag != '':
						plt.title(f"{line_of_site}, position {posicion} ({flag})")
					elif posicion is not None:
						plt.title(f"{line_of_site}, position {posicion}")
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
						locacions.append(locacion)
						flags.append(flag)
						overlapd.append(any(overlap_indicator in filename for overlap_indicator in OVERLAP))

						mean_error = np.sqrt(mean_variance)
						sigma_error = np.sqrt(sigma_variance)
						yield_error = np.sqrt(yield_variance)

						if flag in WEIRD_FILTERS: # account for weird filters if need be
							mean_value, mean_error, sigma_value = perform_correction(
									'filter', WEIRD_FILTERS[flag], mean_value, mean_error, sigma_value)
						if '90' in line_of_site and len(HOHLRAUM_LAYERS) > 0:
							mean_value, mean_error, sigma_value = perform_correction(
									'hohlraum', HOHLRAUM_LAYERS, mean_value, mean_error, sigma_value)

						rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR = calculate_rhoR(
							mean_value, mean_error, shot_day+shot_number) # calculate ρR if you can
						
						means.append([mean_value, mean_error]) # and add the info to the list
						sigmas.append([sigma_value, sigma_error])
						yields.append([yield_value, yield_error])
						rhoRs.append([rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR])

						compression_value = np.sum(spectrum[:,1], where=spectrum[:,0] < 11)
						compression_error = yield_error/yield_value*compression_value#1/np.sqrt(np.sum(1/spectrum[:,2]**2, where=spectrum[:,0] < 11))
						compression_yields.append([compression_value, compression_error])
					else:
						print("this one had an invalid analysis.")

	assert len(means) > 0, "No datum were found."
	means = np.array(means)
	sigmas = np.array(sigmas)
	yields = np.array(yields)
	rhoRs = np.array(rhoRs)
	compression_yields = np.array(compression_yields)

	labels = []
	for shot_day, shot_number, locacion, flag in zip(shot_days, shot_numbers, locacions, flags): # compose labels of the appropirate specificity
		if len(set(shot_days)) > 1 and len(shot_number) < 4:
			labels.append(f"{shot_day}-{shot_number}\n{locacion}")
		elif len(set(shot_numbers)) > 1:
			labels.append(f"{shot_number} {locacion}")
		else:
			labels.append(f"{locacion}")
		if len(set(flags)) > 1:
			labels[-1] += f" ({flag})"

	widths = sigmas*2.355e3
	temps = np.empty(sigmas.shape)
	temps[:,0] = (np.sqrt(sigmas[:,0]**2 - σWRF**2)/76.68115805e-3)**2
	temps[:,1] = np.sqrt((2*sigmas[:,0]*sigmas[:,1])**2 + (2*σWRF*δσWRF)**2)/76.68115805e-3**2

	base_directory = os.path.join(ROOT, FOLDERS[0])

	try:
		secondary_stuff = np.atleast_2d(np.loadtxt(os.path.join(base_directory, f'Te.txt')))
	except IOError:
		secondary_stuff = np.full((means.shape[0], 6), np.nan)
		np.savetxt(os.path.join(base_directory, f'Te.txt'), secondary_stuff)
	assert secondary_stuff.shape[0] == means.shape[0], "This secondary analysis file has the rong number of entries"
	secondary_rhoRs = secondary_stuff[:,0:3]
	secondary_temps = secondary_stuff[:,3:6]

	workbook = xls.Workbook(os.path.join(base_directory, 'spectra.xlsx'))
	worksheet = workbook.add_worksheet() # save the spectra in a spreadsheet
	for i in range(len(spectra)):
		worksheet.merge_range(0, 4*i, 0, 4*i+2, labels[i])
		worksheet.write(1, 4*i,   "Energy (MeV)")
		worksheet.write(1, 4*i+1, "Spectrum (MeV^-1)")
		worksheet.write(1, 4*i+2, "Error bar (MeV^-1)")
		spectrum = spectra[i]
		for j in range(spectrum.shape[0]):
			for k in range(3):
				worksheet.write(2+j, 4*i+k, spectrum[j,k])
	workbook.close()

	print()
	with open(os.path.join(base_directory, 'wrf_analysis.csv'), 'w') as f:
		print("|  WRF              |  Yield              | Mean energy (MeV) |  ρR (mg/cm^2)  |")
		print("|-------------------|----------------------|-----------------|-----------------|")
		f.write(
			"WRF, Yield, Yield unc., Mean energy (MeV), Mean energy unc. (MeV), "+
			"Sigma (MeV), Sigma unc. (MeV), Rho-R (mg/cm^2), Rho-R unc. (mg/cm^2), "+
			"Hot-spot rho-R (mg/cm^2), Shell rho-R (mg/cm^2)\n")
		for [label, \
				(yield_value, yield_error), \
				(mean_value, mean_error), \
				(rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR), \
				(sigma_value, sigma_error), \
				(width_value, width_error), \
				(temp_value, temp_error), \
				] in zip(labels, yields, means, rhoRs, sigmas, widths, temps):
			label = label.replace('\n', ' ')
			print("|  {:15.15s}  |  {:#.2g}  ± {:#.2g}  |  {:5.2f}  ± {:4.2f}  |  {:5.1f}  ± {:4.1f}  |".format(
				label, yield_value, yield_error, mean_value, mean_error, rhoR_value, rhoR_error))
			f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
				label, yield_value, yield_error, mean_value, mean_error, sigma_value, sigma_error,
				rhoR_value, rhoR_error, hotspot_rhoR, shell_rhoR))
	print()

	# for shot in sorted(shots):
	# 	matching_shot = [shot in label for label in loong_labels]
	# 	print(f"{shot} ρR breakdown:")
	# 	print(f"  Total: {np.average(rhoRs[:,0], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")
	# 	print(f"  Fuel: {np.average(rhoRs[:,2], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")
	# 	print(f"  Shell: {np.average(rhoRs[:,3], weights=rhoRs[:,1]**(-2)*matching_shot):.1f}")

	if len(shot_numbers) <= 6: # choose label spacing based on number of shots
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

	for label, filetag, values in [
			("Yield", 'yield', yields),
			("Compression yield", 'yield_compression', compression_yields),
			("Mean energy (MeV)", 'mean', means),
			("Total ρR (mg/cm^2)", 'rhoR_total', rhoRs),
			("Fuel ρR (mg/cm^2)", 'rhoR_fuel', secondary_rhoRs),
			("Electron temperature (keV)", 'temperature_electron', secondary_temps),
			("Width (keV)", 'width', widths),
			("Ion temperature (keV)", 'temperature_ion', temps)
			]:
		if np.all(np.isnan(values)): # skip if there's noting here
			continue
		if values.shape[1] != 3: # first, reshape the data array to be in a consistent format
			values = np.stack([values[:,0], values[:,1], values[:,1]]).T
		if np.any(overlapd):
			if filetag in ['yield', 'yield_compression', 'rhoR_fuel', 'temperature_electron']: # alter the error bars if there is track overlap
				values[overlapd,1] = 2e20

		plt.figure(figsize=(1.5+values.shape[0]*spacing, 4.5)) # then plot it!
		plt.errorbar(x=np.arange(values.shape[0]), y=values[:,0], yerr=[values[:,2], values[:,1]], fmt='.k', elinewidth=2, markersize=12)
		plt.xlim(-1/2, values.shape[0]-1/2)

		max_value = np.max(values[:,0]) # figure out the scale and limits
		min_value = np.min(values[:,0], where=values[:,0] != 0, initial=np.inf)
		tops = values[:,0] + values[:,1]
		bottoms = values[:,0] - values[:,2]
		if np.any(bottoms > 0) and np.any(tops < 1e20):
			plot_top = max(np.max(tops[(bottoms>0)&(tops<1e20)]), max_value)
			plot_bottom = min(np.min(bottoms[bottoms>0]), min_value)
			if min_value > 0 and max_value/min_value > 30 and np.any(bottoms > 0):
				plt.yscale('log')
				rainge = plot_top/plot_bottom
				plt.ylim(plot_bottom/rainge**0.1, plot_top*rainge**0.1)
			else:
				rainge = plot_top - plot_bottom
				plt.ylim(plot_bottom - 0.1*rainge, plot_top + 0.1*rainge)

		# if filetag == "yield":
		# 	plt.ylim(-.1e11, 2e11)
		if filetag == "temperature_electron":
			plt.ylim(None, 4)
		plt_set_locators()
		
		plt.xticks(ticks=np.arange(values.shape[0]), labels=labels, rotation=rotation, ha=alignment) # then do the labels and stuff
		plt.ylabel(label)
		plt.grid()
		plt.tight_layout()
		plt.savefig(os.path.join(base_directory, f'summary_{filetag}.png'), dpi=300)
		plt.savefig(os.path.join(base_directory, f'summary_{filetag}.eps'))

	if SHOW_PLOTS:
		plt.show()
	plt.close('all')
