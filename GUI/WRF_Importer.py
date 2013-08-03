__author__ = 'Alex Zylstra'

import tkinter as tk
from DB import Database

class WRF_Importer(tk.Toplevel):
    """Implement a GUI dialog for importing a WRF analysis."""
    csv_filename = ''
    image_filename = ''

    def __init__(self, parent=None):
        """Initialize the GUI."""
        super(WRF_Importer, self).__init__(master=parent)

        # create the unique UI:
        self.__create_widgets__()

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.title('Import a WRF')

    def __create_widgets__(self):
        """Create the UI elements for the import"""
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

        self.cancel_button = tk.Button(self, text='Cancel', command=self.withdraw)
        self.cancel_button.grid(row=4, column=0)
        self.go_button = tk.Button(self, text='Go', command=self.do_analysis)
        self.go_button.grid(row=4, column=1)

    def select_csv(self):
        """Select a CSV file containing the wedge analysis."""
        from tkinter.filedialog import askopenfilename
        opts = dict(title='Open WRF Analysis CSV',
                    initialdir=Database.DIR,
                    defaultextension='.csv',
                    filetypes=[('CSV','*.csv')],
                    multiple=False)
        self.csv_filename = askopenfilename(**opts)
        self.label_csv.configure(text=self.csv_filename)

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
        self.label_image.configure(text=self.image_filename)

    def do_analysis(self):
        asdf=1