
import DB.Database as Database
from DB.Generic_DB import *

# The table is arranged with columns:
# (id text, shots int, status text )

class WRF_Inventory_DB(Generic_DB):
    """Provide a wrapper for WRF inventory DB actions.
    :author: Alex Zylstra
    :date: 2013/07/11
    """
    # name of the table for the snout data
    TABLE = Database.WRF_INVENTORY_TABLE

    def __init__(self, fname):
        """Initialize the WRF inventory database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_Inventory_DB,self).__init__(fname) # call super constructor
        self.__init_wrf_inventory__()

    def __init_wrf_inventory__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0:  # table does not exist
            self.c.execute('''CREATE TABLE %s
                (id text, shots int, status text)''' % self.TABLE)
            self.c.execute('CREATE INDEX wrf_inventory_index on %s(id)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def get_ids(self) -> list:
        """Get a list of (unique) WRF IDs in the database.
        :returns: a python list of the ID strings"""
        query = self.c.execute( 'SELECT Distinct id from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_shots(self, wrf_id):
        """Get number of shots for a given wedge ID.
        :param wrf_id: the WRF id (aka serial number) [as str]
        :returns: number of shots the wedge has been used on
        """
        assert isinstance(wrf_id, str)

        query = self.c.execute( 'SELECT shots from %s where id=?' % self.TABLE , (wrf_id,) )
        return flatten(array_convert(query))[0]

    def get_status(self, wrf_id):
        """Get current stats for a given wedge ID.
        :param wrf_id: the WRF wrf_id (aka serial number) [as str]
        :returns: this wedge's status
        """
        assert isinstance(wrf_id, str)

        query = self.c.execute( 'SELECT status from %s where id=?' % self.TABLE , (wrf_id,) )
        return flatten(array_convert(query))[0]

    def insert(self, wrf_id, shots, status):
        """Insert a new row of data into the table.
        :param wrf_id: the WRF wrf_id (aka serial number) [as str]
        :param shots: the number of shots this wedge has been used on [int or str]
        :param status: the current WRF status [str]
        """
        # sanity checks:
        assert isinstance(wrf_id, str)
        assert isinstance(shots, int) or isinstance(shots, str)
        assert isinstance(status, str)

        # first check for duplicates:
        query = self.c.execute( 'SELECT * from %s where id=?'
            % self.TABLE, (wrf_id,))

        # not found:
        if len(query.fetchall()) <= 0:  # not found in table:
            newval = (wrf_id,shots,status,)
            self.c.execute( 'INSERT INTO %s values (?,?,?)' % self.TABLE , newval )

        # if the row exists already, do an update instead
        else:
            self.update(wrf_id,shots,status)

        # save change:
        self.db.commit()

    def update(self, wrf_id, shots, status):
        """Update data for a wedge already in the table.
        :param wrf_id: the wedge wrf_id to update [str]
        :param shots: the number of shots this wedge has been used on [int or str]
        :param status: the current status of this wedge [str]
        """
        # sanity checks:
        assert isinstance(wrf_id, str)
        assert isinstance(shots, int) or isinstance(shots, str)
        assert isinstance(status, str)

        # update columns one at a time:
        s = 'UPDATE %s SET shots=? WHERE id=?' % self.TABLE
        self.c.execute( s , (shots,wrf_id,) )
        s = 'UPDATE %s SET status=? WHERE id=?' % self.TABLE
        self.c.execute( s , (status,wrf_id,) )

        # save changes to db:
        self.db.commit()