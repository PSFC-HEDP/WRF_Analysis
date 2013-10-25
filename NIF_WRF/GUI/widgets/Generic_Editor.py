__author__ = 'Alex Zylstra'

import tkinter as tk

class Generic_Editor(tk.Toplevel):
    """A generic editor for database objects.

    :param db: the Database object to use
    :param parent: (optional) the parent (usually should be None) [default=None]
    :param column_names: (optional) the names to use for columns [default is to use SQL names]
    """

    def __init__(self, db, parent=None, column_names=None):
        """Initialize the editor"""
        super(Generic_Editor, self).__init__(parent)

        self.db = db

        self.grid()
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        self.__createUI__(column_names)

        # a couple key bindings:
        self.bind('<Return>', self.write)
        self.bind('<Escape>', self.close)

    def __createUI__(self, columns=None):
        """Helper method to create the UI elements"""
        # get a list of columns
        if columns is None:
            columns = self.db.get_column_names()

        # for UI element storage:
        self.labels = []
        self.entries = []
        self.vars = []

        # iteratively create the UI:
        for i in range(len(columns)):
            # create a label
            label = tk.Label(self, text=columns[i])
            label.grid(row=i, column=0)

            # and a box for entry
            var = tk.StringVar()
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=i, column=1)
            entry.bind('<Return>', self.write)

            # add to arrays:
            self.labels.append(label)
            self.entries.append(entry)
            self.vars.append(var)

        # some control buttons
        self.write_button = tk.Button(self, text='Write', command=self.write)
        self.write_button.grid(row=len(columns), column=0, sticky='s')
        self.close_button = tk.Button(self, text='Close', command=self.close)
        self.close_button.grid(row=len(columns), column=1, sticky='s')

    def close(self, *args):
        """Close this window."""
        self.withdraw()