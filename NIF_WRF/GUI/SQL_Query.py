__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
from NIF_WRF.DB.Shot_DB import *


class SQL_Query(tk.Toplevel):
    """Dialog to directly execute a SQL command

        :param parent: (optional) the parent (usually should be None) [default=None]
        """

    def __init__(self, parent=None):
        """Initialize the editor"""
        super(SQL_Query, self).__init__(parent)

        # connect to the database
        try:
            self.db = sqlite3.connect(Database.FILE)
            self.c = self.db.cursor()
        except sqlite3.OperationalError:
            print("Error opening database file.")

        self.grid()
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        self.__createUI__()
        self.title('Execute command')

        # a couple key bindings:
        self.bind('<Return>', self.execute)
        self.bind('<Escape>', self.withdraw)
        self.configure(background='#eeeeee')

    def __createUI__(self):
        """Helper method to create the UI elements"""

        self.label1 = ttk.Label(self, text='Enter SQL command')
        self.label1.grid(row=0, column=0, columnspan=2)

        self.command_var = tk.StringVar()
        self.command = ttk.Entry(self, textvariable=self.command_var)
        self.command.grid(row=1, column=0, columnspan=2, sticky='ew')

        self.go_button = ttk.Button(self, text='Execute', command=self.execute)
        self.go_button.grid(row=2, column=0)

        self.cancel_button = ttk.Button(self, text='Cancel', command=self.withdraw)
        self.cancel_button.grid(row=2, column=1)

    def execute(self, *args):
        """Execute the entered query"""
        print(self.command_var.get())
        query = self.c.execute(self.command_var.get())
        print(query.fetchall())
        # display the result:
        result_str = ""
        for row in array_convert(query):
            result_str += str(row) + '\n'
        from tkinter.messagebox import showinfo
        showinfo('Result', result_str, parent=self)