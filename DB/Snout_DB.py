## Python-based database utility for WRF snout configurations
# @author Alex Zylstra
# @date 2013/03/01

import sqlite3
import csv

import Database
from Generic_DB import *
from util import *

# The table is arranged with columns:
# (name text, DIM text, pos int, theta real, phi real, r real )

class Snout_DB(Generic_DB):
	"""Provide a wrapper for snout DB actions."""
	## database connector
	db = 0
	## database cursor
	c = 0 
	## name of the table for the snout data
	TABLE = Database.SNOUT_TABLE
	
	## Class constructor, which connects to the database
	# @param fname the file location/name for the database
	def __init__(self, fname):
		"""Initialize the snout database wrapper."""
		super(Snout_DB,self).__init__(fname) # call super constructor
		self.__init_snout__()

	def __init_snout__(self):
		"""initialize the snout table."""
		# check to see if it exists already
		query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

		# create new table:
		if(query.fetchone()[0] == 0): # table does not exist
			self.c.execute('''CREATE TABLE %s 
				(name text, DIM text, pos int, theta real, phi real, r real)''' % self.TABLE)
			self.c.execute('CREATE INDEX snout_index on %s(name)' % self.TABLE)

		# finish changes:
		self.db.commit()

	## Get a list of (unique) names in the database
	# @return python array of name strings
	def get_names(self):
		"""Get a list of unique snout names in the table."""
		query = self.c.execute( 'SELECT Distinct name from %s' % self.TABLE)
		return flatten(array_convert(query))

	## Get a list of (unique) positions defined for the given name.
	# @param name the snout name
	# @param DIM the NIF DIM (text, e.g. '90-78')
	# @return a python array of positions (integers)
	def get_pos(self, name, DIM):
		"""Get a list of positions for the configuration specified by name and DIM."""
		query = self.c.execute( 'SELECT Distinct pos from %s where name=? and DIM=?' % self.TABLE , (name,DIM,) )
		return flatten(array_convert(query))

	## Get a list of (unique) DIMs defined for the given name.
	# @param name the snout name
	# @return a python array of DIMs (strings)
	def get_DIM(self, name):
		"""Get a list of DIMs for the configuration specified by name."""
		query = self.c.execute( 'SELECT Distinct DIM from %s where name=?' % self.TABLE , (name,) )
		return flatten(array_convert(query))

	## Insert a new row into the table.
	# @param name the snout configuration name
	# @param DIM the NIF DIM (text, e.g. '90-78')
	# @param pos the WRF position number (1,2,3,4,...)
	# @param theta the WRF polar angle in degrees
	# @param phi the WRF azimuthal angle in degrees
	# @param r the WRF radial distance in cm
	def insert(self, name, DIM, pos, theta, phi, r):
		"""Insert a new row of data into the table."""
		# first check for duplicates:
		query = self.c.execute( 'SELECT * from %s where name=? and DIM=? and pos=?' 
			% self.TABLE, (name,DIM,pos,))

		# not found:
		if(len(query.fetchall()) <= 0): # not found in table:
			newval = (name,DIM,pos,theta,phi,r,)
			self.c.execute( 'INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE , newval )

		# if the row exists already, do an update instead
		else: 
			self.update(name,pos,'theta',theta)
			self.update(name,pos,'phi',phi)
			self.update(name,pos,'r',r)

		# save change:
		self.db.commit()

	## Update an existing row in the table
	# @param name the snout configuration name
	# @param DIM the NIF DIM (text, e.g. '90-78')
	# @param pos the WRF position number (1,2,3,4,...)
	# @param col the column name to alter
	# @param val the column value
	def update(self, name, DIM, pos, col, val):
		"""Update a value in the table."""
		s = 'UPDATE %s SET %s=%s WHERE name=? AND DIM=? AND pos=?' % (self.TABLE,col,val,)
		self.c.execute( s , (name,DIM,pos,) )
		self.db.commit()

	## Get all rows for a given name and position
	# @param name of the configuration you want
	# @param DIM the NIF DIM (text, e.g. '90-78')
	# @param pos the WRF position # (int)
	# @return all rows found which match name and pos
	def query(self, name, DIM, pos):
		"""Find data specified by name and position."""
		query = self.c.execute( 'SELECT * from %s where name=? and DIM=? and pos=?'
			 % self.TABLE , (name,DIM,pos,))
		return array_convert(query)