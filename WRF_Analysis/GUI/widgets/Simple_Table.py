__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

class SimpleTable(tk.Toplevel):
    """Implement a very simple table display, using only tkinter elements. Currently has issues.

    :param parent: The parent UI object
    :param rows: (optional) number of rows to display [default=10]
    :param columns: (optional) number of columns to display [default=2]
    :param title: (optional) Window title to display [default='']
    :param width: (optional) Width of the display window [default=10]
    """

    def __init__(self, parent, rows=10, columns=2, title="", width=10):
        """Constructor"""
        # use black background so it "peeks through" to
        # form grid lines
        super(SimpleTable, self).__init__(parent, background="black")

        # add scrollbar
        frame = self.frame = ttk.Frame(self)
        self.configure(background='#eeeeee')
        self.frame.grid(row=1, columnspan=2, padx=2, pady=2, sticky=tk.N+tk.E+tk.S+tk.W)

        self.text_area = tk.Canvas(self.frame, background="black", width=400, height=500, scrollregion=(0,0,1200,800))
        self.hscroll = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.vscroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area['xscrollcommand'] = self.hscroll.set
        self.text_area['yscrollcommand'] = self.vscroll.set

        self.text_area.configure(scrollregion=self.text_area.bbox("all"))

        self.text_area.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.hscroll.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.vscroll.grid(row=0, column=1, sticky=tk.N+tk.S)

        self._widgets = []

        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = ttk.Label(self.text_area, text="",
                                 borderwidth=0, width=width)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        #self.pack(side="top", fill="x")
        self.set(0,0,"Hello, world")
        self.title(title)

    def set(self, row, column, value):
        """Set the value at a specified location in the table.

        :param row: The row index
        :param column: The column index
        :param value: The value to set at row, column
        """
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def get(self, row, column):
        """Get the value currently contained in the cell.

        :param row: The row to get
        :param column: The column to get
        :returns: `str` representation of the value
        """
        return self._widgets[row][column].cget('text')

    def __myfunction__(self, event):
        self.text_area.configure(scrollregion=self.text_area.bbox("all"),width=200,height=200)