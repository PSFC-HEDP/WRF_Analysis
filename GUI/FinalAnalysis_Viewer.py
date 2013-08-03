__author__ = 'Alex Zylstra'

import tkinter as tk
from GUI.widgets.Analysis_Viewer import *
from DB.WRF_Analysis_DB import *


class FinalAnalysis_Viewer(Analysis_Viewer):
    def __init__(self):
        super(FinalAnalysis_Viewer, self).__init__(WRF_Analysis_DB(Database.FILE), parent=None)

        # make the unique widgets
        self.title('WRF Analysis')