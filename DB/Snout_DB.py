
import DB.Database as Database
from DB.Generic_DB import *

# The table is arranged with columns:
# (name text, DIM text, pos int, theta real, phi real, r real )
# name is the name of the snout configuration
# DIM is a string describing which DIM it is placed on (e.g. '90-78')
# pos is the WRF number within that DIM, e.g. 1,2,3,4
# theta is the polar angle in degrees
# phi is the azimuthal angle in degrees
# r is the radial distance in cm

class Snout_DB(Generic_DB):
	"""Provide a wrapper for snout DB actions.
	:author: Alex Zylstra
	:date: 2013/06/11
	"""

	# name of the table for the snout data
	TABLE = Database.SNOUT_TABLE

	def __init__(self, fname):
		"""Initialize the snout database wrapper and connects to the database.
		:param fname: the file location/name for the database
		"""
		super(Snout_DB,self).__init__(fname) # call super constructor
		self.__init_snout__()

	def __init_snout__(self):
		"""initialize the snout table."""
		# check to see if it exists already
		query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

		# create new table:
		if query.fetchone()[0] == 0:  # table does not exist
			self.c.execute('''CREATE TABLE %s 
				(name text, DIM text, pos int, theta real, phi real, r real)''' % self.TABLE)
			self.c.execute('CREATE INDEX snout_index on %s(name)' % self.TABLE)

		# finish changes:
		self.db.commit()

	def get_names(self) -> list:
		"""Get a list of unique snout names in the table.
		:returns: a list of snout names
		"""
		query = self.c.execute( 'SELECT Distinct name from %s' % self.TABLE)
		return flatten(array_convert(query))

	def get_pos(self, name, DIM) -> list:
		"""Get a list of (unique) positions for the configuration specified by name and DIM.
		:param name: the snout name
		:param DIM: DIM the NIF DIM (text, e.g. '90-78')
		:returns: a python list of the positions (integers)
		"""
		query = self.c.execute( 'SELECT Distinct pos from %s where name=? and DIM=?' % self.TABLE , (name,DIM,) )
		return flatten(array_convert(query))

	def get_DIM(self, name) -> list:
		"""Get a list of (unique) DIMs for the configuration specified.
		:param name: the snout name
		:returns: a python list of DIMs (strings)
		"""
		query = self.c.execute( 'SELECT Distinct DIM from %s where name=?' % self.TABLE , (name,) )
		return flatten(array_convert(query))

	def insert(self, name, DIM, pos, theta, phi, r):
		"""Insert a new row of data into the table.
		:param name: the snout configuration name
		:param DIM: the NIF DIM (text, e.g. '90-78')
		:param pos: the WRF position number (1,2,3,4,...)
		:param theta: the WRF polar angle in degrees
		:param phi: the WRF azimuthal angle in degrees
		:param r: the WRF radial distance in cm
		"""
		# first check for duplicates:
		query = self.c.execute( 'SELECT * from %s where name=? and DIM=? and pos=?' 
			% self.TABLE, (name,DIM,pos,))

		# not found:
		if len(query.fetchall()) <= 0:  # not found in table:
			newval = (name,DIM,pos,theta,phi,r,)
			self.c.execute( 'INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE , newval )

		# if the row exists already, do an update instead
		else: 
			self.update(name,DIM,pos,'theta',theta)
			self.update(name,DIM,pos,'phi',phi)
			self.update(name,DIM,pos,'r',r)

		# save change:
		self.db.commit()

	def update(self, name, DIM, pos, col, val):
		"""Update an existing row in the table.
		:param name: the snout configuration name
		:param DIM: the NIF DIM (text, e.g. '90-78')
		:param pos: the WRF position number (1,2,3,4,...)
		:param col: the column name to alter
		:param val: the column value
		"""
		s = 'UPDATE %s SET %s=%s WHERE name=? AND DIM=? AND pos=?' % (self.TABLE,col,val,)
		self.c.execute( s , (name,DIM,pos,) )
		self.db.commit()

	def query(self, name, DIM, pos) -> list:
		"""Get all rows for a given name and position.
		:param name: the name of the configuration you want
		:param DIM: the NIF DIM (text, e.g. '90-78')
		:param pos: the WRF position # (int)
		:returns:all rows found which match name and pos
		"""
		query = self.c.execute( 'SELECT * from %s where name=? and DIM=? and pos=?'
			 % self.TABLE , (name,DIM,pos,))
		return array_convert(query)