#!/usr/bin/env python

__author__ = 'Alex Zylstra'
__date__ = '2013-07-30'

import tkinter as tk
import ttk
from GUI.widgets.Table_View import *
from GUI.widgets.WRF_Progress_Dialog import *
from GUI.DB_Info import *
import tkinter.font as tkFont
#import tkinter.tkFont as tkFont

class Application(tk.Tk):
    """docstring for Application"""
    #bigFont = tk.font(family='Arial', size=14, weight='bold')
    bigFont = ("Arial", "14", "bold")
    Font = ("Arial", "12")

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

    def createWidgets(self):
        # database utilities:
        self.label1 = tk.Label(self, text="Database", font=self.bigFont, background='lightgray')
        self.label1.grid(row=0, column=0)
        self.DBInfoButton = tk.Button(self, text="Info", command=self.DB_Info, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.DBInfoButton.grid(row=1, column=0)

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

        # Inventory DB controls:
        self.inventoryInfo = tk.Label(self, text="Inventory DB", font=self.Font, background='lightgray')
        self.inventoryInfo.grid(row=6, column=0)
        self.inventoryViewButton = tk.Button(self, text='View', command=self.viewInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryViewButton.grid(row=6, column=1, sticky=tk.N)
        self.inventoryEditButton = tk.Button(self, text='Edit', command=self.editInventoryDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.inventoryEditButton.grid(row=6, column=2, sticky=tk.N)

        # Setup DB controls:
        self.setupInfo = tk.Label(self, text="Setup DB", font=self.Font, background='lightgray')
        self.setupInfo.grid(row=7, column=0)
        self.setupViewButton = tk.Button(self, text='View', command=self.viewSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupViewButton.grid(row=7, column=1, sticky=tk.N)
        self.setupEditButton = tk.Button(self, text='Edit', command=self.editSetupDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.setupEditButton.grid(row=7, column=2, sticky=tk.N)

        # Analysis DB controls:
        self.analysisInfo = tk.Label(self, text="Analysis DB", font=self.Font, background='lightgray')
        self.analysisInfo.grid(row=8, column=0)
        self.initialAnalysisViewButton = tk.Button(self, text='Initial', command=self.viewInitialAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.initialAnalysisViewButton.grid(row=8, column=1, sticky=tk.N)
        self.finalAnalysisViewButton = tk.Button(self, text='Final', command=self.viewFinalAnalysisDB, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.finalAnalysisViewButton.grid(row=8, column=2, sticky=tk.N)

        ttk_sep_2 = ttk.Separator(self, orient="vertical")
        ttk_sep_2.grid(row=9, column=0, columnspan=3, sticky='ew')

        # options for adding data, etc
        self.label3 = tk.Label(self, text="Utilities", font=self.bigFont, background='lightgray')
        self.label3.grid(row=10, column=0)
        self.addWRFButton = tk.Button(self, text='Add WRF', command=self.addWRF, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addWRFButton.grid(row=11, column=0)
        self.addShotButton = tk.Button(self, text='Add Shot', command=self.addShot, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.addShotButton.grid(row=11, column=1)
        self.csvExportButton = tk.Button(self, text='Export CSV', command=self.exportCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvExportButton.grid(row=12, column=0)
        self.csvImportButton = tk.Button(self, text='Import CSV', command=self.importCSV, font=self.Font, background='lightgray', highlightbackground='lightgray')
        self.csvImportButton.grid(row=12, column=1)

        self.quitButton = tk.Button(self, text='Quit', command=self.quit, font=self.Font, bg='lightgray', highlightbackground='lightgray')
        self.quitButton.grid(row=13, column=0)

    def DB_Info(self):
        t = DB_Info()

    def viewShotDB(self):
        t = Table2(None)

    def editShotDB(self):
        t = 1

    def viewSnoutDB(self):
        asdf = 1

    def editSnoutDB(self):
        asdf = 1

    def viewInventoryDB(self):
        asdf = 1

    def editInventoryDB(self):
        asdf = 1

    def viewSetupDB(self):
        asdf = 1

    def editSetupDB(self):
        asdf = 1

    def viewInitialAnalysisDB(self):
        asdf = 1

    def viewFinalAnalysisDB(self):
        asdf = 1

    def addShot(self):
        asdf = 1

    def addWRF(self):
        import time
        foo = WRF_Progress_Dialog(None)
        foo.progress_bar.start()


    def exportCSV(self):
        asdf = 1

    def importCSV(self):
        asdf = 1

def main():
    #root = Tkinter.Tk()
    #root.wm_title("root")
    #root.wm_iconname("mclist")

    import GUI.widgets.plastik_theme as plastik_theme
    try:
        plastik_theme.install('~/.tile-themes/plastik/plastik')
    except Exception:
        import warnings
        warnings.warn("plastik theme being used without images")

    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()