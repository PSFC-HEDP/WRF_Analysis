__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

class Option_Prompt(tk.Toplevel):
    """Implement a dialog window to prompt a user to select one of several options."""

    def __init__(self, parent, title=None, text=None, options=[], width=10):
        """Initialize the dialog window"""
        super(Option_Prompt, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.lift()

        self.grab_set()

        self.result = None
        self.__create_widgets__(title, text, options, width)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # a couple key bindings:
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)

        self.configure(background='#eeeeee')

        # a couple key bindings:
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.wait_window(self)

    def __create_widgets__(self, title, text, options, width):
        """Create the UI"""
        if title is not None:
            self.title(title)

        if text is not None:
            label1 = ttk.Label(self, text=text)
            label1.pack()

        if options is not None:
            self.var = tk.StringVar()
            options = [''] + options
            menu = ttk.OptionMenu(self, self.var, *options)
            menu.configure(width=width)
            menu.pack()
            menu.focus_force()

        self.__make_buttons__()

    def __make_buttons__(self):
        """Add the OK and cancel buttons"""
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        """Handle activation of the OK button."""
        if not self.validate():
            print('not valid')
            return

        self.apply()
        self.withdraw()
        self.update_idletasks()

        self.cancel()

    def cancel(self, event=None):
        """Handle cancel button"""
        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def validate(self):
        """Validate the selection, returns true if it is OK"""
        return self.var.get() != ''

    def apply(self):
        """Set the result"""
        self.result = self.var.get()