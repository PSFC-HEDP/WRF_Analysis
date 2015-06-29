__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
import matplotlib
import matplotlib.pyplot
from WRF_Analysis.Analysis import rhoR_model_plots
from WRF_Analysis.GUI.widgets.Model_Frame import Model_Frame
from WRF_Analysis.GUI.widgets.Value_Prompt import Value_Prompt
from threading import Thread


class ModelPlotter(tk.Toplevel):
    """Widget to create rhoR model plots.

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(ModelPlotter, self).__init__()

        self.ax = None
        self.fig = None
        self.canvas = None

        # make the UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        # a couple key bindings:
        self.bind('<Escape>', self.close)
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Set the window title:
        self.title('Model Plotter')

    def __create_widgets__(self):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)
        frame.configure(background='#eeeeee')

        self.plotTypes = {'rhoR vs energy': rhoR_model_plots.plot_rhoR_v_Energy,
                          'Rcm vs energy': rhoR_model_plots.plot_Rcm_v_Energy,
                          'rhoR vs Rcm': rhoR_model_plots.plot_rhoR_v_Rcm,
                          'rhoR fractions': rhoR_model_plots.plot_rhoR_fractions,
                          'Profile': rhoR_model_plots.plot_profile,
                          'Stopping Power': rhoR_model_plots.plot_stoppow}
        self.plotTypeVar = tk.StringVar()
        self.plotType = ttk.OptionMenu(frame, self.plotTypeVar, '', *self.plotTypes.keys())
        self.plotType.grid(row=0, column=0, columnspan=2)

        self.plotButton = ttk.Button(frame, text='Plot', command=self.__plot__)
        self.plotButton.configure(state=tk.DISABLED)
        self.plotButton.grid(row=1, column=0, columnspan=2)

        self.updateModelButton = ttk.Button(frame, text='Run Model', command=self.__updateModel__)
        self.updateModelButton.grid(row=3, column=0)
        self.updateModelLabel = ttk.Label(frame, text='')
        self.updateModelLabel.grid(row=3, column=1)

        frame.pack()
        self.adv_frame = Model_Frame(self, text='Model Parameters', relief=tk.RAISED, borderwidth=1)
        self.adv_frame.pack()

        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

    def __plot__(self, *args):
        """Event handler called to update the calculation"""
        # Some sanity checks:
        if self.model == None:
            return

        # Configure matplotlib
        if self.ax is None:
            self.fig = matplotlib.figure.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # Get type of plot to generate:
        plotType = self.plotTypeVar.get()

        args = {}
        if plotType == 'Profile' or plotType == 'Stopping Power':
            prompt = Value_Prompt(self, title='Plot Option', text='Choose Rcm (um)', default=250)
            Rcm = prompt.result
            args = {Rcm*1e-4}

        # Do the plot
        self.plotTypes[plotType](self.model, *args, ax=self.ax)

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def __updateModel__(self, *args):
        # Clear existing:
        self.model = None

        # Notify the user and prevent subsequent press:
        self.updateModelLabel.configure(text='Running...')
        self.updateModelButton.configure(state=tk.DISABLED)

        # Use threading for the calculation to avoid locking GUI
        def helper():
            self.model = self.adv_frame.get_rhoR_Analysis()
        t = Thread(target=helper)
        t.start()

        # Need to watch for thread completion:
        def callback():
            nonlocal t
            if not t.is_alive():
                # Re-enable:
                self.updateModelLabel.configure(text='')
                self.updateModelButton.configure(state=tk.ACTIVE)
                self.plotButton.configure(state=tk.ACTIVE)
            else:
                self.after(50, callback)
        self.after(50, callback)

    def close(self, *args):
        """Close this window"""
        self.withdraw()