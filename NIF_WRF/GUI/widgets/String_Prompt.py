__author__ = 'Alex Zylstra'

import tkinter as tk

class String_Prompt(tk.Toplevel):
    """Implement a dialog window to prompt a user to input a string."""

    def __init__(self, parent, title=None, text=None, default=None, invalid=None):
        """Initialize the dialog window"""
        super(String_Prompt, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.lift()

        self.grab_set()

        self.result = default
        self.invalid = invalid
        self.__create_widgets__(title, text, default)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # a couple key bindings:
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)

        self.wait_window(self)

    def __create_widgets__(self, title, text, default):
        """Create the UI"""
        if title is not None:
            self.title(title)

        if text is not None:
            label1 = tk.Label(self, text=text)
            label1.pack()

        if default is not None:
            self.var = tk.StringVar(value=str(default))
            entry = tk.Entry(self, textvariable=self.var)
            entry.pack()
            entry.focus_force()

        self.__make_buttons__()

    def __make_buttons__(self):
        """Add the OK and cancel buttons"""
        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
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
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        """Validate the selection, returns true if it is OK"""
        ret = (self.var.get() != '')
        # also check against list of invalid options if requested:
        if self.invalid is not None:
            for i in self.invalid:
                ret = ret and (self.var.get() != i)
        return ret

    def apply(self):
        """Set the result"""
        self.result = self.var.get()