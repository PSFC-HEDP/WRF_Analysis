__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from tkinter.filedialog import asksaveasfilename
from WRF_Analysis.GUI.widgets.Model_Frame import Model_Frame
import os, platform
import matplotlib
from WRF_Analysis.Analysis.Asymmetries import *


class AsymmetryPlot(tk.Toplevel):
    """Implement a GUI dialog for plotting rhoR asymmetries.

    :param parent: (optional) The parent UI element to this window [default=None]
    """
    AsymmetryPlot_last_dir = None

    def __init__(self, parent=None):
        """Initialize the GUI."""
        super(AsymmetryPlot, self).__init__(master=parent)

        self.theta = None
        self.plot_Rcm = None
        self.plot_rhoR = None

        # For plot:
        self.fig = None
        self.ax = None
        self.ax2 = None
        self.canvas = None

        # create the unique UI:
        self.__create_widgets__()

        self.configure(background='#eeeeee')

        self.title('Asymmetry Plots')

        # a couple key bindings:
        self.bind('<Return>', self.plot)
        self.bind('<Escape>', self.withdraw)

        # Text for shortcuts:
        if platform.system() == 'Darwin':
            shortcutType = '⌘'
            shortcutModifier = 'Command-'
        else:
            shortcutType = 'Ctrl+'
            shortcutModifier = 'Control-'
        self.bind('<' + shortcutModifier + 's>', self.save)
        self.bind('<' + shortcutModifier + 'c>', self.copy)
        self.bind('<' + shortcutModifier + 'w>', self.withdraw)


    def __create_widgets__(self):
        """Create the UI elements for the import"""
        frame = tk.Frame(self) # frame for UI elements
        self.frame = frame
        frame.configure(background='#eeeeee')
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(frame, 0, weight=1)
        tk.Grid.columnconfigure(frame, 1, weight=1)
        tk.Grid.columnconfigure(frame, 2, weight=1)

        row = 0

        ttk.Label(frame, text='Mode ℓ [int ≥ 1]').grid(row=row, column=0, columnspan=2)
        self.mode_var = tk.StringVar()
        self.mode_entry = ttk.Entry(frame, width=8, textvariable=self.mode_var)
        self.mode_var.set('2')
        self.mode_entry.grid(row=row, column=2)
        row += 1

        self.ttk_sep1 = ttk.Separator(frame, orient="vertical")
        self.ttk_sep1.grid(row=row, column=0, columnspan=3, sticky="ew")
        row += 1

        ttk.Label(frame, text='R₀ (μm)').grid(row=row, column=0)
        self.R0_var = tk.StringVar()
        self.R0_entry = ttk.Entry(frame, textvariable=self.R0_var)
        self.R0_entry.grid(row=row, column=1, columnspan=2)
        row += 1

        ttk.Label(frame, text='Δ (%)').grid(row=row, column=0)
        self.delta_var = tk.StringVar()
        self.delta_entry = ttk.Entry(frame, textvariable=self.delta_var)
        self.delta_entry.grid(row=row, column=1, columnspan=2)
        row += 1

        self.modelFrame = Model_Frame(frame, text='Model Parameters', relief=tk.RAISED, borderwidth=1)
        self.modelFrame.grid(row=row, columnspan=3)
        row += 1

        # control buttons at the bottom:
        self.plot_button = ttk.Button(frame, text='Plot', command=self.plot)
        self.plot_button.grid(row=row, column=0)
        self.copy_button = ttk.Button(frame, text='Copy', command=self.copy)
        self.copy_button.configure(state=tk.DISABLED)
        self.copy_button.grid(row=row, column=1)
        self.save_button = ttk.Button(frame, text='Save', command=self.save)
        self.save_button.configure(state=tk.DISABLED)
        self.save_button.grid(row=row, column=2)

        frame.pack()

        # For the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

    def copy(self, *args):
        """Copy info about asymmetry fit to the clipboard"""
        self.clipboard_append(self._text())

    def save(self, *args):
        """Save info about asymmetry fit to a file"""
        opts = dict(title='Save asymmetry fit',
                    initialdir=AsymmetryPlot.AsymmetryPlot_last_dir,
                    defaultextension='.tsv',
                    filetypes=[('TSV','*.tsv'), ('CSV','*.csv')])
        fname = asksaveasfilename(**opts)
        AsymmetryPlot.AsymmetryPlot_last_dir = os.path.split(fname)[0]

        with open(fname,'w') as file:
            text = self._text()
            if fname[-4:] == '.csv' or fname[-4:] == '.CSV':
                text = text.replace('\t', ',')
            file.write(text)
            file.close()

    def _text(self, *args):
        """Get a text representation of the input and results"""
        if self.theta is None:
            return ''
        text = 'theta (deg)\tRcm(um)\trhoR(mg/cm2)\n'
        for i in range(len(self.theta)):
            text += '{:.3f}'.format(self.theta[i]) + '\t'+ '{:.3f}'.format(self.plot_Rcm[i]*1e4) + '\t' + '{:.3f}'.format(self.plot_rhoR[i]) + '\n'
        return text

    def plot(self, *args):
        """Generate or update the hohlraum plot"""
        # generate axes if necessary:
        if self.ax is None:
            self.fig = matplotlib.figure.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
            self.ax2.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

        # Generate the data
        r0 = float(self.R0_var.get()) * 1e-4
        delta = float(self.delta_var.get()) * 1e-2
        l = int(self.mode_var.get())
        m = 0
        theta = np.linspace(0, 180, 100)
        phi = np.zeros_like(theta)
        plot_Rcm = Rcm(theta, phi, r0, delta, l, m, angles=ANGLE_DEG)
        plot_rhoR = rhoR(theta, phi, r0, delta, l, m, angles=ANGLE_DEG)

        # plot the data
        self.ax.plot(theta, plot_rhoR, 'b-')
        self.ax.set_xlabel('theta (deg)')
        self.ax.set_ylabel('rhoR (mg/cm2)')
        self.ax.yaxis.label.set_color('blue')
        self.ax.tick_params(axis='y', colors='blue')
        self.ax.spines['left'].set_color('blue')

        if self.ax2 is None:
            self.ax2 = self.ax.twinx()
        self.ax2.plot(theta, plot_Rcm*1e4, 'r-')
        self.ax2.set_ylabel('Rcm (um)')
        self.ax2.yaxis.label.set_color('red')
        self.ax2.tick_params(axis='y', colors='red')
        self.ax.spines['right'].set_color('red')

        # save:
        self.theta = theta
        self.plot_Rcm = plot_Rcm
        self.plot_rhoR = plot_rhoR

        # Enable copy/save:
        self.copy_button.configure(state=tk.ACTIVE)
        self.save_button.configure(state=tk.ACTIVE)

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()