__author__ = 'Alex Zylstra'

import DB.Database as Database
from DB.Generic_DB import *
import datetime

# The table is arranged with columns:
# (shot text, dim text, position int, analysis_date datetime, program_date date, scan_file text,
#  distance real, wrf_id text, al_blast real, calibration text,
#  data_region_x0 int, data_region_x1 int, data_region_y0 int, data_region y1 int,
#  back1_region_x0 int, back1_region_x1 int, back1_region_y0 int, back1_region_y1 int,
#  back2_region_x0 int, back2_region_x1 int, back2_region_y0 int, back2_region_y1 int,
#  c_limit real, e_limit real,
#  d_low real, d_high real, d_auto bit, e_low real, e_high real,
#  dve_c real, dve_dc real, fit_chi2 real, fit_e_min real, fit_e_max real,
#  fit_mean real, fit_sigma real, fit_yield real,
#  unc_mean_random real, unc_sigma_random real, unc_yield_random real,
#  unc_mean_sys real, unc_sigma_sys real, unc_yield_sys real,
#  unc_item_counting_mean real, unc_item_counting_sigma real, unc_item_counting_yield real,
#  unc_item_dve_mean real, unc_item_dve_sigma real, unc_item_dve_yield real,
#  unc_item_dmax_mean real, unc_item_dmax_sigma real, unc_item_dmax_yield real,
#  unc_item_etchscan_mean real, unc_item_etchscan_sigma real, unc_item_etchscan_yield real,
#  unc_item_nonlinearity_mean real, unc_item_nonlinearity_sigma real, unc_item_nonlinearity_yield real,
#  unc_item_calibration_mean real, unc_item_calibration_sigma real, unc_item_calibration_yield real)


class WRF_InitAnalysis_DB(Generic_DB):
    """Provide a wrapper for WRF 'initial analysis', e.g. the stuff that comes from the Analysis Program.
    :author: Alex Zylstra
    :date: 2013/07/07
    """
    ## name of the table for the snout data
    TABLE = Database.WRF_INITANALYSIS_TABLE

    def __init__(self, fname):
        """Initialize the WRF initial analysis database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_InitAnalysis_DB, self).__init__(fname) # call super constructor
        self.__init_table__()

    def __init_table__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, analysis_date datetime, program_date date, scan_file text,
                distance real, wrf_id text, al_blast real, calibration text,
                data_region_x0 int, data_region_x1 int, data_region_y0 int, data_region y1 int,
                back1_region_x0 int, back1_region_x1 int, back1_region_y0 int, back1_region_y1 int,
                back2_region_x0 int, back2_region_x1 int, back2_region_y0 int, back2_region_y1 int,
                c_limit real, e_limit real,
                d_low real, d_high real, d_auto bit, e_low real, e_high real,
                dve_c real, dve_dc real, fit_chi2 real, fit_e_min real, fit_e_max real,
                fit_mean real, fit_sigma real, fit_yield real,
                unc_mean_random real, unc_sigma_random real, unc_yield_random real,
                unc_mean_sys real, unc_sigma_sys real, unc_yield_sys real,
                unc_item_counting_mean real, unc_item_counting_sigma real, unc_item_counting_yield real,
                unc_item_dve_mean real, unc_item_dve_sigma real, unc_item_dve_yield real,
                unc_item_dmax_mean real, unc_item_dmax_sigma real, unc_item_dmax_yield real,
                unc_item_etchscan_mean real, unc_item_etchscan_sigma real, unc_item_etchscan_yield real,
                unc_item_nonlinearity_mean real, unc_item_nonlinearity_sigma real, unc_item_nonlinearity_yield real,
                unc_item_calibration_mean real, unc_item_calibration_sigma real, unc_item_calibration_yield real
                )''' % self.TABLE)
            self.c.execute('CREATE INDEX init_analysis_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def insert(self, shot, dim, position, analysis_date):
        """ Insert a new row of data into the table. This is done with a minimum amount of info, add more via set_column
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        """
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
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param column_name: the column name as a string
        :param value:
        """
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
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param column_name: the column name as a string
        :param analysis_date: (optional) which analysis date/time to use. Defaults to latest analysis.
        :returns: column's value
        """
        # get default date is one isn't supplied:
        if analysis_date is None:
            analysis_date = self.__latest_date__(shot, dim, position)

        # execute query and return result:
        query = self.c.execute('SELECT [%s] from %s where shot=? AND dim=? AND position=? AND analysis_date=?'
                               % (column_name, self.TABLE), (shot, dim, position,analysis_date,))
        return flatten(array_convert(query))

    def get_row(self, shot, dim, position, analysis_date=None) -> list:
        """Get all values (e.g. a row) for a given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param analysis_date: (optional) which analysis date/time to use. Defaults to latest analysis.
        :returns: the row as a python list
        """
        # get default date is one isn't supplied:
        if analysis_date is None:
            analysis_date = self.__latest_date__(shot, dim, position)

        # execute query and return result:
        query = self.c. execute('SELECT * from %s where shot=? AND dim=? AND position=? AND analysis_date=?'
                                % self.TABLE, (shot, dim, position,analysis_date,))
        return array_convert(query)

    def __latest_date__(self, shot, dim, position):
        """Get the latest analysis date for the given shot, DIM, position. Helper function for data retrieval.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        """
        query = self.c.execute('SELECT Distinct analysis_date from %s where shot=? AND dim=? AND position=?'
                               % self.TABLE,
                              (shot, dim, position,))

        # array conversion:
        avail_date = flatten(array_convert(query))
        return avail_date[0]