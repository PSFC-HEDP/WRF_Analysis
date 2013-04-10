## Python-based database utility for a generic database wrapper
# @author Alex Zylstra
# @date 2013/02/17

import sqlite3
import csv
import shlex

import Database
from util import *

class Generic_DB:
	"""Provide a wrapper for generic DB actions."""
	## database connector
	db = 0
	## database cursor
	c = 0 
	## name of the table for the data
	TABLE = ''
	
	## Class constructor, which connects to the database
	# @param fname the file location/name for the database
	def __init__(self, fname):
		"""Initialize the database wrapper."""
		self.db = sqlite3.connect(fname)
		self.c = self.db.cursor()

	## Class desctructor
	def __del__(self):
		"""Properly close database objects."""
		self.db.commit()
		self.db.close()
	
	## Get the number of rows in the database
	# @return the number of rows
	def num_rows(self):
		"""Get the total number of rows in table."""
		query = self.c.execute( 'SELECT count(*) from %s' % self.TABLE )

		return query.fetchone()[0]

	## Get the number of columns in the database
	# @return the number of columns
	def num_columns(self):
		"""Get the number of columns in the table."""
		return len(self.get_columns())

	## Get a list of columns in the table
	def get_columns(self):
		"""Get a list of columns in the table."""
		query = self.c.execute( 'PRAGMA table_info(%s)' % self.TABLE )
		return array_convert(query)

	## Get a list of column names in the table
	def get_column_names(self):
		"""Get a list of columns in the table."""
		query = self.c.execute( 'PRAGMA table_info(%s)' % self.TABLE )
		# get an array of column info:
		columns = array_convert(query)

		# The default SQL result contains other metainfo (data type, etc)
		# Cut it down to just the column names:
		ret = []
		for i in columns:
			ret.append(i[1])
		return ret

	## Execute a generic SQL query. Be careful!
	# @param the query (ie a string in SQL syntax)
	# @return your results
	def sql_query(self,query):
		"""Execute a generic SQL query. Be careful!"""
		return self.c.execute(query)

	## Clear all data from the table
	def clear(self):
		"""Clear all data from the table."""
		self.c.execute( 'DELETE from %s' % self.TABLE )
		self.db.commit()

	## Add a column to the table
	# @param name the name of the column you want to add
	# @param type a string defining the type of data for this column
	def add_column(self, name, type):
		"""Add a new column to the table."""
		# First, check for existing column to avoid duplicates:
		if name not in self.get_column_names():
			# add the column and commit changes to DB:
			self.c.execute( "ALTER TABLE %s ADD [%s] %s" % (self.TABLE, name, type))
			self.db.commit()

	## Import data from a CSV file
	# @fname the file to import from
	def csv_import(self, fname):
		"""Read all data from a csv file into the table"""
		# drop the existing table
		self.c.execute( 'DROP TABLE %s' % self.TABLE )
		table_created = False

		# try to open the file:
		with open(fname) as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',')
			header = next(csvreader) # read header

			# add columns to the table from the header info:
			for col in header:
				# use the shlex to split the header text into list:
				splitter = shlex.shlex(col, posix=True)
				splitter.whitespace += ','
				splitter.whitespace_split = True
				h = list(splitter) # temporary list

				# if the table hasn't been remade yet:
				if table_created == False:
					# create a new table with the first column:
					self.c.execute( 'CREATE TABLE %s ([%s] %s)' % (self.TABLE, h[1], h[2]))
					# automatically index by the first column:
					self.c.execute( 'CREATE INDEX %s_index on %s([%s])' % (self.TABLE, self.TABLE, h[1]))
					table_created = True
				# otherwise just add a column:
				else:
					self.c.execute( "ALTER TABLE %s ADD [%s] %s" % (self.TABLE , h[1] , h[2]) )

			# iterate over each row in the CSV file:
			for row in csvreader:
				# create a command string and array of values to insert:
				command = 'INSERT INTO %s values(' % self.TABLE
				values = []
				for val in row:
					values.append(val)
					command += '?,'
				# remove trailing ',' and then add a close paren to command:
				command = command[:-1]
				command += ')'
				# execute the operation:
				self.c.execute( command, values )

		# finalize changes to database:
		self.db.commit()

	## Export data to CSV
	# @fname the file name to write CSV file
	def csv_export(self, fname):
		"""Write all data from the table to a csv file"""
		with open(fname, 'w', newline='\n') as csvfile:
			csvwriter = csv.writer(csvfile, delimiter=',')

			# write header:
			query = self.c.execute( "PRAGMA table_info(%s)" % self.TABLE )
			csvwriter.writerow( query.fetchall() )

			# query all rows from the DB:
			query = self.c.execute( 'SELECT * from %s' % self.TABLE )
			for row in query:
				csvwriter.writerow(row)