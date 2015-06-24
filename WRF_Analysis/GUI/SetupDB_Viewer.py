__author__ = 'Alex Zylstra'

import tkinter as tk
from NIF_WRF.GUI.widgets.Table_View import *
from NIF_WRF.DB.WRF_Setup_DB import *

class SetupDB_Viewer(Table_Viewer):
    """View information in the setup database."""

    def __init__(self):
        super(SetupDB_Viewer, self).__init__(parent=None, build=False)

        # connect to the database
        self.db = WRF_Setup_DB(Database.FILE)

        # make the unique widgets
        self.title('Setup DB')
        self.minsize(500,200)
        self.configure(background='#eeeeee')
        #self.maxsize(600,400)

        # Add some UI elements:
        #label1 = ttk.Label(self, text='Shot')
        #self.header_widgets.append(label1)

        self.shot_var = tk.StringVar()
        shots = [''] + self.db.get_shots()
        self.shot_selector = ttk.OptionMenu(self, self.shot_var, *shots)
        self.shot_selector.configure(width=20)
        self.shot_var.trace('w', self.update)
        self.header_widgets.append(self.shot_selector)

        # set the data
        self.update_data()

        # invoke the widget construction manually:
        self.__setup_widgets__()
        self.__build_tree__()


    def update_data(self, *args):
        """Retrieve all data from the DB to display."""
        shot = self.shot_var.get()
        # set the columns:
        self.tree_columns = ['Shot', 'Name', 'DIM', 'Pos', 'r (cm)', 'WRF', 'CR-39']
        self.tree_data = []

        raw = self.db.query(shot)
        for row in raw:
            tree_row = [row[0], row[2], row[4], row[7], row[5], row[8], row[9]]
            self.tree_data.append(tree_row)

    def update(self, *args):
        """Triggered when the shot selection is changed."""
        self.update_data()
        self.__build_tree__()