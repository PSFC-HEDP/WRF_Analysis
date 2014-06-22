#!/usr/bin/env python3

import logging, platform
if platform.system() is 'Darwin':
    import syslog
    syslog.openlog("Python")

# TODO: Improve error handling, logging, and notifications
# TODO: Better detection of shot number by splitting _ vs -
# TODO: Add drop ability to hohlraum import
# TODO: Remember last directory? For various opening/saving modules
# TODO: cr39_2_id not grayed out for -10 setups
# TODO: Should close “Add Shot” thing after spawning setup windows
# TODO: No way to add a shot to the shot DB? “Add Shot” should do this
# TODO: Need to catch bugs while running analysis and display error message
# TODO: Edit ShotDB window has a bug with dropdowns after column is added


__author__ = 'Alex Zylstra'
__date__ = '2014-03-22'
__version__ = '0.1.3'

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.filedialog import asksaveasfilename, askdirectory
    from tkinter.messagebox import askyesnocancel, askyesno
    import threading

    from NIF_WRF.GUI.DB_Info import *
    from NIF_WRF.GUI.ShotDB_Viewer import *
    from NIF_WRF.GUI.ShotDB_Editor import *
    from NIF_WRF.GUI.SQL_Query import *
    from NIF_WRF.GUI.SnoutDB_Viewer import *
    from NIF_WRF.GUI.SnoutDB_Editor import *
    from NIF_WRF.GUI.InventoryDB_Editor import *
    from NIF_WRF.GUI.InventoryDB_Viewer import *
    from NIF_WRF.GUI.SetupDB_Viewer import *
    from NIF_WRF.GUI.SetupDB_Editor import *
    from NIF_WRF.GUI.HohlraumDB_Plot import *
    from NIF_WRF.GUI.HohlraumDB_Import import *
    from NIF_WRF.GUI.InitialAnalysis_Viewer import *
    from NIF_WRF.GUI.FinalAnalysis_Viewer import *
    from NIF_WRF.GUI.WRF_Importer import *
    from NIF_WRF.GUI.AddShot import *
    from NIF_WRF.GUI.Plot_Spectrum import Plot_Spectrum
    from NIF_WRF.GUI.WRF_Analyzer import WRF_Analyzer
    from NIF_WRF.GUI.Plot_RhoR import Plot_RhoR
    from NIF_WRF.GUI.Plot_Yield import Plot_Yield
    from NIF_WRF.GUI.Plot_Shot import Plot_Shot
    from NIF_WRF.GUI.Plot_ShotAsymmetry import Plot_ShotAsymmetry
    from NIF_WRF.GUI.Plot_Asymmetry import Plot_Asymmetry
    from NIF_WRF.GUI.ModelCalculator import ModelCalculator
    from NIF_WRF.GUI.ModelPlotter import ModelPlotter
    from NIF_WRF.GUI.Bump_Editor import Bump_Editor
    from NIF_WRF.util.scripts import *
    from NIF_WRF.GUI.widgets import Option_Prompt
    from NIF_WRF.util.rerun import rerun_all

except Exception as inst:
    if platform.system() is 'Darwin':
        syslog.syslog(syslog.LOG_ALERT, 'Python error: '+str(inst))
    from tkinter.messagebox import showerror
    showerror("Error!", "Problem loading python modules" + "\n" + str(inst))
    import sys
    sys.exit(1)

