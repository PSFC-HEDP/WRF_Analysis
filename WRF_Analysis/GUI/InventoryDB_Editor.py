__author__ = 'Alex Zylstra'

from tkinter.messagebox import showinfo, showerror
import sys

from NIF_WRF.DB.WRF_Inventory_DB import *
from NIF_WRF.GUI.widgets.Generic_Editor import *


class InventoryDB_Editor(Generic_Editor):
    """Perform basic editing of the inventory database.

    :param parent: (optional) the parent (usually should be None) [default=None]
    """
    def __init__(self, parent=None):
        """Initialize the editor"""
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
            showinfo('', 'Database updated', parent=self)
        except:
            showerror('An error occurred', sys.exc_info()[0], parent=self)