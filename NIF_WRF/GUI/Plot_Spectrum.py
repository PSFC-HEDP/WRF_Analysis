__author__ = 'Alex Zylstra'

import tkinter as tk

import ttk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from NIF_WRF.DB.WRF_Data_DB import *


class Plot_Spectrum(tk.Toplevel):
    """Generic viewer for spectrum plots

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(Plot_Spectrum, self).__init__(parent=parent)

        # initializations
        self.db = WRF_Data_DB()
        self.canvas = None
        self.ax = None

        # size limits
        #self.minsize(600,400)
        #self.maxsize(900,600)

        # make the UI:
        self.__create_widgets__()

        # a couple key bindings:
        self.bind('<Escape>', self.close)

    def __create_widgets__(self):
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
        self.pos_var.trace('w', self.update_plot)
        self.pos_selector.grid(row=2, column=1)

        self.corr_var = tk.BooleanVar()
        self.corr_var_check = tk.Checkbutton(frame, text='Hohlraum corrected?', variable=self.corr_var)
        self.corr_var_check.grid(row=3, column=0, columnspan=2)
        self.corr_var.trace('w', self.update_plot)

        sep = ttk.Separator(frame, orient='vertical')
        sep.grid(row=4, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()


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
        self.update_plot()

    def update_dim(self, *args):
        """Called to update displayed info when the DIM selection is changed."""
        shot = self.shot_var.get()  # selected shot
        dim = self.dim_var.get()  # selected DIM

        # get available positions:
        positions = self.db.get_positions(shot, dim)

        # update position menu:
        self.pos_selector['menu'].delete(0, "end")
        if len(positions) == 0:
            positions = ['']
        for val in positions:
            self.pos_selector['menu'].add_command(label=val,
                             command=lambda value=val:
                                  self.pos_var.set(value))

    def update_plot(self, *args):
        """Update the displayed plot"""

        # get info:
        shot = self.shot_var.get()  # selected shot
        dim = self.dim_var.get()  # selected DIM
        pos = self.pos_var.get()  # selected position
        corr = bool(self.corr_var.get())  # if the hohlraum is corrected

        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = plt.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # sanity check:
        if shot == '' or dim == '' or pos == '':
            return

        # get the data:
        spectrum = self.db.get_spectrum(shot, dim, pos, corr)

        # sanity:
        if spectrum is None or len(spectrum) == 0:
            return

        # split up the data:
        data_x = []
        data_y = []
        data_err = []
        for row in spectrum:
            data_x.append(row[0])
            data_y.append(row[1])
            data_err.append(row[2])

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            plt.switch_backend('TkAgg')

        # plot the data with error bars
        self.ax.errorbar(
            data_x, # x values
            data_y, # y values
            yerr=data_err, # y error bars
            marker='s', # square markers
            lw=0, # no lines connecting points
            elinewidth=1, # error bar line width
            mfc='black', # marker color
            mec='black', # marker line color
            ecolor='black') # error bar color
        self.ax.grid(True)
        self.ax.set_xlabel('Energy (MeV)')
        self.ax.set_ylabel('Yield / MeV')

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def close(self, *args):
        """Close this window"""
        self.withdraw()