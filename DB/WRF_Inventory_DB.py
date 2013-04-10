## Python-based database utility for WRF inventory management
# @author Alex Zylstra
# @date 2013/03/01

import sqlite3
import csv

import Database
from Generic_DB import *
from util import *

# The table is arranged with columns:
# (name text, DIM text, pos int, theta real, phi real, r real )

class WRF_Inventory_DB(Generic_DB):
	"""Provide a wrapper for WRF inventory DB actions."""
	## database connector
	db = 0
	## database cursor
	c = 0 
	## name of the table for the snout data
	TABLE = Database.WRF_INVENTORY_TABLE
	
	## Class constructor, which connects to the database
	# @param fname the file location/name for the database
	def __init__(self, fname):
		"""Initialize the WRF inventory database wrapper."""
		super(WRF_Inventory_DB,self).__init__(fname) # call super constructor
		self.__init_wrf_inventory__()

	def __init_wrf_inventory__(self):
		"""initialize the table."""
		# check to see if it exists already
		query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

		# create new table:
		if(query.fetchone()[0] == 0): # table does not exist
			self.c.execute('''CREATE TABLE %s 
				(id text, shots int, status text)''' % self.TABLE)
			self.c.execute('CREATE INDEX wrf_inventory_index on %s(id)' % self.TABLE)

		# finish changes:
		self.db.commit()

	## Get a list of (unique) WRF IDs in the database
	# @return python array of ID strings
	def get_ids(self):
		"""Get a list of (unique) WRF IDs in the database."""
		query = self.c.execute( 'SELECT Distinct id from %s' % self.TABLE)
		return flatten(array_convert(query))

	## Get number of shots for a given wedge ID.
	# @param id the WRF id (aka serial number)
	# @return number of shots the wedge has been used on
	def get_shots(self, id):
		"""Get number of shots for a given wedge ID."""
		query = self.c.execute( 'SELECT shots from %s where id=?' % self.TABLE , (id,) )
		return flatten(array_convert(query))[0]

	## Get current stats for a given wedge ID.
	# @param id the WRF id (aka serial number)
	# @return this wedge's status
	def get_status(self, id):
		"""Get current stats for a given wedge ID."""
		query = self.c.execute( 'SELECT status from %s where id=?' % self.TABLE , (id,) )
		return flatten(array_convert(query))[0]

	## Insert a new row into the table.
	# @param id the WRF id (aka serial number)
	# @param shots the number of shots this wedge has been used on
	# @param status the current WRF status
	def insert(self, id, shots, status):
		"""Insert a new row of data into the table."""
		# first check for duplicates:
		query = self.c.execute( 'SELECT * from %s where id=?' 
			% self.TABLE, (id,))

		# not found:
		if(len(query.fetchall()) <= 0): # not found in table:
			newval = (id,shots,status,)
			self.c.execute( 'INSERT INTO %s values (?,?,?)' % self.TABLE , newval )

		# if the row exists already, do an update instead
		else: 
			self.update(id,shots,status)

		# save change:
		self.db.commit()

	## Update data for a wedge in the table
	# @param id the wedge id to update
	# @param shots the number of shots this wedge has been used on
	# @param status the current status of this wedge
	def update(self, id, shots, status):
		"""Update a value in the table."""
		# update columns one at a time:
		s = 'UPDATE %s SET shots=? WHERE id=?' % self.TABLE
		self.c.execute( s , (shots,id,) )
		s = 'UPDATE %s SET status=? WHERE id=?' % self.TABLE
		self.c.execute( s , (status,id,) )

		# save changes to db:
		self.db.commit()