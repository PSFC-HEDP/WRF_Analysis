__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
import os, platform
import matplotlib, matplotlib.pyplot
from WRF_Analysis.util.Import_WRF_CSV import WRF_CSV
from WRF_Analysis.Analysis.Hohlraum import Hohlraum


class HohlraumUI(tk.Toplevel):
    """Implement a GUI dialog for doing basic hohlraum corrections.

    :param parent: (optional) The parent UI element to this window [default=None]
    """
    HohlraumUI_last_dir = None

    def __init__(self, parent=None):
        """Initialize the GUI."""
        super(HohlraumUI, self).__init__(master=parent)

        self.csv_filename = ''
        self.file = None
        self.h = None
        self.fig = None
        self.ax = None
        self.canvas = None

        # create the unique UI:
        self.__create_widgets__()

        self.configure(background='#eeeeee')

        self.title('Hohlraum Analysis')

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
        self.bind('<' + shortcutModifier + 'o>', self.select_csv)
        self.bind('<' + shortcutModifier + 'c>', self.copy)
        self.bind('<' + shortcutModifier + 'w>', self.withdraw)


    def __create_widgets__(self):
        """Create the UI elements for the import"""
        frame = tk.Frame(self) # frame for UI elements
        frame.configure(background='#eeeeee')
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(frame, 0, weight=1)
        tk.Grid.columnconfigure(frame, 1, weight=1)
        tk.Grid.columnconfigure(frame, 2, weight=1)

        row = 0

        # controls for selecting a CSV and image file:
        self.csv_button = ttk.Button(frame, text='Open CSV', command=self.select_csv)
        self.csv_button.grid(row=row, column=0, columnspan=3)
        row += 1

        self.label_csv = ttk.Label(frame, text='')
        self.label_csv.grid(row=row, column=0, columnspan=3)
        row += 1

        self.ttk_sep1 = ttk.Separator(frame, orient="vertical")
        self.ttk_sep1.grid(row=row, column=0, columnspan=3, sticky="ew")
        row += 1

        self.label_DU = ttk.Label(frame, text='DU')
        self.label_DU.grid(row=row, column=0)
        self.var_DU = tk.StringVar()
        self.entry_DU = ttk.Entry(frame, width=10, textvariable=self.var_DU)
        self.var_DU.set('0')
        self.entry_DU.grid(row=row, column=1)
        self.label_DU2 = ttk.Label(frame, text='μm')
        self.label_DU2.grid(row=row, column=2)
        row += 1

        self.label_Au = ttk.Label(frame, text='Au')
        self.label_Au.grid(row=row, column=0)
        self.var_Au = tk.StringVar()
        self.entry_Au = ttk.Entry(frame, width=10, textvariable=self.var_Au)
        self.var_Au.set('0')
        self.entry_Au.grid(row=row, column=1)
        self.label_Au2 = ttk.Label(frame, text='μm')
        self.label_Au2.grid(row=row, column=2)
        row += 1

        self.label_Al = ttk.Label(frame, text='Al')
        self.label_Al.grid(row=row, column=0)
        self.var_Al = tk.StringVar()
        self.entry_Al = ttk.Entry(frame, width=10, textvariable=self.var_Al)
        self.var_Al.set('0')
        self.entry_Al.grid(row=row, column=1)
        self.label_Al2 = ttk.Label(frame, text='μm')
        self.label_Al2.grid(row=row, column=2)
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

        frame.pack()

        # For the plot:
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack()

    def select_csv(self, *args):
        """Select a CSV file containing the wedge analysis."""
        opts = dict(title='Open WRF Analysis CSV',
                    initialdir=HohlraumUI.HohlraumUI_last_dir,
                    defaultextension='.csv',
                    filetypes=[('CSV','*.csv')],
                    multiple=False)
        self.csv_filename = askopenfilename(**opts)
        HohlraumUI.HohlraumUI_last_dir = os.path.split(self.csv_filename)[0]
        # condense for display
        short = os.path.split(self.csv_filename)[-1]
        self.label_csv.configure(text=short)

    def calculate(self, *args):
        """Using the information above, import the data and run the analysis if requested."""
        # sanity check:
        if not os.path.exists(self.csv_filename):
            return
        try:
            self.file = WRF_CSV(self.csv_filename)
        except:
            showerror('Error', 'Problem with WRF CSV file')
            return

        # Thicknesses:
        try:
            DU = float(self.var_DU.get())
            Au = float(self.var_Au.get())
            Al = float(self.var_Al.get())
            assert DU >= 0 and Au >= 0 and Al >= 0
        except:
            showerror('Error', 'Invalid hohlraum thicknesses')
            return

        self.h = Hohlraum(self.file.spectrum, Thickness=[Au,DU,Al])
        self.save_button.configure(state=tk.ACTIVE)
        self.copy_button.configure(state=tk.ACTIVE)
        self.plot()

    def plot(self, *args):
        """Generate or update the hohlraum plot"""
        # generate axes if necessary:
        if self.ax is None:
            #self.fig = plt.Figure(figsize=(4,3))
            self.fig = matplotlib.figure.Figure()
            self.ax = self.fig.add_subplot(111)
        else:  # if ax exists, clear it:
            self.ax.clear()
        if self.canvas is not None:  # update the drawing if necessary
            self.canvas.draw()

        # sanity:
        if self.file is None or self.h is None:
            return

        # set matplotlib backend
        if matplotlib.get_backend() != 'tkagg':
            matplotlib.pyplot.switch_backend('TkAgg')

        # plot the data
        self.h.plot(self.ax)

        # check to see if we need to create the canvas:
        if self.canvas is None:
            self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(self.canvas, self.plot_frame)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.draw()

    def copy(self, *args):
        """Copy info about corrected spectrum to the clipboard"""
        if self.h is None:
            return
        self.clipboard_append(self._genText())

    def save(self, *args):
        """Save info about corrected spectrum to a file"""
        if self.h is None:
            return
        opts = dict(title='Save corrected spectrum',
                    initialdir=HohlraumUI.HohlraumUI_last_dir,
                    defaultextension='.tsv',
                    filetypes=[('TSV','*.tsv'), ('CSV','*.csv')])
        fname = asksaveasfilename(**opts)
        HohlraumUI.HohlraumUI_last_dir = os.path.split(fname)[0]

        with open(fname,'w') as file:
            text = self._genText()
            if fname[-4:] == '.csv' or fname[-4:] == '.CSV':
                text = text.replace('\t', ',')
            file.write(text)
            file.close()

    def _genText(self):
        text = ''

        if self.file is not None and self.h is not None:
            raw_spec = self.h.get_data_raw()
            corr_spec = self.h.get_data_corr()
            raw_fit = self.h.get_fit_raw()
            corr_fit = self.h.get_fit_corr()
            DU = self.h.DU
            Au = self.h.Au
            Al = self.h.Al

            text += 'DU (um)' + '\t' + '{:.2f}'.format(DU) + '\n'
            text += 'Au (um)' + '\t' + '{:.2f}'.format(Au) + '\n'
            text += 'Al (um)' + '\t' + '{:.2f}'.format(Al) + '\n'
            text += '\n'
            text += 'Quantity\tRaw\tCorrected\n'
            text += 'Yp\t' + '{:.2e}'.format(raw_fit[0]) + '\t' + '{:.2e}'.format(corr_fit[0]) + '\n'
            text += 'Ep\t' + '{:.3f}'.format(raw_fit[1]) + '\t' + '{:.3f}'.format(corr_fit[1]) + '\n'
            text += 'sig\t' + '{:.3f}'.format(raw_fit[2]) + '\t' + '{:.3f}'.format(corr_fit[2]) + '\n'
            text += '\n'
            text += 'Corrected spectrum\n'
            text += 'Ep\tY/Mev\tUnc\n'
            for row in corr_spec:
                for val in row:
                    text += '{:.3e}'.format(val) + '\t'
                text += '\n'

        return text