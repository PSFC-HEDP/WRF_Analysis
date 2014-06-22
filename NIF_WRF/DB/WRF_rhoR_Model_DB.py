__author__ = 'Alex Zylstra'

from NIF_WRF.DB.Generic_Param_DB import *
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis

# The table is arranged with columns:

# shell_mat='CH', Ri=9e-2, Ro=11e-2, fD=0.3, f3He=0.7, P0=50,
#                  Te_Gas=3, Te_Shell=0.2, Te_Abl=0.3, Te_Mix=0.5,
#                  rho_Abl_Max=1.5, rho_Abl_Min=0.1, rho_Abl_Scale=70e-4, MixF=0.025,
#                  Tshell=40e-4, Mrem=0.175, E0=14.7,
#                  Ri_Err=5e-4, Ro_Err=5e-4, P0_Err=1, fD_Err=0, f3He_Err=0,
#                  Te_Gas_Err=2,Te_Shell_Err=0.1, Te_Abl_Err=0.1, Te_Mix_Err=0.2,
#                  rho_Abl_Max_Err=0.5, rho_Abl_Min_Err=0.05, rho_Abl_Scale_Err=30e-4,
#                  MixF_Err=0.025, Tshell_Err=10e-4, Mrem_Err=0.05

class WRF_rhoR_Model_DB(Generic_Param_DB):
    """Provide a wrapper for WRF rhoR model options

    :param fname: the file location/name for the database
    :author: Alex Zylstra
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

    def load_from_model(self, shot, dim, pos, model):
        """Load rhoR model parameters into the database from a `rhoR_Analysis` object.

        :param shot: The shot number
        :param dim: the DIM
        :param position: The position
        :param model: The rhoR analysis object
        """
        assert isinstance(model, rhoR_Analysis)
        values = {'shell_mat': model.shell_mat,
                  'Ri': model.Ri[1],
                  'Ro': model.Ro[1],
                  'fD': model.fD[1],
                  'f3He': model.f3He[1],
                  'P0': model.P0[1],
                  'Te_Gas': model.Te_Gas[1],
                  'Te_Shell': model.Te_Shell[1],
                  'Te_Abl': model.Te_Abl[1],
                  'Te_Mix': model.Te_Mix[1],
                  'rho_Abl_Max': model.rho_Abl_Max[1],
                  'rho_Abl_Min': model.rho_Abl_Min[1],
                  'rho_Abl_Scale': model.rho_Abl_Scale[1],
                  'MixF': model.MixF[1],
                  'Tshell': model.Tshell[1],
                  'Mrem': model.Mrem[1],
                  'E0': model.E0,
                  'Ri_Err': model.Ri_Err,
                  'Ro_Err': model.Ro_Err,
                  'fD_Err': model.fD_Err,
                  'f3He_Err': model.f3He_Err,
                  'P0_Err': model.P0_Err,
                  'Te_Gas_Err': model.Te_Gas_Err,
                  'Te_Shell_Err': model.Te_Shell_Err,
                  'Te_Abl_Err': model.Te_Abl_Err,
                  'Te_Mix_Err': model.Te_Mix_Err,
                  'rho_Abl_Max_Err': model.rho_Abl_Max_Err,
                  'rho_Abl_Min_Err': model.rho_Abl_Min_Err,
                  'rho_Abl_Scale_Err': model.rho_Abl_Scale_Err,
                  'MixF_Err': model.MixF_Err,
                  'Tshell_Err': model.Tshell_Err,
                  'Mrem_Err': model.Mrem_Err}
        self.load_results(shot, dim, pos, values)