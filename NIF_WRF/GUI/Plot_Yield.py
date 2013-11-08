__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk
import numpy as np
import matplotlib
import matplotlib.pyplot
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.Analysis.Shot_Analysis import avg_Yield


class Plot_Yield(tk.Toplevel):
    """Generate a summary plot of all yield data from the equator.

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(Plot_Yield, self).__init__()

        # initializations
        self.db = WRF_Analysis_DB()
        self.canvas = None
        self.ax = None

        # generate the data
        self.__generate_data__()

        # make the UI:
        self.__create_widgets__()

        # a couple key bindings:
        self.bind('<Escape>', self.close)

        # Set the window title:
        self.title('Yield summary plot')

    def __create_widgets__(self):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)

        self.show_shots_var = tk.BooleanVar()
        self.show_shots_var_check = tk.Checkbutton(frame, text='Show Shot #s?', variable=self.show_shots_var)
        self.show_shots_var_check.grid(row=0, column=0, columnspan=2)
        self.show_shots_var.trace('w', self.update_plot)

        sep2 = ttk.Separator(frame, orient='vertical')
        sep2.grid(row=1, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

        # Try to display data (if shot, dim, pos are supplied):
        self.update_plot()

    def __generate_data__(self):
        """Generate the data for plotting"""
        # only use equatorial dim for this plot
        dim = '90-78'
        n = len(self.db.get_shots()) # max number of points
        self.data_x = np.ndarray(n, dtype=np.float64)
        self.data_y = np.ndarray(n, dtype=np.float64)
        self.data_err = np.ndarray(n, dtype=np.float64)
        self.data_lab = []

        # loop over all shots:
        i=0
        for shot in self.db.get_shots():
            Y, dY = avg_Yield(shot, dim)

            if Y is not None:
                self.data_x[i] = i+1
                self.data_y[i] = Y
                self.data_err[i] = dY
                self.data_lab.append(shot)

                i+=1

        # crop:
        self.data_x = self.data_x[0:i]
        self.data_y = self.data_y[0:i]
        self.data_err = self.data_err[0:i]

    def update_plot(self, *args):
        """Update the displayed plot"""
        # Get info on options chosen:
        show_shots = self.show_shots_var.get()

        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = matplotlib.pyplot.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        if show_shots:
            self.ax.set_position((0.1,0.15,0.85,0.8))
        else:
            self.ax.set_position((0.1,0.05,0.85,0.9))

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

        # setup:
        self.ax.set_ylabel(r'Proton Yield')
        self.ax.set_xticks([])
        self.ax.set_xlim(0, 1+len(self.data_x))
        self.ax.set_ylim(8e6, 5e8)
        self.ax.set_yscale('log')
        # plot data:
        self.ax.errorbar(self.data_x, self.data_y, yerr=self.data_err, fmt='bo')
        # add labels:
        if show_shots:
            for i in range(len(self.data_lab)):
                self.ax.text(i+1, 7e6, self.data_lab[i], ha='center', va='top', rotation='vertical', fontsize=6)

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def close(self, *args):
        """Close this window"""
        self.withdraw()