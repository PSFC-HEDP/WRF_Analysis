__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.DB.Snout_DB import *
from NIF_WRF.Analysis import Asymmetries


class Plot_ShotAsymmetry(tk.Toplevel):
    """Generate a summary plot of asymmetries on a given shot.

    :param parent: (optional) The parent UI window to this one [default=None]
    :param shot: (optional) The shot number to use [default=None]
    """

    def __init__(self, parent=None, shot=None):
        """Initialize the viewer window."""
        super(Plot_ShotAsymmetry, self).__init__()

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
        self.title('Asymmetry summary')

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

        # Choose mode to fit:
        label2 = tk.Label(frame, text='l = ')
        label2.grid(row=1, column=0)
        self.mode_var = tk.StringVar(value='2')
        self.mode_selector = tk.Entry(frame, textvariable=self.mode_var)
        self.mode_selector.configure(width=20)
        self.mode_var.trace('w', self.update_plot)
        self.mode_selector.grid(row=1, column=1)

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
        self.title('Asymmetry summary: ' + self.shot)
        self.update_plot()

    def update_plot(self, *args):
        """Update the displayed plot"""
        shot = self.shot # for shorthand
        try:
            mode = int(self.mode_var.get())
        except:
            return
        if shot is None or mode is None or mode <= 0:
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

        # Plot the rhoR data:
        for dim in self.db.get_dims(shot):
            data_x = []
            data_y = []
            data_err = []
            for pos in self.db.get_pos(shot, dim):
                val = self.db.get_value(shot, dim, pos, 'rhoR')[0]
                err_ran = self.db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0]

                angle = self.db_snout.get_theta('Generic', dim, pos)[0]
                err = err_ran

                data_x.append(angle)
                data_y.append(val)
                data_err.append(err)

            # handle displacements:
            data_x = self.__displace__(data_x, dim)

            # plot if data exists:
            if len(data_x) > 0:
                self.ax.errorbar(data_x, data_y, yerr=data_err, fmt=style[dim])

        # Fit the asymmetry only if 2 DIMs available:
        if len(self.db.get_dims(shot)) > 1:
            r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc = Asymmetries.fit_shot(shot, mode)
            # and make a plot:
            fit_x = np.arange(0., self.ax.get_xlim()[1]+2.5, 2.5)
            fit_y = Asymmetries.rhoR(fit_x, np.zeros_like(fit_x), r0, delta, mode, 0, angles=Asymmetries.ANGLE_DEG)
            self.ax.plot(fit_x, fit_y, 'k--')
            # and add a label:
            x = np.mean(self.ax.get_xlim())
            y = self.ax.get_ylim()[0]
            dy = (self.ax.get_ylim()[1]-self.ax.get_ylim()[0])/15.
            y+=dy
            text1 = r'$\ell$ = ' + str(mode) + ', $m$ = 0'
            self.ax.text(x, y+3*dy, text1, ha='center', va='center', backgroundcolor='w')
            text2 = r'$R_0$ = ' + '{:.0f}'.format(r0*1e4) + ' $\pm$ ' + '{:.0f}'.format(r0_unc*1e4) +' $\mu$m'
            self.ax.text(x, y+2*dy, text2, ha='center', va='center', backgroundcolor='w')
            text3 = '$\Delta$ = ' + '{:.2f}'.format(delta) + ' $\pm$ ' + '{:.2f}'.format(delta_unc)
            self.ax.text(x, y+dy, text3, ha='center', va='center', backgroundcolor='w')
            text4 = r'$\rho R_0$ = ' + '{:.0f}'.format(rhoR0) + ' $\pm$ ' + '{:.0f}'.format(rhoR0_unc) + ' mg/cm$^2$'
            self.ax.text(x, y, text4, ha='center', va='center', backgroundcolor='w')
        else:
            # Add message
            x = np.mean(self.ax.get_xlim())
            y = np.mean(self.ax.get_ylim())
            self.ax.text(x,y, 'Cannot fit 1 DIM', ha='center', va='center', backgroundcolor='w')


        # add labels to the plot:
        self.ax.set_xlabel(r'$\theta$ (deg)')
        self.ax.set_ylabel(r'$\rho$R (mg/cm$^2$)')

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