import DB.Database as Database
from DB.Generic_DB import *

# The table is arranged with columns:
# (shot text, wrf_type text, shot_name text, hohl_drawing text, dim text, r real, snout text, position int,
#	wrf_id text, cr39_1_id text, cr39_2_id text, cr39_3_id text, poly_1 real, poly_2 real,
#   vacuum_pre time, vacuum_post time)

class WRF_Setup_DB(Generic_DB):
    """Provide a wrapper for WRF Setup DB actions.
    :author: Alex Zylstra
    :date: 2013/07/11
    """
    ## name of the table for the snout data
    TABLE = Database.WRF_SETUP_TABLE

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF setup database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_Setup_DB, self).__init__(fname) # call super constructor
        self.__init_wrf_setup__()

    def __init_wrf_setup__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, wrf_type text, shot_name text, hohl_drawing text, dim text, r real, snout text, position int,
                    wrf_id text, cr39_1_id text, cr39_2_id text, cr39_3_id text, poly_1 real, poly_2 real, vacuum_pre time, vacuum_post time)''' % self.TABLE)
            self.c.execute('CREATE INDEX wrf_setup_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def get_shots(self) -> list:
        """Get a list of unique shot names in the table.
        :returns: a python list of shot strings"""
        query = self.c.execute('SELECT Distinct shot from %s' % self.TABLE)
        return flatten(array_convert(query))

    def insert(self, shot, wrf_type, shot_name, hohl_drawing, dim, r, snout, position, wrf_id, cr39_1_id, cr39_2_id, cr39_3_id,
               poly_1, poly_2, vacuum_pre, vacuum_post):
        """Insert a new row of data into the table.
        :param shot: the shot ID (eg 'N130102-001-999')
        :param wrf_type: the WRF module drawing # (eg AAA10-108020-10)
        :param shot_name: text description of the shot
        :param hohl_drawing: the hohlraum's drawing number as identification
        :param dim: the DIM (eg '90-78')
        :param r: the radius from tcc in cm
        :param snout: name of the snout used
        :param position: the WRF position # (1,2,3,4,...)
        :param wrf_id: the WRF id
        :param cr39_1_id: serial number for first piece of CR-39
        :param cr39_2_id: serial number for second piece of CR-39
        :param cr39_3_id: serial number for third piece of CR-39
        :param poly_1: thickness in um of first poly n converter
        :param poly_2: thickness in um of second poly n converter
        :param vacuum_pre: pre-shot vacuum exposure ('HH:MM:SS')
        :param vacuum_post: post-shot vacuum exposure ('HH:MM:SS')
        """
        # sanity checking:
        assert isinstance(shot, str)
        assert isinstance(wrf_type, str)
        assert isinstance(shot_name, str)
        assert isinstance(hohl_drawing, str)
        assert isinstance(dim, str)
        assert isinstance(r, str) or isinstance(r, int) or isinstance(r, float)
        assert isinstance(snout, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(wrf_id, str)
        assert isinstance(cr39_1_id, str)
        assert isinstance(cr39_2_id, str)
        assert isinstance(cr39_3_id, str)
        assert isinstance(poly_1, str) or isinstance(poly_1, int) or isinstance(poly_1, float)
        assert isinstance(poly_2, str) or isinstance(poly_2, int) or isinstance(poly_2, float)
        assert isinstance(vacuum_pre, str)
        assert isinstance(vacuum_post, str)

        # first check for duplicates:
        query = self.c.execute('SELECT * from %s where shot=? and dim=? and snout=? and position=?'
                               % self.TABLE, (shot, dim, snout, position,))

        # not found:
        if len(query.fetchall()) <= 0: # not found in table:
            newval = (
                shot, wrf_type, shot_name, hohl_drawing, dim, r, snout, position, wrf_id, cr39_1_id, cr39_2_id, cr39_3_id, poly_1, poly_2,
                vacuum_pre, vacuum_post,)
            self.c.execute('INSERT INTO %s values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)' % self.TABLE, newval)
        # if the row exists already, do an update instead:
        else:
            # update relevant columns one at a time:
            self.update(shot, dim, snout, position, 'wrf_type', wrf_type)
            self.update(shot, dim, snout, position, 'shot_name', shot_name)
            self.update(shot, dim, snout, position, 'hohl_drawing', hohl_drawing)
            self.update(shot, dim, snout, position, 'r', r)
            self.update(shot, dim, snout, position, 'wrf_id', wrf_id)
            self.update(shot, dim, snout, position, 'cr39_1_id', cr39_1_id)
            self.update(shot, dim, snout, position, 'cr39_2_id', cr39_2_id)
            self.update(shot, dim, snout, position, 'cr39_3_id', cr39_3_id)
            self.update(shot, dim, snout, position, 'poly_1', poly_1)
            self.update(shot, dim, snout, position, 'poly_2', poly_2)
            self.update(shot, dim, snout, position, 'vacuum_pre', vacuum_pre)
            self.update(shot, dim, snout, position, 'vacuum_post', vacuum_post)

        # save change:
        self.db.commit()

    def update(self, shot, dim, snout, position, col, val):
        """Update an existing row in the table.
        :param shot: the shot number
        :param dim: the DIM (eg '90-78')
        :param snout: name of the snout used
        :param position: the WRF position # (1,2,3,4,...)
        :param col: the column name to alter
        :param val: the column value
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(snout, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(col, str)

        # SQL query:
        s = 'UPDATE %s SET [%s]=? WHERE shot=? and dim=? and snout=? and position=?' % (self.TABLE, col,)
        self.c.execute(s, (val, shot, dim, snout, position,))
        self.db.commit()

    def query(self, shot):
        """Find data specified by shot number.
        :param shot: the shot number to query
        :returns: all rows found for shot
        """
        assert isinstance(shot, str)

        # SQL query:
        query = self.c.execute('SELECT * from %s WHERE shot=?' % self.TABLE, (shot,))
        return array_convert(query)

    def query_col(self, shot, dim, position, col):
        """Get data for a specific shot and column.
        :param shot the shot to query
        :param dim: the DIM (eg '90-78')
        :param position: the WRF position # (1,2,3,4,...)
        :param col name of the column you want
        :returns: the column's value"""
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(col, str)

        # SQL query
        query = self.c.execute('SELECT [%s] from %s WHERE shot=? AND dim=? AND position=?'
                               % (col, self.TABLE), (shot, dim, position,))
        converted_query = array_convert(query)
        if len(converted_query) > 0:
            value = converted_query[0]
        else:
            value = ''

        return value

    def find_wrf(self, wrf_id) -> list:
        """Get a list of shots that a WRF was used on
        :param wrf_id the WRF id
        :returns: a python list of the shots"""
        # sanity check:
        assert isinstance(wrf_id, str)

        # SQL query:
        query = self.c.execute('SELECT shot from %s where wrf_id=?' % self.TABLE, (wrf_id,))
        return flatten(array_convert(query))

    # @return python array of shots
    def find_cr39(self, cr39_id) -> list:
        """Get a list of shots that a piece of CR-39 was used on (presumably just one)
        :param cr39_id the CR-39 ID or serial number
        :returns: a python list of the shots"""
        # sanity check:
        assert isinstance(cr39_id, str)

        # since we have 3 columns that potentially contain CR39 IDs, have to do three queries:
        query = self.c.execute('SELECT shot from %s where cr39_1_id=? or cr39_2_id=? or cr39_3_id=?' % self.TABLE,
                               (cr39_id, cr39_id, cr39_id,))
        return flatten(array_convert(query))