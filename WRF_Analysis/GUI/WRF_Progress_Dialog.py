__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk

class WRF_Progress_Dialog(tk.Toplevel):
    """Implement a generic progress bar dialog.

    :param parent: (optional) the parent (usually should be None) [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the progress dialog"""
        super(WRF_Progress_Dialog, self).__init__(parent)

        self.cancelled = False

        self.__createUI__()
        self.configure(background='#eeeeee')

    def __createUI__(self):
        """Helper method to create the UI elements"""
        self.grid()
        self.label = ttk.Label(self, text="Importing WRF")
        self.label.grid(sticky='N', padx=2, pady=2)

        self.counter = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.counter, maximum=100)
        self.progress_bar.grid(sticky='N', padx=2, pady=2)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(stick='S', padx=2, pady=2)

    def step(self, amount):
        """Increase the amount on the progress bar."""
        self.progress_bar.step(amount)

    def cancel(self):
        """Attempt to cancel the operation."""
        self.cancelled = True
        self.withdraw()

    def set_text(self, new_text):
        """
        Update the displayed info at the top of the window
        :param new_text: The new text string to display
        """
        self.label.configure(text=new_text)