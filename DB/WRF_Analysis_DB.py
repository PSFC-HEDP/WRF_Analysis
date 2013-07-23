__author__ = 'Alex Zylstra'

import DB.Database as Database
from DB.Generic_Analysis_DB import *

# The table is arranged with columns:
# (shot text, dim text, position int, analysis_date datetime,
# E_raw real, E_raw_posunc real, E_raw_negunc real, E_corr real, E_corr_posunc real, E_corr_negunc real,
# Au real, Au_unc real, DU real, DU_ucn real, Al real, Al_unc real,
# Hohl_Y_posunc real, Hohl_Y_negunc real,
# Hohl_E_posunc real, Hohl_E_negunc real,
# Hohl_sigma_posunc real, Hohl_sigma_negunc real,
# Yield real, Yield_ran_unc real, Yield_sys_unc real,
# Energy real, Energy_ran_unc real, Energy_sys_unc real,
# Sigma real, Sigma_ran_unc real, Sigma_sys_unc real,
# rhoR real, rhoR_ran_unc real, rhoR_sys_unc real,
# Rcm real, Rcm_ran_unc real, Rcm_sys_unc real)


class WRF_Analysis_DB(Generic_Analysis_DB):
    """Provide a wrapper for WRF analysis, e.g. the stuff that comes from the analysis routines in this program.
    :author: Alex Zylstra
    :date: 2013/07/23
    """
    ## name of the table for the snout data
    TABLE = Database.WRF_ANALYSIS_TABLE

    def __init__(self, fname):
        """Initialize the WRF analysis database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_Analysis_DB, self).__init__(fname) # call super constructor
        self.__init_table__()

    def __init_table__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, analysis_date datetime,
                E_raw real, E_raw_posunc real, E_raw_negunc real, E_corr real, E_corr_posunc real, E_corr_negunc real,
                Au real, Au_unc real, DU real, DU_ucn real, Al real, Al_unc real,
                Hohl_Y_posunc real, Hohl_Y_negunc real,
                Hohl_E_posunc real, Hohl_E_negunc real,
                Hohl_sigma_posunc real, Hohl_sigma_negunc real,
                Yield real, Yield_ran_unc real, Yield_sys_unc real,
                Energy real, Energy_ran_unc real, Energy_sys_unc real,
                Sigma real, Sigma_ran_unc real, Sigma_sys_unc real,
                rhoR real, rhoR_ran_unc real, rhoR_sys_unc real,
                Rcm real, Rcm_ran_unc real, Rcm_sys_unc real)''' % self.TABLE)
            self.c.execute('CREATE INDEX analysis_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()