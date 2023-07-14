from src.rhoR_Model import rhoR_Model
import numpy
import math

__author__ = 'Alex Zylstra'


# Encapsulate analysis of energy -> rhoR using various error bars for assumed parameters.
class rhoR_Analysis(object):
    """A three-part rhoR model for NIF WRF analysis
    including fuel, shell, and ablated mass.
    This class encapsulates the model itself, adding in
    error bars and sensitivity analysis.
    Arguments taken in the constructor are primarily shot-dependent initial conditions.

    :param shell_mat: (optional) the shell material to use {default='CH'}
    :param Ri: (optional) initial shell inner radius [cm] {default=0.09}
    :param Ro: (optional) initial shell outer radius [cm] {default=0.11}
    :param fD: (optional) deuterium atomic fraction in the fuel [fractional] {default=0.3}
    :param f3He: (optional) 3He atomic fraction in the fuel [fractional] {default=0.7}
    :param P0: (optional) initial gas fill pressure [atm] {default=50}
    :param Te_Gas: (optional) gas electron temperature [keV] {default=3}
    :param Te_Shell: (optional) shell electron temperature [keV] {default=0.2}
    :param Te_Abl: (optional) ablated mass electron temperature [keV] {default=0.3}
    :param Te_Mix: (optional) mix mass electron temperature [keV] {default=0.5}
    :param rho_Abl_Max: (optional) maximum density in the ablated mass [g/cc] {default=1.5}
    :param rho_Abl_Min: (optional) minimum density in the ablated mass [g/cc] {default=0.1}
    :param rho_Abl_Scale: (optional) scale length for the ablated mass [cm] {default=70e-4}
    :param f_Mix: (optional) amount of shell material mixed into the fuel [fractional] {default=0.05}
    :param t_Shell: (optional) shell thickness during the implosion [cm] {default=40e-4}
    :param f_Remain: (optional) shell mass remaining during the implosion [fractional] {default=0.175}
    :param E0: (optional) initial proton energy [MeV] {default=14.7}
    :param dEdx_model: (optional) Stopping model to use, valid choices are 'LP', 'BPS', 'Z' {default='LP'}

    :author: Alex Zylstra
    :date: 2014/09/25
    """

    # set verbosity for console output:
    verbose = False

    # values below are defaults
    # anything beginning with a def_ is replaced with a class variable

    def_Ri = 900e-4  # initial inner radius [cm]
    def_Ri_err = 5e-4
    def_Ro = 1100e-4  # initial outer radius [cm]
    def_Ro_err = 5e-4
    def_P0 = 50  # initial pressure [atm]
    def_P0_err = 1
    def_fD = 0.3  # deuterium fraction in fuel
    def_fD_err = 0.
    def_f3He = 0.7  # 3He fraction in fuel
    def_f3He_err = 0.
    def_Te_Gas = 3  # keV
    def_Te_Gas_err = 2
    def_Te_Shell = 0.2  # keV
    def_Te_Shell_err = 0.1
    def_Te_Abl = 0.3  # keV
    def_Te_Abl_err = 0.1
    def_Te_Mix = 1  # keV
    # ablated mass is modeled as an exponential profile
    # specified by max, min, and length scale:
    def_rho_Abl_Max = 1.5  # g/cc
    def_rho_Abl_Max_err = 0.5  # g/cc
    def_rho_Abl_Min = 0.1  # g/cc
    def_rho_Abl_Min_err = 0.05  # g/cc
    def_Te_Mix_err = 0.2  # keV
    def_rho_Abl_Scale = 70e-4  # [cm]
    def_rho_Abl_Scale_err = 30e-4  # [cm]
    # Fraction of CH mixed into the hot spot
    def_f_Mix = 0.005
    def_f_Mix_err = 0.005
    # thickness of the shell in-flight
    def_t_Shell = 40e-4  # [cm]
    def_t_Shell_err = 10e-4
    # mass remaining of the shell:
    def_f_Remain = 0.15  # fractional
    def_f_Remain_err = 0.05

    # initial proton energy:
    def_E0 = 14.7


    def __init__(self,
                 shell_mat='CH',
                 Ri=def_Ri, Ri_err=def_Ri_err,
                 Ro=def_Ro, Ro_err=def_Ro_err,
                 fD=def_fD, fD_err=def_fD_err,
                 f3He=def_f3He, f3He_err=def_f3He_err,
                 P0=def_P0, P0_err=def_P0_err,
                 Te_Gas=def_Te_Gas, Te_Gas_err=def_Te_Gas_err,
                 Te_Shell=def_Te_Shell, Te_Shell_err=def_Te_Shell_err,
                 Te_Abl=def_Te_Abl, Te_Abl_err=def_Te_Abl_err,
                 Te_Mix=def_Te_Mix, Te_Mix_err=def_Te_Mix_err,
                 rho_Abl_Max=def_rho_Abl_Max, rho_Abl_Max_err=def_rho_Abl_Max_err,
                 rho_Abl_Min=def_rho_Abl_Min, rho_Abl_Min_err=def_rho_Abl_Min_err,
                 rho_Abl_Scale=def_rho_Abl_Scale, rho_Abl_Scale_err=def_rho_Abl_Scale_err,
                 f_Mix=def_f_Mix, f_Mix_err=def_f_Mix_err,
                 t_Shell=def_t_Shell, t_Shell_err=def_t_Shell_err,
                 f_Remain=def_f_Remain, f_Remain_err=def_f_Remain_err,
                 E0=def_E0,
                 dEdx_model='LP'):
        """Initialize the rhoR model."""
        self.shell_mat = shell_mat  # shell material

        # set the error bars appropriately:
        self.Ri_err = Ri_err
        self.Ro_err = Ro_err
        self.fD_err = fD_err
        self.f3He_err = f3He_err
        self.P0_err = P0_err
        self.Te_Gas_err = Te_Gas_err
        self.Te_Shell_err = Te_Shell_err
        self.Te_Abl_err = Te_Abl_err
        self.Te_Mix_err = Te_Mix_err
        self.rho_Abl_Max_err = rho_Abl_Max_err
        self.rho_Abl_Min_err = rho_Abl_Min_err
        self.rho_Abl_Scale_err = rho_Abl_Scale_err
        self.f_Mix_err = f_Mix_err
        self.t_Shell_err = t_Shell_err
        self.f_Remain_err = f_Remain_err

        # set the values themselves to be python lists
        # [min, nom, max]
        self.Ri = [Ri - self.Ri_err, Ri, Ri + self.Ri_err]
        self.Ro = [Ro - self.Ro_err, Ro, Ro + self.Ro_err]
        self.fD = [fD - self.fD_err, fD, fD + self.fD_err]
        self.f3He = [f3He - self.f3He_err, f3He, f3He + self.f3He_err]
        self.P0 = [P0 - self.P0_err, P0, P0 + self.P0_err]
        self.Te_Gas = [Te_Gas - self.Te_Gas_err, Te_Gas, Te_Gas + self.Te_Gas_err]
        self.Te_Shell = [Te_Shell - self.Te_Shell_err, Te_Shell, Te_Shell + self.Te_Shell_err]
        self.Te_Abl = [Te_Abl - self.Te_Abl_err, Te_Abl, Te_Abl + self.Te_Abl_err]
        self.Te_Mix = [Te_Mix - self.Te_Mix_err, Te_Mix, Te_Mix + self.Te_Mix_err]
        self.rho_Abl_Max = [rho_Abl_Max - self.rho_Abl_Max_err, rho_Abl_Max, rho_Abl_Max + self.rho_Abl_Max_err]
        self.rho_Abl_Min = [rho_Abl_Min - self.rho_Abl_Min_err, rho_Abl_Min, rho_Abl_Min + self.rho_Abl_Min_err]
        self.rho_Abl_Scale = [rho_Abl_Scale - self.rho_Abl_Scale_err, rho_Abl_Scale,
                              rho_Abl_Scale + self.rho_Abl_Scale_err]
        self.f_Mix = [f_Mix - self.f_Mix_err, f_Mix, f_Mix + self.f_Mix_err]
        self.t_Shell = [t_Shell - self.t_Shell_err, t_Shell, t_Shell + self.t_Shell_err]
        self.f_Remain = [f_Remain - self.f_Remain_err, f_Remain, f_Remain + self.f_Remain_err]
        self.E0 = E0
        self.dEdx_model = dEdx_model

        # start the rhoR model itself:
        self.model = rhoR_Model(self.shell_mat, Ri, Ro, fD, f3He, P0, Te_Gas, Te_Shell, Te_Abl, Te_Mix, rho_Abl_Max,
                                rho_Abl_Min, rho_Abl_Scale, f_Mix, t_Shell, f_Remain, E0, dEdx_model)

        # a list of all parameters
        self.AllParam = []

        # a big python list of models where parameters are varied systematically
        self.__varied_models__ = []  # a 2-D array containing models with varied parameters
        self.__varied_model_names__ = []  # strings containing descriptions of which param was varied for the above

        # set up the models for error bar calculations:
        try:
            self.__setup_error_models__()
        except ValueError:
            raise ValueError("One of the error bars passed to the rhoR_Analysis was too big relative to its corresponding value")

    def Eout(self, Rcm) -> tuple:
        """Main function, which calculates the proton energy downshift.

        :param Rcm: shell radius at shock BT [cm]
        :returns: Eout, error = final proton energy and its error bar [MeV]
        """
        TotalError = self.__calc_error__("Eout", Rcm, breakdown=True)
        return self.model.Eout(Rcm), TotalError

    def Calc_rhoR(self, E1, dE=0, breakdown=False) -> tuple:
        """Alternative analysis method: specify measured E and calc rhoR.

        :param E1: Measured proton energy [MeV]
        :param dE: Uncertainty in measured proton energy [MeV]
        :param breakdown: Whether to provide a summary of the sources of error [default = false]
        :returns: tuple containing (rhoR , Rcm , rhoR error) = modeled areal density to produce modeled E
        """
        rhoR, Rcm = self.model.Calc_rhoR(E1)

        ModelError = self.__calc_error__("Calc_rhoR", Rcm, E1, breakdown=breakdown)
        # Two cases: non-zero user-supplied error bar, or model error only:
        if dE > 0:
            rhoR_min = self.model.Calc_rhoR(min(E1+dE, self.E0))[0]
            rhoR_max = self.model.Calc_rhoR(    E1-dE          )[0]
            TotalError = numpy.sqrt(0.25*(rhoR_max-rhoR_min)**2 + ModelError**2)
        else:
            TotalError = ModelError
        return rhoR, Rcm, TotalError

    def rhoR_Total(self, Rcm) -> tuple:
        """Calculate the total rhoR when the shell is at a given position.

        :param Rcm: shell radius [cm]
        :returns: tuple containing (rhoR,error) with error due to the model
        """
        TotalError = self.__calc_error__("rhoR_Total", Rcm)
        return self.model.rhoR_Total(Rcm), TotalError

    def rhoR_Parts(self, Rcm) -> tuple:
        """Calculate the three components of rhoR.

        :param Rcm: shell radius at shock BT [cm]
        :returns: the three components of rhoR
        """
        #TotalError = self.__calc_error__("rhoR_Parts",Rcm)
        return self.model.rhoR_Parts(Rcm)  # TotalError

    def Calc_Rcm(self, E1, dE, ModelErr=True) -> tuple:
        """Calculate the shell Rcm.

        :param E1: the measured energy [MeV]
        :param dE: the energy uncertainty [MeV]
        :param ModelErr: (optional) whether to include model errors {default=True}
        :returns: a tuple containing (Rcm,Uncertainty)
        """
        rhoR, Rcm = self.model.Calc_rhoR(E1)

        # error due to the rhoR model:
        if ModelErr:
            RcmModelErr = self.__calc_error__("Calc_rhoR_Rcm", 0, E1)
        else:
            RcmModelErr = 0

        # error due to dE, on low energy side:
        Rcm_Emin = numpy.copy(Rcm)
        Emin = E1
        while Emin > (E1 - dE):
            Rcm_Emin -= 1e-4
            Emin = self.Eout(Rcm_Emin)[0]

        # error due to dE, on high energy side:
        Rcm_Emax = numpy.copy(Rcm)
        Emax = E1
        while Emax < (E1 + dE):
            Rcm_Emax += 1e-4
            Emax = self.Eout(Rcm_Emax)[0]

        # Calculate a quadrature sum total error:
        TotalError = math.sqrt(RcmModelErr ** 2 + 0.25*(Rcm_Emax - Rcm_Emin) ** 2)
        return Rcm, TotalError

    def __setup_error_models__(self):
        """Set up extra models corresponding to varying each parameter."""
        # clear, just in case:
        self.__varied_models__ = []
        self.__varied_model_names__ = []

        # Vary the inner radius:
        new_set = []
        for Ri in [self.Ri[0], self.Ri[2]]:  # vary inner radius:
            new_set.append(rhoR_Model(self.shell_mat, Ri, self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Ri')

        # Vary the outer radius:
        new_set = []
        for Ro in [self.Ro[0], self.Ro[2]]:  # vary Ro:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], Ro, self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Ro')

        # Vary the deuterium fraction:
        new_set = []
        for fD in [self.fD[0], self.fD[2]]:  # vary fD:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], fD, self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('fD')

        # Vary the 3He fraction::
        new_set = []
        for f3He in [self.f3He[0], self.f3He[2]]:  # vary f3He:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], f3He, self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('f3He')

        # Vary the initial pressure:
        new_set = []
        for P0 in [self.P0[0], self.P0[2]]:  # vary P0:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], P0,
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('P0')

        # Vary the gas electron temperature:
        new_set = []
        for Te_Gas in [self.Te_Gas[0], self.Te_Gas[2]]:  # vary Te_Gas:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      Te_Gas, self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Gas Te')

        # Vary the shell electron temperature:
        new_set = []
        for Te_Shell in [self.Te_Shell[0], self.Te_Shell[2]]:  # vary Te_Shell:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], Te_Shell, self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Shell Te')

        # Vary the ablated material electron temp:
        new_set = []
        for Te_Abl in [self.Te_Abl[0], self.Te_Abl[2]]:  # vary Te_Abl:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], Te_Abl, self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Ablated Te')

        # Vary the Te_Mix:
        new_set = []
        for Te_Mix in [self.Te_Mix[0], self.Te_Mix[2]]:  # vary Te_Mix:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], Te_Mix,
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Mix Te')

        # Vary the maximum ablated material density:
        new_set = []
        for rho_Abl_Max in [self.rho_Abl_Max[0], self.rho_Abl_Max[2]]:  # vary rho_Abl_Max:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      rho_Abl_Max, self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Abl mass max rho')

        # Vary the minimum ablated mass density:
        new_set = []
        for rho_Abl_Min in [self.rho_Abl_Min[0], self.rho_Abl_Min[2]]:  # vary rho_Abl_Min:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], rho_Abl_Min, self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Abl mass min rho')

        # Vary the ablated mass scale length:
        new_set = []
        for rho_Abl_Scale in [self.rho_Abl_Scale[0], self.rho_Abl_Scale[2]]:  # vary rho_Abl_Scale:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], rho_Abl_Scale, self.f_Mix[1],
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Abl mass exp scale')

        # Vary the mix fraction:
        new_set = []
        for f_Mix in [self.f_Mix[0], self.f_Mix[2]]:  # vary f_Mix:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], f_Mix,
                                      self.t_Shell[1], self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Mix fraction')

        # Vary the shell thickness:
        new_set = []
        for t_Shell in [self.t_Shell[0], self.t_Shell[2]]:  # vary t_Shell:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      t_Shell, self.f_Remain[1], self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Shell Thickness')

        # Vary the mass remaining::
        new_set = []
        for f_Remain in [self.f_Remain[0], self.f_Remain[2]]:  # vary f_Remain:
            new_set.append(rhoR_Model(self.shell_mat, self.Ri[1], self.Ro[1], self.fD[1], self.f3He[1], self.P0[1],
                                      self.Te_Gas[1], self.Te_Shell[1], self.Te_Abl[1], self.Te_Mix[1],
                                      self.rho_Abl_Max[1], self.rho_Abl_Min[1], self.rho_Abl_Scale[1], self.f_Mix[1],
                                      self.t_Shell[1], f_Remain, self.E0))
        self.__varied_models__.append(new_set)
        self.__varied_model_names__.append('Mass Remaining')

    def __call_func__(self, model, func, Rcm, E1=0):
        """Helper function for calculating errors. Calls an appropriate function of the model.

        :param model: The model object to call
        :param func: A string containing the function to call
        :param Rcm: The center of mass radius of the shell [cm]
        :param E1: (optional) second energy value to be passed to the function [MeV]
        """
        if func == "Eout":
            return model.Eout(Rcm)
        if func == "Calc_rhoR":
            return model.Calc_rhoR(E1)[0]
        if func == "Calc_rhoR_Rcm":
            return model.Calc_rhoR(E1)[1]
        if func == "rhoR_Total":
            return model.rhoR_Total(Rcm)
        if func == "rhoR_Parts":
            return model.rhoR_Parts(Rcm)

    def __calc_error__(self, func, Rcm, E1=0, breakdown=False):
        """Helper function for calculating error bars due to uncertainties in model assumptions.

        :param func: The functional to call (i.e. Eout)
        :param Rcm: The center of mass radius [cm]
        :param E1: (optional) The energy to pass to func [MeV]
        :param breakdown: (optional) Whether to provide a summary of the sources of error [default = false]
        """
        if self.verbose:
            print("--------------")
        # list of error bars for various parameters:
        TotalError = 0
        sources = []

        # calculate nominal value:
        nominal = self.__call_func__(self.model, func, Rcm, E1)

        # iterate through all models
        for row in range(len(self.__varied_models__)):
            values = []
            for model in self.__varied_models__[row]:
                values.append(self.__call_func__(model, func, Rcm, E1))

            # calculate the error bar, if valid:
            if numpy.nan not in values:
                val_max = math.fabs(max(values))
                val_min = math.fabs(min(values))
                err = (val_max - val_min) / 2.0
                if self.verbose:
                    print(values, err)
                TotalError += numpy.absolute(err**2.0)

                # if requested, keep track of error sources:
                if breakdown:
                    sources.append([self.__varied_model_names__[row], err])

        # Calculate quadrature sum of Errors, i.e. total error bar:
        TotalError = numpy.sqrt(TotalError)

        # return sources of error if requested:
        if breakdown:
            return TotalError, sources

        # default, just return total error:
        return TotalError
