__author__ = 'Alex Zylstra'

from NIF_WRF.DB.Generic_Param_DB import *


class WRF_Analysis_Param_DB(Generic_Param_DB):
    """Provide a wrapper for WRF analysis parameters

    :param fname: the file location/name for the database
    :author: Alex Zylstra
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF analysis database wrapper and connect to the database."""
        super(WRF_Analysis_Param_DB, self).__init__(fname)  # call super constructor
        # name of the table
        self.TABLE = Database.WRF_ANALYSIS_PARAM_TABLE
        self.__init_table__()

    def __init_table__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, analysis_date datetime,
                use_hohl_corr boolean, name text, summary text, min_E real, max_E real,
                use_bump_corr boolean, bump_corr real)''' % self.TABLE)
            self.c.execute('CREATE INDEX WRF_analysis_param_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()