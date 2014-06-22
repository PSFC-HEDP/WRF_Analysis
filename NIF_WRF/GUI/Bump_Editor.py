__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

from NIF_WRF.DB.Hohlraum_DB import Hohlraum_DB
from NIF_WRF.DB.util import *


class Bump_Editor(tk.Toplevel):
    """Edit information in the hohlraum's bump database.

    :param parent: (optional) the parent (usually should be None) [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the editor"""
        super(Bump_Editor, self).__init__(parent)

        self.db = Hohlraum_DB()

        self.grid()
        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        self.__createUI__()
        self.configure(background='#eeeeee')
        self.title('Edit Bump Table')

        # a couple key bindings:
        self.bind('<Return>', self.__update__)
        self.bind('<Escape>', self.__cancel__)
        self.protocol("WM_DELETE_WINDOW", self.__cancel__)

    def __createUI__(self):
        """Helper method to create the UI elements"""
        row = 0

        label1 = ttk.Label(self, text='Drawing')
        label1.grid(row=row, column=0)

        self.drawing_selector_var = tk.StringVar()
        query = self.db.get_drawings()
        drawings = [''] + query
        self.drawing_selector = ttk.OptionMenu(self, self.drawing_selector_var, *drawings)
        self.drawing_selector.configure(width=16)
        self.drawing_selector.grid(row=row, column=1)
        self.drawing_selector_var.trace('w', self.__update_ui__)
        row += 1

        self.drawing_editor_var = tk.StringVar()
        self.drawing_editor = ttk.Entry(self, textvariable=self.drawing_editor_var)
        self.drawing_editor_var.set('')
        self.drawing_editor.configure(width=16)
        self.drawing_editor.grid(row=row, column=1)
        row += 1

        self.corr_var = tk.BooleanVar()
        self.corr_check = ttk.Checkbutton(self, text='Use correction?', variable=self.corr_var)
        self.corr_var.set(False)
        self.corr_check.grid(row=row, column=0, columnspan=2)
        row += 1

        label2 = ttk.Label(self, text='Thick (μm)')
        label2.grid(row=row, column=0)
        self.thick_var = tk.StringVar()
        self.thick_entry = ttk.Entry(self, textvariable=self.thick_var)
        self.thick_entry.grid(row=row, column=1)
        self.thick_entry.configure(width=8)
        row += 1

        self.update_button = ttk.Button(self, text='Update', command=self.__update__)
        self.update_button.grid(row=row, column=0)
        self.cancel_button = ttk.Button(self, text='Cancel', command=self.__cancel__)
        self.cancel_button.grid(row=row, column=1)

    def __update_ui__(self, *args):
        """Update the UI when the option menu is changed"""
        drawing = self.drawing_selector_var.get()
        if drawing != '':
            try:
                self.drawing_editor_var.set(drawing)
                # get the data from the DB
                temp = self.db.get_bump(drawing)
                self.corr_var.set(temp[1])
                self.thick_var.set(temp[2])
            except:
                pass

    def __update__(self, *args):
        """Update the values in the database based on the entries."""
        try:
            drawing = self.drawing_editor_var.get()
            corr = bool(self.corr_var.get())
            thick = float(self.thick_var.get())
            self.db.set_bump(drawing, corr, thick)
        except:
            pass

    def __cancel__(self, *args):
        """Close this window"""
        self.withdraw()