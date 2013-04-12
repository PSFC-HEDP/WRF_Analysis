import math
import numpy
import scipy.optimize
import matplotlib
import matplotlib.pyplot as plt

## Evaluate a Gaussian distribution
# @param x the independent variable
# @param A amplitude of the distribution
# @param mu mean of the distribution
# @param sigma standard deviation of the distribution
# @return distribution evaluated at x
def Gaussian(x,A,mu,sigma):
	return A*numpy.exp(-(x-mu)**2/(2*sigma**2))/(math.sqrt(2*math.pi)*sigma)

## Perform a Gaussian fit to data, encapsulated in a class
# @class GaussFit
# @brief Wrapper for Gaussian fitting
# @author Alex Zylstra
# @date 203/04/11
# @copyright MIT / Alex Zylstra
class GaussFit(object):
	"""Wrapper class for performing Gaussian fits to data."""
	data = [] # multi-dimensional array containing data
	data_x = [] # x values of the data
	data_y = [] # y values of the data
	data_err = [] # error bars for the data
	fit = [] # result of the fit
	covariance = [] # covariance results of the fit

	# Generic guesses for fitting:
	GUESS = []

	# if the chi2 calculations should restrict limits to 5sigma of the mean
	OPT_RESTRICT_CHI2 = True

	# name of the dataset / fit
	name = ""

	## Constructor
	# @param data The data to fit. Must be 3 x n array (i.e. 3 columns, n row).
	# @param guess (optional) The initial guess for the fitting routine. Default [A,mu,sigma] = [5e7,10,1]
	# @param restrict_chi2 (optional) Whether we should restrict chi2 calculations to +/- 5 sigma of the mean. Default is true.
	# @param name (optional) a text string describing this dataset / fit
	def __init__(self, data, guess=[ 5e7 , 10 , 1 ],restrict_chi2=True,name=""):
		# super constructor:
		super(GaussFit, self).__init__()

		# copy data:
		self.data = numpy.copy(data)

		# set guess parameters:
		self.GUESS = guess

		# set name:
		self.name = name

		# set restrict chi2 option:
		self.OPT_RESTRICT_CHI2 = restrict_chi2

		# split data into components:
		self.data_x = numpy.ndarray( len(data) )
		self.data_y = numpy.ndarray( len(data) )
		self.data_err = numpy.ndarray( len(data) )
		for i in range(len(data)):
			self.data_x[i] = data[i][0]
			self.data_y[i] = data[i][1]
			self.data_err[i] = data[i][2]

		# perform the fit:
		self.do_fit()


	## Perform the fit. Called automatically by the constructor. Can be invoked again with different initial guess if desired.
	# @param guess (optional) The initial guess for the fitting routine.
	def do_fit(self, guess=[]):
		if len(guess) != 3:
			guess = self.GUESS

		# Do fit using downhill simplex:
		fit = scipy.optimize.fmin(
			func=self.chi2_other, # function to minimize
			x0=guess, # initial guess
			disp=False) # turn off console output
		self.fit = fit

	## Get the calculated best fit
	# @return array containing [A,mu,sigma] from best fit
	def get_fit(self):
		return self.fit

	## Get covariance matrix for best fit
	# @return covariance matrix (see scipy.optimize.curve_fit documentation)
	def get_covariance(self):
		return self.self.covariance

	## Evaluate the best fit
	# @param x the independent variable
	# @return the fit evaluted at x
	def eval_fit(self,x):
		return Gaussian(x,self.fit[0],self.fit[1],self.fit[2])

	## Calculate total chi2 for best fit
	# @return chi2
	def chi2(self):
		return self.chi2_other(self.fit)

	## Calculate chi2 for any fit to this data
	# @param fit an array containing the fit parameters [A,mu,sigma]
	# @return chi2 for class data and fit
	def chi2_other(self, fit):
		chi2 = 0

		# iterate over all data:
		for point in self.data:
			# if we want to restrict chi2, only count if we are within 5 sigma of mean:
			if( self.OPT_RESTRICT_CHI2 and math.fabs(point[0]-fit[1])/fit[2] <= 5 ):
				chi2 += ( Gaussian(point[0],fit[0],fit[1],fit[2]) - point[1] )**2 / (point[2])**2
			# otherwise, count all points:
			else:
				chi2 += ( Gaussian(point[0],fit[0],fit[1],fit[2]) - point[1] )**2 / (point[2])**2

		return chi2

	## Calculate reduced chi2 for the best fit
	# @return value of reduced chi2 for the best fit
	def red_chi2(self):
		return self.red_chi2_other(self.fit)

	## Calculate reduced chi2 for any fit to this data
	# @param fit an array containing the fit parameters [A,mu,sigma]
	# @return reduced chi2 for class data and fit
	def red_chi2_other(self,fit):
		return self.chi2_other(fit) / ( len(self.data) - 3 )

	## Calculate increase in chi2 due to a change in amplitude
	# @param dA change in amplitude (A' = A + dA)
	# @param sign (optional) whether amplitude should be increased or decreased (default=1 -> increase)
	# @return change in chi2
	def delta_chi2_amp(self,dA,sign=1):
		# calculate a new best fit:
		new_fit = scipy.optimize.fmin(
			func=(lambda x : self.chi2_other([self.fit[0]+sign*dA,x[0],x[1]])),
			x0=[self.fit[1],self.fit[2]],
			disp=False)

		# calculate a chi2 for the new best fit:
		chi2 = self.chi2_other( [self.fit[0]+sign*dA,new_fit[0],new_fit[1]] )

		return chi2 - self.chi2()

	## Calculate increase in chi2 due to a change in mean
	# @param dmu change in amplitude (mu' = mu + dmu)
	# @param sign (optional) whether mean should be increased or decreased (default=1 -> increase)
	# @return change in chi2
	def delta_chi2_mu(self,dmu,sign=1):
		# calculate a new best fit:
		new_fit = scipy.optimize.fmin(
			func=(lambda x : self.chi2_other([x[0],self.fit[1]+sign*dmu,x[1]])),
			x0=[self.fit[0],self.fit[2]],
			disp=False)

		# calculate a chi2 for the new best fit:
		chi2 = self.chi2_other( [new_fit[0],self.fit[1]+sign*dmu,new_fit[1]] )

		return chi2 - self.chi2()

	## Calculate increase in chi2 due to a change in sigma
	# @param ds change in amplitude (sigma' = sigma + ds)
	# @param sign (optional) whether sigma should be increased or decreased (default=1 -> increase)
	# @return change in chi2
	def delta_chi2_sigma(self,ds,sign=1):
		# calculate a new best fit:
		new_fit = scipy.optimize.fmin(
			func=(lambda x : self.chi2_other([x[0],x[1],self.fit[2]+sign*ds])),
			x0=[self.fit[0],self.fit[1]],
			disp=False)

		# calculate a chi2 for the new best fit:
		chi2 = self.chi2_other( [new_fit[0],new_fit[1],self.fit[2]+sign*ds] )

		return chi2 - self.chi2()

	## Calculate uncertainty in the fit parameters.
	# Routine: each fit parameter is varied to produce an increase of 1 in total chi2
	# @return array containing uncertainties [ [-A,+A] , [-mu,+mu] , [-sigma,+sigma] ]
	def chi2_fit_unc(self):
		# return value: delta unc in each parameter
		delta = [ [] , [] , [] ]

		# Calculate uncertainties
		# need to do for both + and -
		for sign in [-1,1]:
			# calculate uncertainty in the amplitude:
			dA = scipy.optimize.fminbound(
				func=(lambda x: math.fabs(self.delta_chi2_amp(x,sign)-1)), # min @ delta chi2 = 1
				x1=0,x2=self.fit[0], # min is 0, max is 2x nominal
				full_output=False) # suppress full output

			# calculate uncertainty in the mean:
			dmu = scipy.optimize.fminbound(
				func=(lambda x: math.fabs(self.delta_chi2_mu(x,sign)-1)), # min @ delta chi2 = 1
				x1=0,x2=self.fit[2], # min/max change +/- sigma
				full_output=False) # suppress full output

			# calculate uncertainty in sigma:
			ds = scipy.optimize.fminbound(
				func=(lambda x: math.fabs(self.delta_chi2_sigma(x,sign)-1)), # min @ delta chi2 = 1
				x1=0,x2=self.fit[2]*0.99, # min/max change +/- sigma
				full_output=False) # suppress full output

			# add info to delta:
			delta[0].append( sign*dA )
			delta[1].append( sign*dmu )
			delta[2].append( sign*ds )

		return delta

	## Save a plot to file
	# @param fname the file to save
	def plot_file(self,fname):
		if matplotlib.get_backend() is 'agg':
			# get the figure:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			self.plot(ax)

			# save to file:
			fig.savefig(fname)

	## Make a plot in new UI window
	def plot_window(self):
		if matplotlib.get_backend() is 'MacOSX':
			# get the figure:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			self.plot(ax)

			plt.show()

	## Make a plot of the data and fit, drawn into given Axes
	# @param ax Axes instance to plot into
	def plot(self,ax=None):
		# sanity check:
		if ax is None:
			ax = plt.gca()

		# plot the data with error bars
		ax.errorbar(
			self.data_x, # x values
			self.data_y, # y values
			yerr=self.data_err, # y error bars
			marker='s', # square markers
			lw=0, # no lines connecting points
			elinewidth=1, # error bar line width
			mfc='black', # marker color
			mec='black', # marker line color
			ecolor='black') # error bar color

		# make an evaluted fit dataset for plotting
		fit_x = []
		fit_y = []
		x = self.data_x[0]
		dx = (self.data_x[1] - x) / 10
		while x < self.data_x[-1]:
			fit_x.append(x)
			fit_y.append(self.eval_fit(x))
			x += dx

		ax.plot(fit_x,fit_y,'r--')

		# add text with fit parameters
		# location for the text: (based on line position)
		x = self.fit[1] + 4*self.fit[2]
		y = self.fit[0] * 1/2
		# construct a text string to display:
		text = '\n'
		text += r'$Y_p$ = ' + '{:.2e}'.format(self.fit[0])
		text += '\n'
		text += r'$E_p$ = ' + '{:.2f}'.format(self.fit[1]) + ' MeV'
		text += '\n'
		text += r'$\sigma_p$ = ' + '{:.2f}'.format(self.fit[2]) + ' MeV'
		text += '\n'
		text += r'$\chi^2$ red. = ' + '{:.2f}'.format(self.red_chi2())
		# write text to the plot:
		ax.text(x,y, # data
			text, # text to display
			backgroundcolor='white', # fill background
			bbox=dict(fc='white',ec='black', alpha=1.0)) # add black boundary

		ax.grid(True)
		ax.set_xlabel('Energy (MeV)')
		ax.set_ylabel('Yield / MeV')
		ax.set_title(self.name)

		#return fig
