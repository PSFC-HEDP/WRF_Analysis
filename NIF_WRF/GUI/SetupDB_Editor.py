__author__ = 'Alex Zylstra'

from tkinter.messagebox import showinfo

from NIF_WRF.DB.WRF_Setup_DB import *
from NIF_WRF.GUI.widgets.Generic_Editor import *


class SetupDB_Editor(Generic_Editor):
    """Basic editor for the setup database.

    :param parent: (optional) the parent UI element [default=None]
    """

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

        #showinfo('', 'Data saved', parent=self)

        self.withdraw()