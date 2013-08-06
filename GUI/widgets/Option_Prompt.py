__author__ = 'Alex Zylstra'

import tkinter as tk

class Option_Prompt(tk.Toplevel):
    """Implement a dialog window to prompt a user to select one of several options."""

    def __init__(self, parent, title=None, text=None, options=[]):
        """Initialize the dialog window"""
        super(Option_Prompt, self).__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.lift()

        self.grab_set()

        self.result = None
        self.__create_widgets__(title, text, options)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.wait_window(self)

    def __create_widgets__(self, title, text, options):
        """Create the UI"""
        if title is not None:
            self.title(title)

        if text is not None:
            label1 = tk.Label(self, text=text)
            label1.pack()

        if options is not None:
            self.var = tk.StringVar()
            menu = tk.OptionMenu(self, self.var, *options)
            menu.pack()

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
        return self.var.get() != ''

    def apply(self):
        """Set the result"""
        self.result = self.var.get()