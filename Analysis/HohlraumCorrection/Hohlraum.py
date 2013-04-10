## Implement functionality for hohlraum corrections

import numpy
import StopPow
from GaussFit import *
import matplotlib

## Wrapper class for hohlraum corrections, and associated metrics
class Hohlraum(object):
	"""Wrapper class for hohlraum corrections"""
	# set up SRIM calculators:
	Al_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Aluminum.txt")
	Au_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Gold.txt")
	DU_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Uranium.txt")

	raw = [] # raw spectrum
	raw_fit = [] # Gaussian fit to the raw spectrum
	corr = [] # corrected spectrum
	corr_fit = [] # Gaussian fit to the corrected spectrum

	# thickness in um of three hohlraum components:
	Au = 0
	DU = 0
	Al = 0

	def __init__(self, raw, Au, DU, Al):
		super(Hohlraum, self).__init__()
		self.Au = Au
		self.DU = DU
		self.Al = Al

		# copy the raw data to a class variable:
		self.raw = numpy.array(raw)

		# correct the spectrum:
		self.correct_spectrum()

		# fit ot the data:
		self.fit_data()

	def correct_spectrum(self):
		self.corr = numpy.zeros( [len(self.raw) , len(self.raw[0])] , numpy.float32 ) # array of corrected data

		# loop over all data:
		for i in range(len(self.raw)):
			# calculate new energy:
			new_E = self.shift_energy(self.raw[i][0])
			
			# infer the bin size:
			bin = 0
			# make sure we don't cause problems with array indices:
			if i > 0:
				bin = self.raw[i][0] - self.raw[i-1][0]
			else:
				bin = self.raw[i+1][0] - self.raw[i][0]

			# calculate a corrected bin size:
			new_bin = ( self.shift_energy(self.raw[i][0]+bin/2)
				- self.shift_energy(self.raw[i][0]-bin/2) )
			
			# correct for accordian effect due to bin width:
			new_Y = self.raw[i][1] * bin/new_bin

			# error bar is statistical. Sqrt(n) is unchanged, but the
			# Y value is changed due to accordion effect, which we must
			# correct for:
			new_err = self.raw[i][2] * new_Y / self.raw[i][1]

			# Add this data point to the corrected array:
			self.corr[i][0] = new_E
			self.corr[i][1] = new_Y
			self.corr[i][2] = new_err


	def shift_energy(self,E):
		new_E = E
		# correct for Al:
		new_E = self.Al_SRIM.Ein(new_E,self.Al)
		# correct for DU:
		new_E = self.DU_SRIM.Ein(new_E,self.DU)
		# correct for Au:
		new_E = self.Au_SRIM.Ein(new_E,self.Au)

		return new_E

	def fit_data(self):
		# fit to the raw data:
		self.raw_fit = GaussFit(self.raw)

		# fit corrected data:
		g = [ self.get_fit_raw()[0] , 
			self.shift_energy(self.get_fit_raw()[1]) ,
			self.get_fit_raw()[2] ]

		self.corr_fit = GaussFit(self.corr,guess=g)

	def get_fit_raw(self):
		return self.raw_fit.get_fit()
	def get_fit_corr(self):
		return self.corr_fit.get_fit()
	def get_E_shift(self):
		raw = self.raw_fit.get_fit()[1]
		corr = self.corr_fit.get_fit()[1]
		return corr-raw

	## Save a plot to file
	# @param fname the file to save
	def plot_file(self,fname):
		matplotlib.use('Agg')
		import matplotlib.pyplot as plt

		# get the figure:
		fig = self.plot()

		# save to file:
		fig.savefig(fname)

	## Make a plot in new UI window
	def plot_window(self):
		if matplotlib.get_backend() != 'MacOSX':
			matplotlib.pyplot.switch_backend('MacOSX')
		import matplotlib.pyplot as plt

		# get the figure:
		fig = self.plot()

		plt.show()

	## Make a plot of the data and fit
	# @return matplotlib figure
	def plot(self):
		import matplotlib.pyplot as plt

		# make figure and subplot:
		fig = plt.figure()
		ax = fig.add_subplot(111)

		# split up raw data into columns:
		raw_x = numpy.zeros( len(self.raw) )
		raw_y = numpy.zeros( len(self.raw) )
		raw_err = numpy.zeros( len(self.raw) )
		for i in range(len(self.raw)):
			raw_x[i] = self.raw[i][0]
			raw_y[i] = self.raw[i][1]
			raw_err[i] = self.raw[i][2]

		# plot the data with error bars
		ax.errorbar(
			raw_x, # x values
			raw_y, # y values
			yerr=raw_err, # y error bars
			marker='s', # square markers
			lw=0, # no lines connecting points
			elinewidth=1, # error bar line width
			mfc='red', # marker color
			mec='red', # marker line color
			ecolor='red') # error bar color

		# split up corrected data into columns:
		corr_x = numpy.zeros( len(self.corr) )
		corr_y = numpy.zeros( len(self.corr) )
		corr_err = numpy.zeros( len(self.corr) )
		for i in range(len(self.corr)):
			corr_x[i] = self.corr[i][0]
			corr_y[i] = self.corr[i][1]
			corr_err[i] = self.corr[i][2]

		# plot the data with error bars
		ax.errorbar(
			corr_x, # x values
			corr_y, # y values
			yerr=corr_err, # y error bars
			marker='s', # square markers
			lw=0, # no lines connecting points
			elinewidth=1, # error bar line width
			mfc='blue', # marker color
			mec='blue', # marker line color
			ecolor='blue') # error bar color

		# make an evaluted fit dataset for plotting
		fit_x = []
		fit_y = []
		x = raw_x[0]
		dx = (raw_x[1] - x) / 10
		while x < raw_x[-1]:
			fit_x.append(x)
			fit_y.append(self.raw_fit.eval_fit(x))
			x += dx

		ax.plot(fit_x,fit_y,'r--')

		# make an evaluted fit dataset for plotting
		fit_x = []
		fit_y = []
		x = corr_x[0]
		dx = (corr_x[1] - x) / 10
		while x < corr_x[-1]:
			fit_x.append(x)
			fit_y.append(self.corr_fit.eval_fit(x))
			x += dx

		ax.plot(fit_x,fit_y,'b--')

		# add text with fit parameters
		# location for the text: (based on line position)
		x = self.get_fit_corr()[1] + 4*self.get_fit_corr()[2]
		y = self.get_fit_corr()[0] * 1/2
		# construct a text string to display:
		text = '\n'
		text += r'$E_{raw}$ = ' + '{:.2f}'.format(self.get_fit_raw()[1]) + ' MeV'
		text += '\n'
		text += r'$E_{corr}$ = ' + '{:.2f}'.format(self.get_fit_corr()[1]) + ' MeV'
		# write text to the plot:
		ax.text(x,y, # data
			text, # text to display
			color='black',
			backgroundcolor='white', # fill background
			bbox=dict(ec='black', fc='white', alpha=1.0)) # add black boundary

		ax.grid(True)
		ax.set_xlabel('Energy (MeV)')
		ax.set_ylabel('Yield/MeV')
		#ax.set_title(self.name)

		return fig


