# A database wrapper for hohlraum info

import DB.Database as Database
from DB.Generic_DB import *

# The table is arranged with columns:
# (name text, layer int, material text, r real, z real)


class Hohlraum_DB(Generic_DB):
    """Provide a wrapper for hohlraum DB actions.
    :author: Alex Zylstra
    :date: 2013/06/11
    """
    ## name of the table for the hohlraum data
    TABLE = Database.HOHLRAUM_TABLE

    def __init__(self, fname):
        """Initialize the hohlraum database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(Hohlraum_DB, self).__init__(fname)  # call super constructor
        self.__init_hohlraum__()

    def __init_hohlraum__(self):
        """initialize the hohlraum table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0:  # table does not exist
            self.c.execute('''CREATE TABLE %s
                (drawing text, name text, layer int, material text, r real, z real)''' % self.TABLE)
            self.c.execute('CREATE INDEX hohlraum_index on %s(drawing)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def get_names(self) -> list:
        """Get a list of unique hohlraum names in the table.
        :returns: a list containing the unique names (as str)
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
        :param drawing: the drawing number to query
        :returns a unique name found for the drawing number
        """
        query = self.c.execute('SELECT Distinct name from %s where drawing=(?)' % self.TABLE, (drawing,))
        return flatten(array_convert(query))

    def get_name_drawing(self, name) -> str:
        """Get the drawing number for a given name.
        :param name: the hohlraum design name you want to query
        :returns: a unique drawing number found for that name
        """
        query = self.c.execute('SELECT Distinct drawing from %s where name=(?)' % self.TABLE, (name,))
        return flatten(array_convert(query))

    def get_layers(self, name='', drawing='') -> list:
        """Get a list of (unique) layers defined for the given hohlraum name or drawing number.
            If you specify one of name or drawing, that will be used for match.
            If both are given, then the returned result must match both.
        :param name: the hohlraum name
        :param drawing: the drawing number
        :returns: a python array of layer indices (integers)
        """
        # sanity check: if both string are empty, we cannot query
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
        :param drawing: the hohlraum drawing number
        :param name: the hohlraum configuration name
        :param layer: the material wall index (0,1,2,..)
        :param material: the wall material for this layer
        :param r: r radius in cm
        :param z: z length in cm
        """
        # first check for duplicates:
        query = self.c.execute('SELECT * from %s where name=? and drawing=? and layer=? and material=? and r=? and z=?'
                               % self.TABLE, (name, drawing, layer, material, r, z,))

        # not found:
        if len(query.fetchall()) <= 0:  # not found in table:
            newval = (drawing, name, layer, material, r, z,)
            self.c.execute('INSERT INTO %s values (?,?,?,?,?,?)' % self.TABLE, newval)

        # save change:
        self.db.commit()

    def drop(self, drawing, layer):
        """Drop a wall in the table.
        :param drawing: the hohlraum drawing
        :param layer: the layer index (0,1,2...)
        """
        s = 'DELETE FROM %s WHERE drawing=? AND layer=?' % self.TABLE
        self.c.execute(s, (drawing, layer,))
        self.db.commit()

    def query_drawing(self, drawing, layer) -> list:
        """Find data specified by drawing and position.
        :param drawing: the hohlraum drawing number
        :param layer: the wall layer index
        :returns: all rows found which match name and layer
        """
        query = self.c.execute('SELECT * from %s where drawing=? and layer=?' % self.TABLE, (drawing, layer,))
        return array_convert(query)

    def query_name(self, name, layer):
        """Find data specified by name and position.
        :param name: the hohlraum configuration name
        :param layer: the wall layer index
        :returns: all rows found which match name and layer
        """
        query = self.c.execute('SELECT * from %s where name=? and layer=?' % self.TABLE, (name, layer,))
        return array_convert(query)