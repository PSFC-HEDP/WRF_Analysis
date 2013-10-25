from NIF_WRF.DB import Database

__author__ = 'Alex Zylstra'

from NIF_WRF.DB.Generic_Analysis_DB import *

# The table is arranged with columns:

# shell_mat='CH', Ri=9e-2, Ro=11e-2, fD=0.3, f3He=0.7, P0=50,
#                  Te_Gas=3, Te_Shell=0.2, Te_Abl=0.3, Te_Mix=0.5,
#                  rho_Abl_Max=1.5, rho_Abl_Min=0.1, rho_Abl_Scale=70e-4, MixF=0.025,
#                  Tshell=40e-4, Mrem=0.175, E0=14.7,
#                  Ri_Err=5e-4, Ro_Err=5e-4, P0_Err=1, fD_Err=0, f3He_Err=0,
#                  Te_Gas_Err=2,Te_Shell_Err=0.1, Te_Abl_Err=0.1, Te_Mix_Err=0.2,
#                  rho_Abl_Max_Err=0.5, rho_Abl_Min_Err=0.05, rho_Abl_Scale_Err=30e-4,
#                  MixF_Err=0.025, Tshell_Err=10e-4, Mrem_Err=0.05

class WRF_rhoR_Model_DB(Generic_Analysis_DB):
    """Provide a wrapper for WRF rhoR model options

    :param fname: the file location/name for the database
    :author: Alex Zylstra
    :date: 2013/09/03
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF analysis database wrapper and connect to the database."""
        super(WRF_rhoR_Model_DB, self).__init__(fname)  # call super constructor
        # name of the table for the snout data
        self.TABLE = Database.WRF_RHOR_MODEL_TABLE
        self.__init_table__()

    def __init_table__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, analysis_date datetime,
                shell_mat text, Ri real, Ro real, fD real, f3He real, P0 real,
                Te_Gas real, Te_Shell real, Te_Abl real, Te_Mix real,
                rho_Abl_Max real, rho_Abl_Min real, rho_Abl_Scale real, MixF real,
                Tshell real, Mrem real, E0 real,
                Ri_Err real, Ro_Err real, P0_Err real, fD_Err real, f3He_Err real,
                Te_Gas_Err real, Te_Shell_Err real, Te_Abl_Err real, Te_Mix_Err real,
                rho_Abl_Max_Err real, rho_Abl_Min_Err real, rho_Abl_Scale_Err real,
                MixF_Err real, Tshell_Err real, Mrem_Err real)''' % self.TABLE)
            self.c.execute('CREATE INDEX rhoR_model_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def load_results(self, shot, dim, position, results):
        """Load the results of running the analysis code.

        :param shot: The shot number
        :param dim: the DIM
        :param position: The position
        :param results: The result of Analysis.Analyze_Spectrum.Analyze_Spectrum, which is a dict
        """
        # get the date and time:
        import datetime
        now = datetime.datetime.now()
        analysis_date = now.strftime('%Y-%m-%d %H:%M')

        # get a list of columns to update:
        columns = self.get_column_names()
        # remove ones that are not in the dict:
        columns.remove('shot')
        columns.remove('dim')
        columns.remove('position')
        columns.remove('analysis_date')

        # insert a new row into the table:
        self.insert(shot, dim, position, analysis_date)

        # set values from the dict:
        for col in columns:
            self.set_column(shot, dim, position, col, results[col], analysis_date=analysis_date)

        self.db.commit()

