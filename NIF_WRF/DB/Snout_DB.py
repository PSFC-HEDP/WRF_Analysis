from NIF_WRF.DB.Generic_DB import *

# The table is arranged with columns:
# (name text, DIM text, pos int, theta real, phi real, r real )
# name is the name of the snout configuration
# DIM is a string describing which DIM it is placed on (e.g. '90-78')
# pos is the WRF number within that DIM, e.g. 1,2,3,4
# theta is the polar angle in degrees
# phi is the azimuthal angle in degrees
# r is the radial distance in cm
from NIF_WRF.DB import Database


class Snout_DB(Generic_DB):
    """Provide a wrapper for snout DB actions.

    :param fname: the file location/name for the database
    :author: Alex Zylstra
    :date: 2013/08/05
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the snout database wrapper and connects to the database."""
        super(Snout_DB,self).__init__(fname) # call super constructor
        # name of the table for the snout data
        self.TABLE = Database.SNOUT_TABLE
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
        :rtype: list
        """
        query = self.c.execute( 'SELECT Distinct name from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_pos(self, name, DIM) -> list:
        """Get a list of (unique) positions for the configuration specified by name and DIM.

        :param name: the snout name (as str)
        :param DIM: DIM the NIF DIM (text, e.g. '90-78') (as str)
        :returns: a python list of the positions (integers)
        :rtype: list
        """
        # sanity checks
        assert isinstance(name, str) and isinstance(DIM, str)
        # SQL query:
        query = self.c.execute( 'SELECT Distinct pos from %s where name=? and DIM=?' % self.TABLE , (name,DIM,) )
        return flatten(array_convert(query))

    def get_DIM(self, name) -> list:
        """Get a list of (unique) DIMs for the configuration specified.

        :param name: the snout name (as str)
        :returns: a python list of DIMs (strings)
        """
        # sanity check:
        assert isinstance(name, str)

        # SQL query:
        query = self.c.execute( 'SELECT Distinct DIM from %s where name=?' % self.TABLE , (name,) )
        return flatten(array_convert(query))

    def insert(self, name, DIM, pos, theta, phi, r):
        """Insert a new row of data into the table.

        :param name: the snout configuration name (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position number (1,2,3,4,...)
        :param theta: the WRF polar angle in degrees
        :param phi: the WRF azimuthal angle in degrees
        :param r: the WRF radial distance in cm
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)
        assert isinstance(theta, str) or isinstance(theta, int) or isinstance(theta, float)
        assert isinstance(phi, str) or isinstance(phi, int) or isinstance(phi, float)
        assert isinstance(r, str) or isinstance(r, int) or isinstance(r, float)

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

        :param name: the snout configuration name (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position number (1,2,3,4,...)
        :param col: the column name to alter (as str)
        :param val: the column value
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)
        assert isinstance(col, str)
        assert isinstance(val, str) or isinstance(val, int) or isinstance(val, float)

        # SQL query:
        s = 'UPDATE %s SET %s=%s WHERE name=? AND DIM=? AND pos=?' % (self.TABLE,col,val,)
        self.c.execute( s , (name,DIM,pos,) )
        self.db.commit()

    def query(self, name, DIM, pos) -> list:
        """Get all rows for a given name and position.

        :param name: the name of the configuration you want (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position # (int)
        :returns: all rows found which match name and pos
        :rtype: list
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)

        # SQL query:
        query = self.c.execute( 'SELECT * from %s where name=? and DIM=? and pos=?'
             % self.TABLE , (name,DIM,pos,))
        return array_convert(query)

    def get_r(self, name, DIM, pos):
        """Get the position for given parameters.

        :param name: the name of the configuration you want (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position # (int)
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)

        # SQL query:
        query = self.c.execute( 'SELECT r from %s where name=? and DIM=? and pos=?'
             % self.TABLE , (name,DIM,pos,))
        return flatten(array_convert(query))

    def get_theta(self, name, DIM, pos):
        """Get the polar angle for given parameters.

        :param name: the name of the configuration you want (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position # (int)
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)

        # SQL query:
        query = self.c.execute( 'SELECT theta from %s where name=? and DIM=? and pos=?'
             % self.TABLE , (name,DIM,pos,))
        return flatten(array_convert(query))

    def get_phi(self, name, DIM, pos):
        """Get the azimuthal for given parameters.

        :param name: the name of the configuration you want (as str)
        :param DIM: the NIF DIM (text, e.g. '90-78') (as str)
        :param pos: the WRF position # (int)
        """
        # sanity checks:
        assert isinstance(name, str)
        assert isinstance(DIM, str)
        assert isinstance(pos, str) or isinstance(pos, int)

        # SQL query:
        query = self.c.execute( 'SELECT phi from %s where name=? and DIM=? and pos=?'
             % self.TABLE , (name,DIM,pos,))
        return flatten(array_convert(query))