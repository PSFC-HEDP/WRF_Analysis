## Python-based database utility for general shot data
# @author Alex Zylstra
# @date 2013/03/01

import sqlite3
import csv

import Database
from Generic_DB import *
from util import *

# The table is arranged with columns:
# (name text, pos int, theta real, phi real, r real )

class Shot_DB(Generic_DB):
	"""Provide a wrapper for shot DB actions."""
	## database connector
	db = 0
	## database cursor
	c = 0 
	## name of the table for the shot data
	TABLE = Database.SHOT_TABLE
	
	## Class constructor, which connects to the database
	# @param fname the file location/name for the database
	def __init__(self, fname):
		"""Initialize the shot database wrapper."""
		super(Shot_DB,self).__init__(fname) # call super constructor
		self.__init_shot__()

	def __init_shot__(self):
		"""initialize the shot table."""
		# check to see if it exists already
		query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

		# create new table:
		if(query.fetchone()[0] == 0): # table does not exist
			self.c.execute('''CREATE TABLE %s (shot text)''' % self.TABLE)
			self.c.execute('CREATE INDEX shot_index on %s(shot)' % self.TABLE)

		# finish changes:
		self.db.commit()

	## Get a list of (unique) shot in the database
	# @return python array of shot strings
	def get_shots(self):
		"""Get a list of unique shot names in the table."""
		query = self.c.execute( 'SELECT Distinct shot from %s' % self.TABLE)
		return self.array_convert(query)

	## Add a new shot to the table. Data insertion done via update method ONLY (for shot db).
	# @param shot the new shot name
	def insert(self, shot):
		"""Add a new shot to the table. Data insertion done via update method ONLY (for shot db)."""
		# first check for duplicates:
		query = self.c.execute( 'SELECT * from %s where shot=?' % self.TABLE, (shot,))

		# not found:
		if(len(query.fetchall()) <= 0): # not found in table:
			#newval = (name,pos,theta,phi,r,)
			self.c.execute( 'INSERT INTO %s (shot) values (?)' % self.TABLE , (shot,) )

		# save change:
		self.db.commit()

	## Update an existing row in the table
	# @param shot the shot number
	# @param col the column name to alter
	# @param val the column value
	def update(self, shot, col, val):
		"""Update a value in the table."""
		s = 'UPDATE %s SET [%s]=? WHERE shot=?' % (self.TABLE,col,)
		self.c.execute( s , (val,shot,) )
		self.db.commit()

	## Get all rows for a given shot
	# @param shot the shot number to query
	# @return all rows found for shot
	def query(self, shot):
		"""Find data specified by shot number."""
		query = self.c.execute( 'SELECT * from %s where shot=?' % self.TABLE , (shot,))
		return array_convert(query)[0]

	## Get data for a specific shot and column
	# @param shot the shot to query
	# @param col name of the column you want
	# @return column's value, or a 2 value tuple if there is an associated error bar
	def query_col(self, shot, col):
		"""Get data for a specific shot and column."""
		query = self.c.execute( 'SELECT [%s] from %s where shot=?' % (col,self.TABLE) , (shot,))
		value = array_convert(query)[0][0]

		# check if there is an error bar for this value:
		if (col+' Unc') in self.get_column_names():
			query = self.c.execute( 'SELECT [%s] from %s where shot=?' % (col+' Unc',self.TABLE) , (shot,))
			err = array_convert(query)[0][0]
			return value,err

		return value