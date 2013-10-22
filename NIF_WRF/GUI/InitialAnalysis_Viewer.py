__author__ = 'Alex Zylstra'

from NIF_WRF.GUI.widgets.Analysis_Viewer import *
from NIF_WRF.DB.WRF_InitAnalysis_DB import *


class InitAnalysis_Viewer(Analysis_Viewer):
    def __init__(self):
        super(InitAnalysis_Viewer, self).__init__(WRF_InitAnalysis_DB(Database.FILE), parent=None)

        # make the unique widgets
        self.title('WRF Initial Analysis')