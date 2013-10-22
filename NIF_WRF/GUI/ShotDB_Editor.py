__author__ = 'Alex Zylstra'

import tkinter as tk
from NIF_WRF.DB.Shot_DB import *


class ShotDB_Editor(tk.Toplevel):
    def __init__(self, parent=None):
        """
        Initialize the editor
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(ShotDB_Editor, self).__init__(parent)

        # connect to the database
        self.db = Shot_DB(Database.FILE)

        self.grid()
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        self.__createUI__()
        self.title('Edit ShotDB')

    def __createUI__(self):
        """Helper method to create the UI elements"""

        self.label1 = tk.Label(self, text='Shot')
        self.label1.grid(row=0, column=0)
        self.label2 = tk.Label(self, text='Column')
        self.label2.grid(row=1, column=0)
        self.label2 = tk.Label(self, text='Value')
        self.label2.grid(row=2, column=0)

        # shot selector
        self.shot_selector_var = tk.StringVar()
        shots = self.db.get_shots()
        if len(shots) == 0:
            shots = ['']
        self.shot_selector = tk.OptionMenu(self, self.shot_selector_var, *shots)
        self.shot_selector.grid(row=0, column=1)
        self.shot_selector_var.trace('w', self.update_data)
        
        # column selector
        self.col_selector_var = tk.StringVar()
        columns = self.db.get_column_names()
        if len(columns) == 0:
            columns = ['']
        self.col_selector = tk.OptionMenu(self, self.col_selector_var, *columns)
        self.col_selector.grid(row=1, column=1)
        self.col_selector_var.trace('w', self.update_data)

        # value entry
        self.value_entry_var = tk.StringVar()
        self.value_entry = tk.Entry(self, textvariable=self.value_entry_var)
        self.value_entry.grid(row=2, column=1)

        # some control buttons
        self.write_button = tk.Button(self, text='Write', command=self.write)
        self.write_button.grid(row=3, column=0, sticky='s')
        self.close_button = tk.Button(self, text='Close', command=self.close)
        self.close_button.grid(row=3, column=1, sticky='s')

    def update_data(self, *args):
        """Update the displayed data based on what is currently in the database"""
        shot = self.shot_selector_var.get()
        col = self.col_selector_var.get()

        if shot == '' or col == '':
            return

        value = self.db.query_col(shot, col)
        self.value_entry_var.set(value)

    def write(self, *args):
        """Write the value as entered to the database."""
        shot = self.shot_selector_var.get()
        col = self.col_selector_var.get()

        if shot == '' or col == '':
            return

        value = self.value_entry_var.get()
        self.db.update(shot, col, value)

    def close(self):
        """Close, and prompt the user to save if necessary."""
        # do a check to see if new info was entered and not saved:
        shot = self.shot_selector_var.get()
        col = self.col_selector_var.get()

        if shot != '' and col != '':
            value = self.db.query_col(shot, col)
            if value != self.value_entry_var.get():
                from tkinter.messagebox import askyesno
                result = askyesno('Save value?', 'New data was entered. Save?', parent=self)
                if result:
                    self.write()

        self.withdraw()