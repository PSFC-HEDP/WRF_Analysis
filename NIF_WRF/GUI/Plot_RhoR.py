__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import matplotlib
import matplotlib.pyplot
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.Analysis import Shot_Analysis


class Plot_RhoR(tk.Toplevel):
    """Generate and display a summary plot of all rhoR data.

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(Plot_RhoR, self).__init__()
        # Set the window title:
        self.title('ρR summary plot')

        # initializations
        self.canvas = None
        self.ax = None

        # generate the data
        self.__generate_data__()

        # make the UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        # a couple key bindings:
        self.bind('<Escape>', self.close)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def __create_widgets__(self):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)

        # Add some UI elements:
        self.pole_var = tk.BooleanVar()
        self.pole_var_check = ttk.Checkbutton(frame, text='0-0', variable=self.pole_var)
        self.pole_var_check.grid(row=0, column=0)
        self.pole_var.set(True)
        self.pole_var.trace('w', self.update_plot)

        self.eq_var = tk.BooleanVar()
        self.eq_var_check = ttk.Checkbutton(frame, text='90-78', variable=self.eq_var)
        self.eq_var_check.grid(row=0, column=1)
        self.eq_var.set(True)
        self.eq_var.trace('w', self.update_plot)

        sep = ttk.Separator(frame, orient='vertical')
        sep.grid(row=1, column=0, columnspan=2, sticky='ew')

        self.show_shots_var = tk.BooleanVar()
        self.show_shots_var_check = ttk.Checkbutton(frame, text='Show Shot #s?', variable=self.show_shots_var)
        self.show_shots_var_check.grid(row=2, column=0, columnspan=2)
        self.show_shots_var.trace('w', self.update_plot)

        self.err_var = tk.StringVar()
        options = ['Random Error', 'Systematic Error', 'Total Error']
        self.err_method = ttk.OptionMenu(frame, self.err_var, *options)
        self.err_method.configure(width=20)
        self.err_method.grid(row=3, column=0, columnspan=2)
        self.err_var.trace('w', self.update_plot)

        sep2 = ttk.Separator(frame, orient='vertical')
        sep2.grid(row=4, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

        # Try to display data (if shot, dim, pos are supplied):
        self.update_plot()

    def __generate_data__(self):
        """Generate the data for plotting"""
        db = WRF_Analysis_DB()
        # arrays for the data, error bars, and label
        self.x = []
        self.y = []
        self.err_ran = []
        self.err_sys = []
        self.err_tot = []
        self.label = []

        # loop for each DIM:
        for dim in ['0-0', '90-78']:
            # arrays for the individual DIMs
            n = len(db.get_shots())
            data_x = np.ndarray(n, dtype=np.float64)
            data_y = np.ndarray(n, dtype=np.float64)
            data_err_ran = np.ndarray(n, dtype=np.float64)
            data_err_sys = np.ndarray(n, dtype=np.float64)
            data_err_tot = np.ndarray(n, dtype=np.float64)
            i=0
            self.label.append(dim)

            # loop over every shot
            for shot in db.get_shots():
                rhoR, drhoR_ran = Shot_Analysis.avg_rhoR(shot, dim, error=Shot_Analysis.ERR_RANDOM)
                rhoR, drhoR_sys = Shot_Analysis.avg_rhoR(shot, dim, error=Shot_Analysis.ERR_SYSTEMATIC)
                rhoR, drhoR_tot = Shot_Analysis.avg_rhoR(shot, dim, error=Shot_Analysis.ERR_TOTAL)

                if rhoR is not None:
                    data_x[i] = i+1
                    data_y[i] = rhoR
                    data_err_ran[i] = drhoR_ran
                    data_err_sys[i] = drhoR_sys
                    data_err_tot[i] = drhoR_tot
                else:  # no data available:
                    data_x[i] = i+1
                    data_y[i] = -10
                    data_err_ran[i] = 0.1
                    data_err_sys[i] = 0.1
                    data_err_tot[i] = 0.1

                i+=1

            self.x.append(data_x)
            self.y.append(data_y)
            self.err_ran.append(data_err_ran)
            self.err_sys.append(data_err_sys)
            self.err_tot.append(data_err_tot)
            self.shots = db.get_shots()

    def update_plot(self, *args):
        """Update the displayed plot"""
        # Get info:
        show_shots = self.show_shots_var.get()
        err_bar_type = self.err_var.get()
        show_pole = self.pole_var.get()
        show_eq = self.eq_var.get()

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
        #xlabel('Shot')
        self.ax.set_ylabel(r'$\rho$R (mg/cm$^2$)')
        self.ax.set_xticks([])
        self.ax.set_ylim(50,200)
        self.ax.set_xlim(0,np.max(self.x)+1)

        # get the appropriate error bar:
        yerr = [[],[]]
        if err_bar_type == 'Random Error':
            yerr[0] = self.err_ran[0]
            yerr[1] = self.err_ran[1]
        elif err_bar_type == 'Systematic Error':
            yerr[0] = self.err_sys[0]
            yerr[1] = self.err_sys[1]
        else: # 'Total Error'
            yerr[0] = self.err_tot[0]
            yerr[1] = self.err_tot[1]

        # plot the data if requested:
        if (show_pole and self.label[0] == '0-0') or (show_eq and self.label[0] == '90-78'):
            self.ax.errorbar(self.x[0], self.y[0], yerr=yerr[0], fmt='ko', label=self.label[0])
        if (show_pole and self.label[1] == '0-0') or (show_eq and self.label[1] == '90-78'):
            self.ax.errorbar(self.x[1], self.y[1], yerr=yerr[1], fmt='ro', label=self.label[1])

        # add some legends:
        if show_shots:
            for i in range(len(self.shots)):
                self.ax.text(i+1, 48, self.shots[i], ha='center', va='top', rotation='vertical', fontsize=6)
        # finale:
        self.ax.legend(loc=2, numpoints=1)

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