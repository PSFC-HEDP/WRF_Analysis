__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from tkinter.filedialog import asksaveasfilename
from WRF_Analysis.GUI.widgets.Model_Frame import Model_Frame
import os, platform
import matplotlib
from WRF_Analysis.Analysis.Asymmetries import *


class AsymmetryFit(tk.Toplevel):
    """Implement a GUI dialog for plotting rhoR asymmetries.

    :param parent: (optional) The parent UI element to this window [default=None]
    """
    AsymmetryFit_last_dir = None

    def __init__(self, parent=None):
        """Initialize the GUI."""
        super(AsymmetryFit, self).__init__(master=parent)

        self.result = None

        # For plot:
        self.fig = None
        self.ax = None
        self.canvas = None

        # data variables
        self.var_theta = []
        self.var_phi = []
        self.var_rhoR = []
        self.var_drhoR = []

        # create the unique UI:
        self.__create_widgets__()

        self.configure(background='#eeeeee')

        self.title('Asymmetry Fit')

        # a couple key bindings:
        self.bind('<Return>', self.calculate)
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
        tk.Grid.columnconfigure(frame, 3, weight=1)

        row = 0

        ttk.Label(frame, text='Mode ℓ [int ≥ 1]').grid(row=row, column=0, columnspan=2)
        self.mode_var = tk.StringVar()
        self.mode_entry = ttk.Entry(frame, width=8, textvariable=self.mode_var)
        self.mode_var.set('2')
        self.mode_entry.grid(row=row, column=2, columnspan=2)
        row += 1

        ttk.Label(frame, text='# data points').grid(row=row, column=0, columnspan=2)
        self.n_var = tk.StringVar()
        self.n_entry = ttk.Entry(frame, width=8, textvariable=self.n_var)
        self.n_var.set('3')
        self.n_var.trace('w', self._update_n)
        self.n_entry.grid(row=row, column=2, columnspan=2)
        row += 1

        self.ttk_sep1 = ttk.Separator(frame, orient="vertical")
        self.ttk_sep1.grid(row=row, column=0, columnspan=4, sticky="ew")
        row += 1

        ttk.Label(frame, text='ρR data').grid(row=row, column=0, columnspan=4)
        row += 1

        self.n = 3
        self.data_row = row
        self.data_frame = None
        self._create_data_frame()
        self.data_frame.grid(row=row, column=0, columnspan=4)
        row += 1

        ttk.Separator(frame, orient="vertical").grid(row=row, column=0, columnspan=4, sticky="ew")
        row += 1

        ttk.Label(frame, text='R₀ (μm)').grid(row=row, column=0)
        self.label_R0 = ttk.Label(frame, text='')
        self.label_R0.grid(row=row, column=1)
        ttk.Label(frame, text='±').grid(row=row, column=2)
        self.label_dR0 = ttk.Label(frame, text='')
        self.label_dR0.grid(row=row, column=3)
        row += 1

        ttk.Label(frame, text='Δ (%)').grid(row=row, column=0)
        self.label_D = ttk.Label(frame, text='')
        self.label_D.grid(row=row, column=1)
        ttk.Label(frame, text='±').grid(row=row, column=2)
        self.label_dD = ttk.Label(frame, text='')
        self.label_dD.grid(row=row, column=3)
        row += 1

        ttk.Label(frame, text='ρR₀ (mg/cm²)').grid(row=row, column=0)
        self.label_rhoR = ttk.Label(frame, text='')
        self.label_rhoR.grid(row=row, column=1)
        ttk.Label(frame, text='±').grid(row=row, column=2)
        self.label_drhoR = ttk.Label(frame, text='')
        self.label_drhoR.grid(row=row, column=3)
        row += 1

        self.modelFrame = Model_Frame(frame, text='Model Parameters', relief=tk.RAISED, borderwidth=1)
        self.modelFrame.grid(row=row, columnspan=4)
        row += 1

        # control buttons at the bottom:
        self.go_button = ttk.Button(frame, text='Calculate', command=self.calculate)
        self.go_button.grid(row=row, column=0)
        self.copy_button = ttk.Button(frame, text='Copy', command=self.copy)
        self.copy_button.configure(state=tk.DISABLED)
        self.copy_button.grid(row=row, column=1)
        self.save_button = ttk.Button(frame, text='Save', command=self.save)
        self.save_button.configure(state=tk.DISABLED)
        self.save_button.grid(row=row, column=2)
        self.plot_button = ttk.Button(frame, text='Plot', command=self.plot)
        self.plot_button.configure(state=tk.DISABLED)
        self.plot_button.grid(row=row, column=3)

        frame.pack()

        # For the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

    def _create_data_frame(self, *args):
        if self.data_frame is not None:
            self.data_frame.destroy()
        self.data_frame = tk.Frame(self.frame)
        self.data_frame.configure(background='#eeeeee')

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self.data_frame, 0, weight=1)
        tk.Grid.columnconfigure(self.data_frame, 1, weight=1)
        tk.Grid.columnconfigure(self.data_frame, 2, weight=1)
        tk.Grid.columnconfigure(self.data_frame, 3, weight=1)

        row = 0
        ttk.Label(self.data_frame, text='θ (deg)').grid(row=row, column=0)
        ttk.Label(self.data_frame, text='ϕ (deg)').grid(row=row, column=1)
        ttk.Label(self.data_frame, text='ρR (mg/cm²)').grid(row=row, column=2)
        ttk.Label(self.data_frame, text='ΔρR (mg/cm²)').grid(row=row, column=3)
        row += 1

        if self.n > len(self.var_theta):
            for i in range(self.n-len(self.var_theta)):
                var1 = tk.StringVar()
                self.var_theta.append(var1)
                var2 = tk.StringVar()
                self.var_phi.append(var2)
                var3 = tk.StringVar()
                self.var_rhoR.append(var3)
                var4 = tk.StringVar()
                self.var_drhoR.append(var4)

        for i in range(self.n):
            entry1 = ttk.Entry(self.data_frame, width=8, textvariable=self.var_theta[i])
            entry1.grid(row=row, column=0)
            entry2 = ttk.Entry(self.data_frame, width=8, textvariable=self.var_phi[i])
            entry2.grid(row=row, column=1)
            entry3 = ttk.Entry(self.data_frame, width=8, textvariable=self.var_rhoR[i])
            entry3.grid(row=row, column=2)
            entry4 = ttk.Entry(self.data_frame, width=8, textvariable=self.var_drhoR[i])
            entry4.grid(row=row, column=3)
            row += 1

        self.data_frame.grid(row=self.data_row, column=0, columnspan=4)
        self.update()

    def _update_n(self, *args):
        """Update the UI for data based on entry for number of points"""
        try:
            n = int(self.n_var.get())
            if n > 1:
                self.n = n
                self._create_data_frame()
        except:
            return

    def calculate(self, *args):
        """Do the calculation (i.e. fit)"""
        # Clear existing results:
        self.label_R0.configure(text='      ')
        self.label_dR0.configure(text='      ')
        self.label_D.configure(text='      ')
        self.label_dD.configure(text='      ')
        self.label_rhoR.configure(text='      ')
        self.label_drhoR.configure(text='      ')
        if self.ax is not None:
            self.ax.clear()
            self.canvas.draw()

        try:
            # Get the data:
            theta = []
            rR = []
            rR_err = []
            for i in range(self.n):
                theta.append(float(self.var_theta[i].get()))
                rR.append(float(self.var_rhoR[i].get()))
                rR_err.append(float(self.var_drhoR[i].get()))

            # if there are only 2 points scipy is silly and refuses to give pcov
            # fix by adding a third point with giant error bar so it doesn't affect fit
            if len(theta) == 2:
                theta.append(theta[0])
                rR.append(rR[0])
                rR_err.append(100*rR_err[0])

            model = self.modelFrame.get_rhoR_Model()
            l = int(self.mode_var.get())

            r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc = fit_polar(theta, rR, rR_err, l, model=model, angles=ANGLE_DEG)
            self.result = r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc

            self.label_R0.configure(text='{:.1f}'.format(1e4*r0))
            self.label_dR0.configure(text='{:.1f}'.format(1e4*r0_unc))
            self.label_D.configure(text='{:.1f}'.format(1e2*delta))
            self.label_dD.configure(text='{:.1f}'.format(1e2*delta))
            self.label_rhoR.configure(text='{:.1f}'.format(rhoR0))
            self.label_drhoR.configure(text='{:.1f}'.format(rhoR0_unc))

            self.copy_button.configure(state=tk.ACTIVE)
            self.save_button.configure(state=tk.ACTIVE)
            self.plot_button.configure(state=tk.ACTIVE)

        except:
            showerror('Error', 'Could not calculate, check inputs')

    def copy(self, *args):
        """Copy info about asymmetry fit to the clipboard"""
        self.clipboard_append(self._text())

    def save(self, *args):
        """Save info about asymmetry fit to a file"""
        opts = dict(title='Save asymmetry fit',
                    initialdir=AsymmetryFit.AsymmetryFit_last_dir,
                    defaultextension='.tsv',
                    filetypes=[('TSV','*.tsv'), ('CSV','*.csv')])
        fname = asksaveasfilename(**opts)
        AsymmetryFit.AsymmetryFit_last_dir = os.path.split(fname)[0]

        with open(fname,'w') as file:
            text = self._text()
            if fname[-4:] == '.csv' or fname[-4:] == '.CSV':
                text = text.replace('\t', ',')
            file.write(text)
            file.close()

    def _text(self, *args):
        """Get a text representation of the input and results"""
        text = 'Mode ell = ' + self.mode_var.get() + '\n'
        text += 'rhoR data\n'
        text += 'theta(deg)\tphi(deg)\trR(mg/cm2)\tdrhoR(mg/cm2)\n'
        for i in range(self.n):
            text += self.var_theta[i].get() + '\t' + self.var_phi[i].get() + '\t' + self.var_rhoR[i].get() + '\t' + self.var_drhoR[i].get() + '\n'
        if self.result is not None:
            r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc = self.result
            text += 'Results:\n'
            text += 'Quantity\tValue\tUncertainty\n'
            text += 'R0 (um)\t' + '{:.1f}'.format(1e4*r0) + '\t' + '{:.1f}'.format(1e4*r0_unc) + '\n'
            text += 'delta (%)\t' + '{:.1f}'.format(1e2*delta) + '\t' + '{:.1f}'.format(1e2*delta_unc) + '\n'
            text += 'rhoR0 (mg/cm2)\t' + '{:.1f}'.format(rhoR0) + '\t' + '{:.1f}'.format(rhoR0_unc) + '\n'

        return text

    def plot(self, *args):
        """Generate or update the hohlraum plot"""
        # generate axes if necessary:
        if self.ax is None:
            self.fig = matplotlib.figure.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # sanity:
        if self.result is None:
            return
        r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc = self.result
        l = int(self.mode_var.get())

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

        # plot the data
        for i in range(self.n):
            self.ax.errorbar(float(self.var_theta[i].get()),
                             float(self.var_rhoR[i].get()),
                             yerr=float(self.var_drhoR[i].get()),
                             fmt='bo')
        # Plot the fit:
        theta = np.linspace(0, 180, 100)
        phi = np.zeros_like(theta)
        fit = rhoR(theta, phi, r0, delta, l, 0, angles=ANGLE_DEG)
        self.ax.plot(theta, fit, 'r--')
        self.ax.set_xlabel('theta (deg)')
        self.ax.set_ylabel('rhoR (mg/cm2)')

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()