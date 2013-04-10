## Python-based database utility for WRF snout configurations
# @author Alex Zylstra
# @date 2013/03/01

import sqlite3
import csv

import Database
from Generic_DB import *
from util import *

# The table is arranged with columns:
# (name text, layer int, material text, r real, z real)

class Hohlraum_DB(Generic_DB):
	"""Provide a wrapper for hohlraum DB actions."""
	## database connector
	db = 0
	## database cursor
	c = 0 
	## name of the table for the hohlraum data
	TABLE = Database.HOHLRAUM_TABLE
	
	## Class constructor, which connects to the database
	# @param fname the file location/name for the database
	def __init__(self, fname):
		"""Initialize the hohlraum database wrapper."""
		super(Hohlraum_DB,self).__init__(fname) # call super constructor
		self.__init_hohlraum__()

	def __init_hohlraum__(self):
		"""initialize the hohlraum table."""
		# check to see if it exists already
		query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

		# create new table:
		if(query.fetchone()[0] == 0): # table does not exist
			self.c.execute('''CREATE TABLE %s 
				(drawing text, name text, layer int, material text, r real, z real)''' % self.TABLE)
			self.c.execute('CREATE INDEX hohlraum_index on %s(drawing)' % self.TABLE)

		# finish changes:
		self.db.commit()

	## Get a list of (unique) names in the database
	# @return python array of name strings
	def get_names(self):
		"""Get a list of unique hohlraum names in the table."""
		query = self.c.execute( 'SELECT Distinct name from %s' % self.TABLE)
		return flatten(array_convert(query))

	## Get a list of (unique) drawing numbers in the database
	# @return python array of name strings
	def get_drawings(self):
		"""Get a list of unique hohlraum drawing numbers in the table."""
		query = self.c.execute( 'SELECT Distinct drawing from %s' % self.TABLE)
		return flatten(array_convert(query))

	## Get the name for a drawing number
	# @param drawing the drawing number to query
	# @return a unique name found for the drawing number
	def get_drawing_name(self, drawing):
		"""Get the name for a drawing number."""
		query = self.c.execute( 'SELECT Distinct name from %s where drawing=(?)' % self.TABLE, (drawing,) )
		return flatten(array_convert(query))

	## Get the drawing number for a given name
	# @param name the hohlraum desing name you want to query
	# @return a unique drawing number found for that name
	def get_name_drawing(self, name):
		"""Get the drawing number for a given name."""
		query = self.c.execute( 'SELECT Distinct drawing from %s where name=(?)' % self.TABLE, (name,) )
		return flatten(array_convert(query))

	## Get a list of (unique) layers defined for the given hohlraum name or drawing number.
	# @param name the hohlraum name
	# @return a python array of layer indices (integers)
	def get_layers(self, name='', drawing=''):
		"""Get a list of (unique) layers defined for the given hohlraum name or drawing number."""
		# sanity check: if both string are empty, we cannot query
		if name == '' and drawing == '':
			return
		# if both arguments have text, match both:
		elif name != '' and drawing != '':
			query = self.c.execute( 'SELECT Distinct layer from %s where name=? and drawing=?' 
				% self.TABLE , (name,drawing,) )
		# match name only:
		elif name != '':
			query = self.c.execute( 'SELECT Distinct layer from %s where name=?' % self.TABLE , (name,) )
		# match drawing only:
		else:
			query = self.c.execute( 'SELECT Distinct layer from %s where drawing=?' % self.TABLE , (drawing,) )

		return flatten(array_convert(query))

	## Insert a new row into the table.
	# @param drawing the hohlraum drawing number
	# @param name the hohlraum configuration name
	# @param layer the material wall index (0,1,2,..)
	# @param material the wall material for this layer
	# @param r radius in cm
	# @param z length in cm
	def insert(self, drawing, name, layer, material, r, z):
		"""Insert a new row of data into the table."""
		# first check for duplicates:
		query = self.c.execute( 'SELECT * from %s where name=? and drawing=? and layer=? and material=? and r=? and z=?' 
			% self.TABLE, (name,drawing,layer,material,r,z,))

		# not found:
		if(len(query.fetchall()) <= 0): # not found in table:
			newval = (drawing,name,layer,material,r,z,)
			self.c.execute( 'INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE , newval )

		# save change:
		self.db.commit()

	## Drop all rows corresponding to one configuration
	# @param drawing the hohlraum drawing
	# @param layer the layer index (0,1,2...)
	def drop(self, drawing, layer):
		"""Drop a wall in the table."""
		s = 'DELETE FROM %s WHERE drawing=? AND layer=?' % self.TABLE
		self.c.execute( s , (drawing,layer,) )
		self.db.commit()

	## Get all rows for a given drawing and layer
	# @param drawing the hohlraum drawing number
	# @param layer the wall layer index
	# @return all rows found which match name and layer
	def query_drawing(self, drawing, layer):
		"""Find data specified by drawing and position."""
		query = self.c.execute( 'SELECT * from %s where drawing=? and layer=?' % self.TABLE , (drawing,layer,))
		return array_convert(query)

	## Get all rows for a given drawing and layer
	# @param name the hohlraum configuration name
	# @param layer the wall layer index
	# @return all rows found which match name and layer
	def query_name(self, name, layer):
		"""Find data specified by name and position."""
		query = self.c.execute( 'SELECT * from %s where name=? and layer=?' % self.TABLE , (name,layer,))
		return array_convert(query)