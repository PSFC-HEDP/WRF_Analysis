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
# TODO: update WRF adding so that it's more robust to strings enerted for dim and position (i.e. have some entries)
# TODO: Add shot dialog (for ShotDB)
# TODO: Fix backgrounds on Add a WRF shot dialog
# TODO: Close WRF 'Add Shot' dialog after submit
# TODO: Close add WRF dialog after submit, get rip of popup
# TODO: Adding WRF data with user-specified thickness should add corr spectra to DB
# TODO: Spectra plot window needs check/error handle for corrected spectra (if they don't exist)

__author__ = 'Alex Zylstra'
__date__ = '2015-06-24'
__version__ = '0.1'

#try:
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import asksaveasfilename, askdirectory
from tkinter.messagebox import askyesnocancel, askyesno
import threading

# from WRF_Analysis.GUI.WRF_Importer import *
# from WRF_Analysis.GUI.Plot_Spectrum import Plot_Spectrum
# from WRF_Analysis.GUI.WRF_Analyzer import WRF_Analyzer
from WRF_Analysis.GUI.ModelCalculator import ModelCalculator
from WRF_Analysis.GUI.ModelPlotter import ModelPlotter
# from WRF_Analysis.util.scripts import *
# from WRF_Analysis.GUI.widgets import Option_Prompt
#
# except Exception as inst:
#     if platform.system() is 'Darwin':
#         syslog.syslog(syslog.LOG_ALERT, 'Python error: '+str(inst))
#     from tkinter.messagebox import showerror
#     showerror("Error!", "Problem loading python modules" + "\n" + str(inst))
#     import sys
#     sys.exit(1)

class Application(tk.Tk):
    """Analysis and database application for the NIF WRF data"""
    # Some theming:
    bigFont = ("Arial", "14", "bold")
    Font = ("Arial", "12")

    windows = []  # created windows

    def __init__(self):
        super(Application, self).__init__(None)

        from tkinter.ttk import Style
        Style().configure('bg', background='#eeeeee')

        self.configure(background='#eeeeee')
        #self.configure(style='bg')
        self.grid()
        self.createWidgets()
        self.__configureMatplotlib__()
        self.minsize(150,200)
        self.title('WRF Analysis')

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 2, weight=1)

        # a couple key bindings:
        self.bind('<Escape>', self.quit)
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def createWidgets(self):
        row = 0

        # For making plots of various stuff:
        self.plotInfo = ttk.Label(self, text='Analysis', font=self.bigFont)
        self.plotInfo.grid(row=row, column=0)
        row += 1
        self.spectrumPlotButton = ttk.Button(self, text='Plot Spectrum', command=self.plotSpectrum)
        self.spectrumPlotButton.grid(row=row, column=0)
        row += 1

        #TODO: IMPLEMENT SPECTRUM ANALYSIS
        self.analyzeSpectrumButton = ttk.Button(self, text='Analyze Spectrum')
        self.analyzeSpectrumButton.grid(row=row, column=0)
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

    def Analyze(self):
        # WRF_Analyzer()
        pass

    def addWRF(self):
        # WRF_Importer()
        pass

    def plotSpectrum(self):
        #thread = threading.Thread(group=None, target=Plot_Spectrum)
        #thread.start()
        # Plot_Spectrum()
        pass

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