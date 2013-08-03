__author__ = 'Alex Zylstra'

import tkinter as tk
from DB import Database
import os
import sqlite3
from DB.util import *

class DB_Info(tk.Toplevel):
    """Show a window of information about the database file in use."""

    def __init__(self, parent=None):
        """
        Initialize the progress dialog
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(DB_Info, self).__init__(parent)

        # connect to the database
        try:
            self.db = sqlite3.connect(Database.FILE)
            self.c = self.db.cursor()
        except sqlite3.OperationalError:
            print("Error opening database file.")

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

        self.__createUI__()

    def __createUI__(self):
        """Helper method to create the UI elements"""
        self.grid()
        self.label = tk.Label(self, text="File")
        self.label.grid(row=0, column=0, sticky='NSEW', padx=2, pady=2)
        self.file_name = tk.Label(self, text=Database.FILE)
        self.file_name.grid(row=0, column=1, sticky='NSEW', padx=2, pady=2)

        # display file size:
        self.label2 = tk.Label(self, text="Size")
        self.label2.grid(row=1, column=0, sticky='NSEW', padx=2, pady=2)
        if os.path.exists(Database.FILE):
            self.size_label = tk.Label(self, text=str(os.path.getsize(Database.FILE)/1024)+'KB')
            self.size_label.grid(row=1, column=1, sticky='NSEW', padx=2, pady=2)

        # add list of tables
        self.label3 = tk.Label(self, text="Tables")
        self.label3.grid(row=2, column=0, sticky='NSEW', padx=2, pady=2)
        self.spinner_var = tk.StringVar()
        self.table_spinner = tk.OptionMenu(self, self.spinner_var, *self.__get_tables__())
        self.table_spinner.grid(row=2, column=1, sticky='NSEW', padx=2, pady=2)
        # listen for change events:
        self.spinner_var.trace('w', self.update_rows)

        # add a display of rows in the table
        self.label4 = tk.Label(self, text="Rows")
        self.label4.grid(row=3, column=0, sticky='NSEW', padx=2, pady=2)
        self.num_rows = tk.Label(self, text="")
        self.num_rows.grid(row=3, column=1, sticky='NSEW', padx=2, pady=2)


        # add a button to initialize the database
        self.init_button= tk.Button(self, text="Initialize", command=self.initialize)
        self.init_button.grid(row=4, column=0, columnspan=2, sticky='S', padx=2, pady=2)

        # add a button to switch the database
        self.switch_button = tk.Button(self, text="Open DB", command=self.open)
        self.switch_button.grid(row=5, column=0, sticky='NS', padx=2, pady=2)
        self.save_as_button = tk.Button(self, text="Save as", command=self.save)
        self.save_as_button.grid(row=5, column=1, sticky='NS', padx=2, pady=2)

        # a button to close the window:
        self.close_button = tk.Button(self, text="OK", command=self.close)
        self.close_button.grid(row=6, column=0, columnspan=2, sticky='S', padx=2, pady=2)

    def close(self):
        """Close this window"""
        self.withdraw()

    def update_rows(self, *args):
        """Update the displayed number of rows, e.g. when the table selection changes."""
        table = self.spinner_var.get()
        query = self.c.execute('SELECT count(*) from %s' % table)
        rows = query.fetchone()[0]
        self.num_rows.configure(text=str(rows))

    def initialize(self):
        """Trigger the database initialization"""
        from DB.scripts import initialize
        initialize()
        self.refresh()

    def open(self):
        """Open another (existing) database file."""
        # get an existing filename:
        from tkinter.filedialog import askopenfilename
        FILEOPENOPTIONS = dict(defaultextension='.db',
                       filetypes=[('sqlite3 database','*.db'), ('All files','*.*')],
                       multiple=False,
                       initialdir=Database.DIR)
        filename = askopenfilename(**FILEOPENOPTIONS)

        # switch:
        Database.FILE = filename
        self.refresh()

    def save(self):
        """Save the database as a new file."""
        # get a new file:
        from tkinter.filedialog import asksaveasfilename
        FILEOPENOPTIONS = dict(defaultextension='.db',
                       filetypes=[('sqlite3 database','*.db')],
                       initialdir=Database.DIR)
        filename = asksaveasfilename(**FILEOPENOPTIONS)


        import shutil
        # start with a copy:
        shutil.copyfile(Database.FILE, filename)

        # switch:
        Database.FILE = filename
        self.refresh()

    def refresh(self):
        """Refresh the displayed information in this window."""
        self.file_name.configure(text=Database.FILE)
        if os.path.exists(Database.FILE):
            self.size_label.configure(text=str(os.path.getsize(Database.FILE)/1024)+'KB')
        self.table_spinner = tk.OptionMenu(self, tk.StringVar(), *self.__get_tables__())

    def __get_tables__(self):
        """Get a list of tables present in the database."""
        query = self.c.execute("SELECT * FROM sqlite_master WHERE type='table';")
        tables = array_convert(query)

        table_names = []
        for val in tables:
            table_names.append(val[1])

        if len(tables) == 0:
            table_names = ['']

        return table_names
