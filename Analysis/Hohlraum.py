## Implement functionality for hohlraum corrections.
#
# @author Alex Zylstra
# @date 2013/04/19
# @copyright MIT / Alex Zylstra

import numpy
import scipy.interpolate
import scipy.stats
import StopPow
from GaussFit import *
import matplotlib
import matplotlib.pyplot as plt
import sys

## Calculate radius along LOS given z
# @param z the axial position in cm
# @param theta the LOS polar angle
# @return r the radial position in cm
def LOS_r(z, theta):
	theta2 = math.radians( 90 - theta )
	return z / math.tan(theta2)

## Calculate z along LOS given r
# @param r the radial position in cm
# @param theta the LOS polar angle
# @return z the axial position in cm
def LOS_z(r, theta):
	theta2 = math.radians( 90 - theta )
	return r * math.tan(theta2)

## Sort two lists simultaneously, using first as key
# @param list1 first list (will be sorted by this one)
# @param list2 second list
# @return (list1,list2) sorted
def double_list_sort(list1,list2):
	list1 , list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
	return list1 , list2

## Flatten a list, i.e. [[1,2],[3,4]] -> [1,2,3,4]
# @param l the list to flatten
# @return the flattened list
def flatten(l):
	return [item for sublist in l for item in sublist]

## Wrapper class for hohlraum corrections, and associated metrics
# @class Hohlraum
# @brief Correct proton spectra for the hohlraum wall.
# @author Alex Zylstra
# @date 2013/04/11
# @copyright MIT / Alex Zylstra
class Hohlraum(object):
	"""Wrapper class for hohlraum corrections"""
	OutputDir = 'AnalysisOutputs'

	# set up SRIM calculators:
	Al_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Aluminum.txt") ## SRIM stopping power for Al
	Au_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Gold.txt") ## SRIM stopping power for Au
	DU_SRIM = StopPow.StopPow_SRIM("SRIM/Hydrogen in Uranium.txt") ## SRIM stopping power for DU

	raw = [] ## raw spectrum
	raw_fit = [] ## Gaussian fit to the raw spectrum
	corr = [] ## corrected spectrum
	corr_fit = [] ## Gaussian fit to the corrected spectrum

	# thickness in um of three hohlraum components:
	Au = 0 ## Calculated or given thickness of Au
	DU = 0 ## Calculated or given thickness of DU
	Al = 0 ## Calculated or given thickness of Al
	# uncertainties in thickness:
	d_Au = 0 ## Calculated or given uncertainty in thickness of Au
	d_DU = 0 ## Calculated or given uncertainty in thickness of DU
	d_Al = 0 ## Calculated or given uncertainty in thickness of Al

	#  r and z arrays for all wall layers:
	all_r = []
	all_z = []
	layer_mat = []
	angles = []

	## Constructor for the hohlraum. You must supply either the thickness array or an array containing wall data plus view angles.
	# @param raw the raw spectrum
	# @param wall python array of [ Drawing , Name , Layer # , Material , r (cm) , z (cm) ]
	# @param angles python array of [theta_min, theta_max] range in polar angle
	# @param Thickness the [Au,DU,Al] thickness in um
	# @param d_Thickness the uncertainty in wall thickness for [Au,DU,Al] in um
	def __init__(self, raw, wall=None, angles=None, Thickness=None, d_Thickness=[1,1,3]):
		super(Hohlraum, self).__init__() # super constructor

		# if the wall is specified:
		if wall is not None and angles is not None:
			self.calc_from_wall(wall, angles)
		# thickness is specified:
		elif Thickness is not None and len(Thickness) is 3:
			self.Au = Thickness[0]
			self.DU = Thickness[1]
			self.Al = Thickness[2]
		# if neither is supplied, default to 0 thickness to be safe:
		else:
			self.Au = 0
			self.DU = 0
			self.Al = 0

		# copy the raw data to a class variable:
		self.raw = numpy.copy(raw)

		# set the uncertainties:
		self.d_Au = d_Thickness[0]
		self.d_DU = d_Thickness[1]
		self.d_Al = d_Thickness[2]

		# correct the spectrum:
		self.correct_spectrum()

		# fit to the data:
		self.fit_data()

	## Calculate the material thicknesses from a wall definition. Sets the class variables Au, DU, and Al.
	# @param wall python array of [ Drawing , Name , Layer # , Material , r (cm) , z (cm) ]
	# @param angles python array of [theta_min, theta_max] range in polar angle
	def calc_from_wall(self, wall, angles):
		self.Au = 0
		self.DU = 0
		self.Al = 0

		# ------------------------------------------------
		# Split the incoming wall data into layers:
		# ------------------------------------------------
		# figure out how many layers there are:
		num_layers = 0
		for i in wall:
			num_layers = max(num_layers,i[2])
		num_layers += 1 # correct for zero-index data

		# construct r and z arrays for all layers:
		self.all_r = []
		self.all_z = []
		self.layer_mat = []
		# create arrays of correct length for each layer:
		for i in numpy.arange(num_layers):
			self.all_r.append( [] )
			self.all_z.append( [] )
			self.layer_mat.append( [] )

		# now read data into the new arrays:
		for i in wall:
			self.all_r[ int(i[2]) ].append(i[4])
			self.all_z[ int(i[2]) ].append(i[5])
			if len(self.layer_mat[ int(i[2]) ]) is 0:
				self.layer_mat[ int(i[2]) ] = i[3]

		# we need to have the wall data sorted:
		# iterate over each layer
		for i in range(int(num_layers)):
			# sort r values and z values together:
			self.all_z[i] , self.all_r[i] = double_list_sort( self.all_z[i] , self.all_r[i] )

		# ------------------------------------------------
		# Incorporate layer data into the class info:
		# ------------------------------------------------
		# iterate over layers
		# each layer has two walls, thus factor of 2:
		for i in range(int(num_layers/2)):
			thickness = self.calc_layer_thickness( self.all_r[2*i], self.all_z[2*i], self.all_r[2*i+1], self.all_z[2*i+1], angles )
			# check material:
			if self.layer_mat[2*i] == 'Au':
				self.Au += thickness[0]*1e4 # also convert -> um
			elif self.layer_mat[2*i] == 'DU':
				self.DU += thickness[0]*1e4 # also convert -> um
			elif self.layer_mat[2*i] == 'Al':
				self.Al += thickness[0]*1e4 # also convert -> um

		self.angles = angles


	## Calculate the average thickness of a wall layer
	# @param inner_r list of r values for points defining the inner wall
	# @param inner_z list of z values for points defining the inner wall
	# @param outer_r list of r values for points defining the outer wall
	# @param outer_z list of z values for points defining the outer wall
	# @param angles [min,max] polar angles for the line of sight
	# @param n (optional) number of angle points to sample (default = 50)
	# @return (mean , stdev) of the thickness
	def calc_layer_thickness(self,inner_r,inner_z,outer_r,outer_z,angles,n=50):
		values = []
		dtheta = (angles[1] - angles[0])/n
		#iterate over angles:
		for theta in numpy.arange(angles[0],angles[1],dtheta):
			# set up interpolation:
			inner_int = scipy.interpolate.interp1d(
				inner_z,
				inner_r,
				kind='linear', bounds_error=False, fill_value=1e10 )
			outer_int = scipy.interpolate.interp1d(
				outer_z,
				outer_r,
				kind='linear', bounds_error=False, fill_value=1e10 )

			# calculate the intersection points:
			z1 = scipy.optimize.fminbound(
				func=(lambda x: math.fabs(inner_int(x)-LOS_r(x,theta))),
				x1=min(inner_z),
				x2=max(inner_z), 
				xtol=1e-7)
			r1 = LOS_r(z1,theta)
			z2 = scipy.optimize.fminbound(
				func=(lambda x: math.fabs(outer_int(x)-LOS_r(x,theta))),
				x1=min(outer_z),
				x2=max(outer_z), 
				xtol=1e-7)
			r2 = LOS_r(z2,theta)

			# calculate thickness:
			values.append( math.sqrt( (z2-z1)**2 + (r2-r1)**2 ) )

		return scipy.stats.tmean(values) , scipy.stats.tstd(values)


	## Calculate the corrected spectrum
	# @param Al (optional) the aluminum thickness in um
	# @param DU (optional) the uranium thickness in um
	# @param Au (optional) the gold thickness in um
	def correct_spectrum(self, Al=None, DU=None, Au=None):
		self.corr = numpy.zeros( [len(self.raw) , len(self.raw[0])] , numpy.float32 ) # array of corrected data

		# if no thicknesses are input, use default class variables:
		if Al is None:
			Al = self.Al
		if DU is None:
			DU = self.DU
		if Au is None:
			Au = self.Au

		# loop over all data:
		for i in range(len(self.raw)):
			# calculate new energy:
			new_E = self.shift_energy(self.raw[i][0],Al=Al,DU=DU,Au=Au)
			
			# infer the bin size:
			bin = 0
			# make sure we don't cause problems with array indices:
			if i > 0:
				bin = self.raw[i][0] - self.raw[i-1][0]
			else:
				bin = self.raw[i+1][0] - self.raw[i][0]

			# calculate a corrected bin size:
			new_bin = ( self.shift_energy(self.raw[i][0]+bin/2,Al=Al,DU=DU,Au=Au)
				- self.shift_energy(self.raw[i][0]-bin/2,Al=Al,DU=DU,Au=Au) )
			
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

	## Calculate the energy shift for a given incident energy
	# @param E the incident energy for a proton in MeV
	# @param Al (optional) the aluminum thickness in um
	# @param DU (optional) the uranium thickness in um
	# @param Au (optional) the gold thickness in um
	# @return the energy out in MeV
	def shift_energy(self,E, Al=None, DU=None, Au=None):
		# if no thicknesses are input, use default class variables:
		if Al is None:
			Al = self.Al
		if DU is None:
			DU = self.DU
		if Au is None:
			Au = self.Au
		
		new_E = E
		# correct for Al:
		new_E = self.Al_SRIM.Ein(new_E,Al)
		# correct for DU:
		new_E = self.DU_SRIM.Ein(new_E,DU)
		# correct for Au:
		new_E = self.Au_SRIM.Ein(new_E,Au)

		return new_E

	## Calculate fits to the raw and shifted spectra
	def fit_data(self):
		# fit to the raw data:
		self.raw_fit = GaussFit(self.raw)

		# fit corrected data:
		g = [ self.get_fit_raw()[0] , 
			self.shift_energy(self.get_fit_raw()[1]) ,
			self.get_fit_raw()[2] ]

		self.corr_fit = GaussFit(self.corr,guess=g)

	## Get the fit to the raw data
	# @return an array containing [Yp,Ep,sigma]
	def get_fit_raw(self):
		return self.raw_fit.get_fit()

	## Get the fit to the corrected data
	# @return an array containing [Yp,Ep,sigma]
	def get_fit_corr(self):
		return self.corr_fit.get_fit()

	## Get the raw data
	# @return array containing raw data
	def get_data_raw(self):
		return self.raw

	## Get the hohlraum-corrected data
	# @return array containing corrected data
	def get_data_corr(self):
		return self.corr

	## Get the peak's energy shift due to the hohlraum
	# @return peak shift in MeV
	def get_E_shift(self):
		raw = self.raw_fit.get_fit()[1]
		corr = self.corr_fit.get_fit()[1]
		return corr-raw

	## Get the uncertainty in proton mean energy due to
	# the hohlraum correction w/ given uncertainties
	# @return the uncertainties as [ [-dY,+dy] , [-dE,+dE] , [-ds,+ds] ]
	def get_unc(self):
		# nominal raw and corrected energies:
		fit_nominal = self.corr_fit.get_fit()

		# minimum thicknesses:
		Au = self.Au
		if Au > 0:
			Au -= self.d_Au
		DU = self.DU
		if DU > 0:
			DU -= self.d_DU
		Al = self.Al
		if Al > 0:
			Al -= self.d_Al

		# calculate new spectrum and fits with these thicknesses:
		self.correct_spectrum(Al=Al,DU=DU,Au=Au)
		self.fit_data()

		# fit to corrected spectrum with minimum thickness:
		fit_min = self.get_fit_corr()

		# minimum thicknesses:
		Au = self.Au
		if Au > 0:
			Au += self.d_Au
		DU = self.DU
		if DU > 0:
			DU += self.d_DU
		Al = self.Al
		if Al > 0:
			Al += self.d_Al

		# calculate new spectrum and fits with these thicknesses:
		self.correct_spectrum(Al=Al,DU=DU,Au=Au)
		self.fit_data()

		# fit to corrected spectrum with minimum thickness:
		fit_max = self.get_fit_corr()

		# put things back to nominal:
		self.correct_spectrum()
		self.fit_data()

		# we want to return uncertainties and not absolute values,
		# so reference to nominal fit:
		fit_min = numpy.absolute(fit_min - fit_nominal)
		fit_max = numpy.absolute(fit_max - fit_nominal)

		# return:
		dY = [ fit_min[0] , fit_max[0] ]
		dE = [ fit_min[1] , fit_max[1] ]
		ds = [ fit_min[2] , fit_max[2] ]
		return [ dY , dE , ds ]



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

	## Make a plot of the spectrum data (raw & corrected) and fit
	# @param ax Axes instance to plot into
	def plot(self, ax=None):
		import matplotlib.pyplot as plt
		# sanity check:
		if ax is None:
			ax = plt.gca()

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
		ax.set_title('Hohlraum Correction')

	## Save a hohlraum plot to file
	# @param fname the file to save
	def plot_hohlraum_file(self,fname):
		if matplotlib.get_backend() is 'agg':
			# get the figure:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			self.plot_hohlraum(ax)

			# save to file:
			fig.savefig(fname)

	## Make a hohlraum plot in new UI window
	def plot_hohlraum_window(self):
		if matplotlib.get_backend() is 'MacOSX':
			# get the figure:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			self.plot_hohlraum(ax)

			plt.show()

	## Make a plot of the hohlraum wall and LOS into given Axes
	# @param ax Axes instance to plot into
	def plot_hohlraum(self, ax=None):
		import matplotlib.pyplot as plt
		# sanity check:
		if ax is None:
			ax = plt.gca()

		# iterate over all layers:
		for i in numpy.arange( len(self.all_z)/2-1 , -1, -1 , int ):
			# choose a color based on material type:
			c='black'
			if self.layer_mat[2*i] == 'Au':
				c = 'orange'
			if self.layer_mat[2*i] == 'DU':
				c = '#555555'
			if self.layer_mat[2*i] == 'Al':
				c = '#aaaaaa'

			# plot this layer:
			ax.fill_between( # use fill_between type plot
				self.all_z[2*i] , # z points
				self.all_r[2*i] , # inner wall
				self.all_r[2*i+1] , # outer wall
				color=c ) # options

		# now plot the LOS:
		# find the max/min r we should plot:
		r_max = max(flatten(self.all_r))*1.1
		r_min = min(flatten(self.all_r))*0.9
		for theta in self.angles:
			r = numpy.linspace(r_min,r_max,100)
			z = LOS_z(r,theta)

			ax.plot( z , r , 'b--' )

		# add a WRF text annotation for blue lines:
		text = 'WRF LOS'
		theta = scipy.stats.tmean(self.angles)
		ax.text(LOS_z(r_max,theta),r_max, # where to put it
			text, # text to display
			color='blue', horizontalalignment='center')
			#backgroundcolor='blue') # fill background
			#bbox=dict(ec='black', fc='blue', alpha=1.0)) # add black boundary

		# add some text annotation with thicknesses:
		text = '\n'
		text += '{:.1f}'.format(self.Au) + r' $\mu$m Au'
		text += '\n'
		text += '{:.1f}'.format(self.DU) + r' $\mu$m DU'
		text += '\n'
		text += '{:.1f}'.format(self.Al) + r' $\mu$m Al'
		text += '\n'
		ax.text( 0 , r_min , text , horizontalalignment='center')

		# add an indicator showing where N pole is in this plot
		z_max = max(flatten(self.all_z))
		ax.arrow( z_max , r_min, z_max/8, 0 , fc='k', ec='k', head_width=z_max/30, head_length=z_max/30 )
		ax.text( z_max , r_min*1.02 , 'N pole' , ha='left', va='bottom')

		ax.set_xlabel('z (cm)')
		ax.set_ylabel('r (cm)')

		ax.set_title('Hohlraum Profile')
