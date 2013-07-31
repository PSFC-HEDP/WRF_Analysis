__author__ = 'Alex Zylstra'

import tkinter as tk
from DB import Database
import os

class DB_Info(tk.Toplevel):
    def __init__(self, parent=None):
        """
        Initialize the progress dialog
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(DB_Info, self).__init__(parent)

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
            self.size_label = tk.Label(self, text=os.path.getsize(Database.FILE)+'KB')
            self.size_label.grid(row=1, column=1, sticky='NSEW', padx=2, pady=2)

        self.spinner = tk.OptionMenu(self, tk.StringVar(), 'foo', 'bar')
        self.spinner.grid()

        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(stick='S', padx=2, pady=2)

    def cancel(self):
        self.withdraw()