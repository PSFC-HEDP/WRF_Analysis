__author__ = 'Alex Zylstra'

import tkinter as tk

class SimpleTable(tk.Toplevel):
    """Implement a very simple table display, using only tkinter elements. Currently has issues"""

    def __init__(self, parent, rows=10, columns=2, title="", width=10):
        # use black background so it "peeks through" to
        # form grid lines
        super(SimpleTable, self).__init__(parent, background="black")

        # add scrollbar
        frame = self.frame = tk.Frame(self)
        self.frame.grid(row=1, columnspan=2, padx=2, pady=2, sticky=tk.N+tk.E+tk.S+tk.W)

        self.text_area = tk.Canvas(self.frame, background="black", width=400, height=500, scrollregion=(0,0,1200,800))
        self.hscroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.vscroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text_area.yview)
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
                label = tk.Label(self.text_area, text="",
                                 borderwidth=0, width=width)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        #self.pack(side="top", fill="x")
        self.set(0,0,"Hello, world")
        self.title(title)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def get(self, row, column):
        return self._widgets[row][column].cget('text')

    def myfunction(self, event):
        self.text_area.configure(scrollregion=self.text_area.bbox("all"),width=200,height=200)