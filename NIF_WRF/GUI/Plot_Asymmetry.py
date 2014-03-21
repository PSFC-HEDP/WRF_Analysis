__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import matplotlib
import matplotlib.pyplot
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.Analysis import Asymmetries


class Plot_Asymmetry(tk.Toplevel):
    """Generate a summary plot of all yield data from the equator.

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(Plot_Asymmetry, self).__init__()

        # initializations
        self.db = WRF_Analysis_DB()
        self.canvas = None
        self.ax = None
        self.last_mode = -1

        # make the UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        # a couple key bindings:
        self.bind('<Escape>', self.close)

        # Set the window title:
        self.title('Asymmetry summary plot')

    def __create_widgets__(self):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)

        self.show_shots_var = tk.BooleanVar()
        self.show_shots_var_check = ttk.Checkbutton(frame, text='Show Shot #s?', variable=self.show_shots_var)
        self.show_shots_var_check.grid(row=0, column=0, columnspan=2)
        self.show_shots_var.trace('w', self.update_plot)

        self.show_chi2_var = tk.BooleanVar()
        self.show_chi2_var_check = ttk.Checkbutton(frame, text='Show χ^2?', variable=self.show_chi2_var)
        self.show_chi2_var_check.grid(row=1, column=0, columnspan=2)
        self.show_chi2_var.trace('w', self.update_plot)

        # Choose mode to fit:
        label2 = tk.Label(frame, text='l = ')
        label2.grid(row=2, column=0)
        self.mode_var = tk.StringVar(value='2')
        self.mode_selector = ttk.Entry(frame, textvariable=self.mode_var)
        self.mode_selector.configure(width=20)
        self.mode_var.trace('w', self.update_plot)
        self.mode_selector.grid(row=2, column=1)

        sep2 = ttk.Separator(frame, orient='vertical')
        sep2.grid(row=3, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

        # Try to display data (if shot, dim, pos are supplied):
        self.update_plot()

    def __generate_data__(self):
        """Generate the data for plotting"""
        # get mode #:
        mode = int(self.mode_var.get())

        # check to see if we actually need to regenerate data:
        if mode == self.last_mode:
            return

        # figure out which shots
        self.shots = []
        for s in self.db.get_shots():
            if len(self.db.get_dims(s)) >= 2:
                self.shots.append(s)

        n = len(self.shots)
        self.data_x = np.ndarray(n, dtype=np.float64)
        self.data_y = np.ndarray(n, dtype=np.float64)
        self.data_err = np.ndarray(n, dtype=np.float64)

        # loop over all shots:
        for i in range(len(self.shots)):
            shot = self.shots[i]
            r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc = Asymmetries.fit_shot(shot, mode)

            self.data_x[i] = i+1
            self.data_y[i] = delta
            self.data_err[i] = delta_unc

        self.last_mode = mode

    def __calc_chi2__(self):
        """Calculate the chi^2/dof of the dataset relative to 0"""
        chi2 = np.power(np.divide(self.data_y,self.data_err) ,2)
        dof = len(chi2)
        return np.sum(chi2)/dof

    def update_plot(self, *args):
        """Update the displayed plot"""
        # Get info on options chosen:
        show_shots = self.show_shots_var.get()
        show_chi2 = self.show_chi2_var.get()
        try:
            mode = int(self.mode_var.get())
        except:
            return

        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = matplotlib.pyplot.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        self.__generate_data__()

        if show_shots:
            self.ax.set_position((0.1,0.15,0.85,0.8))
        else:
            self.ax.set_position((0.1,0.05,0.85,0.9))

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

        # setup:
        self.ax.set_ylabel(r'$\Delta$ ($\ell$ = ' + str(mode) + ', $m$ = 0)')
        self.ax.set_xticks([])
        self.ax.set_xlim(0, 1+len(self.data_x))
        # plot data:
        self.ax.errorbar(self.data_x, self.data_y, yerr=self.data_err, fmt='bo')
        # and a bar for 0:
        self.ax.axhline(0, c='k', ls='--')

        # add labels if requested:
        if show_shots:
            for i in range(len(self.shots)):
                min_y = self.ax.get_ylim()[0]
                self.ax.text(i+1, min_y*1.05, self.shots[i], ha='center', va='top', rotation='vertical', fontsize=6)

        # add chi2 if requested:
        if show_chi2:
            chi2 = self.__calc_chi2__()
            x = np.average(self.ax.get_xlim())
            y = self.ax.get_ylim()[0]*0.9
            self.ax.text(x,y, r'$\chi^2$ = ' + '{:.2f}'.format(chi2), ha='center', va='center')

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