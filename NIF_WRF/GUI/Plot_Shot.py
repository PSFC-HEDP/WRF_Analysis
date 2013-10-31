__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.DB.Snout_DB import *
from NIF_WRF.Analysis.Shot_Analysis import avg_Yield


class Plot_Shot(tk.Toplevel):
    """Generate a summary plot of all data from a given shot.

    :param parent: (optional) The parent UI window to this one [default=None]
    :param shot: (optional) The shot number to use [default=None]
    """

    def __init__(self, parent=None, shot=None):
        """Initialize the viewer window."""
        super(Plot_Shot, self).__init__()

        # initializations
        self.db = WRF_Analysis_DB()
        self.db_snout = Snout_DB()
        self.canvas = None
        self.ax = None
        self.shot = shot

        # make the UI:
        self.__create_widgets__(shot)

        # a couple key bindings:
        self.bind('<Escape>', self.close)

        # Set the window title:
        self.title('Shot summary')

    def __create_widgets__(self, shot):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)

        # Add some control UI:
        label1 = tk.Label(frame, text='Shot')
        label1.grid(row=0, column=0)

        # Shot selection:
        shots = self.db.get_shots()
        if len(shots) == 0:
            shots = ['']
        self.shot_var = tk.StringVar(value=shot)
        self.shot_selector = tk.OptionMenu(frame, self.shot_var, *shots)
        self.shot_selector.configure(width=20)
        self.shot_var.trace('w', self.update_shot)
        self.shot_selector.grid(row=0, column=1)

        # Plot type selection:
        label2 = tk.Label(frame, text='Plot Type')
        label2.grid(row=1, column=0)
        self.plot_var = tk.StringVar(value='ρR')
        options = ['ρR', 'Yield', 'Energy']
        self.plot_selector = tk.OptionMenu(frame, self.plot_var, *options)
        self.plot_selector.configure(width=20)
        self.plot_var.trace('w', self.update_plot)
        self.plot_selector.grid(row=1, column=1, columnspan=2)

        label3 = tk.Label(frame, text='Error bars')
        label3.grid(row=2, column=0)
        self.err_var = tk.StringVar(value='Total Error')
        options = ['Random Error', 'Systematic Error', 'Total Error']
        self.err_method = tk.OptionMenu(frame, self.err_var, *options)
        self.err_method.configure(width=20)
        self.err_method.grid(row=2, column=1)
        self.err_var.trace('w', self.update_plot)

        sep2 = ttk.Separator(frame, orient='vertical')
        sep2.grid(row=3, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

        # Try to display data (if shot, dim, pos are supplied):
        self.update_plot()

    def update_shot(self, *args):
        """Update after shot selection is changed."""
        self.shot = self.shot_var.get()
        self.title('Shot summary: ' + self.shot)
        self.update_plot()

    def update_plot(self, *args):
        """Update the displayed plot"""
        shot = self.shot # for shorthand
        plotType = self.plot_var.get()
        errorType = self.err_var.get()
        if shot is None or plotType is None or errorType is None:
            return

        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = plt.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            plt.switch_backend('TkAgg')

        # Define styles for the DIMs:
        style = {'0-0': 'ro', '90-78': 'bo'}

        # do the actual plotting:
        for dim in self.db.get_dims(shot):
            data_x = []
            data_y = []
            data_err = []
            for pos in self.db.get_pos(shot, dim):
                if plotType == 'ρR':
                    val = self.db.get_value(shot, dim, pos, 'rhoR')[0]
                    err_ran = self.db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0]
                    err_sys = self.db.get_value(shot, dim, pos, 'rhoR_sys_unc')[0]
                elif plotType == 'Yield':
                    val = self.db.get_value(shot, dim, pos, 'Yield')[0]
                    err_ran = self.db.get_value(shot, dim, pos, 'Yield_ran_unc')[0]
                    err_sys = self.db.get_value(shot, dim, pos, 'Yield_sys_unc')[0]
                else: # plotType == 'Energy':
                    val = self.db.get_value(shot, dim, pos, 'Energy')[0]
                    err_ran = self.db.get_value(shot, dim, pos, 'Energy_ran_unc')[0]
                    err_sys = self.db.get_value(shot, dim, pos, 'Energy_sys_unc')[0]

                theta = self.db_snout.get_theta('Generic', dim, pos)[0]

                # Decide which error bar we should use:
                if errorType == 'Random Error':
                    err = err_ran
                elif errorType == 'Systematic Error':
                    err = err_sys
                else:
                    err = np.sqrt(err_ran**2 + err_sys**2)

                data_x.append(theta)
                data_y.append(val)
                data_err.append(err)

            # handle displacements:
            data_x = self.__displace__(data_x, dim)

            # plot if data exists:
            if len(data_x) > 0:
                self.ax.errorbar(data_x, data_y, yerr=data_err, fmt=style[dim])

        # add labels to the plot:
        self.ax.set_xlabel(r'$\theta$ (deg)')
        if plotType == 'ρR':
            self.ax.set_ylabel(r'$\rho$R (mg/cm$^2$)')
        elif plotType == 'Yield':
            self.ax.set_ylabel(r'Proton Yield / MeV')
        elif plotType == 'Energy':
            self.ax.set_ylabel(r'Proton Energy (MeV)')

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)

            toolbar = NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def __displace__(self, data, dim):
        """Handle displacement of data points to avoid overlap"""
        delta = 1

        if len(data) == 0 or len(data) == 1:
            return data

        if len(data) == 2:
            if dim == '0-0' or data[0]==data[1]:
                data[0] -= delta/2
                data[1] += delta/2

        if len(data) == 3:
            if dim == '0-0':
                data[0] -= delta
                data[2] += delta
            elif dim == '90-78':
                if data[0] == data[1]:
                    data[0] -= delta/2
                    data[1] += delta/2
                elif data[0] == data[2]:
                    data[0] -= delta/2
                    data[2] += delta/2
                else:
                    data[1] -= delta/2
                    data[2] += delta/2

        if len(data) == 4:
            if dim == '0-0':
                data[0] -= 2*delta
                data[1] -= delta
                data[3] += delta
            elif dim == '90-78':
                data[0] -= delta/2
                data[1] += delta/2
                data[2] -= delta/2
                data[3] += delta/2

        return data

    def close(self, *args):
        """Close this window"""
        self.withdraw()