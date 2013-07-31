__author__ = 'Alex Zylstra'

import tkinter as tk
from DB.WRF_Inventory_DB import *
from GUI.widgets.Generic_Editor import *
from tkinter.messagebox import showinfo, showerror
import sys

class InventoryDB_Editor(Generic_Editor):
    def __init__(self, parent=None):
        """
        Initialize the editor
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(InventoryDB_Editor, self).__init__(WRF_Inventory_DB(Database.FILE),
                                                 parent=parent,
                                                 column_names=['WRF', '# shots', 'Status'])
        self.title('Edit Inventory DB')

    def write(self, *args):
        """Write the value as entered to the database."""
        WRF = self.vars[0].get()
        shots = self.vars[1].get()
        status = self.vars[2].get()

        try:
            self.db.insert(WRF, shots, status)
            showinfo('', 'Database updated')
        except:
            showerror('An error occurred', sys.exc_info()[0])