__author__ = 'Alex Zylstra'

import tkinter as tk
from NIF_WRF.GUI.widgets.Table_View import *
from NIF_WRF.DB.Generic_Analysis_DB import *


class Analysis_Viewer(Table_Viewer):
    """Generic viewer for analysis data.

        :param db: The database object to use, which must be of type Generic_Analysis_DB
        :param parent: (optional) The parent object [default=None]
        """

    def __init__(self, db, parent=None):
        """Initialize the viewer window."""
        super(Analysis_Viewer, self).__init__(parent=None, build=False)
        assert isinstance(db, Generic_Analysis_DB)

        self.db = db

        self.minsize(300,200)
        self.maxsize(600,400)

        # make a frame for stuff:
        frame = tk.Frame(self)

        # Add some UI elements:
        label1 = tk.Label(frame, text='Shot')
        label1.grid(row=0, column=0)
        label2 = tk.Label(frame, text='DIM')
        label2.grid(row=1, column=0)
        label3 = tk.Label(frame, text='Pos')
        label3.grid(row=2, column=0)

        shots = self.db.get_shots()
        if len(shots) == 0:
            shots = ['']

        self.shot_var = tk.StringVar()
        self.shot_selector = tk.OptionMenu(frame, self.shot_var, *shots)
        self.shot_selector.configure(width=20)
        self.shot_var.trace('w', self.update_shot)
        self.shot_selector.grid(row=0, column=1)

        self.dim_var = tk.StringVar()
        self.dim_selector = tk.OptionMenu(frame, self.dim_var, [])
        self.dim_selector.configure(width=20)
        self.dim_var.trace('w', self.update_dim)
        self.dim_selector.grid(row=1, column=1)

        self.pos_var = tk.StringVar()
        self.pos_selector = tk.OptionMenu(frame, self.pos_var, [])
        self.pos_selector.configure(width=20)
        self.pos_var.trace('w', self.update_data)
        self.pos_selector.grid(row=2, column=1)

        # add the frame
        self.header_widgets.append(frame)

        # set the data
        self.update_data()

        # invoke the widget construction manually:
        self.__setup_widgets__()
        self.__build_tree__()

        # a couple key bindings:
        self.bind('<Escape>', self.close)

    def update_shot(self, *args):
        """Called to update displayed info when the shot selection is updated."""
        shot = self.shot_var.get()  # selected shot
        selected_dim = self.dim_var.get()  # currently selected value
        # get available DIMs:
        DIMs = self.db.get_dims(shot)

        # update DIM menu:
        self.dim_selector['menu'].delete(0, "end")
        if len(DIMs) == 0:
            DIMs = ['']
        for val in DIMs:
            self.dim_selector['menu'].add_command(label=val,
                             command=lambda value=val:
                                  self.dim_var.set(value))

        # check to see if we should save the selection:
        if selected_dim in DIMs:
            self.dim_var.set(selected_dim)

        # also update the position:
        self.update_dim()
        # and the displayed data
        self.update_data()

    def update_dim(self, *args):
        """Called to update displayed info when the DIM selection is changed."""
        shot = self.shot_var.get()  # selected shot
        dim = self.dim_var.get()  # selected DIM

        # get available positions:
        positions = self.db.get_pos(shot, dim)

        # update position menu:
        self.pos_selector['menu'].delete(0, "end")
        if len(positions) == 0:
            positions = ['']
        for val in positions:
            self.pos_selector['menu'].add_command(label=val,
                             command=lambda value=val:
                                  self.pos_var.set(value))

        # update the displayed data
        self.update_data()


    def update_data(self, *args):
        """Retrieve all data from the DB to display."""
        shot = self.shot_var.get()  # selected shot
        dim = self.dim_var.get()  # selected DIM
        pos = self.pos_var.get()  # selected position

        # set the columns:
        self.tree_columns = ['Quantity', 'Value']
        self.tree_data = []

        # sanity check:
        if shot == '' or dim == '' or pos == '':
            return

        columns = self.db.get_column_names()
        for col in columns:
            value = self.db.get_value(shot, dim, pos, col)
            self.tree_data.append([col, value[0]])

        self.__build_tree__()