class Application(tk.Tk):
    """Analysis and database application for the NIF WRF data"""
    # Some theming:
    bigFont = ("Arial", "14", "bold")
    Font = ("Arial", "12")

    windows = []  # created windows

    def __init__(self):
        super(Application, self).__init__(None)
        
        self.configure(background='#eeeeee')
        self.grid()
        self.createWidgets()
        self.__configureMatplotlib__()
        self.minsize(150,200)
        self.title('NIF WRF')

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 2, weight=1)

        # a couple key bindings:
        self.bind('<Escape>', self.quit)
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def createWidgets(self):
        row = 0

        # database utilities:
        self.label1 = ttk.Label(self, text="Database", font=self.bigFont)
        self.label1.grid(row=row, column=0)
        row += 1
        self.DBInfoButton = ttk.Button(self, text="Info", command=self.DB_Info)
        self.DBInfoButton.grid(row=row, column=0)
        self.SQLCommandButton = ttk.Button(self, text="SQL", command=self.SQL_Query)
        self.SQLCommandButton.grid(row=row, column=1)
        row += 1

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # options to launch various databases:
        self.label2 = ttk.Label(self, text="View Data", font=self.bigFont)
        self.label2.grid(row=row, column=0)
        row += 1

        # Shot DB controls:
        self.shotInfo = ttk.Label(self, text="Shot DB", font=self.Font)
        self.shotInfo.grid(row=row, column=0)
        self.shotViewButton = ttk.Button(self, text='View', command=self.viewShotDB)
        self.shotViewButton.grid(row=row, column=1, sticky=tk.N)
        self.shotEditButton = ttk.Button(self, text='Edit', command=self.editShotDB)
        self.shotEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Snout DB controls:
        self.snoutInfo = ttk.Label(self, text="Snout DB", font=self.Font)
        self.snoutInfo.grid(row=row, column=0)
        self.snoutViewButton = ttk.Button(self, text='View', command=self.viewSnoutDB)
        self.snoutViewButton.grid(row=row, column=1, sticky=tk.N)
        self.snoutEditButton = ttk.Button(self, text='Edit', command=self.editSnoutDB)
        self.snoutEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Hohlraum DB controls
        self.hohlraum_info = ttk.Label(self, text="Hohlraum DB", font=self.Font)
        self.hohlraum_info.grid(row=row, column=0)
        self.hohlraum_plot_button = ttk.Button(self, text='Plot', command=self.plotHohlraum)
        self.hohlraum_plot_button.grid(row=row, column=1, sticky=tk.N)
        self.hohlraum_import_button = ttk.Button(self, text='Import', command=self.importHohlraum)
        self.hohlraum_import_button.grid(row=row, column=2, sticky=tk.N)
        row += 1
        self.hohlraum_bump_button = ttk.Button(self, text="Bump", command=self.bumpControl)
        self.hohlraum_bump_button.grid(row=row, column=1, sticky=tk.N)
        row += 1

        # Inventory DB controls:
        self.inventoryInfo = ttk.Label(self, text="Inventory DB", font=self.Font)
        self.inventoryInfo.grid(row=row, column=0)
        self.inventoryViewButton = ttk.Button(self, text='View', command=self.viewInventoryDB)
        self.inventoryViewButton.grid(row=row, column=1, sticky=tk.N)
        self.inventoryEditButton = ttk.Button(self, text='Edit', command=self.editInventoryDB)
        self.inventoryEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Setup DB controls:
        self.setupInfo = ttk.Label(self, text="Setup DB", font=self.Font)
        self.setupInfo.grid(row=row, column=0)
        self.setupViewButton = ttk.Button(self, text='View', command=self.viewSetupDB)
        self.setupViewButton.grid(row=row, column=1, sticky=tk.N)
        self.setupEditButton = ttk.Button(self, text='Edit', command=self.editSetupDB)
        self.setupEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Analysis DB controls:
        self.analysisInfo = ttk.Label(self, text="Analysis DB", font=self.Font)
        self.analysisInfo.grid(row=row, column=0)
        self.initialAnalysisViewButton = ttk.Button(self, text='Initial', command=self.viewInitialAnalysisDB)
        self.initialAnalysisViewButton.grid(row=row, column=1, sticky=tk.N)
        self.finalAnalysisViewButton = ttk.Button(self, text='Final', command=self.viewFinalAnalysisDB)
        self.finalAnalysisViewButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # For making plots of various stuff:
        self.plotInfo = ttk.Label(self, text='Plots', font=self.bigFont)
        self.plotInfo.grid(row=row, column=0)
        self.spectrumPlotButton = ttk.Button(self, text='Spectra', command=self.plotSpectrum)
        self.spectrumPlotButton.grid(row=row, column=1)
        self.shotPlotButton = ttk.Button(self, text='Shot', command=self.plotShot)
        self.shotPlotButton.grid(row=row, column=2)
        row += 1

        self.rhoRPlotButton = ttk.Button(self, text='ρR', command=self.plotRhoR)
        self.rhoRPlotButton.grid(row=row, column=1)
        self.YieldPlotButton = ttk.Button(self, text='Yield', command=self.plotYield)
        self.YieldPlotButton.grid(row=row, column=2)
        row += 1

        self.plotInfo = ttk.Label(self, text='Asymmetries', font=self.Font)
        self.plotInfo.grid(row=row, column=0)
        self.shotAsymmetryButton = ttk.Button(self, text='Shot', command=self.plotShotAsymmetry)
        self.shotAsymmetryButton.grid(row=row, column=1)
        self.asymmetryButton = ttk.Button(self, text='All', command=self.plotAsymmetry)
        self.asymmetryButton.grid(row=row, column=2)
        row += 1

        ttk_sep_4 = ttk.Separator(self, orient="vertical")
        ttk_sep_4.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # options for adding data, etc
        self.label3 = ttk.Label(self, text="Utilities", font=self.bigFont)
        self.label3.grid(row=row, column=0)
        row += 1

        self.addAnalysisButton = ttk.Button(self, text='Analyze', command=self.Analyze)
        self.addAnalysisButton.grid(row=row, column=0)
        self.addWRFButton = ttk.Button(self, text='Add WRF', command=self.addWRF)
        self.addWRFButton.grid(row=row, column=1)
        self.addShotButton = ttk.Button(self, text='Add Shot', command=self.addShot)
        self.addShotButton.grid(row=row, column=2)
        row += 1

        self.rerunAnalysisButton = ttk.Button(self, text='Rerun Analysis', command=self.rerunAnalysis)
        self.rerunAnalysisButton.grid(row=row, column=0, columnspan=2)
        row += 1

        self.label3a = ttk.Label(self, text='Summary CSVs', font=self.Font)
        self.label3a.grid(row=row, column=0)
        row += 1

        self.shotDimSummaryButton = ttk.Button(self, text='Shot/DIM', command=self.shotDimSummary)
        self.shotDimSummaryButton.grid(row=row, column=0, sticky='NS')
        self.allShotDimSummaryButton = ttk.Button(self, text='All Shot/DIM', command=self.allShotDimSummary)
        self.allShotDimSummaryButton.grid(row=row, column=1)
        self.summaryCSVButton = ttk.Button(self, text='Summary', command=self.summaryCSV)
        self.summaryCSVButton.grid(row=row, column=2)
        row += 1

        self.csvExportButton = ttk.Button(self, text='Export DB', command=self.exportCSV)
        self.csvExportButton.grid(row=row, column=0)
        self.csvImportButton = ttk.Button(self, text='Import DB', command=self.importCSV)
        self.csvImportButton.grid(row=row, column=1)
        row += 1

        self.label4 = ttk.Label(self, text='ρR Model', font=self.Font)
        self.label4.grid(row=row, column=0)
        self.modelCalculatorButton = ttk.Button(self, text='Calculator', command=self.modelCalculator)
        self.modelCalculatorButton.grid(row=row, column=1)
        self.modelPlotterButton = ttk.Button(self, text='Plotter', command=self.modelPlotter)
        self.modelPlotterButton.grid(row=row, column=2)
        row += 1

        ttk_sep_3 = ttk.Separator(self, orient="vertical")
        ttk_sep_3.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        self.style = ttk.Style()
        themes = self.style.theme_names()
        self.style_var = tk.StringVar()
        self.style_menu = ttk.OptionMenu(self, self.style_var, themes[0], *themes)
        self.style_var.trace_variable('w', self.update_style)
        self.style_menu.grid(row=row, column=0, columnspan=3, sticky='NS')
        row += 1

        self.quitButton = ttk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=row, column=0, columnspan=3, sticky='S')
        row += 1

    def DB_Info(self):
        DB_Info()

    def SQL_Query(self):
        result = askyesno('Do manual SQL?', 'Are you sure you want to do that?', parent=self)
        if result:
            SQL_Query()

    def viewShotDB(self):
        ShotDB_Viewer()

    def editShotDB(self):
        ShotDB_Editor()

    def viewSnoutDB(self):
        SnoutDB_Viewer()

    def editSnoutDB(self):
        SnoutDB_Editor()

    def plotHohlraum(self):
        HohlraumDB_Plot()

    def importHohlraum(self):
        HohlraumDB_Import()

    def bumpControl(self):
        Bump_Editor()

    def viewInventoryDB(self):
        InventoryDB_Viewer()

    def editInventoryDB(self):
        InventoryDB_Editor()

    def viewSetupDB(self):
        SetupDB_Viewer()

    def editSetupDB(self):
        SetupDB_Editor()

    def viewInitialAnalysisDB(self):
        InitAnalysis_Viewer()

    def viewFinalAnalysisDB(self):
        FinalAnalysis_Viewer()

    def Analyze(self):
        WRF_Analyzer()

    def addShot(self):
        AddShot()

    def addWRF(self):
        WRF_Importer()

    def rerunAnalysis(self):
        from tkinter.messagebox import askyesnocancel
        dialog = askyesnocancel('Rerun all analysis?', 'Are you sure? It will take a long time')
        if dialog == True:
            thread = threading.Thread(target=rerun_all)
            thread.start()

    def plotSpectrum(self):
        #thread = threading.Thread(group=None, target=Plot_Spectrum)
        #thread.start()
        Plot_Spectrum()

    def plotShot(self):
        Plot_Shot()

    def plotRhoR(self):
        thread = threading.Thread(group=None, target=Plot_RhoR)
        thread.start()

    def plotYield(self):
        Plot_Yield()

    def plotShotAsymmetry(self):
        Plot_ShotAsymmetry()

    def plotAsymmetry(self):
        Plot_Asymmetry()

    def exportCSV(self):
        """Save the database information to CSV files."""
        # get a new file:
        FILEOPENOPTIONS = dict(title='Export CSV to',
                       initialdir=Database.DIR,
                       mustexist=False)
        save_dir = askdirectory(**FILEOPENOPTIONS)

        # check to see if the user cancelled:
        if save_dir == '':
            return

        # check to see if it exists, create it otherwise:
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        # call the export script:
        from NIF_WRF.DB.scripts import export_all
        export_all(export_dir=save_dir)

        # show a notification that the export is complete:
        from tkinter.messagebox import showinfo
        showinfo(message='Export to CSV complete')

    def importCSV(self):
        """Import the database information from CSV files."""
        # get an existing directory
        FILEOPENOPTIONS = dict(title='Import CSV from',
                       initialdir=Database.DIR,
                       mustexist=True)
        open_dir = askdirectory(**FILEOPENOPTIONS)

        # check to see if the user cancelled:
        if open_dir == '':
            return

        # call the import script:
        from NIF_WRF.DB.scripts import import_all
        import_all(import_dir=open_dir)

        # show a notification that the import is complete:
        from tkinter.messagebox import showinfo
        showinfo(message='Import from CSV complete')

    def shotDimSummary(self, shot=None, DIM=None):
        # get shot and DIM:
        db = WRF_Analysis_DB()

        # if no shot was supplied, prompt for one:
        if shot is None:
            shots = db.get_shots()

            # sanity check for edge case where no shots are available:
            if len(shots) == 0:
                from tkinter.messagebox import showerror
                showerror('Error', message='No WRF data available, import some', parent=self)
                self.__cancel__()
                return

            dialog = Option_Prompt.Option_Prompt(self, title='Select shot', text='Shot numbers available', options=shots, width=20)
            shot = dialog.result

            # if the user canceled:
            if shot is None:
                return

        # if no DIM was supplied, prompt for one:
        if DIM is None:
            dims = db.get_dims(shot)
            dialog = Option_Prompt.Option_Prompt(self, title='Select DIM', text='DIMs available for '+shot, options=dims)
            DIM = dialog.result

            # if the user canceled:
            if DIM is None:
                return

        OPTIONS = dict(title='Save ' + shot + '/' + DIM + ' summary to',
                       defaultextension='.csv',
                       filetypes=[('Comma-Separated Values','.csv')],
                       initialdir=Database.DIR)
        open_fname = asksaveasfilename(**OPTIONS)

        if open_fname is '':
            return

        generate_shot_dim_summary(shot, DIM, fname=open_fname)


    def allShotDimSummary(self):
        """Save all shot/dim summary CSVs to a directory"""
        # get an existing directory
        FILEOPENOPTIONS = dict(title='Save all Shot/DIM CSVs to directory',
                       initialdir=Database.DIR,
                       mustexist=False)
        open_dir = askdirectory(**FILEOPENOPTIONS)

        # check to see if the user cancelled:
        if open_dir == '':
            return

        # ask if the user wants to split output into shot directories
        dialog = askyesnocancel('', 'Split output into shot directories?')
        if dialog is None:
            return

        all_shot_dim_summary(open_dir, use_shot_dirs=dialog)

    def summaryCSV(self):
        """Write a single summary CSV for all shots"""
        OPTIONS = dict(title='Save summary CSV as',
                       defaultextension='.csv',
                       filetypes=[('Comma-Separated Values','.csv')],
                       initialdir=Database.DIR)
        open_fname = asksaveasfilename(**OPTIONS)

        if open_fname is '':
            return

        generate_allshot_summary(fname=open_fname)

    def update_style(self, *args):
        """Update the displayed style"""
        self.style.theme_use(self.style_var.get())

    def modelCalculator(self, *args):
        """Display a simple calculator widget for the rhoR model."""
        ModelCalculator(self)

    def modelPlotter(self, *args):
        """Display a simple plot widget for the rhoR model."""
        ModelPlotter(self)

    def __configureMatplotlib__(self):
        import matplotlib, matplotlib.pyplot
        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')
        #matplotlib.pyplot.rc('font', **{'size':'8'})
        #matplotlib.pyplot.rc('text', **{'usetex':False})

def main():
    # import NIF_WRF.GUI.widgets.plastik_theme as plastik_theme
    # try:
    #     plastik_theme.install(os.path.expanduser('~/.tile-themes/plastik/plastik/'))
    # except Exception:
    #     logging.warning('plastik theme being used without images')

    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()