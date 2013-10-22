__author__ = 'Alex Zylstra'

from NIF_WRF.DB.Snout_DB import *
from NIF_WRF.GUI.widgets.Generic_Editor import *

class SnoutDB_Editor(Generic_Editor):
    def __init__(self, parent=None):
        """
        Initialize the editor
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(SnoutDB_Editor, self).__init__(Snout_DB(Database.FILE),
                                             parent=parent,
                                             column_names=['Name', 'DIM', 'Pos', 'r (cm)', 'θ (deg)', 'ϕ (deg)'])

        self.title('Edit Snout DB')

    def write(self, *args):
        """Write the value as entered to the database."""
        name = self.vars[0].get()
        DIM = self.vars[1].get()
        pos = self.vars[2].get()
        r = self.vars[3].get()
        theta = self.vars[4].get()
        phi = self.vars[5].get()

        self.db.insert(name, DIM, pos, theta, phi, r)
