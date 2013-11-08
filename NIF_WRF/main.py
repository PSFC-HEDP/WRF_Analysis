#!/usr/bin/env python3

import logging, syslog
syslog.openlog("Python")

# TODO: Improve error handling, logging, and notifications
# TODO: Better detection of shot number by splitting _ vs -
# TODO: Add drop ability to hohlraum import
# TODO: Remember last directory? For various opening/saving modules

__author__ = 'Alex Zylstra'
__date__ = '2013-11-08'
__version__ = '0.1.2'

try:
    import tkinter as tk
    import ttk
    from tkinter.filedialog import asksaveasfilename, askdirectory
    from tkinter.messagebox import askyesnocancel, askyesno

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
    from NIF_WRF.util.scripts import *
    from NIF_WRF.GUI.widgets import Option_Prompt
except Exception as inst:
    syslog.syslog(syslog.LOG_ALERT, 'Python error: '+str(inst))
    from tkinter.messagebox import showerror
    showerror("Error!", "Problem loading python modules")

class Application(tk.Tk):
    """Analysis and database application for the NIF WRF data"""
    bigFont = ("Arial", "14", "bold")
    Font = ("Arial", "12")

    windows = []  # created windows

    def __init__(self):
        super(Application, self).__init__(None)
        
        self.configure(background='lightgray')
        self.grid()
        self.createWidgets()
        self.minsize(150,200)
        self.title('NIF WRF')

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 2, weight=1)

        # add a key binding to close:
        self.bind('<Escape>', self.quit)

    def createWidgets(self):
        row = 0

        # database utilities:
        self.label1 = tk.Label(self, text="Database", font=self.bigFont, background='lightgray')
        self.label1.grid(row=row, column=0)
        row += 1
        self.DBInfoButton = tk.Button(self, text="Info", command=self.DB_Info, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.DBInfoButton.grid(row=row, column=0)
        self.SQLCommandButton = tk.Button(self, text="SQL", command=self.SQL_Query, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.SQLCommandButton.grid(row=row, column=1)
        row += 1

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # options to launch various databases:
        self.label2 = tk.Label(self, text="View Data", font=self.bigFont, background='lightgray')
        self.label2.grid(row=row, column=0)
        row += 1

        # Shot DB controls:
        self.shotInfo = tk.Label(self, text="Shot DB", font=self.Font, background='lightgray')
        self.shotInfo.grid(row=row, column=0)
        self.shotViewButton = tk.Button(self, text='View', command=self.viewShotDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotViewButton.grid(row=row, column=1, sticky=tk.N)
        self.shotEditButton = tk.Button(self, text='Edit', command=self.editShotDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Snout DB controls:
        self.snoutInfo = tk.Label(self, text="Snout DB", font=self.Font, background='lightgray')
        self.snoutInfo.grid(row=row, column=0)
        self.snoutViewButton = tk.Button(self, text='View', command=self.viewSnoutDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.snoutViewButton.grid(row=row, column=1, sticky=tk.N)
        self.snoutEditButton = tk.Button(self, text='Edit', command=self.editSnoutDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.snoutEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Hohlraum DB controls
        self.hohlraum_info = tk.Label(self, text="Hohlraum DB", font=self.Font, bg='lightgray')
        self.hohlraum_info.grid(row=row, column=0)
        self.hohlraum_plot_button = tk.Button(self, text='Plot', command=self.plotHohlraum, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.hohlraum_plot_button.grid(row=row, column=1, sticky=tk.N)
        self.hohlraum_import_button = tk.Button(self, text='Import', command=self.importHohlraum, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.hohlraum_import_button.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Inventory DB controls:
        self.inventoryInfo = tk.Label(self, text="Inventory DB", font=self.Font, background='lightgray')
        self.inventoryInfo.grid(row=row, column=0)
        self.inventoryViewButton = tk.Button(self, text='View', command=self.viewInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryViewButton.grid(row=row, column=1, sticky=tk.N)
        self.inventoryEditButton = tk.Button(self, text='Edit', command=self.editInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Setup DB controls:
        self.setupInfo = tk.Label(self, text="Setup DB", font=self.Font, background='lightgray')
        self.setupInfo.grid(row=row, column=0)
        self.setupViewButton = tk.Button(self, text='View', command=self.viewSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupViewButton.grid(row=row, column=1, sticky=tk.N)
        self.setupEditButton = tk.Button(self, text='Edit', command=self.editSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupEditButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        # Analysis DB controls:
        self.analysisInfo = tk.Label(self, text="Analysis DB", font=self.Font, background='lightgray')
        self.analysisInfo.grid(row=row, column=0)
        self.initialAnalysisViewButton = tk.Button(self, text='Initial', command=self.viewInitialAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.initialAnalysisViewButton.grid(row=row, column=1, sticky=tk.N)
        self.finalAnalysisViewButton = tk.Button(self, text='Final', command=self.viewFinalAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.finalAnalysisViewButton.grid(row=row, column=2, sticky=tk.N)
        row += 1

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # For making plots of various stuff:
        self.plotInfo = tk.Label(self, text='Plots', font=self.bigFont, background='lightgray')
        self.plotInfo.grid(row=row, column=0)
        self.spectrumPlotButton = tk.Button(self, text='Spectra', command=self.plotSpectrum, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.spectrumPlotButton.grid(row=row, column=1)
        self.shotPlotButton = tk.Button(self, text='Shot', command=self.plotShot, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotPlotButton.grid(row=row, column=2)
        row += 1

        self.rhoRPlotButton = tk.Button(self, text='ρR', command=self.plotRhoR, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.rhoRPlotButton.grid(row=row, column=1)
        self.YieldPlotButton = tk.Button(self, text='Yield', command=self.plotYield, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.YieldPlotButton.grid(row=row, column=2)
        row += 1

        self.plotInfo = tk.Label(self, text='Asymmetries', font=self.Font, background='lightgray')
        self.plotInfo.grid(row=row, column=0)
        self.shotAsymmetryButton = tk.Button(self, text='Shot', command=self.plotShotAsymmetry, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotAsymmetryButton.grid(row=row, column=1)
        self.asymmetryButton = tk.Button(self, text='All', command=self.plotAsymmetry, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.asymmetryButton.grid(row=row, column=2)
        row += 1

        ttk_sep_4 = ttk.Separator(self, orient="vertical")
        ttk_sep_4.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # options for adding data, etc
        self.label3 = tk.Label(self, text="Utilities", font=self.bigFont, background='lightgray')
        self.label3.grid(row=row, column=0)
        row += 1

        self.addAnalysisButton = tk.Button(self, text='Analyze', command=self.Analyze, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addAnalysisButton.grid(row=row, column=0)
        self.addWRFButton = tk.Button(self, text='Add WRF', command=self.addWRF, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addWRFButton.grid(row=row, column=1)
        self.addShotButton = tk.Button(self, text='Add Shot', command=self.addShot, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addShotButton.grid(row=row, column=2)
        row += 1

        self.label3a = tk.Label(self, text='Summary CSVs', font=self.Font, background='lightgray')
        self.label3a.grid(row=row, column=0)
        row += 1

        self.shotDimSummaryButton = tk.Button(self, text='Shot/DIM', command=self.shotDimSummary, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotDimSummaryButton.grid(row=row, column=0, sticky='NS')
        self.allShotDimSummaryButton = tk.Button(self, text='All Shot/DIM', command=self.allShotDimSummary, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.allShotDimSummaryButton.grid(row=row, column=1)
        self.summaryCSVButton = tk.Button(self, text='Summary', command=self.summaryCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.summaryCSVButton.grid(row=row, column=2)
        row += 1

        self.csvExportButton = tk.Button(self, text='Export DB', command=self.exportCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvExportButton.grid(row=row, column=0)
        self.csvImportButton = tk.Button(self, text='Import DB', command=self.importCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvImportButton.grid(row=row, column=1)
        row += 1

        ttk_sep_3 = ttk.Separator(self, orient="vertical")
        ttk_sep_3.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        self.quitButton = tk.Button(self, text='Quit', command=self.quit, font=self.Font, bg='lightgray', highlightbackground='lightgray')
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

    def plotSpectrum(self):
        Plot_Spectrum()

    def plotShot(self):
        Plot_Shot()

    def plotRhoR(self):
        Plot_RhoR()

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

            dialog = Option_Prompt(self, title='Select shot', text='Shot numbers available', options=shots, width=20)
            shot = dialog.result

            # if the user canceled:
            if shot is None:
                return

        # if no DIM was supplied, prompt for one:
        if DIM is None:
            dims = db.get_dims(shot)
            dialog = Option_Prompt(self, title='Select DIM', text='DIMs available for '+shot, options=dims)
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

def main():
    import NIF_WRF.GUI.widgets.plastik_theme as plastik_theme
    try:
        plastik_theme.install(os.path.expanduser('~/.tile-themes/plastik/plastik/'))
    except Exception:
        logging.warning('plastik theme being used without images')

    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()