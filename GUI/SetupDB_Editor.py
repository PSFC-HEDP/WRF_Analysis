__author__ = 'Alex Zylstra'

import tkinter as tk
from DB.WRF_Setup_DB import *
from GUI.widgets.Generic_Editor import *
from tkinter.messagebox import showinfo

class SetupDB_Editor(Generic_Editor):
    def __init__(self, parent=None):
        """
        Initialize the editor
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(SetupDB_Editor, self).__init__(WRF_Setup_DB(Database.FILE), parent=parent)

        self.title('Edit Setup DB')

    def write(self, *args):
        """Write the value as entered to the database."""
        values = []
        for x in self.vars:
            values.append(x.get())

        self.db.insert(*values)

        showinfo('', 'Data saved', parent=self)