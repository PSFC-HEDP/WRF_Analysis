__author__ = 'Alex Zylstra'

from NIF_WRF.GUI.widgets.Table_View import *
from NIF_WRF.DB.WRF_Inventory_DB import *
import tkinter as tk
import tkinter.ttk as ttk

class InventoryDB_Viewer(Table_Viewer):
    """Display data available in the inventory database"""

    def __init__(self):
        super(InventoryDB_Viewer, self).__init__(parent=None, build=False)

        # connect to the database
        self.db = WRF_Inventory_DB(Database.FILE)

        # make the unique widgets
        self.title('Inventory DB')
        self.minsize(300,200)
        self.maxsize(600,400)
        self.configure(background='#eeeeee')

        # set the data
        self.update_data()

        # add a button to update the database:
        update_button = ttk.Button(self, text='Update DB', command=self.refresh_from_setup)
        self.header_widgets.append(update_button)

        # invoke the widget construction manually:
        self.__setup_widgets__()
        self.__build_tree__()

    def update_data(self, *args):
        """Retrieve all data from the DB to display."""
        # set the columns:
        self.tree_columns = ['WRF ID', '# shots', 'Status']
        self.tree_data = []

        ids = self.db.get_ids()
        for WRF in ids:
            row = [WRF, self.db.get_shots(WRF), self.db.get_status(WRF)]
            self.tree_data.append(row)

    def refresh_from_setup(self):
        """Refresh the displayed data from the Setup DB"""
        self.db.refresh_from_setup()
        self.refresh()