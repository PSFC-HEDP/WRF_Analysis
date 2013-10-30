__author__ = 'Alex Zylstra'

import tkinter as tk
import os

from NIF_WRF.DB import Database
from NIF_WRF.DB.WRF_Data_DB import *
from NIF_WRF.DB.WRF_InitAnalysis_DB import *
from NIF_WRF.DB.WRF_Inventory_DB import *
from NIF_WRF.GUI.WRF_Progress_Dialog import *
from NIF_WRF.GUI.WRF_Analyzer import *
from NIF_WRF.util.Import_WRF_CSV import WRF_CSV
from NIF_WRF.util.Import_Nxy import load_image


class WRF_Importer(tk.Toplevel):
    """Implement a GUI dialog for importing a WRF analysis.

    :param parent: (optional) The parent UI element to this window [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the GUI."""
        super(WRF_Importer, self).__init__(master=parent)

        self.csv_filename = ''
        self.image_filename = ''

        # create the unique UI:
        self.__create_widgets__()

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.title('Import a WRF')

        # a couple key bindings:
        self.bind('<Return>', self.do_import)
        self.bind('<Escape>', self.withdraw)

    def __create_widgets__(self):
        """Create the UI elements for the import"""
        # controls for selecting a CSV and image file:
        self.label1 = tk.Label(self, text='Select CSV')
        self.label1.grid(row=0, column=0)

        self.label_csv = tk.Label(self, text='')
        self.label_csv.grid(row=1, column=0, columnspan=2)

        self.label2 = tk.Label(self, text='Select image')
        self.label2.grid(row=2, column=0)

        self.label_image = tk.Label(self, text='')
        self.label_image.grid(row=3, column=0, columnspan=2)

        self.csv_button = tk.Button(self, text='Open CSV', command=self.select_csv)
        self.csv_button.grid(row=0, column=1)

        self.image_button = tk.Button(self, text='Open N(x,y)', command=self.select_Nxy)
        self.image_button.grid(row=2, column=1)

        # option to run analysis
        self.run_analysis_var = tk.BooleanVar()
        self.run_analysis = tk.Checkbutton(self, text='Run analysis', variable=self.run_analysis_var)
        self.run_analysis.select()  # start activated
        self.run_analysis.grid(row=4, column=0, columnspan=2)

        # control buttons at the bottom:
        self.cancel_button = tk.Button(self, text='Cancel', command=self.withdraw)
        self.cancel_button.grid(row=5, column=0)
        self.go_button = tk.Button(self, text='Go', command=self.do_import)
        self.go_button.grid(row=5, column=1)

    def select_csv(self):
        """Select a CSV file containing the wedge analysis."""
        from tkinter.filedialog import askopenfilename
        opts = dict(title='Open WRF Analysis CSV',
                    initialdir=Database.DIR,
                    defaultextension='.csv',
                    filetypes=[('CSV','*.csv')],
                    multiple=False)
        self.csv_filename = askopenfilename(**opts)
        # condense for display
        short = os.path.split(self.csv_filename)[-1]
        self.label_csv.configure(text=short)

    def select_Nxy(self):
        """Select an image file to use as N(x,y)"""
        from tkinter.filedialog import askopenfilename
        opts = dict(title='Open WRF Analysis N(x,y)',
                    initialdir=Database.DIR,
                    defaultextension='.bmp',
                    filetypes=[('Bitmap','*.bmp'),
                               ('GIF','*.gif'),
                               ('JPEG','*.jpg'),
                               ('PNG','*.png')],
                    multiple=False)
        self.image_filename = askopenfilename(**opts)
        # condense for display
        short = os.path.split(self.image_filename)[-1]
        self.label_image.configure(text=short)

    def do_import(self, *args):
        """Using the information above, import the data and run the analysis if requested."""
        # sanity check:
        if not os.path.exists(self.csv_filename):
            return

        # make a progress bar, since this can be lengthy:
        #self.iconify()

        # use the DB's method to load the data
        db = WRF_Data_DB()
        raw = WRF_CSV(self.csv_filename)
        if os.path.exists(self.image_filename):
            image = load_image(self.image_filename)
        else:
            image = None
        db.add_data(raw, image)

        # also now call function to add to the initial analysis DB
        db = WRF_InitAnalysis_DB()
        db.import_csv(raw)

        if self.run_analysis_var.get():
            WRF_Analyzer(shot=raw.shot, dim=raw.dim, pos=raw.pos)

        db = WRF_Inventory_DB()
        db.refresh_from_setup()

        self.withdraw()