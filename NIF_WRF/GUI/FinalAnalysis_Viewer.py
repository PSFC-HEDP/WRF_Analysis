__author__ = 'Alex Zylstra'

from NIF_WRF.GUI.widgets.Analysis_Viewer import *
from NIF_WRF.DB.WRF_Analysis_DB import *


class FinalAnalysis_Viewer(Analysis_Viewer):
    """View information in the final WRF analysis table."""

    def __init__(self):
        super(FinalAnalysis_Viewer, self).__init__(WRF_Analysis_DB(Database.FILE), parent=None)

        # make the unique widgets
        self.title('WRF Analysis')