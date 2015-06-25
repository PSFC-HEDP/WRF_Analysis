from WRF_Analysis.GUI.widgets import Value_Prompt

__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from WRF_Analysis.GUI.widgets.Value_Prompt import Value_Prompt

import math
import matplotlib

from WRF_Analysis.GUI.widgets.Option_Prompt import Option_Prompt
from WRF_Analysis.GUI.widgets.Model_Frame import Model_Frame
from WRF_Analysis.GUI.WRF_Progress_Dialog import WRF_Progress_Dialog
from WRF_Analysis.Analysis.Analyze_Spectrum import Analyze_Spectrum
from WRF_Analysis.Analysis.rhoR_Analysis import rhoR_Analysis
from WRF_Analysis.Analysis.rhoR_Model import rhoR_Model
from WRF_Analysis.GUI.Plot_Spectrum import Plot_Spectrum


class WRF_Analyzer(tk.Toplevel):
    """Implement a GUI dialog for providing input to the WRF analysis.

    :param parent: (optional) The parent element in Tkinter [default=None]
    :param shot: (optional) The shot number used, as a str [default prompts user]
    :param dim: (optional) The DIM used, as a str [default prompts user]
    :param pos: (optional) The WRF position used, as a str [default prompts user]
    """
    WRF_Analyzer_last_dir = None

    def __init__(self, file, image, parent=None):
        """Initialize the GUI."""
        super(WRF_Analyzer, self).__init__(master=parent)

        self.file = file
        self.image = image

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.title('Analyze a WRF')

        # create the unique UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        self.minsize(300,200)

    def __create_widgets__(self):
        """Create the UI elements."""

        # now make some UI:
        # display shot/dim/pos as labels:
        # Button to launch a plot of the raw data in a separate window:
        plot_button = ttk.Button(self, text='Plot', command=self.__plot__)
        plot_button.grid(row=1, column=0, columnspan=2, sticky='NS')

        sep1 = ttk.Separator(self, orient="vertical")
        sep1.grid(row=2, column=0, columnspan=2, sticky='ew')

        # some options via checkbutton:
        self.hohl_var = tk.BooleanVar()
        check0 = ttk.Checkbutton(self, text='Hohlraum correction?', variable=self.hohl_var)
        check0.grid(row=3, column=0, columnspan=2, sticky='NS')
        self.hohl_var.trace('w', self.__hohl_var_callback__)

        self.verbose_var = tk.BooleanVar()
        check1 = ttk.Checkbutton(self, text='Output CSV?', variable=self.verbose_var)
        self.verbose_var.set(True)
        check1.grid(row=6, column=0, columnspan=2, sticky='NS')

        self.plot_var = tk.BooleanVar()
        check2 = ttk.Checkbutton(self, text='Make plots?', variable=self.plot_var)
        self.plot_var.set(True)
        check2.grid(row=7, column=0, columnspan=2, sticky='NS')

        self.rhoR_plot_var = tk.BooleanVar()
        check3 = ttk.Checkbutton(self, text='rhoR model plot?', variable=self.rhoR_plot_var)
        check3.grid(row=8, column=0, columnspan=2, sticky='NS')

        self.display_results = tk.BooleanVar()
        check4 = ttk.Checkbutton(self, text='Display results?', variable=self.display_results)
        self.display_results.set(True)
        check4.grid(row=9, column=0, columnspan=2, sticky='NS')

        sep2 = ttk.Separator(self, orient='vertical')
        sep2.grid(row=10, column=0, columnspan=2, sticky='ew')

        self.energy_limits = tk.BooleanVar()
        check5 = ttk.Checkbutton(self, text='Energy limits?', variable=self.energy_limits)
        check5.grid(row=11, column=0, columnspan=2, sticky='NS')
        self.energy_limits.set(True)
        self.min_energy = tk.StringVar()
        self.max_energy = tk.StringVar()
        box1 = ttk.Entry(self, width=10, textvariable=self.min_energy)
        box1.grid(row=12, column=0)
        box2 = ttk.Entry(self, width=10, textvariable=self.max_energy)
        box2.grid(row=12, column=1)
        # Default options for energy limits set via initial analysis info
        fit_mean = self.file.Fit[0]
        fit_sig = self.file.Fit[1]
        self.min_energy.set(fit_mean - 3*fit_sig)
        self.max_energy.set(fit_mean + 3*fit_sig)

        sep2 = ttk.Separator(self, orient='vertical')
        sep2.grid(row=13, column=0, columnspan=2, sticky='ew')

        self.__generate_adv__(14)

        sep3 = ttk.Separator(self, orient='vertical')
        sep3.grid(row=15, column=0, columnspan=2, sticky='ew')

        # buttons:
        go_button = ttk.Button(self, text='Go', command=self.__run_analysis__)
        go_button.grid(row=16, column=0)
        cancel_button = ttk.Button(self, text='Cancel', command=self.__cancel__)
        cancel_button.grid(row=16, column=1)

        # a couple key bindings:
        self.bind('<Return>', self.__run_analysis__)
        self.bind('<Escape>', self.__cancel__)

    def __generate_adv__(self, row):
        """Helper method to generate the GUI for advanced analysis options"""
        # set up the frame:
        self.adv_frame = Model_Frame(self, text='Advanced', relief=tk.RAISED, borderwidth=1)
        self.adv_frame.grid(row=row, column=0, columnspan=2, sticky='nsew')

    def __plot__(self):
        """Generate a plot of the raw data"""
        Plot_Spectrum(self.file)

    def __run_analysis__(self, *args):
        """Run the analysis routine for the selected parameters"""
        # get the spectrum and image:
        spectrum = self.file.spectrum
        # sanity check:
        if spectrum is None:
            from tkinter.messagebox import showerror
            showerror('Error', 'Could not load spectrum')
            return
        Nxy = self.image

        # get uncertainties
        random = [0, 0, 0]
        random[0] = self.file.Unc_Random[2]
        random[1] = self.file.Unc_Random[0]
        random[2] = self.file.Unc_Random[1]
        systematic = [0, 0, 0]
        systematic[0] = self.file.Unc_Systematic[2]
        systematic[1] = self.file.Unc_Systematic[0]
        systematic[2] = self.file.Unc_Systematic[1]

        # get a name and summary
        name = self.file.fname.split('/')[-1]
        # Get the shot title/name description thing
        shot_name_query = self.file.shot
        summary = self.file.shot
        # if we are using TeX for rendering, then fix underscores:
        if matplotlib.rcParams['text.usetex'] == True:
            summary = summary.replace('_',r'$\textunderscore$')

        # get the hohlraum wall:
        do_hohl_corr = self.hohl_var.get()
        if do_hohl_corr:
            dialog = Value_Prompt(self, title='Hohlraum', text='Input Au thickness in um', default=0.)
            Au = dialog.result
            dialog = Value_Prompt(self, title='Hohlraum', text='Input DU thickness in um', default=0.)
            DU = dialog.result
            dialog = Value_Prompt(self, title='Hohlraum', text='Input Al thickness in um', default=0.)
            Al = dialog.result

            hohl_thick = [Au, DU, Al]
            wall = None
        else:
            wall = None
            hohl_thick = None
        use_bump_corr = False
        bump_corr = 0

        # ask if we should generate rhoR plots
        from tkinter.filedialog import askdirectory
        opts = dict(mustexist='False',
                       initialdir=WRF_Analyzer.WRF_Analyzer_last_dir,
                       title='Save files to')
        OutputDir = askdirectory(**opts)
        # sanity check:
        if OutputDir == '':  # user cancelled
            return
        WRF_Analyzer.WRF_Analyzer_last_dir = OutputDir

        # Get a guess to help the fitting routine from the numbers in the initial analysis
        guess_Y = self.file.Fit[2]
        guess_E = self.file.Fit[0]
        guess_s = self.file.Fit[1]
        if guess_Y < 0 or guess_E < 0 or guess_s < 0:
            guess_Y = self.file.Fit_Raw[2]
            guess_E = self.file.Fit_Raw[0]
            guess_s = self.file.Fit_Raw[1]
        fit_guess = [guess_Y, guess_E, guess_s]

        # energy limits if requested:
        if self.energy_limits.get():
            try:
                minE = float(self.min_energy.get())
                maxE = float(self.max_energy.get())
                limits = [minE,maxE]
            except:
                limits = None
        else:
            limits = None

        # get the model
        model = self.adv_frame.get_rhoR_Analysis()

        result, corr_spec = Analyze_Spectrum(spectrum,
                                  random,
                                  systematic,
                                  [0,0],
                                  hohl_wall=wall,
                                  hohl_thick=hohl_thick,
                                  name=name,
                                  summary=summary,
                                  plots=self.plot_var.get(),
                                  verbose=self.verbose_var.get(),
                                  rhoR_plots=self.rhoR_plot_var.get(),
                                  OutputDir=OutputDir,
                                  Nxy=Nxy,
                                  ProgressBar=None,
                                  ShowSlide=self.display_results.get(),
                                  model=model,
                                  fit_guess=fit_guess,
                                  limits=limits,
                                  use_bump_corr=use_bump_corr,
                                  bump_corr=bump_corr)

        # add to DB:
        print(result)

        # finish by removing the window:
        self.__cancel__()

    def __cancel__(self, *args):
        """Cancel, and remove the window."""
        self.withdraw()

    def __hohl_var_callback__(self, *args):
        """Handle UI changes when the hohlraum correction is enabled or disabled."""
        pass
