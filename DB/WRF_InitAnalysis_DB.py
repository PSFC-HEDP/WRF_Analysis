__author__ = 'Alex Zylstra'

import DB.Database as Database
from DB.Generic_Analysis_DB import *

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


class WRF_InitAnalysis_DB(Generic_Analysis_DB):
    """Provide a wrapper for WRF 'initial analysis', e.g. the stuff that comes from the Analysis Program.
    :author: Alex Zylstra
    :date: 2013/07/23
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
