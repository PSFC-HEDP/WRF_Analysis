__author__ = 'Alex Zylstra'

import tkinter as tk

import ttk

from NIF_WRF.GUI.widgets.Collapsible_Frame import *
from NIF_WRF.Analysis.rhoR_Model import rhoR_Model
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis
from NIF_WRF.DB.WRF_rhoR_Model_DB import *
from NIF_WRF.DB.Shot_DB import *


class Model_Frame(Collapsible_Frame):
    """Implement a collapsible frame for configuring rhoR models"""

    def __init__(self, parent, text='', shot=None, **options):
        Collapsible_Frame.__init__(self, parent, text, **options)

        # for getting info from the database:
        self.shot = shot
        if shot is not None:
            self.db = Shot_DB()

        self.__create_widgets__()

    def __create_widgets__(self):
        """Create the GUI elements"""

        n = 0  # for keeping track of the number of rows

        # -------------------------
        #    Database Queries
        # -------------------------
        if self.shot is not None:
            try:
                CapsuleOR = float(self.db.query_col(self.shot, 'Capsule OR (um)'))
            except:
                CapsuleOR = None
            try:
                AblatorThickness = float(self.db.query_col(self.shot, 'Ablator Thickness (um)'))
            except:
                AblatorThickness = None
            try:
                ShellMat = self.db.query_col(self.shot, 'Ablator')
            except:
                ShellMat = None
            try:
                GasP = float(self.db.query_col(self.shot, 'Gas Pressure (atm)'))
            except:
                GasP = None
            try:
                fD = float(self.db.query_col(self.shot, 'fD'))
            except:
                fD = None
            try:
                f3He = float(self.db.query_col(self.shot, 'f3He'))
            except:
                f3He = None

        # -------------------------
        #    Shell Configuration
        # -------------------------
        tk.Label(self.subFrame, text='Shell', font=("Arial", "14", "bold")).grid(row=n, column=0, columnspan=4)

        # entry for inner radius
        n+=1
        tk.Label(self.subFrame, text='Ri (μm)').grid(row=n, column=0)
        self.entry_Ri = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Ri).grid(row=n, column=1)
        # set based on data availability:
        if CapsuleOR is not None and AblatorThickness is not None:
            self.entry_Ri.set(str( (CapsuleOR-AblatorThickness) ))
        else:
            self.entry_Ri.set(str(rhoR_Model.def_Ri*1e4))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Ri_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Ri_err).grid(row=n, column=3)
        self.entry_Ri_err.set(str(rhoR_Analysis.def_Ri_Err*1e4))

        # entry for outer radius
        n+=1
        tk.Label(self.subFrame, text='Ro (μm)').grid(row=n, column=0)
        self.entry_Ro = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Ro).grid(row=n, column=1)
        # set based on data availability:
        if CapsuleOR is not None and AblatorThickness is not None:
            self.entry_Ro.set(str( CapsuleOR ))
        else:
            self.entry_Ro.set(str(rhoR_Model.def_Ro*1e4))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Ro_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Ro_err).grid(row=n, column=3)
        self.entry_Ro_err.set(str(rhoR_Analysis.def_Ro_Err*1e4))

        # entry for shell material
        n+=1
        tk.Label(self.subFrame, text='Shell').grid(row=n, column=0)
        self.entry_shell_mat = tk.StringVar()
        shell_opts = list(rhoR_Model.shell_opts)
        tk.OptionMenu(self.subFrame, self.entry_shell_mat, *shell_opts).grid(row=n, column=1)
        # set based on data availability
        if self.shot is not None:
            self.entry_shell_mat.set(ShellMat)
        else:
            self.entry_shell_mat.set(shell_opts[0])
        # watch for changes to selection, and update density when necessary
        self.entry_shell_mat.trace_variable('w',
                                            lambda *args: self.entry_shell_rho.set(
                                                str(rhoR_Model.__shell_rho__[self.entry_shell_mat.get()])))

        # entry for shell density
        n+=1
        tk.Label(self.subFrame, text='ρ (g/cc)').grid(row=n, column=0)
        self.entry_shell_rho = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_shell_rho, state=tk.DISABLED).grid(row=n, column=1)
        self.entry_shell_rho.set(str(rhoR_Model.__shell_rho__[rhoR_Model.def_shell_mat]))

        # entry for mass remaining
        n+=1
        tk.Label(self.subFrame, text='Mrem').grid(row=n, column=0)
        self.entry_Mrem = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Mrem).grid(row=n, column=1)
        self.entry_Mrem.set(str(rhoR_Model.def_Mrem))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Mrem_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Mrem_err).grid(row=n, column=3)
        self.entry_Mrem_err.set(str(rhoR_Analysis.def_Mrem_Err))

        # entry for in-flight thickness
        n+=1
        tk.Label(self.subFrame, text='Tshell (μm)').grid(row=n, column=0)
        self.entry_Tshell = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Tshell).grid(row=n, column=1)
        self.entry_Tshell.set(str(rhoR_Model.def_Tshell*1e4))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Tshell_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Tshell_err).grid(row=n, column=3)
        self.entry_Tshell_err.set(str(rhoR_Analysis.def_Tshell_Err*1e4))


        # --------------------------
        #   Gas Configuration
        # --------------------------
        n+=1
        sep1 = ttk.Separator(self.subFrame, orient='vertical')
        sep1.grid(row=n, column=0, columnspan=4, sticky='ew')
        n+=1
        tk.Label(self.subFrame, text='Gas', font=("Arial", "14", "bold")).grid(row=n, column=0, columnspan=4)

        # entry for pressure
        n+=1
        tk.Label(self.subFrame, text='P (atm)').grid(row=n, column=0)
        self.entry_P = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_P).grid(row=n, column=1)
        # set based on data availability:
        if GasP is not None:
            self.entry_P.set(str(GasP))
        else:
            self.entry_P.set(str(rhoR_Model.def_P0))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_P_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_P_err).grid(row=n, column=3)
        self.entry_P_err.set(str(rhoR_Analysis.def_P0_Err))

        # entry for deuterium fraction
        n+=1
        tk.Label(self.subFrame, text='fD').grid(row=n, column=0)
        self.entry_fD = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_fD).grid(row=n, column=1)
        # set based on data availability:
        if fD is not None:
            self.entry_fD.set(str(fD))
        else:
            self.entry_fD.set(str(rhoR_Model.def_fD))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_fD_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_fD_err).grid(row=n, column=3)
        self.entry_fD_err.set(str(rhoR_Analysis.def_fD_Err))

        # entry for 3He fraction
        n+=1
        tk.Label(self.subFrame, text='f3He').grid(row=n, column=0)
        self.entry_f3He = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_f3He).grid(row=n, column=1)
        # set based on data availability:
        if f3He is not None:
            self.entry_f3He.set(str(f3He))
        else:
            self.entry_f3He.set(str(rhoR_Model.def_f3He))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_f3He_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_f3He_err).grid(row=n, column=3)
        self.entry_f3He_err.set(str(rhoR_Analysis.def_f3He_Err))


        # --------------------------
        #   Ablated mass & Mix
        # --------------------------
        n+=1
        sep1 = ttk.Separator(self.subFrame, orient='vertical')
        sep1.grid(row=n, column=0, columnspan=4, sticky='ew')
        n+=1
        tk.Label(self.subFrame, text='Ablation & Mix', font=("Arial", "14", "bold")).grid(row=n, column=0, columnspan=4)

        # entry for ablated mass max density
        n+=1
        tk.Label(self.subFrame, text='ρ Abl Max (g/cc)').grid(row=n, column=0)
        self.entry_rho_Abl_Max = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Max).grid(row=n, column=1)
        self.entry_rho_Abl_Max.set(str(rhoR_Model.def_rho_Abl_Max))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_rho_Abl_Max_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Max_err).grid(row=n, column=3)
        self.entry_rho_Abl_Max_err.set(str(rhoR_Analysis.def_rho_Abl_Max_Err))

        # entry for ablated mass min density
        n+=1
        tk.Label(self.subFrame, text='ρ Abl Min (g/cc)').grid(row=n, column=0)
        self.entry_rho_Abl_Min = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Min).grid(row=n, column=1)
        self.entry_rho_Abl_Min.set(str(rhoR_Model.def_rho_Abl_Min))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_rho_Abl_Min_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Min_err).grid(row=n, column=3)
        self.entry_rho_Abl_Min_err.set(str(rhoR_Analysis.def_rho_Abl_Min_Err))

        # entry for ablated mass gradient scale length
        n+=1
        tk.Label(self.subFrame, text='Scale (μm)').grid(row=n, column=0)
        self.entry_rho_Abl_Scale = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Scale).grid(row=n, column=1)
        self.entry_rho_Abl_Scale.set(str(rhoR_Model.def_rho_Abl_Scale*1e4))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_rho_Abl_Scale_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_rho_Abl_Scale_err).grid(row=n, column=3)
        self.entry_rho_Abl_Scale_err.set(str(rhoR_Analysis.def_rho_Abl_Scale_Err*1e4))

        # entry for ablated mass gradient scale length
        n+=1
        tk.Label(self.subFrame, text='Mix Fraction').grid(row=n, column=0)
        self.entry_MixF = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_MixF).grid(row=n, column=1)
        self.entry_MixF.set(str(rhoR_Model.def_MixF))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_MixF_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_MixF_err).grid(row=n, column=3)
        self.entry_MixF_err.set(str(rhoR_Analysis.def_MixF_Err))
        self.entry_f3He_err.set(str(rhoR_Analysis.def_f3He_Err))


        # --------------------------
        #   dE/dx
        # --------------------------
        n+=1
        sep1 = ttk.Separator(self.subFrame, orient='vertical')
        sep1.grid(row=n, column=0, columnspan=4, sticky='ew')
        n+=1
        tk.Label(self.subFrame, text='dE/dx', font=("Arial", "14", "bold")).grid(row=n, column=0, columnspan=4)

        # entry for fuel Te
        n+=1
        tk.Label(self.subFrame, text='Fuel Te (keV)').grid(row=n, column=0)
        self.entry_Te_Gas = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Gas).grid(row=n, column=1)
        self.entry_Te_Gas.set(str(rhoR_Model.def_Te_Gas))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Te_Gas_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Gas_err).grid(row=n, column=3)
        self.entry_Te_Gas_err.set(str(rhoR_Analysis.def_Te_Gas_Err))

        # entry for shell Te
        n+=1
        tk.Label(self.subFrame, text='Shell Te (keV)').grid(row=n, column=0)
        self.entry_Te_Shell = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Shell).grid(row=n, column=1)
        self.entry_Te_Shell.set(str(rhoR_Model.def_Te_Shell))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Te_Shell_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Shell_err).grid(row=n, column=3)
        self.entry_Te_Shell_err.set(str(rhoR_Analysis.def_Te_Shell_Err))

        # entry for ablated mass Te
        n+=1
        tk.Label(self.subFrame, text='Abl Mass Te (keV)').grid(row=n, column=0)
        self.entry_Te_Abl = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Abl).grid(row=n, column=1)
        self.entry_Te_Abl.set(str(rhoR_Model.def_Te_Abl))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Te_Abl_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Abl_err).grid(row=n, column=3)
        self.entry_Te_Abl_err.set(str(rhoR_Analysis.def_Te_Abl_Err))

        # entry for mix mass Te
        n+=1
        tk.Label(self.subFrame, text='Mix Mass Te (keV)').grid(row=n, column=0)
        self.entry_Te_Mix = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Mix).grid(row=n, column=1)
        self.entry_Te_Mix.set(str(rhoR_Model.def_Te_Mix))
        tk.Label(self.subFrame, text='±').grid(row=n, column=2)
        self.entry_Te_Mix_err = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_Te_Mix_err).grid(row=n, column=3)
        self.entry_Te_Mix_err.set(str(rhoR_Analysis.def_Te_Mix_Err))

        # entry for initial proton energy
        n+=1
        tk.Label(self.subFrame, text='Ep (MeV)').grid(row=n, column=0)
        self.entry_E0 = tk.StringVar()
        tk.Entry(self.subFrame, width=8, textvariable=self.entry_E0).grid(row=n, column=1)
        self.entry_E0.set(str(rhoR_Model.def_E0))

    def get_rhoR_Analysis(self):
        """Get a rhoR_Analysis object as specified by the option boxes in this frame"""
        self.__update_param__()

        # create a new rhoR_Analysis with the passed parameters
        ret = rhoR_Analysis(self.shell_mat, self.Ri, self.Ro, self.fD, self.f3He, self.P0,
                            self.Te_Gas, self.Te_Shell, self.Te_Abl, self.Te_Mix,
                            self.rho_Abl_Max, self.rho_Abl_Min, self.rho_Abl_Scale,
                            self.MixF, self.Tshell, self.Mrem, self.E0,
                            self.Ri_err, self.Ro_err, self.P0_err, self.fD_err, self.f3He_err,
                            self.Te_Gas_err, self.Te_Shell_err, self.Te_Abl_err, self.Te_Mix_err,
                            self.rho_Abl_Max_err, self.rho_Abl_Min_err, self.rho_Abl_Scale_err,
                            self.MixF_err, self.Tshell_err, self.Mrem_err)

        return ret

    def get_rhoR_Model(self):
        """Get a rhoR_Model object as specified by the option boxes in this frame"""
        self.__update_param__()

        # create a new rhoR_Analysis with the passed parameters
        ret = rhoR_Model(self.shell_mat, self.Ri, self.Ro, self.fD, self.f3He, self.P0,
                            self.Te_Gas, self.Te_Shell, self.Te_Abl, self.Te_Mix,
                            self.rho_Abl_Max, self.rho_Abl_Min, self.rho_Abl_Scale,
                            self.MixF, self.Tshell, self.Mrem, self.E0)

        return ret

    def add_to_db(self, shot, dim, position):
        """Add the model parameters to the database
        :param shot: The shot number
        :param dim: the DIM
        :param position: The position"""
        self.__update_param__()

        # construct the appropriate dict
        values = {'shell_mat': self.shell_mat, 'Ri': self.Ri, 'Ro': self.Ro, 'fD': self.fD, 'f3He': self.f3He,
                  'P0': self.P0, 'Te_Gas': self.Te_Gas, 'Te_Shell': self.Te_Shell, 'Te_Abl': self.Te_Abl, 'Te_Mix': self.Te_Mix,
                  'rho_Abl_Max': self.rho_Abl_Max, 'rho_Abl_Min': self.rho_Abl_Min, 'rho_Abl_Scale': self.rho_Abl_Scale,
                  'MixF': self.MixF, 'Tshell': self.Tshell, 'Mrem': self.Mrem, 'E0': self.E0,
                  'Ri_Err': self.Ri_err, 'Ro_Err': self.Ro_err, 'fD_Err': self.fD_err, 'f3He_Err': self.f3He_err,
                  'P0_Err': self.P0_err, 'Te_Gas_Err': self.Te_Gas_err, 'Te_Shell_Err': self.Te_Shell_err,
                  'Te_Abl_Err': self.Te_Abl_err, 'Te_Mix_Err': self.Te_Mix_err,
                  'rho_Abl_Max_Err': self.rho_Abl_Max_err, 'rho_Abl_Min_Err': self.rho_Abl_Min_err, 'rho_Abl_Scale_Err': self.rho_Abl_Scale_err,
                  'MixF_Err': self.MixF_err, 'Tshell_Err': self.Tshell_err, 'Mrem_Err': self.Mrem_err}

        DB = WRF_rhoR_Model_DB()
        DB.load_results(shot, dim, position, values)

    def __update_param__(self):
        """Update the parameter values as entered into the GUI"""
        # get the various parameters:
        self.shell_mat = self.entry_shell_mat.get()
        self.Ri = float(self.entry_Ri.get()) / 1.e4  # convert to cm
        self.Ro = float(self.entry_Ro.get()) / 1.e4  # convert to cm
        self.fD = float(self.entry_fD.get())
        self.f3He = float(self.entry_f3He.get())
        self.P0 = float(self.entry_P.get())
        self.Te_Gas = float(self.entry_Te_Gas.get())
        self.Te_Shell = float(self.entry_Te_Shell.get())
        self.Te_Abl = float(self.entry_Te_Abl.get())
        self.Te_Mix = float(self.entry_Te_Mix.get())
        self.rho_Abl_Max = float(self.entry_rho_Abl_Max.get())
        self.rho_Abl_Min = float(self.entry_rho_Abl_Min.get())
        self.rho_Abl_Scale = float(self.entry_rho_Abl_Scale.get()) / 1.e4
        self.MixF = float(self.entry_MixF.get())
        self.Tshell = float(self.entry_Tshell.get()) / 1.e4
        self.Mrem = float(self.entry_Mrem.get())
        self.E0 = float(self.entry_E0.get())

        # and their uncertainties:
        self.Ri_err = float(self.entry_Ri_err.get()) / 1.e4  # convert to cm
        self.Ro_err = float(self.entry_Ro_err.get()) / 1.e4  # convert to cm
        self.fD_err = float(self.entry_fD_err.get())
        self.f3He_err = float(self.entry_f3He_err.get())
        self.P0_err = float(self.entry_P_err.get())
        self.Te_Gas_err = float(self.entry_Te_Gas_err.get())
        self.Te_Shell_err = float(self.entry_Te_Shell_err.get())
        self.Te_Abl_err = float(self.entry_Te_Abl_err.get())
        self.Te_Mix_err = float(self.entry_Te_Mix_err.get())
        self.rho_Abl_Max_err = float(self.entry_rho_Abl_Max_err.get())
        self.rho_Abl_Min_err = float(self.entry_rho_Abl_Min_err.get())
        self.rho_Abl_Scale_err = float(self.entry_rho_Abl_Scale_err.get()) / 1.e4
        self.MixF_err = float(self.entry_MixF_err.get())
        self.Tshell_err = float(self.entry_Tshell_err.get()) / 1.e4
        self.Mrem_err = float(self.entry_Mrem_err.get())

