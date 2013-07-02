
import numpy
import csv
import os

def float_perc(input):
	"""Convert a string to float with correction for percent symbols.
		i.e. 10% converts to 0.1."""
	assert isinstance(input,str)

	input = input.replace('%','e-2')

	return float(input)


class WRF_CSV(object):
	"""docstring for WRF_CSV"""
	# File name for the input
	fname = ""
	# Date the analysis was done:
	date = ""
	# Time the analysis was done:
	time = ""
	# Program version date:
	program_date = ""
	# Scan file name:
	scan_file = ""
	# WRF port
	port = ""
	# WRF distance (cm)
	distance = 0
	# WRF ID
	WRF_ID = ""
	# Blast filter thickness:
	Al_Blast_Filter = 0
	# Calibration info:
	WRF_Cal = ""
	# Data region limits:
	Data_Limits = (-1,-1,-1,-1)
	# Background #1 limits:
	BG1_Limits = (-1,-1,-1,-1)
	# Background #2 limits:
	BG2_Limits = (-1,-1,-1,-1)
	# Diameter limits:
	Dia_Limits = (-1,-1)
	# Whether diameter limits were chosen automatically
	Dia_Auto = False
	# Energy limits corresponding to the diameter limits
	E_Limits = (-1,-1)
	# DvE c parameter
	c = 0
	# Uncertainty in c parameter
	dc = 0
	# Chi^2 from fit
	chi2 = 0
	# energy limits used for the fit
	Fit_Limits = (-1,-1)
	# Fit values (E,sigma,Yield)
	Fit = (-1,-1,-1)
	# Random uncertainties in the fit values (dE,ds,dY)
	Unc_Random = (-1,-1,-1)
	# Systematic uncertainties in the fit values (dE,ds,dY)
	Unc_Systematic = (-1,-1,-1)
	# CountingStats uncertainties in the fit values (dE,ds,dY)
	Unc_CountingStats = (-1,-1,-1)
	# DvE uncertainties in the fit values (dE,ds,dY)
	Unc_DvE = (-1,-1,-1)
	# Dmax uncertainties in the fit values (dE,ds,dY)
	Unc_Dmax = (-1,-1,-1)
	# EtchScan uncertainties in the fit values (dE,ds,dY)
	Unc_EtchScan = (-1,-1,-1)
	# Nonlinearity uncertainties in the fit values (dE,ds,dY)
	Unc_Nonlinearity = (-1,-1,-1)
	# CalProc uncertainties in the fit values (dE,ds,dY)
	Unc_CalProc = (-1,-1,-1)

	# Spectrum data:
	spectrum = []

	def __init__(self, fname):
		super(WRF_CSV, self).__init__()

		self.fname = fname

		# open file:
		fileReader = csv.reader(open(fname,'r'),delimiter=',')

		# read in the data from file:
		fileData = []
		for row in fileReader:
			fileData.append(row)

		# Parse the meta data:
		for row in fileData:
			if len(row) > 0:
				if 'Date & time' in row[0] and len(row) >= 3:
					self.date = row[1].strip()
					self.time = row[2].strip()
				if 'Program version' in row[0] and len(row) >=2:
					self.program_date = row[1].strip()
				if 'Scan file' in row[0] and len(row) >= 2:
					self.scan_file = row[1].strip()
				if 'Port & distance' in row[0]  and len(row) >=3:
					self.port = row[1].strip()
					self.distance = float(row[2])
				if 'WRF ID; Al blast(um) & cal' in row[0] and len(row) >=4:
					self.WRF_ID = row[1].strip()
					self.Al_Blast_Filter = float(row[2])
					self.WRF_Cal = row[3].strip()
				if 'Data x0; x1; y0; y1' in row[0] and len(row) >=5:
					xmin = float(row[1])
					xmax = float(row[2])
					ymin = float(row[3])
					ymax = float(row[4])
					self.Data_Limits = (xmin,xmax,ymin,ymax)
				if 'Back x0; x1; y0; y1' in row[0] and len(row) >=5 and self.BG1_Limits==(-1,-1,-1,-1):
					xmin = float(row[1])
					xmax = float(row[2])
					ymin = float(row[3])
					ymax = float(row[4])
					self.BG1_Limits = (xmin,xmax,ymin,ymax)
				if 'Back x0; x1; y0; y1' in row[0] and len(row) >=5:
					xmin = float(row[1])
					xmax = float(row[2])
					ymin = float(row[3])
					ymax = float(row[4])
					self.BG2_Limits = (xmin,xmax,ymin,ymax)
				if 'Dlow; Dhigh; Dauto; Elims' in row[0] and len(row) >=6:
					self.Dia_Limits = (float(row[1]),float(row[2]))
					if 'yes' in row[3] or 'Yes' in row[3] or 'true' in row[3] or 'True' in row[3]:
						self.Dia_Auto = True
					else:
						self.Dia_Auto = False
					self.E_Limits = (float(row[4]),float(row[5]))
				if 'DvE fit: c; dc; red. Chi^2' in row[0] and len(row) >= 4:
					self.c = float(row[1])
					self.dc = float(row[2])
					self.chi2 = float(row[3])
				if 'Fit limits' in row[0] and len(row) >= 3:
					self.Fit_Limits = (float(row[1]),float(row[2]))
				if 'Value:' in row[0] and len(row) >= 4:
					self.Fit = (float(row[1]),float(row[2]),float(row[3]))
				if '    Random:' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_Random = (dE,ds,dY)
				if '    Systematic calib:' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_Systematic = (dE,ds,dY)
				if '     Counting statistics' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_CountingStats = (dE,ds,dY)
				if '     DvE fit:' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_DvE = (dE,ds,dY)
				if '     Dmax scaling' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_Dmax = (dE,ds,dY)
				if '     Etch & scan' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_EtchScan = (dE,ds,dY)
				if '     WRF nonlinearity' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_Nonlinearity = (dE,ds,dY)
				if '     Cal. processing' in row[0] and len(row) >= 4:
					dE = float(row[1])
					ds = float(row[2])
					# deal with converting %:
					dY = float_perc(row[3].strip()) * self.Fit[2]
					self.Unc_CalProc = (dE,ds,dY)

		# Parse the spectrum:
		spectrum_index = 0;
		for i in range(len(fileData)):
			if 'PROTON SPECTRUM' in fileData[i]:
				spectrum_index = i
		spectrum_index += 2 # now this is the first row of spectral data
		for i in range(spectrum_index,len(fileData)):
			if len(fileData[i]) > 0:
				line = fileData[i][0].split(sep='\t')
				E = float(line[0]) # Energy
				s = float(line[1]) # sigma
				Y = float(line[2]) # Yield
				self.spectrum.append( [E,s,Y] )

	def Print(self):
		info = "=== Metadata ===\n"
		info += "Date: " + self.date + '\n'
		info += "Time: " + self.time + '\n'
		info += "Program version: " + self.program_date + '\n'
		info += "Scan file: " + self.scan_file + '\n'
		info += "Port: " + self.port + '\n'
		info += "Distance: " + str(self.distance) + '\n'
		info += "WRF ID: " + self.WRF_ID + '\n'
		info += "Al blast filter: " + str(self.Al_Blast_Filter) + '\n'
		info += "WRF Cal: " + self.WRF_Cal + '\n'
		info += "Data limits: "
		for x in self.Data_Limits:
			info += str(x) + ','
		info += '\n'
		info += "Background 1: "
		for x in self.BG1_Limits:
			info += str(x) + ','
		info += '\n'
		info += "Background 2: "
		for x in self.BG2_Limits:
			info += str(x) + ','
		info += '\n'
		info += "Dia limits: " + str(self.Dia_Limits[0]) + ',' + str(self.Dia_Limits[1]) + '\n'
		info += "Auto dia: " + str(self.Dia_Auto) + '\n'
		info += "Energy limits: " + str(self.E_Limits[0]) + ',' + str(self.E_Limits[1]) + '\n'
		info += "C parameter = " + str(self.c) + " +/- " + str(self.dc) + " [chi^2 = " + str(self.chi2) + "]\n"
		info += "Fit limits: " + str(self.Fit_Limits[0]) + " - " + str(self.Fit_Limits[1]) + '\n'
		info += "Fit: "
		for x in self.Fit:
			info += str(x) + ','
		info += '\n'
		info += "Ran unc: "
		for x in self.Unc_Random:
			info += str(x) + ','
		info += '\n'
		info += "Sys unc: "
		for x in self.Unc_Systematic:
			info += str(x) + ','
		info += '\n'

		info += "=== Spectrum ===\n"
		for x in self.spectrum:
			info += str(x[0]) + ',' + str(x[1]) + ',' + str(x[2]) + '\n'


		print(info)
	