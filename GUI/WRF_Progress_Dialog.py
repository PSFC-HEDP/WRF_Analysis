__author__ = 'Alex Zylstra'

import tkinter as tk
import ttk

class WRF_Progress_Dialog(tk.Toplevel):
    def __init__(self, parent=None):
        """
        Initialize the progress dialog
        :param parent: (optional) the parent (usually should be None) [default=None]
        """
        super(WRF_Progress_Dialog, self).__init__(parent)

        self.__createUI__()

    def __createUI__(self):
        """Helper method to create the UI elements"""
        self.grid()
        self.label = tk.Label(self, text="Importing WRF")
        self.label.grid(sticky='N', padx=2, pady=2)

        self.counter = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.counter)
        self.progress_bar.grid(sticky='N', padx=2, pady=2)

        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(stick='S', padx=2, pady=2)

    def step(self, amount):
        """Increase the amount on the progress bar."""
        self.progress_bar.step(amount)

    def cancel(self):
        """Attempt to cancel the operation."""
        self.withdraw()

    def set_text(self, new_text):
        """
        Update the displayed info at the top of the window
        :param new_text: The new text string to display
        """
        self.label.configure(text=new_text)