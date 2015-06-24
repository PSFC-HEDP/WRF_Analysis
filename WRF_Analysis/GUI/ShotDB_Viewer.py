__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

from NIF_WRF.GUI.widgets.Table_View import *
from NIF_WRF.DB.Shot_DB import *

class ShotDB_Viewer(Table_Viewer):
    """View data stored in the shot database."""

    def __init__(self):
        """Constructor"""
        super(ShotDB_Viewer, self).__init__(parent=None, build=False)

        # connect to the database
        self.db = Shot_DB(Database.FILE)

        # make the unique widgets
        self.title('Shot DB')
        self.minsize(300,200)
        self.configure(background='#eeeeee')

        # shot selector
        self.selector_var = tk.StringVar()
        shots = [''] + self.db.get_shots()
        selector = ttk.OptionMenu(self, self.selector_var, *shots)
        selector.configure(width=20)
        self.header_widgets.append(selector)
        self.selector_var.trace('w', self.update_data)

        # invoke the widget construction manually:
        self.__setup_widgets__()
        self.__build_tree__()

    def update_data(self, *args):
        """Update displayed data"""
        shot = self.selector_var.get()
        if shot is None or shot == '':
            return

        # get the columns and rows:
        columns = self.db.get_column_names()
        rows = []
        for i in columns:
            rows.append(self.db.query_col(shot, i))

        # add to the data for table:
        self.tree_data = []
        for i in range(len(columns)):
            self.tree_data.append((columns[i], rows[i]))

        # refresh the table:
        self.__build_tree__()