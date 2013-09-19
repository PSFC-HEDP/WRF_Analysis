__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk
from DB import Database
from DB.WRF_Data_DB import *
from DB.WRF_InitAnalysis_DB import *
from DB.WRF_Setup_DB import *
from DB.Hohlraum_DB import *
from DB.Snout_DB import *
from DB.WRF_Analysis_DB import *
from GUI.widgets.Option_Prompt import Option_Prompt
from GUI.widgets.Model_Frame import Model_Frame
from GUI.WRF_Progress_Dialog import WRF_Progress_Dialog
import math
import matplotlib
from Analysis.Analyze_Spectrum import Analyze_Spectrum
from Analysis.rhoR_Analysis import rhoR_Analysis
from Analysis.rhoR_Model import rhoR_Model


class WRF_Analyzer(tk.Toplevel):
    """Implement a GUI dialog for providing input to the WRF analysis."""

    def __init__(self, parent=None, shot=None, dim=None, pos=None):
        """Initialize the GUI.
        :param parent: (optional) The parent element in Tkinter [default=None]
        :param shot: (optional) The shot number used, as a str [default prompts user]
        :param dim: (optional) The DIM used, as a str [default prompts user]
        :param pos: (optional) The WRF position used, as a str [default prompts user]
        """
        super(WRF_Analyzer, self).__init__(master=parent)

        # necessary databases:
        self.init_db = WRF_InitAnalysis_DB()
        self.data_db = WRF_Data_DB()
        self.setup_db = WRF_Setup_DB()
        self.hohl_db = Hohlraum_DB()
        self.snout_db = Snout_DB()
        self.analysis_db = WRF_Analysis_DB()

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

        self.minsize(300,200)

    def __create_widgets__(self):
        """Create the UI elements."""

        # if no shot was supplied, prompt for one:
        if self.shot is None:
            shots = self.init_db.get_shots()
            dialog = Option_Prompt(self, title='Select shot', text='Shot numbers available', options=shots)
            self.shot = dialog.result

        # if no DIM was supplied, prompt for one:
        if self.dim is None:
            dims = self.init_db.get_dims(self.shot)
            dialog = Option_Prompt(self, title='Select DIM', text='DIMs available for '+self.shot, options=dims)
            self.dim = dialog.result

        # if no pos was supplied, prompt for one:
        if self.pos is None:
            positions = self.init_db.get_pos(self.shot, self.dim)
            dialog = Option_Prompt(self, title='Select Position', text='Available positions', options=positions)
            self.pos = dialog.result

        # now make some UI:
        # display shot/dim/pos as labels:
        label1 = tk.Label(self, text='Shot: ' + self.shot)
        label1.grid(row=0, column=0, columnspan=2, sticky='NS')

        label2 = tk.Label(self, text='DIM: ' + self.dim)
        label2.grid(row=1, column=0, columnspan=2, sticky='NS')

        label3 = tk.Label(self, text='Pos: ' + self.pos)
        label3.grid(row=2, column=0, columnspan=2, sticky='NS')

        sep1 = ttk.Separator(self, orient="vertical")
        sep1.grid(row=3, column=0, columnspan=2, sticky='ew')

        # some options via checkbutton:
        self.verbose_var = tk.BooleanVar()
        check0 = tk.Checkbutton(self, text='Output CSV?', variable=self.verbose_var)
        check0.select()
        check0.grid(row=4, column=0, columnspan=2, sticky='NS')
        self.plot_var = tk.BooleanVar()
        check1 = tk.Checkbutton(self, text='Make plots?', variable=self.plot_var)
        check1.select()
        check1.grid(row=5, column=0, columnspan=2, sticky='NS')
        self.rhoR_plot_var = tk.BooleanVar()
        check2 = tk.Checkbutton(self, text='rhoR model plot?', variable=self.rhoR_plot_var)
        check2.grid(row=6, column=0, columnspan=2, sticky='NS')
        self.display_results = tk.BooleanVar()
        check3 = tk.Checkbutton(self, text='Display results?', variable=self.display_results)
        check3.select()
        check3.grid(row=7, column=0, columnspan=2, sticky='NS')

        sep2 = ttk.Separator(self, orient='vertical')
        sep2.grid(row=8, column=0, columnspan=2, sticky='ew')

        self.__generate_adv__(9)

        sep3 = ttk.Separator(self, orient='vertical')
        sep3.grid(row=10, column=0, columnspan=2, sticky='ew')

        # buttons:
        go_button = tk.Button(self, text='Go', command=self.__run_analysis__)
        go_button.grid(row=11, column=0)
        cancel_button = tk.Button(self, text='Cancel', command=self.__cancel__)
        cancel_button.grid(row=11, column=1)

        # a couple key bindings:
        self.bind('<Return>', self.__run_analysis__)
        self.bind('<Escape>', self.__cancel__)

    def __generate_adv__(self, row):
        """Helper method to generate the GUI for advanced analysis options"""
        # set up the frame:
        self.adv_frame = Model_Frame(self, text='Advanced', relief=tk.RAISED, borderwidth=1)
        self.adv_frame.grid(row=row, column=0, columnspan=2, sticky='nsew')

    def __run_analysis__(self, *args):
        """Run the analysis routine for the selected parameters"""
        # get the spectrum and image:
        spectrum = self.data_db.get_spectrum(self.shot, self.dim, self.pos, False)
        # sanity check:
        if spectrum is None:  # TODO: troubleshoot, seems to have issues with multiple available spectra
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
        name = self.shot + '_' + self.dim + '_Pos' + self.pos
        # Get the shot title/name description thing
        shot_name_query = self.setup_db.query_col(self.shot, self.dim, self.pos, 'shot_name')
        # check for errors
        if shot_name_query is None or len(shot_name_query) is 0:
            from tkinter.messagebox import showerror
            showerror('Error', 'Could not load shot meta info (name), aborting analysis. Add it to the setup DB.')
            return
        summary = self.shot + ' , ' + shot_name_query[0]
        # if we are using TeX for rendering, then fix underscores:
        if matplotlib.rcParams['text.usetex'] == True:
            summary = summary.replace('_',r'$\textunderscore$')
        #summary = summary.encode('unicode-escape')

        # get the hohlraum wall:
        snout = self.setup_db.query_col(self.shot, self.dim, self.pos, 'snout')[0]
        hohl_drawing = self.setup_db.query_col(self.shot, self.dim, self.pos, 'hohl_drawing')[0]
        wall = self.hohl_db.get_wall(drawing=hohl_drawing)
        if wall is None or len(wall) == 0:
            from tkinter.messagebox import showerror
            showerror('Error', 'Could not load hohlraum definition for '+hohl_drawing)
            return

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

        # get the model
        model = self.adv_frame.get_rhoR_Analysis()

        result, corr_spec = Analyze_Spectrum(spectrum,
                                  random,
                                  systematic,
                                  angles,
                                  hohl_wall=wall,
                                  name=name,
                                  summary=summary,
                                  plots=self.plot_var.get(),
                                  verbose=self.verbose_var.get(),
                                  rhoR_plots=self.rhoR_plot_var.get(),
                                  OutputDir=OutputDir,
                                  Nxy=Nxy,
                                  ProgressBar=None,
                                  ShowSlide=self.display_results.get(),
                                  model=model)

        # add to DB:
        print(result)
        self.analysis_db.load_results(self.shot, self.dim, self.pos, result)
        self.adv_frame.add_to_db(self.shot, self.dim, self.pos)
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