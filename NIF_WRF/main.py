#!/usr/bin/env python3

import logging
logging.warning('foo')

# TODO: Improve error handling, logging, and notifications
# TODO: Better detection of shot number by splitting _ vs -
# TODO: Add drop ability to hohlraum import
# TODO: Remember last directory? For various opening/saving modules

__author__ = 'Alex Zylstra'
__date__ = '2013-10-30'
__version__ = '0.1.1'

import tkinter as tk
import ttk
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
        # database utilities:
        self.label1 = tk.Label(self, text="Database", font=self.bigFont, background='lightgray')
        self.label1.grid(row=0, column=0)
        self.DBInfoButton = tk.Button(self, text="Info", command=self.DB_Info, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.DBInfoButton.grid(row=1, column=0)
        self.SQLCommandButton = tk.Button(self, text="SQL", command=self.SQL_Query, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.SQLCommandButton.grid(row=1, column=1)

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=2, column=0, columnspan=3, sticky='ew')

        # options to launch various databases:
        self.label2 = tk.Label(self, text="View Data", font=self.bigFont, background='lightgray')
        self.label2.grid(row=3, column=0)

        # Shot DB controls:
        self.shotInfo = tk.Label(self, text="Shot DB", font=self.Font, background='lightgray')
        self.shotInfo.grid(row=4, column=0)
        self.shotViewButton = tk.Button(self, text='View', command=self.viewShotDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotViewButton.grid(row=4, column=1, sticky=tk.N)
        self.shotEditButton = tk.Button(self, text='Edit', command=self.editShotDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotEditButton.grid(row=4, column=2, sticky=tk.N)

        # Snout DB controls:
        self.snoutInfo = tk.Label(self, text="Snout DB", font=self.Font, background='lightgray')
        self.snoutInfo.grid(row=5, column=0)
        self.snoutViewButton = tk.Button(self, text='View', command=self.viewSnoutDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.snoutViewButton.grid(row=5, column=1, sticky=tk.N)
        self.snoutEditButton = tk.Button(self, text='Edit', command=self.editSnoutDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.snoutEditButton.grid(row=5, column=2, sticky=tk.N)

        # Hohlraum DB controls
        self.hohlraum_info = tk.Label(self, text="Hohlraum DB", font=self.Font, bg='lightgray')
        self.hohlraum_info.grid(row=6, column=0)
        self.hohlraum_plot_button = tk.Button(self, text='Plot', command=self.plotHohlraum, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.hohlraum_plot_button.grid(row=6, column=1, sticky=tk.N)
        self.hohlraum_import_button = tk.Button(self, text='Import', command=self.importHohlraum, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.hohlraum_import_button.grid(row=6, column=2, sticky=tk.N)

        # Inventory DB controls:
        self.inventoryInfo = tk.Label(self, text="Inventory DB", font=self.Font, background='lightgray')
        self.inventoryInfo.grid(row=7, column=0)
        self.inventoryViewButton = tk.Button(self, text='View', command=self.viewInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryViewButton.grid(row=7, column=1, sticky=tk.N)
        self.inventoryEditButton = tk.Button(self, text='Edit', command=self.editInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryEditButton.grid(row=7, column=2, sticky=tk.N)

        # Setup DB controls:
        self.setupInfo = tk.Label(self, text="Setup DB", font=self.Font, background='lightgray')
        self.setupInfo.grid(row=8, column=0)
        self.setupViewButton = tk.Button(self, text='View', command=self.viewSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupViewButton.grid(row=8, column=1, sticky=tk.N)
        self.setupEditButton = tk.Button(self, text='Edit', command=self.editSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupEditButton.grid(row=8, column=2, sticky=tk.N)

        # Analysis DB controls:
        self.analysisInfo = tk.Label(self, text="Analysis DB", font=self.Font, background='lightgray')
        self.analysisInfo.grid(row=9, column=0)
        self.initialAnalysisViewButton = tk.Button(self, text='Initial', command=self.viewInitialAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.initialAnalysisViewButton.grid(row=9, column=1, sticky=tk.N)
        self.finalAnalysisViewButton = tk.Button(self, text='Final', command=self.viewFinalAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.finalAnalysisViewButton.grid(row=9, column=2, sticky=tk.N)

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=10, column=0, columnspan=3, sticky='ew')

        # options for adding data, etc
        self.label3 = tk.Label(self, text="Utilities", font=self.bigFont, background='lightgray')
        self.label3.grid(row=11, column=0)
        self.addAnalysisButton = tk.Button(self, text='Analyze', command=self.Analyze, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addAnalysisButton.grid(row=12, column=0)
        self.addWRFButton = tk.Button(self, text='Add WRF', command=self.addWRF, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addWRFButton.grid(row=12, column=1)
        self.addShotButton = tk.Button(self, text='Add Shot', command=self.addShot, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addShotButton.grid(row=12, column=2)
        self.csvExportButton = tk.Button(self, text='Export CSV', command=self.exportCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvExportButton.grid(row=13, column=0)
        self.csvImportButton = tk.Button(self, text='Import CSV', command=self.importCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvImportButton.grid(row=13, column=1)

        ttk_sep_3 = ttk.Separator(self, orient="vertical")
        ttk_sep_3.grid(row=14, column=0, columnspan=3, sticky='ew')

        # For making plots of various stuff:
        self.plotInfo = tk.Label(self, text='Plots', font=self.bigFont, background='lightgray')
        self.plotInfo.grid(row=15, column=0)

        self.spectrumPlotButton = tk.Button(self, text='Spectra', command=self.plotSpectrum, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.spectrumPlotButton.grid(row=15, column=1)

        self.shotPlotButton = tk.Button(self, text='Shot', command=self.plotShot, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotPlotButton.grid(row=15, column=2)

        self.rhoRPlotButton = tk.Button(self, text='ρR', command=self.plotRhoR, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.rhoRPlotButton.grid(row=16, column=1)
        self.YieldPlotButton = tk.Button(self, text='Yield', command=self.plotYield, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.YieldPlotButton.grid(row=16, column=2)

        self.plotInfo = tk.Label(self, text='Asymmetries', font=self.Font, background='lightgray')
        self.plotInfo.grid(row=17, column=0)
        self.shotAsymmetryButton = tk.Button(self, text='Shot', command=self.plotShotAsymmetry, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.shotAsymmetryButton.grid(row=17, column=1)
        self.asymmetryButton = tk.Button(self, text='All', command=self.plotAsymmetry, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.asymmetryButton.grid(row=17, column=2)

        ttk_sep_4 = ttk.Separator(self, orient="vertical")
        ttk_sep_4.grid(row=18, column=0, columnspan=3, sticky='ew')

        self.quitButton = tk.Button(self, text='Quit', command=self.quit, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.quitButton.grid(row=19, column=0, columnspan=3, sticky='S')

    def DB_Info(self):
        DB_Info()

    def SQL_Query(self):
        from tkinter.messagebox import askyesno
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
        #foo = WRF_Progress_Dialog(None)
        #foo.progress_bar.start()

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
        from tkinter.filedialog import askdirectory
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
        from tkinter.filedialog import askdirectory
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

def main():
    #root = Tkinter.Tk()
    #root.wm_title("root")
    #root.wm_iconname("mclist")

    import NIF_WRF.GUI.widgets.plastik_theme as plastik_theme
    try:
        plastik_theme.install('~/.tile-themes/plastik/plastik')
    except Exception:
        import warnings
        warnings.warn("plastik theme being used without images")

    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()