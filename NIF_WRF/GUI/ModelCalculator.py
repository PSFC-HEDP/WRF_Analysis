__author__ = 'Alex Zylstra'

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from NIF_WRF.GUI.widgets.Model_Frame import Model_Frame
from threading import Thread


class ModelCalculator(tk.Toplevel):
    """Widget to allow manual calculation of rhoR and Rcm from Ep.

    :param parent: (optional) The parent UI window to this one [default=None]
    """

    def __init__(self, parent=None):
        """Initialize the viewer window."""
        super(ModelCalculator, self).__init__()

        # make the UI:
        self.__create_widgets__()
        self.configure(background='#eeeeee')

        # a couple key bindings:
        self.bind('<Escape>', self.close)
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Set the window title:
        self.title('Model Calculator')

    def __create_widgets__(self):
        """Create the UI elements"""
        # make a frame for stuff:
        frame = tk.Frame(self)
        frame.configure(background='#eeeeee')

        label1 = ttk.Label(frame, text='Ep (MeV)')
        label1.grid(row=0, column=0)
        self.entryEvar = tk.StringVar()
        self.entryEvar.trace('w', self.__update__)
        self.entryE = ttk.Entry(frame, textvariable=self.entryEvar, width=10)
        self.entryE.grid(row=0, column=1)
        label1b = ttk.Label(frame, text='±')
        label1b.grid(row=0, column=2)
        self.entryEerrvar = tk.StringVar()
        self.entryEerrvar.trace('w', self.__update__)
        self.entryEerr = ttk.Entry(frame, textvariable=self.entryEerrvar, width=8)
        self.entryEerr.grid(row=0, column=3)

        label2 = ttk.Label(frame, text='ρR (mg/cm2)')
        label2.grid(row=1, column=0)
        self.labelRhoR = ttk.Label(frame, text='')
        self.labelRhoR.grid(row=1, column=1)
        label2b = ttk.Label(frame, text='±')
        label2b.grid(row=1, column=2)
        self.labelRhoRerr = ttk.Label(frame, text='')
        self.labelRhoRerr.grid(row=1, column=3)

        label3 = ttk.Label(frame, text='Rcm (um)')
        label3.grid(row=2, column=0)
        self.labelRcm = ttk.Label(frame, text='')
        self.labelRcm.grid(row=2, column=1)
        label3b = ttk.Label(frame, text='±')
        label3b.grid(row=2, column=2)
        self.labelRcmerr = ttk.Label(frame, text='')
        self.labelRcmerr.grid(row=2, column=3)

        self.updateModelButton = ttk.Button(frame, text='Update Model', command=self.__updateModel__)
        self.updateModelButton.grid(row=3, column=0, columnspan=2)
        self.updateModelLabel = ttk.Label(frame, text='')
        self.updateModelLabel.grid(row=3, column=2, columnspan=2)

        frame.pack()
        self.adv_frame = Model_Frame(self, text='Model Parameters', relief=tk.RAISED, borderwidth=1)
        self.adv_frame.pack()

        self.__updateModel__()

    def __update__(self, *args):
        """Event handler called to update the calculation"""
        # Some sanity checks:
        if self.model == None:
            self.after(100, self.__update__)
            return
        if len(self.entryEvar.get()) == 0:
            return

        # Get the energy from user input
        try:
            energy = float(self.entryEvar.get())
            try:
                energyerr = float(self.entryEerrvar.get())
            except:
                energyerr = 0

            # get values:
            rhoR, Rcm, rhoRerr = self.model.Calc_rhoR(energy, energyerr)
            Rcm, Rcmerr = self.model.Calc_Rcm(energy, energyerr, False)
        except Exception as e:  # handle bad user input
            self.labelRhoR.configure(text='')
            self.labelRcm.configure(text='')
            self.labelRhoRerr.configure(text='')
            self.labelRcmerr.configure(text='')
            return

        # Set the label:
        if not np.isnan(rhoR) and not np.isnan(Rcm):
            self.labelRhoR.configure(text='{:.1f}'.format(rhoR*1e3))
            self.labelRcm.configure(text='{:.0f}'.format(Rcm*1e4))
            self.labelRhoRerr.configure(text='{:.1f}'.format(rhoRerr*1e3))
            self.labelRcmerr.configure(text='{:.0f}'.format(Rcmerr*1e4))
        else:
            self.labelRhoR.configure(text='')
            self.labelRcm.configure(text='')
            self.labelRhoRerr.configure(text='')
            self.labelRcmerr.configure(text='')

    def __updateModel__(self, *args):
        # Clear existing:
        self.model = None
        self.labelRhoR.configure(text='')
        self.labelRcm.configure(text='')

        # Notify the user and prevent subsequent press:
        self.updateModelLabel.configure(text='Running...')
        self.updateModelButton.configure(state=tk.DISABLED)

        # Use threading for the calculation to avoid locking GUI
        def helper():
            self.model = self.adv_frame.get_rhoR_Analysis()
        t = Thread(target=helper)
        t.start()

        # Need to watch for thread completion:
        def callback():
            nonlocal t
            if not t.is_alive():
                # Re-enable:
                self.updateModelLabel.configure(text='')
                self.updateModelButton.configure(state=tk.ACTIVE)
                self.__update__()
            else:
                self.after(50, callback)
        self.after(50, callback)

    def close(self, *args):
        """Close this window"""
        self.withdraw()