__author__ = 'Alex Zylstra'

import tkinter as tk
from NIF_WRF.DB import Database
from NIF_WRF.Analysis.Hohlraum import *
from NIF_WRF.DB.Hohlraum_DB import *

class HohlraumDB_Plot(tk.Toplevel):
    """Show a window which allows making plots of hohlraum profiles.

        :param parent: (optional) the parent (usually should be None) [default=None]
        """

    def __init__(self, parent=None):
        """Initialize the window"""
        super(HohlraumDB_Plot, self).__init__(parent)

        # connect to the database
        self.db = Hohlraum_DB(Database.FILE)

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.__createUI__()

    def __createUI__(self):
        """Helper method to create the UI elements"""
        # radiobutton for name vs drawing mode
        self.radio_var = tk.IntVar()
        self.radio1 = tk.Radiobutton(self, text='Name', variable=self.radio_var, value=0, command=self.__radio_select__)
        self.radio1.grid(row=0, column=0)
        self.radio2 = tk.Radiobutton(self, text='Drawing', variable=self.radio_var, value=1, command=self.__radio_select__)
        self.radio2.grid(row=0, column=1)

        # label for Shot
        self.label = tk.Label(self, text='Name')
        self.label.grid(row=1, column=0)

        # selector for name/drawing
        self.selector_var = tk.StringVar()
        opts = self.db.get_names()
        if len(opts) == 0:
            opts = ['']
        self.selector = tk.OptionMenu(self, self.selector_var, *opts)
        self.selector.configure(width=20)
        self.selector.grid(row=1, column=1)

        # entry functionality for min/max angle
        self.label2 = tk.Label(self, text='θ min')
        self.label2.grid(row=2, column=0)
        self.theta_min_var = tk.DoubleVar(value=(90-14.6))
        self.theta_min_entry = tk.Entry(self, textvariable=self.theta_min_var)
        self.theta_min_entry.grid(row=2, column=1)

        self.label3 = tk.Label(self, text='θ max')
        self.label3.grid(row=3, column=0)
        self.theta_max_var = tk.DoubleVar(value=(90-12.6))
        self.theta_max_entry = tk.Entry(self, textvariable=self.theta_max_var)
        self.theta_max_entry.grid(row=3, column=1)

        # Buttons
        self.plot_button = tk.Button(self, text='Plot', command=self.plot)
        self.plot_button.grid(row=4, column=0)
        self.close_button = tk.Button(self, text='Close', command=self.withdraw)
        self.close_button.grid(row=4, column=1)

    def __radio_select__(self):
        """Respond to the user toggling radio buttons"""
        # get initial value
        init_val = self.selector_var.get()

        # get state:
        var = self.radio_var.get()
        opts = []
        # configure to use name mode:
        if var==0:
            self.label.configure(text='Name')
            opts = self.db.get_names()
            try:
                final_val = self.db.get_drawing_name(init_val)[0]
            except:
                final_val = ''

        # configure to use drawing mode:
        if var==1:
            self.label.configure(text='Drawing')
            opts = self.db.get_drawings()
            try:
                final_val = self.db.get_name_drawing(init_val)[0]
            except:
                final_val = ''

        # clear current contents:
        self.selector['menu'].delete(0,"end")
        if len(opts) == 0:
            opts = ['']
        for string in opts:
            self.selector['menu'].add_command(label=string,
                             command=lambda value=string:
                                  self.selector_var.set(value))
        self.selector_var.set(final_val)

    def plot(self):
        """Make a plot, using the analysis Hohlraum class and the current selection."""
        # get the data:
        radio = self.radio_var.get()
        if radio == 0:
            data = self.db.query_name(self.selector_var.get())
        if radio == 1:
            data = self.db.query_drawing(self.selector_var.get())

        # launch the hohlraum:
        h = Hohlraum(raw=None, wall=data, angles=[90-14.1, 90-13.1])
        h.plot_hohlraum_window(interactive=True)