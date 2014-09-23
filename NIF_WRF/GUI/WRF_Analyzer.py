from NIF_WRF.GUI.widgets import Value_Prompt

__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

import math
import matplotlib

from NIF_WRF.DB import Database
from NIF_WRF.DB.WRF_Data_DB import *
from NIF_WRF.DB.WRF_InitAnalysis_DB import *
from NIF_WRF.DB.WRF_Setup_DB import *
from NIF_WRF.DB.Hohlraum_DB import *
from NIF_WRF.DB.Snout_DB import *
from NIF_WRF.DB.WRF_Analysis_DB import *
from NIF_WRF.DB.WRF_Analysis_Param_DB import *
from NIF_WRF.GUI.widgets.Option_Prompt import Option_Prompt
from NIF_WRF.GUI.widgets.Model_Frame import Model_Frame
from NIF_WRF.GUI.WRF_Progress_Dialog import WRF_Progress_Dialog
from NIF_WRF.Analysis.Analyze_Spectrum import Analyze_Spectrum
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis
from NIF_WRF.Analysis.rhoR_Model import rhoR_Model
from NIF_WRF.GUI.Plot_Spectrum import Plot_Spectrum


class WRF_Analyzer(tk.Toplevel):
    """Implement a GUI dialog for providing input to the WRF analysis.

    :param parent: (optional) The parent element in Tkinter [default=None]
    :param shot: (optional) The shot number used, as a str [default prompts user]
    :param dim: (optional) The DIM used, as a str [default prompts user]
    :param pos: (optional) The WRF position used, as a str [default prompts user]
    """

    def __init__(self, parent=None, shot=None, dim=None, pos=None):
        """Initialize the GUI."""
        super(WRF_Analyzer, self).__init__(master=parent)

        # necessary databases:
        self.init_db = WRF_InitAnalysis_DB()
        self.data_db = WRF_Data_DB()
        self.setup_db = WRF_Setup_DB()
        self.hohl_db = Hohlraum_DB()
        self.snout_db = Snout_DB()
        self.analysis_db = WRF_Analysis_DB()
        self.param_db = WRF_Analysis_Param_DB()

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.title('Analyze a WRF')

        # set class variables
        self.shot = shot
        self.dim = dim
        self.pos = pos

        # create the unique UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        self.minsize(300,200)

    def __create_widgets__(self):
        """Create the UI elements."""

        # if no shot was supplied, prompt for one:
        if self.shot is None:
            shots = self.init_db.get_shots()

            # sanity check for edge case where no shots are available:
            if len(shots) == 0:
                from tkinter.messagebox import showerror
                showerror('Error', message='No WRF data available, import some', parent=self)
                self.__cancel__()
                return

            dialog = Option_Prompt(self, title='Select shot', text='Shot numbers available', options=shots, width=20)
            self.shot = dialog.result

            # if the user canceled:
            if self.shot is None:
                self.__cancel__()
                return

        # if no DIM was supplied, prompt for one:
        if self.dim is None:
            dims = self.init_db.get_dims(self.shot)
            dialog = Option_Prompt(self, title='Select DIM', text='DIMs available for '+self.shot, options=dims)
            self.dim = dialog.result

            # if the user canceled:
            if self.dim is None:
                self.__cancel__()
                return

        # if no pos was supplied, prompt for one:
        if self.pos is None:
            positions = self.init_db.get_pos(self.shot, self.dim)
            dialog = Option_Prompt(self, title='Select Position', text='Available positions', options=positions)
            self.pos = dialog.result

            # if the user canceled:
            if self.pos is None:
                self.__cancel__()
                return

        # now make some UI:
        # display shot/dim/pos as labels:
        label1 = ttk.Label(self, text=self.shot + ', ' + self.dim + ' Pos ' + str(self.pos))
        label1.grid(row=0, column=0, columnspan=2, sticky='NS')
        # Button to launch a plot of the raw data in a separate window:
        plot_button = ttk.Button(self, text='Plot', command=self.__plot__)
        plot_button.grid(row=1, column=0, columnspan=2, sticky='NS')

        sep1 = ttk.Separator(self, orient="vertical")
        sep1.grid(row=2, column=0, columnspan=2, sticky='ew')

        # some options via checkbutton:
        self.hohl_var = tk.BooleanVar()
        check0 = ttk.Checkbutton(self, text='Hohlraum correction?', variable=self.hohl_var)
        check0.grid(row=3, column=0, columnspan=2, sticky='NS')
        # set based on DIM:
        if self.dim == '0-0':
            self.hohl_var.set(False)
        else:
            self.hohl_var.set(True)
        self.hohl_var.trace('w', self.__hohl_var_callback__)

        # UI to allow for correction of the 'bump'
        self.bump_var = tk.BooleanVar()
        self.bump_check = ttk.Checkbutton(self, text='Bump correction?', variable=self.bump_var)
        self.bump_check.grid(row=4, column=0, columnspan=2, sticky='NS')
        self.bump_check.configure(state=tk.DISABLED)
        self.bump_var.trace('w', self.__bump_var_callback__)
        bump_label = ttk.Label(self, text='Correction (μm)')
        bump_label.grid(row=5, column=0)
        self.bump_dt_var = tk.StringVar()
        self.bump_entry = ttk.Entry(self, textvariable=self.bump_dt_var)
        self.bump_entry.configure(width=8)
        self.bump_entry.grid(row=5, column=1)
        self.bump_entry.configure(state=tk.DISABLED)
        self.bump_dt_var.set('-10')
        self.__init_bump__()

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
        fit_mean = self.init_db.get_value(self.shot, self.dim, self.pos, 'fit_mean')[0]
        self.min_energy.set(fit_mean - 2)
        self.max_energy.set(fit_mean + 2)

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
        self.adv_frame = Model_Frame(self, text='Advanced', shot=self.shot, relief=tk.RAISED, borderwidth=1)
        self.adv_frame.grid(row=row, column=0, columnspan=2, sticky='nsew')

    def __plot__(self):
        """Generate a plot of the raw data"""
        Plot_Spectrum(self, shot=self.shot, dim=self.dim, pos=self.pos)

    def __run_analysis__(self, *args):
        """Run the analysis routine for the selected parameters"""
        # get the spectrum and image:
        spectrum = self.data_db.get_spectrum(self.shot, self.dim, self.pos, False)
        # sanity check:
        if spectrum is None:
            from tkinter.messagebox import showerror
            showerror('Error', 'Could not load spectrum from database')
            return
        try:
            Nxy = self.data_db.get_Nxy(self.shot, self.dim, self.pos, False)
        except TypeError:  # data not found
            Nxy = None

        # get uncertainties
        random = [0, 0, 0]
        random[0] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_yield_random')[0]
        random[1] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_mean_random')[0]
        random[2] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_sigma_random')[0]
        systematic = [0, 0, 0]
        systematic[0] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_yield_sys')[0]
        systematic[1] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_mean_sys')[0]
        systematic[2] = self.init_db.get_value(self.shot, self.dim, self.pos, 'unc_sigma_sys')[0]

        # get a name and summary
        name = self.shot + '_' + self.dim + '_Pos' + str(self.pos)
        # Get the shot title/name description thing
        shot_name_query = self.setup_db.query_col(self.shot, self.dim, self.pos, 'shot_name')
        # check for errors
        if shot_name_query is None or len(shot_name_query) is 0:
            from tkinter.messagebox import showerror
            showerror('Error', 'Could not load shot meta info (name). Add it to the setup DB.')
            summary = self.shot
            print(self.shot)
            print(self.setup_db.get_shots())
            return
        else:
            summary = self.shot + ' , ' + shot_name_query[0]
        # if we are using TeX for rendering, then fix underscores:
        if matplotlib.rcParams['text.usetex'] == True:
            summary = summary.replace('_',r'$\textunderscore$')
        #summary = summary.encode('unicode-escape')

        # get snout info:
        snout = self.setup_db.query_col(self.shot, self.dim, self.pos, 'snout')[0]

        # get the hohlraum wall:
        do_hohl_corr = self.hohl_var.get()
        if do_hohl_corr:
            hohl_drawing = self.setup_db.query_col(self.shot, self.dim, self.pos, 'hohl_drawing')[0]
            while ' ' in hohl_drawing:
                hohl_drawing = hohl_drawing.replace(' ', '')
            wall = self.hohl_db.get_wall(drawing=hohl_drawing)
            hohl_thick = None
            if wall is None or len(wall) == 0:
                from tkinter.messagebox import askyesnocancel

                # First, lets try to pick hohlraum from a list:
                response = askyesnocancel('Warning', 'Could not load hohlraum definition for ' + hohl_drawing
                                                     + '. Choose from list?')
                if response:
                    dialog = Option_Prompt(self, title='Choose hohlraum', text='Pre-existing hohlraums',
                                           options=self.hohl_db.get_drawings())
                    wall = self.hohl_db.get_wall(drawing=dialog.result)
                elif not response:
                    response = askyesnocancel('Warning', 'Could not load hohlraum definition for ' + hohl_drawing
                                                         + '. Specify manually?')
                    if response:
                        from NIF_WRF.GUI.widgets.Value_Prompt import Value_Prompt
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

                elif response is None:
                    return
                else:
                    wall = None

            # Stuff for the bump correction:
            use_bump_corr = self.bump_var.get()
            bump_corr = float(self.bump_dt_var.get())
        else:
            wall = None
            hohl_thick = None
            use_bump_corr = False
            bump_corr = 0

        # calculate angles:
        theta = self.snout_db.get_theta(snout, self.dim, self.pos)[0]
        r = self.snout_db.get_r(snout, self.dim, self.pos)[0]
        dtheta = math.atan2(1., r)*180./math.pi
        angles = [theta-dtheta, theta+dtheta]

        # ask if we should generate rhoR plots
        from tkinter.filedialog import askdirectory
        opts = dict(mustexist='False',
                       initialdir=Database.DIR,
                       title='Save files to')
        OutputDir = askdirectory(**opts)
        # sanity check:
        if OutputDir == '':  # user cancelled
            return

        # Get a guess to help the fitting routine from the numbers in the initial analysis
        guess_Y = self.init_db.get_value(self.shot, self.dim, self.pos, 'fit_yield')
        guess_E = self.init_db.get_value(self.shot, self.dim, self.pos, 'fit_mean')
        guess_s = self.init_db.get_value(self.shot, self.dim, self.pos, 'fit_sigma')
        if len(guess_Y) > 0 and len(guess_E) > 0 and len(guess_s) > 0:
            fit_guess = [guess_Y[0], guess_E[0], guess_s[0]]
        else:
            fit_guess = None

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
                                  angles,
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
        self.analysis_db.load_results(self.shot, self.dim, self.pos, result)
        self.adv_frame.add_to_db(self.shot, self.dim, self.pos)
        analysis_param = {'use_hohl_corr': do_hohl_corr,
                          'name': name,
                          'summary': summary,
                          'min_E': limits[0],
                          'max_E': limits[1],
                          'use_bump_corr': use_bump_corr,
                          'bump_corr': bump_corr}
        self.param_db.load_results(self.shot, self.dim, self.pos, analysis_param)

        # Add hohlraum-corrected spectrum to the database if necessary:
        if corr_spec is not None:
            wrf_id = self.data_db.get_wrf_id(self.shot, self.dim, self.pos)[0]
            cr39_id = self.data_db.get_cr39_id(self.shot, self.dim, self.pos)[0]
            # get the date and time:
            import datetime
            now = datetime.datetime.now()
            analysis_date = now.strftime('%Y-%m-%d %H:%M')
            print(wrf_id, cr39_id)
            self.data_db.insert(self.shot, self.dim, self.pos, wrf_id, cr39_id, analysis_date, True, corr_spec)

        # finish by removing the window:
        self.__cancel__()

    def __cancel__(self, *args):
        """Cancel, and remove the window."""
        self.withdraw()

    def __hohl_var_callback__(self, *args):
        """Handle UI changes when the hohlraum correction is enabled or disabled."""
        if self.hohl_var.get() == True:
            self.bump_check.configure(state=tk.ACTIVE)
        else:
            self.bump_check.configure(state=tk.DISABLED)

    def __bump_var_callback__(self, *args):
        """Handle UI changes when the hohlraum bump correction is enabled or disabled"""
        if self.bump_var.get() == True:
            self.bump_entry.configure(state=tk.ACTIVE)
        else:
            self.bump_entry.configure(state=tk.DISABLED)

    def __init_bump__(self):
        """Get info on the bump from the hohlraum database."""
        # If the hohlraum correction is initially enabled, the bump correction can be used:
        if self.hohl_var.get():
            self.bump_check.configure(state=tk.ACTIVE)
            self.bump_entry.configure(state=tk.ACTIVE)

        # Try to fetch info on the bump from the database:
        try:
            hohl_drawing = self.setup_db.query_col(self.shot, self.dim, self.pos, 'hohl_drawing')[0]
            while ' ' in hohl_drawing:
                hohl_drawing = hohl_drawing.replace(' ', '')
            bump = self.hohl_db.get_bump(hohl_drawing)
            if isinstance(bump, list) and isinstance(bump[0],str):
                self.bump_var.set(bump[1])
                self.bump_dt_var.set(bump[2])
        except:
            pass