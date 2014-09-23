# A database wrapper for hohlraum info

__author__ = 'Alex Zylstra'

import os

import NIF_WRF.DB.Database as Database
from NIF_WRF.DB.Generic_DB import *


# The table is arranged with columns:
# (name text, layer int, material text, r real, z real)


class Hohlraum_DB(Generic_DB):
    """Provide a wrapper for hohlraum DB actions.

    :param fname: (optional) the file location/name for the database [default=Database.FILE]
    :author: Alex Zylstra
    :date: 2013/07/31
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the hohlraum database wrapper and connect to the database."""
        super(Hohlraum_DB, self).__init__(fname)  # call super constructor
        # name of the table for the hohlraum data
        self.TABLE = Database.HOHLRAUM_TABLE
        self.TABLE_BUMP = Database.HOHLRAUM_BUMP_TABLE
        self.__init_hohlraum__()

    def __init_hohlraum__(self):
        """initialize the hohlraum table."""

        # check to see if the main hohlraum table exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)
        # create new table if necessary:
        if query.fetchone()[0] == 0:  # table does not exist
            self.c.execute('''CREATE TABLE %s
                (drawing text, name text, layer int, material text, r real, z real)''' % self.TABLE)
            self.c.execute('CREATE INDEX hohlraum_index on %s(drawing)' % self.TABLE)

        # check to see if the hohlraum bump table exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE_BUMP)
        # create new table if necessary:
        if query.fetchone()[0] == 0:  # table does not exist
            self.c.execute('''CREATE TABLE %s
                (drawing text UNIQUE, use_corr boolean, corr real)''' % self.TABLE_BUMP)
            self.c.execute('CREATE INDEX hohlraum_bump_index on %s(drawing)' % self.TABLE_BUMP)

        # finish changes:
        self.db.commit()

    def add_from_file(self, fname):
        """Add a set of points to the database from a CSV file.

        :param fname: the file to open
        """
        assert os.path.isfile(fname)  # sanity check

        # open as a CSV:
        from NIF_WRF.util.CSV import read_csv
        data = read_csv(fname, cols=[2,4,5])

        # data format is:
        #  drawing, name, layer, material, r, z
        for row in data:
            self.insert(*row)

    def get_names(self) -> list:
        """Get a list of unique hohlraum names in the table.

        :returns: a list containing the unique names (as str)
        :rtype: list
        """
        #assert isinstance(self.c,sqlite3.Connection)

        query = self.c.execute('SELECT Distinct name from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_drawings(self):
        """Get a list of unique hohlraum drawing numbers in the table.
        :returns: a list containing unique hohlraum drawing numbers as str
        """
        query = self.c.execute('SELECT Distinct drawing from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_drawing_name(self, drawing) -> str:
        """Get the name for a drawing number.

        :param drawing: the drawing number to query as str
        :returns: a unique name found for the drawing number
        :rtype: str
        """
        # sanity check:
        assert isinstance(drawing, str)

        query = self.c.execute('SELECT Distinct name from %s where drawing=(?)' % self.TABLE, (drawing,))
        return flatten(array_convert(query))

    def get_name_drawing(self, name) -> str:
        """Get the drawing number for a given name.

        :param name: the hohlraum design name you want to query (as str)
        :returns: a unique drawing number found for that name
        :rtype: str
        """
        # sanity check
        assert isinstance(name, str)

        query = self.c.execute('SELECT Distinct drawing from %s where name=(?)' % self.TABLE, (name,))
        return flatten(array_convert(query))

    def get_layers(self, name='', drawing='') -> list:
        """Get a list of (unique) layers defined for the given hohlraum name or drawing number.
        If you specify one of name or drawing, that will be used for match.
        If both are given, then the returned result must match both.

        :param name: the hohlraum name (as str)
        :param drawing: the drawing number (as str)
        :returns: a python array of layer indices (integers)
        :rtype: list
        """
        # sanity check for types
        assert isinstance(name, str)
        assert isinstance(drawing, str)

        # further sanity check: if both string are empty, we cannot query
        if name == '' and drawing == '':
            return
        # if both arguments have text, match both:
        elif name != '' and drawing != '':
            query = self.c.execute('SELECT Distinct layer from %s where name=? and drawing=?'
                                   % self.TABLE, (name, drawing,))
        # match name only:
        elif name != '':
            query = self.c.execute('SELECT Distinct layer from %s where name=?' % self.TABLE, (name,))
        # match drawing only:
        else:
            query = self.c.execute('SELECT Distinct layer from %s where drawing=?' % self.TABLE, (drawing,))

        return flatten(array_convert(query))

    def insert(self, drawing, name, layer, material, r, z):
        """Insert a new row of data into the table.

        :param drawing: the hohlraum drawing number (as str)
        :param name: the hohlraum configuration name (as str)
        :param layer: the material wall index (0,1,2,..)
        :param material: the wall material for this layer (as str)
        :param r: r radius in cm
        :param z: z length in cm
        """
        # sanity checks:
        assert isinstance(drawing, str)
        assert isinstance(name, str)
        assert (isinstance(layer, str) or isinstance(layer, int) or isinstance(layer, float))
        assert isinstance(material, str)
        assert isinstance(r, str) or isinstance(r, int) or isinstance(r, float)
        assert isinstance(z, str) or isinstance(z, int) or isinstance(z, float)

        # first check for duplicates:
        query = self.c.execute('SELECT * from %s where name=? and drawing=? and layer=? and material=? and r=? and z=?'
                               % self.TABLE, (name, drawing, layer, material, r, z,))

        # not found:
        if len(query.fetchall()) <= 0:  # not found in table:
            newval = (drawing, name, layer, material, r, z,)
            self.c.execute('INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE, newval)
        else: # overwrite
            s = 'DELETE FROM %s WHERE drawing=? AND layer=? AND z=?' % self.TABLE
            self.c.execute(s, (drawing,layer,z,))
            newval = (drawing, name, layer, material, r, z,)
            self.c.execute('INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE, newval)

        # save change:
        self.db.commit()

    def drop(self, drawing, layer):
        """Drop a wall in the table.

        :param drawing: the hohlraum drawing (as str)
        :param layer: the layer index (0,1,2...)
        """
        # sanity checks:
        assert isinstance(drawing, str)
        assert (isinstance(layer, str) or isinstance(layer, int))

        s = 'DELETE FROM %s WHERE drawing=? AND layer=?' % self.TABLE
        self.c.execute(s, (drawing, layer,))
        self.db.commit()

    def query_drawing(self, drawing, layer=None) -> list:
        """Find data specified by drawing and position.

        :param drawing: the hohlraum drawing number (as str)
        :param layer: (optional) the wall layer index [default = all layers]
        :returns: all rows found which match name and layer
        :rtype: list
        """
        # sanity checks:
        assert isinstance(drawing, str)

        if layer is None:
            query = self.c.execute('SELECT * from %s where drawing=?' % self.TABLE, (drawing,))
        else:
            assert (isinstance(layer, str) or isinstance(layer, int))
            query = self.c.execute('SELECT * from %s where drawing=? and layer=?' % self.TABLE, (drawing, layer,))
        return array_convert(query)

    def query_name(self, name, layer=None):
        """Find data specified by name and position.

        :param name: the hohlraum configuration name (as str)
        :param layer: (optional) the wall layer index [default = all layers]
        :returns: all rows found which match name and layer
        """
        # sanity checks:
        assert isinstance(name, str)

        if layer is None:
            query = self.c.execute('SELECT * from %s where name=?' % self.TABLE, (name,))
        else:
            assert (isinstance(layer, str) or isinstance(layer, int))
            query = self.c.execute('SELECT * from %s where name=? and layer=?' % self.TABLE, (name, layer,))
        return array_convert(query)

    def get_wall(self, name='', drawing=''):
        """Get the hohlraum wall data for the given hohlraum name or drawing number.
        If you specify one of name or drawing, that will be used for match.
        If both are given, then the returned result must match both.

        :param name: the hohlraum name (as str)
        :param drawing: the drawing number (as str)
        :returns: a python array of layer indices (integers)
        :rtype: list
        """
        # sanity check for types
        assert isinstance(name, str)
        assert isinstance(drawing, str)

        # further sanity check: if both string are empty, we cannot query
        if name == '' and drawing == '':
            return
        # if both arguments have text, match both:
        elif name != '' and drawing != '':
            query = self.c.execute('SELECT * from %s where name=? and drawing=?'
                                   % self.TABLE, (name, drawing,))
        # match name only:
        elif name != '':
            query = self.c.execute('SELECT * from %s where name=?' % self.TABLE, (name,))
        # match drawing only:
        else:
            query = self.c.execute('SELECT * from %s where drawing=?' % self.TABLE, (drawing,))

        return array_convert(query)

    def set_bump(self, drawing, use_corr, corr):
        """Set the database entry for a hohlraum's bump correction.

        :param use_corr: whether to use a correction factor (boolean)
        :param corr: the correction in um to the wall thickness (float or int)
        :param drawing: the drawing number (as str)
        """
        # sanity checks for types
        assert isinstance(drawing, str)
        assert isinstance(use_corr, bool)
        assert isinstance(corr, float) or isinstance(corr, int)

        # insert or replace:
        self.c.execute('INSERT OR REPLACE INTO %s VALUES (?,?,?)'
                               % self.TABLE_BUMP, (drawing,use_corr,corr))
        self.db.commit()

    def get_bump(self, drawing):
        """Get whether a bump correction is required for the given hohlraum drawing.

        :param drawing: the drawing number (as str)
        :returns: whether the bump correction is required and it's thickness as (use_corr, corr)
        :rtype: list if one match, list of lists if multiple matches, or None if no match
        """
        # sanity check for type
        assert isinstance(drawing, str)

        query = self.c.execute('SELECT * from %s where drawing=?' % self.TABLE_BUMP, (drawing,))
        temp = array_convert(query)
        if len(temp) == 0:
            return None
        elif len(temp) == 1:
            return temp[0]
        return temp