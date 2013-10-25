__author__ = 'Alex Zylstra'

import tkinter as tk
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
        self.__createUI__()
        self.title('Execute command')

        # a couple key bindings:
        self.bind('<Return>', self.execute)
        self.bind('<Escape>', self.withdraw)

    def __createUI__(self):
        """Helper method to create the UI elements"""

        self.label1 = tk.Label(self, text='Enter SQL command')
        self.label1.grid(row=0, column=0, columnspan=2)

        self.command_var = tk.StringVar()
        self.command = tk.Entry(self, textvariable=self.command_var)
        self.command.grid(row=1, column=0, columnspan=2)

        self.go_button = tk.Button(self, text='Execute', command=self.execute)
        self.go_button.grid(row=2, column=0)

        self.cancel_button = tk.Button(self, text='Cancel', command=self.withdraw)
        self.cancel_button.grid(row=2, column=1)

    def execute(self, *args):
        """Execute the entered query"""
        query = self.c.execute(self.command_var.get())
        # display the result:
        result_str = ""
        for row in array_convert(query):
            result_str += str(row) + '\n'
        from tkinter.messagebox import showinfo
        showinfo('Result', result_str, parent=self)