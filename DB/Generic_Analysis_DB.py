__author__ = 'Alex Zylstra'

from DB.Generic_DB import *
from DB import Database


class Generic_Analysis_DB(Generic_DB):
    """The analysis tables are indexed by shot, DIM, and position with date stamps
    and fairly arbitrary columns beyond that.
    This class is an abstraction of that concept, and handles most of the heavy
    lifting for the analysis table objects. Note that inheriting classes must have columns:
    shot text, dim text, position int, analysis_date datetime
    :author: Alex Zylstra
    :date: 2013/07/23
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the analysis database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(Generic_Analysis_DB, self).__init__(fname) # call super constructor

    def get_shots(self):
        """Return all shots available in the database."""
        query = self.c.execute('SELECT Distinct shot from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_dims(self, shot):
        """Get all DIMs present for a given shot.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        """
        query = self.c.execute('SELECT Distinct dim from %s WHERE shot=?' % self.TABLE, (shot,))
        return flatten(array_convert(query))

    def get_pos(self, shot, dim):
        """Get available positions for a given shot and DIM.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        """
        query = self.c.execute('SELECT Distinct position from %s WHERE shot=? AND dim=?' % self.TABLE, (shot,dim,))
        return flatten(array_convert(query))

    def insert(self, shot, dim, position, analysis_date):
        """ Insert a new row of data into the table. This is done with a minimum amount of info, add more via set_column
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        # check for duplicates
        # at a minimum, rows should be distinguished by unique analysis dates
        query = self.c.execute('SELECT * from %s where shot=? AND dim=? AND position=? AND analysis_date=?'
                               % self.TABLE, (shot, dim, position, analysis_date,))

        # not found, so insertion is OK:
        if len(query.fetchall()) <= 0:
            self.c.execute('INSERT INTO %s (shot,dim,position,analysis_date) values (?,?,?,?)'
                           % self.TABLE, (shot, dim, position, analysis_date,))

            # save changes
            self.db.commit()

    def set_column(self, shot, dim, position, column_name, value, analysis_date=None):
        """Set the value of a specified column for row corresponding to given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        :param column_name: the column name as a string
        :param value:
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        # build the command
        # have to do direct string substitution for some things to make it work
        # (injection attacks not an issue for this program)
        command = 'UPDATE %s SET [%s]=? WHERE shot=? AND dim=? AND position=? AND analysis_date=?' % (self.TABLE, column_name,)

        # get default date is one isn't supplied:
        if analysis_date is None:
            analysis_date = self.__latest_date__(shot, dim, position)

        self.c.execute(command, (value, shot, dim, position,analysis_date,))
        self.db.commit()

    def get_value(self, shot, dim, position, column_name, analysis_date=None):
        """Get a specific value from the table.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        :param column_name: the column name as a string
        :param analysis_date: (optional) which analysis date/time to use. Defaults to latest analysis.
        :returns: column's value
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        # get default date is one isn't supplied:
        if analysis_date is None:
            analysis_date = self.__latest_date__(shot, dim, position)

        # execute query and return result:
        query = self.c.execute('SELECT [%s] from %s where shot=? AND dim=? AND position=? AND analysis_date=?'
                               % (column_name, self.TABLE), (shot, dim, position,analysis_date,))
        return flatten(array_convert(query))

    def get_row(self, shot, dim, position, analysis_date=None) -> list:
        """Get all values (e.g. a row) for a given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        :param analysis_date: (optional) which analysis date/time to use. Defaults to latest analysis.
        :returns: the row as a python list
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        # get default date is one isn't supplied:
        if analysis_date is None:
            analysis_date = self.__latest_date__(shot, dim, position)

        # execute query and return result:
        query = self.c. execute('SELECT * from %s where shot=? AND dim=? AND position=? AND analysis_date=?'
                                % self.TABLE, (shot, dim, position,analysis_date,))
        return array_convert(query)

    def __latest_date__(self, shot, dim, position):
        """Get the latest analysis date for the given shot, DIM, position. Helper function for data retrieval.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        query = self.c.execute('SELECT Distinct analysis_date from %s where shot=? AND dim=? AND position=?'
                               % self.TABLE,
                              (shot, dim, position,))

        # array conversion:
        avail_date = flatten(array_convert(query))
        avail_date.sort()
        return avail_date[-1]