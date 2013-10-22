__author__ = 'Alex Zylstra'

from NIF_WRF.GUI.widgets.Table_View import *
from NIF_WRF.DB.Snout_DB import *

class SnoutDB_Viewer(Table_Viewer):
    def __init__(self):
        super(SnoutDB_Viewer, self).__init__(parent=None, build=False)

        # connect to the database
        self.db = Snout_DB(Database.FILE)

        # make the unique widgets
        self.title('Snout DB')
        self.minsize(300,200)
        self.maxsize(600,400)

        self.update_data()

        # invoke the widget construction manually:
        self.__setup_widgets__()
        self.__build_tree__()

    def update_data(self, *args):
        """Retrieve all data from the DB to display."""
        # set the columns:
        self.tree_columns = ['Name', 'DIM', 'Pos', 'θ (deg)', 'ϕ (deg)', 'r (cm)']
        self.tree_data = []

        names = self.db.get_names()
        for name in names:
            DIMs = self.db.get_DIM(name)
            for DIM in DIMs:
                positions = self.db.get_pos(name, DIM)
                for pos in positions:  # now get the rows for name/dim/pos
                    data = self.db.query(name, DIM, pos)
                    for row in data:
                        self.tree_data.append(row)