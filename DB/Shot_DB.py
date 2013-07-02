import DB.Database as Database
from DB.Generic_DB import *


class Shot_DB(Generic_DB):
    """Provide a wrapper for shot DB actions.
    :author: Alex Zylstra
    :date: 2013/06/11
    """

    # name of the table for the shot data
    TABLE = Database.SHOT_TABLE

    def __init__(self, fname):
        """Initialize the shot database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(Shot_DB, self).__init__(fname)  # call super constructor
        self.__init_shot__()

    def __init_shot__(self):
        """initialize the shot table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0:  # table does not exist
            self.c.execute('''CREATE TABLE %s (shot text)''' % self.TABLE)
            self.c.execute('CREATE INDEX shot_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def get_shots(self) -> list:
        """Get a list of unique shot names in the table.
        :returns: a list of shot names as strings
        """
        query = self.c.execute('SELECT Distinct shot from %s' % self.TABLE)
        return array_convert(query)

    def insert(self, shot):
        """Add a new shot to the table. Data insertion done via update method ONLY (for shot db).
        :param shot: the new shot name
        """
        # first check for duplicates:
        query = self.c.execute('SELECT * from %s where shot=?' % self.TABLE, (shot,))

        # not found:
        if len(query.fetchall()) <= 0:  # not found in table:
            #newval = (name,pos,theta,phi,r,)
            self.c.execute('INSERT INTO %s (shot) values (?)' % self.TABLE, (shot,))

        # save change:
        self.db.commit()

    def update(self, shot, col, val):
        """Update a value in the table.
        :param shot: the shot number
        :param col: the column name to alter
        :param val: the column value
        """
        s = 'UPDATE %s SET [%s]=? WHERE shot=?' % (self.TABLE, col,)
        self.c.execute(s, (val, shot,))
        self.db.commit()

    def query(self, shot):
        """Find data rows specified by shot number.
        :param shot: the shot number to query
        :returns: the rows found for the shot from the SQL query
        """
        query = self.c.execute('SELECT * from %s where shot=?' % self.TABLE, (shot,))
        return array_convert(query)[0]

    def query_col(self, shot, col):
        """Get data for a specific shot and column.
        :param shot: the shot to query
        :param col: name of the column you want
        :returns: column's value, or a 2 value tuple if there is an associated error bar
        """
        query = self.c.execute('SELECT [%s] from %s where shot=?' % (col, self.TABLE), (shot,))
        value = array_convert(query)[0][0]

        # check if there is an error bar for this value:
        if (col + ' Unc') in self.get_column_names():
            query = self.c.execute('SELECT [%s] from %s where shot=?' % (col + ' Unc', self.TABLE), (shot,))
            err = array_convert(query)[0][0]
            return value, err

        return value