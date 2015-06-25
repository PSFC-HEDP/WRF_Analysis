#!/usr/bin/env python3

import logging, platform
if platform.system() is 'Darwin':
    import syslog
    syslog.openlog("Python")

# TODO: Better detection of shot number by splitting _ vs -
# TODO: Need to catch bugs while running analysis and display error message
# TODO: Don't auto-run model calculator and plotter

__author__ = 'Alex Zylstra'
__date__ = '2015-06-24'
__version__ = '0.1'

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.filedialog import asksaveasfilename, askdirectory
    from tkinter.messagebox import askyesnocancel, askyesno
    import threading
    import matplotlib
    matplotlib.use('tkagg')

    from WRF_Analysis.GUI.WRF_Importer import *
    from WRF_Analysis.GUI.Plot_Spectrum import Plot_Spectrum
    from WRF_Analysis.GUI.ModelCalculator import ModelCalculator
    from WRF_Analysis.GUI.ModelPlotter import ModelPlotter
    from WRF_Analysis.GUI.widgets import Option_Prompt
    from WRF_Analysis.GUI.HohlraumUI import HohlraumUI

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

        # Some instance variables:
        self.plotSpectrum_last_dir = None

    def createWidgets(self):
        row = 0

        self.infoLabel = ttk.Label(self, text="WRF Analysis Utility")
        self.infoLabel.grid(row=row, column=0, columnspan=3)
        row += 1
        self.authLabel = ttk.Label(self, text="Alex Zylstra")
        self.authLabel.grid(row=row, column=0, columnspan=3)
        row += 1
        self.dateLabel = ttk.Label(self, text="2015-06-24")
        self.dateLabel.grid(row=row, column=0, columnspan=3)
        row += 1

        ttk_sep_1 = ttk.Separator(self, orient="vertical")
        ttk_sep_1.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # For making plots of various stuff:
        self.plotInfo = ttk.Label(self, text='Analysis', font=self.bigFont)
        self.plotInfo.grid(row=row, column=0)
        row += 1

        self.label1 = ttk.Label(self, text="Spectrum:")
        self.label1.grid(row=row, column=0)
        self.spectrumPlotButton = ttk.Button(self, text='Plot', command=self.plotSpectrum)
        self.spectrumPlotButton.grid(row=row, column=1)
        self.analyzeSpectrumButton = ttk.Button(self, text='Analyze', command=self.Analyze)
        self.analyzeSpectrumButton.grid(row=row, column=2)
        row += 1

        self.label2 = ttk.Label(self, text='Asymmetries:')
        self.label2.grid(row=row, column=0)
        self.asymPlotButton = ttk.Button(self, text='Plot', command=self.plotAsymmetry)
        self.asymPlotButton.grid(row=row, column=1)
        self.asymFitButton = ttk.Button(self, text='Fit', command=self.fitAsymmetry)
        self.asymFitButton.grid(row=row, column=2)
        row += 1

        self.label3 = ttk.Label(self, text='Hohlraum:')
        self.label3.grid(row=row, column=0)
        self.hohlraumButton = ttk.Button(self, text='Correct Spectrum', command=self.hohlCorr)
        self.hohlraumButton.grid(row=row, column=1, columnspan=2)
        row += 1

        ttk_sep_4 = ttk.Separator(self, orient="vertical")
        ttk_sep_4.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        # options for adding data, etc
        self.label3 = ttk.Label(self, text="ρR Model", font=self.bigFont)
        self.label3.grid(row=row, column=0)
        self.modelCalculatorButton = ttk.Button(self, text='Calculator', command=self.modelCalculator)
        self.modelCalculatorButton.grid(row=row, column=1)
        self.modelPlotterButton = ttk.Button(self, text='Plotter', command=self.modelPlotter)
        self.modelPlotterButton.grid(row=row, column=2)
        row += 1

        ttk_sep_3 = ttk.Separator(self, orient="vertical")
        ttk_sep_3.grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1

        self.quitButton = ttk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=row, column=0, columnspan=3, sticky='S')
        row += 1

    def Analyze(self):
        WRF_Importer()

    def plotSpectrum(self):
        from tkinter.filedialog import askopenfilename
        opts = dict(title='Open WRF Analysis CSV',
                    initialdir=self.plotSpectrum_last_dir,
                    defaultextension='.csv',
                    filetypes=[('CSV','*.csv')],
                    multiple=False)
        csv_filename = askopenfilename(**opts)
        if csv_filename is None or len(csv_filename) == 0:
            return
        self.plotSpectrum_last_dir = os.path.split(csv_filename)[0]
        spectrum = WRF_CSV(csv_filename)
        Plot_Spectrum(spectrum)

    def modelCalculator(self, *args):
        """Display a simple calculator widget for the rhoR model."""
        ModelCalculator(self)

    def modelPlotter(self, *args):
        """Display a simple plot widget for the rhoR model."""
        ModelPlotter(self)

    def hohlCorr(self, *args):
        """Perform a hohlraum correction on a spectrum."""
        HohlraumUI(self)

    def plotAsymmetry(self, *args):
        pass

    def fitAsymmetry(self, *args):
        pass

    def __configureMatplotlib__(self):
        """Configure options for matplotlib"""
        matplotlib.pyplot.rc('text', **{'usetex':False})

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()