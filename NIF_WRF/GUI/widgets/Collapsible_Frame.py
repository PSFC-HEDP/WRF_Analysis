__author__ = 'Alex Zylstra'
# adapted from: http://stackoverflow.com/questions/13141259/expandable-collapsible-frame-in-python-tkinter

import tkinter as tk
import ttk

class Collapsible_Frame(tk.Frame):
    """Implement a Tkinter frame which can be hidden/shown by the user"""

    def __init__(self, parent, text='',**options):
        tk.Frame.__init__(self, parent, **options)
        self.show=tk.IntVar()
        self.show.set(0)
        self.titleFrame=ttk.Frame(self)
        self.titleFrame.pack(fill=tk.X, expand=1)
        ttk.Label(self.titleFrame, text=text).pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.toggleButton=ttk.Checkbutton(self.titleFrame, width=2,text='+', command=self.toggle, variable=self.show, style='Toolbutton')
        self.toggleButton.pack(side=tk.LEFT)
        self.subFrame=tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)

        # stretch the column to fill all space:
        tk.Grid.columnconfigure(self.subFrame, 0, weight=1)
        tk.Grid.columnconfigure(self.subFrame, 1, weight=1)
        tk.Grid.columnconfigure(self.subFrame, 2, weight=1)
        tk.Grid.columnconfigure(self.subFrame, 3, weight=1)

    def toggle(self):
        if bool(self.show.get()):
            self.subFrame.pack(fill=tk.X, expand=1)
            self.toggleButton.configure(text='-')
        else:
            self.subFrame.forget()
            self.toggleButton.configure(text='+')