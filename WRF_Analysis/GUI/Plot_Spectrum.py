__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

import numpy
import matplotlib
import matplotlib.pyplot
from WRF_Analysis.util.GaussFit import Gaussian


class Plot_Spectrum(tk.Toplevel):
    """Generic viewer for spectrum plots

    :param file: The WRF CSV object to plot
    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, file, parent=None):
        """Initialize the viewer window."""
        super(Plot_Spectrum, self).__init__()

        # initializations
        self.canvas = None
        self.ax = None
        self.file = file
        self.spectrum = file.spectrum

        # size limits
        #self.minsize(600,400)
        #self.maxsize(900,600)

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

        self.fit_var = tk.BooleanVar()
        self.fit_var_check = ttk.Checkbutton(frame, text='Show fit?', variable=self.fit_var)
        self.fit_var_check.grid(row=4, column=0, columnspan=2)
        self.fit_var.trace('w', self.update_plot)

        sep = ttk.Separator(frame, orient='vertical')
        sep.grid(row=5, column=0, columnspan=2, sticky='ew')

        # add the frame
        frame.pack()

        # add a frame for the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

        # Try to display data (if shot, dim, pos are supplied):
        self.update_plot()

    def update_plot(self, *args):
        """Update the displayed plot"""
        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = matplotlib.figure.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # sanity:
        if self.spectrum is None or len(self.spectrum) == 0:
            return

        # split up the data:
        data_x = []
        data_y = []
        data_err = []
        for row in self.spectrum:
            data_x.append(row[0])
            data_y.append(row[1])
            data_err.append(row[2])

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

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

        # Show a fit if requested:
        if self.fit_var.get():
            try:
                dx = 0.1 * (max(data_x)-min(data_x))/len(data_x)
                fit_x = numpy.arange(min(data_x), max(data_x), dx)
                fit_Y = self.file.Fit[2]
                fit_E = self.file.Fit[0]
                fit_s = self.file.Fit[1]
                fit_y = Gaussian(fit_x, fit_Y, fit_E, fit_s)
                self.ax.plot(fit_x, fit_y, 'r--')
            except Exception as inst:
                print('Could not show fit')
                print(inst)

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def close(self, *args):
        """Close this window"""
        self.withdraw()