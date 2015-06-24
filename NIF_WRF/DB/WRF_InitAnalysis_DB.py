from NIF_WRF import DB as Database

__author__ = 'Alex Zylstra'

from NIF_WRF.DB import Database
from NIF_WRF.DB.Generic_Analysis_DB import *
from NIF_WRF.util.Import_WRF_CSV import WRF_CSV

# The table is arranged with columns:
# (shot text, dim text, position int, analysis_date datetime, program_date date, scan_file text,
#  distance real, wrf_id text, al_blast real, calibration text,
#  data_region_x0 int, data_region_x1 int, data_region_y0 int, data_region y1 int,
#  back1_region_x0 int, back1_region_x1 int, back1_region_y0 int, back1_region_y1 int,
#  back2_region_x0 int, back2_region_x1 int, back2_region_y0 int, back2_region_y1 int,
#  c_limit real, e_limit real, Dmax real, dDmax real,
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

    :param fname: the file location/name for the database
    :author: Alex Zylstra
    :date: 2013/10/24
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF initial analysis database wrapper and connect to the database."""
        super(WRF_InitAnalysis_DB, self).__init__(fname) # call super constructor
        # name of the table for the snout data
        self.TABLE = Database.WRF_INITANALYSIS_TABLE
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
                data_region_x0 int, data_region_x1 int, data_region_y0 int, data_region_y1 int,
                back1_region_x0 int, back1_region_x1 int, back1_region_y0 int, back1_region_y1 int,
                back2_region_x0 int, back2_region_x1 int, back2_region_y0 int, back2_region_y1 int,
                c_limit real, e_limit real, Dmax real, dDmax real,
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

    def import_csv(self, raw):
        """Import from a WRF_CSV object."""
        assert isinstance(raw, WRF_CSV)
        # construct analysis date/time string:
        ad = raw.date + ' ' + raw.time
        # add row to the DB:
        self.insert(raw.shot, raw.dim, raw.pos, ad)

        # this is clunky but necessary to convert from Fredrick's naming scheme to mine:
        self.set_column(raw.shot, raw.dim, raw.pos, 'program_date', raw.program_date, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'scan_file', raw.scan_file, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'distance', raw.distance, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'wrf_id', raw.WRF_ID, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'al_blast', raw.Al_Blast_Filter, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'calibration', raw.WRF_Cal, analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'data_region_x0', raw.Data_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'data_region_x1', raw.Data_Limits[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'data_region_y0', raw.Data_Limits[2], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'data_region_y1', raw.Data_Limits[3], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'back1_region_x0', raw.BG1_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back1_region_x1', raw.BG1_Limits[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back1_region_y0', raw.BG1_Limits[2], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back1_region_y1', raw.BG1_Limits[3], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'back2_region_x0', raw.BG2_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back2_region_x1', raw.BG2_Limits[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back2_region_y0', raw.BG2_Limits[2], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'back2_region_y1', raw.BG2_Limits[3], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'c_limit', raw.Contrast_Limit, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'e_limit', raw.Ecc_Limit, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'Dmax', raw.Dmax, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'dDmax', raw.Dmax_Unc, analysis_date=ad)


        self.set_column(raw.shot, raw.dim, raw.pos, 'd_low', raw.Dia_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'd_high', raw.Dia_Limits[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'd_auto', raw.Dia_Auto, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'e_low', raw.E_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'e_high', raw.E_Limits[1], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'dve_c', raw.c, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'dve_dc', raw.dc, analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_chi2', raw.chi2, analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_e_min', raw.Fit_Limits[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_e_max', raw.Fit_Limits[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_mean', raw.Fit[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_sigma', raw.Fit[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'fit_yield', raw.Fit[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_mean_random', raw.Unc_Random[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_sigma_random', raw.Unc_Random[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_yield_random', raw.Unc_Random[2], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_mean_sys', raw.Unc_Systematic[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_sigma_sys', raw.Unc_Systematic[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_yield_sys', raw.Unc_Systematic[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_counting_mean', raw.Unc_CountingStats[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_counting_sigma', raw.Unc_CountingStats[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_counting_yield', raw.Unc_CountingStats[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dve_mean', raw.Unc_DvE[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dve_sigma', raw.Unc_DvE[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dve_yield', raw.Unc_DvE[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dmax_mean', raw.Unc_Dmax[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dmax_sigma', raw.Unc_Dmax[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_dmax_yield', raw.Unc_Dmax[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_etchscan_mean', raw.Unc_EtchScan[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_etchscan_sigma', raw.Unc_EtchScan[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_etchscan_yield', raw.Unc_EtchScan[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_nonlinearity_mean', raw.Unc_Nonlinearity[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_nonlinearity_sigma', raw.Unc_Nonlinearity[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_nonlinearity_yield', raw.Unc_Nonlinearity[2], analysis_date=ad)

        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_calibration_mean', raw.Unc_CalProc[0], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_calibration_sigma', raw.Unc_CalProc[1], analysis_date=ad)
        self.set_column(raw.shot, raw.dim, raw.pos, 'unc_item_calibration_yield', raw.Unc_CalProc[2], analysis_date=ad)