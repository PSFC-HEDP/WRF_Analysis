import math
import scipy
import scipy.interpolate
#try:
#    import scipy.interpolate
#except:
#    import syslog
#    syslog.syslog(syslog.LOG_ALERT, 'Error loading scipy submodule(s)')
import numpy
from NIF_WRF.util.Constants import *
from NIF_WRF.util.StopPow import StopPow_LP, DoubleVector

__author__ = 'Alex Zylstra'


class rhoR_Model(object):
    """3-part (shell, fuel, ablated mass) rhoR model. Arguments taken here are primarily shot-dependent initial conditions.

    :param shell_mat: (optional) the shell material to use {default='CH'}
    :param Ri: (optional) initial shell inner radius [cm] {default=0.09}
    :param Ro: (optional) initial shell outer radius [cm] {default=0.11}
    :param fD: (optional) deuterium atomic fraction in the fuel [fractional] {default=0.3}
    :param f3He: (optional) 3He atomic fraction in the fuel [fractional] {default=0.7}
    :param P0: (optional) initial gas fill pressure [atm] {default=50}
    :param Te_Gas: (optional) gas electron temperature [keV] {default=1}
    :param Te_Shell: (optional) shell electron temperature [keV] {default=0.2}
    :param Te_Abl: (optional) ablated mass electron temperature [keV] {default=0.3}
    :param Te_Mix: (optional) mix mass electron temperature [keV] {default=0.3}
    :param rho_Abl_Max: (optional) maximum density in the ablated mass [g/cc] {default=1.5}
    :param rho_Abl_Min: (optional) minimum density in the ablated mass [g/cc] {default=0.1}
    :param rho_Abl_Scale: (optional) scale length for the ablated mass [cm] {default=70e-4}
    :param MixF: (optional) amount of shell material mixed into the fuel [fractional] {default=0.025}
    :param Tshell: (optional) thickness of the shell in-flight [cm] {default = 40e-4}
    :param Mrem: (optional) mass remaining of the in-flight shell [fractional] {default=0.15}
    :param E0: (optional) initial proton energy [MeV] {default=14.7}
    :author: Alex Zylstra
    :date: 2013/09/04
    """

    # values below are defaults
    # anything beginning with a def_ is replaced with a class variable

    # initial shell conditions:
    def_Ri = 900e-4  # initial inner radius [cm]
    def_Ro = 1100e-4  # initial outer radius [cm]
    def_P0 = 50  # initial pressure [atm]
    def_fD = 0.3  # deuterium fraction in fuel
    def_f3He = 0.7  # 3He fraction in fuel

    # a few densities and masses for the shell
    def_shell_mat = 'CH'
    # CH = standard plastic
    # HDC = diamond
    # SiO2 = standard glass
    # Be = standard beryllium
    # CHGe = standard plastic, with 0.5% Ge dopant, same mass density
    # CHSi = standard plastic, with 1.0% Si dopant, same mass density
    # plastic with higher hydrogen content
    shell_opts = ['CH', 'HDC', 'SiO2', 'Be', 'CHGe', 'CHSi', 'CHSi2x', 'CH2']

    __shell_rho__ = {   'CH': 1.084, 
                        'HDC': 3.5, 
                        'SiO2': 2.56, 
                        'Be': 1.85, 
                        'CHGe': 1.084, 
                        'CHSi': 1.084,
                        'CHSi2x': 1.084,
                        'CH2': 1.084}

    __shell_A__ = {     'CH': [1,12,16], 
                        'HDC': [12], 
                        'SiO2': [28,16], 
                        'Be': [9],
                        'CHGe': [1,12,16,72.6],
                        'CHSi': [1,12,16,28.1],
                        'CHSi2x': [1,12,16,28.1],
                        'CH2': [1,12]}

    __shell_AvgA__ = {  'CH': 5.728, 
                        'HDC': 12., 
                        'SiO2': 20., 
                        'Be': 9.,
                        'CHGe': 5.862,
                        'CHSi': 5.817,
                        'CHSi2x': 5.906,
                        'CH2': 4.66}

    __shell_Z__ = {     'CH': [1,6,8], 
                        'HDC': [6], 
                        'SiO2': [14,8], 
                        'Be': [4],
                        'CHGe': [1,6,8,32],
                        'CHSi': [1,6,8,14],
                        'CHSi2x': [1,6,8,14],
                        'CH2': [1,6]}

    __shell_AvgZ__ = {  'CH': 3.19, 
                        'HDC': 6., 
                        'SiO2': 10., 
                        'Be': 4.,
                        'CHGe': 3.248,
                        'CHSi': 3.233,
                        'CHSi2x': 3.276,
                        'CH2': 2.665}

    __shell_F__ = {     'CH': [0.572,0.423,0.005], 
                        'HDC': [1], 
                        'SiO2': [0.333,0.667], 
                        'Be': [1],
                        'CHGe': [0.571,0.422,0.005,0.002],
                        'CHSi': [0.570,0.421,0.005,0.004],
                        'CHSi2x': [0.567,0.419,0.006,0.008],
                        'CH2': [0.667,0.333]}

    # some info for the gas:
    rho_D2_STP = 2 * 0.08988e-3  # density of D2 gas at STP [g/cc]
    rho_3He_STP = (3 / 4) * 0.1786e-3  # density of 3he gas at STP [g/cc]
    # rho0_Gas = 0  # initial gas density [atm]

    # total masses in the system:
    #def_Mass_Shell_Total = 0  # total mass of shell in the implosion [g]
    #def_Mass_Mix_Total = 0  # total mix mass [g]

    # ASSUMED CONDITIONS
    def_Te_Gas = 3  # keV
    def_Te_Shell = 0.2  # keV
    def_Te_Abl = 0.3  # keV
    def_Te_Mix = 1  # keV
    # ablated mass is modeled as an exponential profile
    # specified by max, min, and length scale:
    def_rho_Abl_Max = 1.5  # g/cc
    def_rho_Abl_Min = 0.1  # g/cc
    def_rho_Abl_Scale = 70e-4  # [cm]
    # Fraction of CH mixed into the hot spot
    def_MixF = 0.005
    # thickness of the shell in-flight
    def_Tshell = 40e-4  # [cm]
    # mass remaining of the shell:
    def_Mrem = 0.15  # fractional

    # initial proton energy:
    def_E0 = 14.7

    # options for stop pow calculations:
    steps = 100  # steps in radius per region

    def __init__(self, shell_mat='CH', Ri=9e-2, Ro=11e-2, fD=0.3, f3He=0.7, P0=50,
                 Te_Gas=3, Te_Shell=0.2, Te_Abl=0.3, Te_Mix=1,
                 rho_Abl_Max=1.5, rho_Abl_Min=0.1, rho_Abl_Scale=70e-4, MixF=0.005,
                 Tshell=40e-4, Mrem=0.15, E0=14.7):
        """Initialize the rhoR model."""
        self.shell_mat = shell_mat
        self.Ri = Ri
        self.Ro = Ro
        self.fD = fD
        self.f3He = f3He
        self.P0 = P0
        self.Te_Gas = Te_Gas
        self.Te_Shell = Te_Shell
        self.Te_Abl = Te_Abl
        self.Te_Mix = Te_Mix
        self.rho_Abl_Max = rho_Abl_Max
        self.rho_Abl_Min = rho_Abl_Min
        self.rho_Abl_Scale = rho_Abl_Scale
        self.MixF = MixF
        self.Tshell = Tshell
        self.Mrem = Mrem
        self.E0 = E0

        # calculate initial gas density in g/cc
        self.rho0_Gas = P0 * ((fD / 2) * self.rho_D2_STP + f3He * self.rho_3He_STP)

        # calculate initial masses:
        # total mass of shell in the implosion [g]
        self.Mass_Shell_Total = (4 * math.pi / 3) * self.__shell_rho__[self.shell_mat] * (Ro ** 3 - Ri ** 3)
        # mix mass in g:
        self.Mass_Mix_Total = self.Mass_Shell_Total * self.MixF

        # set up stopping power definitions
        # for the downshift calculations
        # shell material shorthand:
        A = self.__shell_A__[self.shell_mat]
        Z = self.__shell_Z__[self.shell_mat]
        # Set up DoubleVectors for gas plus mix stopping power
        self.__mfGasMix__ = DoubleVector(3+len(A))  # eg e-, D , 3He , H , C
        self.__mfGasMix__[0] = me / mp
        self.__mfGasMix__[1] = 2
        self.__mfGasMix__[2] = 3
        for i in range(len(A)):
            self.__mfGasMix__[3+i] = A[i]
        self.__ZfGasMix__ = DoubleVector(3+len(A))  # eg e-, D , 3He , H , C
        self.__ZfGasMix__[0] = -1
        self.__ZfGasMix__[1] = 1
        self.__ZfGasMix__[2] = 2
        for i in range(len(Z)):
            self.__ZfGasMix__[3+i] = Z[i]
        self.__TfGasMix__ = DoubleVector(3+len(A))  # eg e-, D , 3He , H , C
        self.__TfGasMix__[0] = self.Te_Gas
        self.__TfGasMix__[1] = self.Te_Gas
        self.__TfGasMix__[2] = self.Te_Gas
        for i in range(len(Z)):
            self.__TfGasMix__[3+i] = self.Te_Mix

        # some field particle info for the shell stopping power:
        self.__mfShell__ = DoubleVector(1+len(A))
        self.__mfShell__[0] = me / mp
        for i in range(len(A)):
            self.__mfShell__[1+i] = A[i]
        self.__ZfShell__ = DoubleVector(1+len(Z))
        self.__ZfShell__[0] = -1
        for i in range(len(Z)):
            self.__ZfShell__[1+i] = Z[i]
        self.__TfShell__ = DoubleVector(1+len(A))
        for i in range(1+len(A)):
            self.__TfShell__[i] = Te_Shell

        # field particle info for the ablated material stopping power:
        self.__mfAbl__ = DoubleVector(1+len(A))
        self.__mfAbl__[0] = me / mp
        for i in range(len(A)):
            self.__mfAbl__[1+i] = A[i]
        self.__ZfAbl__ = DoubleVector(1+len(Z))
        self.__ZfAbl__[0] = -1
        for i in range(len(Z)):
            self.__ZfAbl__[1+i] = Z[i]
        self.__TfAbl__ = DoubleVector(1+len(A))
        for i in range(1+len(A)):
            self.__TfAbl__[i] = self.Te_Abl

        # set up arrays for precomputed data for a few things:
        self.__RcmList__ = []
        self.__EoutList__ = []
        self.__rhoRList__ = []
        self.__interp_Eout__ = 0
        self.__interp_rhoR__ = 0
        self.__interp_Rcm__ = 0

        # precompute Eout and rhoR vs Rcm
        r = self.Ri
        dr = r/50.
        Eout = self.__precompute_Eout__(r)
        while Eout > 0.:
            Eout = self.__precompute_Eout__(r)
            rhoR = self.rhoR_Total(r)
            if Eout >= 0.:
                self.__RcmList__.append(r)
                self.__EoutList__.append(Eout)
                self.__rhoRList__.append(rhoR)

            # decrement r:
            r -= dr
            dr = r/50.

        # have to flip the arrays to make spline happy:
        self.__RcmList__ = self.__RcmList__[::-1]
        self.__EoutList__ = self.__EoutList__[::-1]
        self.__rhoRList__ = self.__rhoRList__[::-1]
        # also cut off one:
        self.__RcmList__ = self.__RcmList__[1:]
        self.__EoutList__ = self.__EoutList__[1:]
        self.__rhoRList__ = self.__rhoRList__[1:]

        # set up interpolation:
        self.__interp_Eout__ = scipy.interpolate.interp1d(self.__RcmList__, self.__EoutList__, kind='linear', bounds_error=True)
        self.__interp_Rcm__ = scipy.interpolate.interp1d(self.__EoutList__, self.__RcmList__, kind='linear', bounds_error=True)
        self.__interp_rhoR__ = scipy.interpolate.interp1d(self.__RcmList__, self.__rhoRList__, kind='linear', bounds_error=True)


    def Eout(self, Rcm) -> float:
        """Main function, which calculates the proton energy downshift.

        :param Rcm: shell radius at shock BT [cm]
        :returns: the final proton energy [MeV]
        """
        Eout = numpy.nan
        try:
            Eout = self.__interp_Eout__(Rcm)
        except ValueError:
            Eout = numpy.nan
        return Eout

    def __precompute_Eout__(self, Rcm) -> float:
        """Main function, which calculates the proton energy downshift.

        :param Rcm: shell radius at shock BT [cm]
        :returns: the final proton energy [MeV]
        """
        E = self.E0
        # range through gas+mix:
        dr = 1e4 * (Rcm - self.Tshell / 2)  # length in um
        E = self.Eout_GasMix(E, dr, Rcm)

        #range through shell:
        dr = 1e4 * self.Tshell
        E = self.Eout_Shell(E, dr, Rcm)

        #range through ablated mass gradient:
        r1, r2, r3 = self.get_Abl_radii(Rcm)
        dr = (r2 - r1) / self.steps
        # have to do manually b/c of density gradient:
        for i in range(self.steps):
            E += dr * self.dEdr_Abl(E, r1 + dr * i, Rcm)
        # for the rest of the ablated mass, stopping power is constant:
        dEdr = self.dEdr_Abl(E, (r2+r3)/2, Rcm)
        dr = (r3 - r2) / self.steps
        # have to do manually b/c of density gradient:
        for i in range(self.steps):
            E += dr * dEdr

        return max(E, 0)

    def Calc_rhoR(self, E1) -> tuple:
        """Alternative analysis method: specify measured E and calculate rhoR.

        :param E1: Measured proton energy [MeV]
        :returns: model areal density to produced measured E [g/cm2], Rcm [cm]
        """
        # check limits:
        if E1 < min(self.__EoutList__) or E1 > max(self.__EoutList__):
            return numpy.nan, numpy.nan
        try:
            Rcm = self.__interp_Rcm__(E1)
            rhoR = self.rhoR_Total(Rcm)  #self.__interp_rhoR__(Rcm)

            return rhoR, Rcm
        except ValueError:
            return numpy.nan, numpy.nan

    # ----------------------------------------------------------------
    #         Calculators for rho, rhoR, n
    # ----------------------------------------------------------------
    def rho_Gas(self, Rcm) -> float:
        """Calculate gas density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: gas density [g/cc]
        """
        Rgas = Rcm - self.Tshell / 2
        return self.rho0_Gas * (self.Ri / Rgas) ** 3

    def rhoR_Gas(self, Rcm) -> float:
        """Calculate gas areal density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: the gas areal density [g/cm2]
        """
        Rgas = Rcm - self.Tshell / 2
        return self.rho0_Gas * Rgas * (self.Ri / Rgas) ** 3

    def n_Gas(self, Rcm) -> tuple:
        """Calculate particle number density in the gas.

        :param Rcm: shell radius at shock BT [cm]
        :returns: ni,ne [1/cc]
        """
        A = self.fD * 2 + self.f3He * 3
        ni = self.rho_Gas(Rcm) / (A * mp)
        Z = self.fD + self.f3He * 2
        ne = Z * ni
        return ni, ne

    def rho_Mix(self, Rcm) -> float:
        """Calculate the mix mass density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: mix mass density [g/cc]
        """
        V = (4 * math.pi / 3) * (Rcm - self.Tshell / 2) ** 3
        return self.Mass_Mix_Total / V

    def rhoR_Mix(self, Rcm,) -> float:
        """Calculate mix areal density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: mix mass areal density [g/cm2]"""
        V = (4 * math.pi / 3) * (Rcm - self.Tshell / 2) ** 3
        return (Rcm - self.Tshell / 2) * self.Mass_Mix_Total / V

    def n_Mix(self, Rcm) -> tuple:
        """Calculate mix number density

        :param Rcm: shell radius at shock BT [cm]
        :return: ni,ne [1/cc]
        """
        ni = self.rho_Mix(Rcm) / (self.__shell_AvgA__[self.shell_mat] * mp)
        ne = self.__shell_AvgZ__[self.shell_mat] * ni
        return ni, ne

    def rho_Shell(self, Rcm) -> float:
        """Calculate shell mass density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: mass density in the shell [g/cc]
        """
        m = self.Mass_Shell_Total * self.Mrem
        V = (4 * math.pi / 3) * ((Rcm + self.Tshell / 2) ** 3 - (Rcm - self.Tshell / 2) ** 3)
        return m / V

    def rhoR_Shell(self, Rcm) -> float:
        """Calculate the shell's areal density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: areal density [g/cm2]
        """
        m = self.Mass_Shell_Total * self.Mrem
        V = (4 * math.pi / 3) * ((Rcm + self.Tshell / 2) ** 3 - (Rcm - self.Tshell / 2) ** 3)
        return self.Tshell * m / V

    def n_Shell(self, Rcm) -> tuple:
        """Calculate particle number density in the shell.

        :param Rcm: shell radius at shock BT [cm]
        :returns: ni,ne [1/cc]
        """
        ni = self.rho_Shell(Rcm) / (self.__shell_AvgA__[self.shell_mat] * mp)
        ne = self.__shell_AvgZ__[self.shell_mat] * ni
        return ni, ne

    def get_Abl_radii(self, Rcm) -> tuple:
        """Helper function for the ablated mass profile
        Calculates the beginning, end of exp ramp, and final r
        of the profile

        :param Rcm: shell radius at shock BT [cm]
        :returns: r1,r2,r3 three radii [cm]
        """
        # density has an exponential ramp from max to min rho, then flat tail
        # as far out as necessary to conserve mass.
        m = self.Mass_Shell_Total * (1 - self.Mrem - self.MixF)
        r1 = Rcm + self.Tshell / 2  # start of ablated mass
        # end of exponential ramp:
        r2 = r1 + self.rho_Abl_Scale * math.log(self.rho_Abl_Max / self.rho_Abl_Min)
        # mass left in the "tail""
        scale = self.rho_Abl_Scale  # shorthand
        m23 = m - 4 * math.pi * scale * (2 * scale ** 2 + 2 * r1 * scale
                                         - math.exp((r1 - r2) / scale) * (2 * scale ** 2 + 2 * scale * r2 + r2 ** 2))
        if m23 > 0:
            r3 = (math.pow(3 * m23 + 4 * math.pi * r2 ** 3 * scale, 1 / 3)
                  / (math.pow(4 * math.pi * self.rho_Abl_Min, 1 / 3)))
        else:
            r3 = r2
        return r1, r2, r3

    def rho_Abl(self, r, Rcm) -> float:
        """Calculates the ablated mass density as a function of radius.

        :param r: the radius to calculate density at [cm]
        :param Rcm: shell radius at shock BT [cm]
        :returns: the mass density [g/cc]
        """
        r1, r2, r3 = self.get_Abl_radii(Rcm)

        # density is constructed piecewise, depending on where we are:
        if r1 <= r < r2:
            return self.rho_Abl_Max * math.exp(-(r - r1) / self.rho_Abl_Scale)
        if r2 <= r <= r3:
            return self.rho_Abl_Min
        return 0.

    def rhoR_Abl(self, Rcm) -> float:
        """Calculate the ablated mass areal density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: areal density [g/cm2]"""
        r1, r2, r3 = self.get_Abl_radii(Rcm)
        # integrate from r1 to r3
        #return scipy.integrate.quad(self.rho_Abl, r1, r3, args=(Rcm, self.Tshell, Mrem))[0]
        # contribution from exponential part:
        rhoR = self.rho_Abl_Max * self.rho_Abl_Scale * (1 - math.exp(-(r2-r1)/self.rho_Abl_Scale))
        # contribution from linear part:
        rhoR += (r3-r2)*self.rho_Abl_Min

        return rhoR

    def n_Abl(self, r, Rcm) -> tuple:
        """Calculate the ablated mass number density.

        :param Rcm: shell radius at shock BT [cm]
        :returns: ni,ne [1/cc] """
        ni = self.rho_Abl(r, Rcm) / (self.__shell_AvgA__[self.shell_mat] * mp)
        ne = self.__shell_AvgZ__[self.shell_mat] * ni
        return ni, ne

    def rhoR_Total(self, Rcm) -> float:
        """Calculate the total rhoR for given conditions.

        :param Rcm: shell radius at shock BT [cm]
        :returns: the total areal density [g/cm2]
        """
        ret = self.rhoR_Gas(Rcm)
        ret += self.rhoR_Mix(Rcm)
        ret += self.rhoR_Shell(Rcm)
        ret += self.rhoR_Abl(Rcm)
        return ret

    def rhoR_Parts(self, Rcm) -> tuple:
        """Get the three components of rhoR for given conditions.

        :param Rcm: shell radius at shock BT [cm]
        :returns: a tuple containing (fuel,shell,ablated) rhoR [g/cm2]
        """
        gas = self.rhoR_Gas(Rcm)
        gas += self.rhoR_Mix(Rcm)
        shell = self.rhoR_Shell(Rcm)
        abl = self.rhoR_Abl(Rcm)
        return gas, shell, abl

    # ----------------------------------------------------------------
    #         Calculators for stopping power
    # ----------------------------------------------------------------
    __mt__ = 1
    __Zt__ = 1

    def Eout_GasMix(self, Ep, x, Rcm) -> float:
        """Calculate gas+mix downshift for protons

        :param Ep: proton energy [MeV]
        :param x: path length [um]
        :param Rcm: shell radius at shock BT [cm]
        :returns: downshifted energy [MeV]
        """
        # sanity check:
        if x <= 0:
            return 0

        ni_gas, ne_gas = self.n_Gas(Rcm)
        ni_mix, ne_mix = self.n_Mix(Rcm)
        nf = DoubleVector(3+len(self.__shell_A__[self.shell_mat]))
        nf[0] = ne_gas + ne_mix
        nf[1] = ni_gas * self.fD
        nf[2] = ni_gas * self.f3He
        for i in range(len(self.__shell_F__[self.shell_mat])):
            nf[3+i] = ni_mix * self.__shell_F__[self.shell_mat][i]

        # if any densities are zero, it is problematic (no mix does this)
        # add 1 particle per cc minimum:
        for i in range(len(nf)):
            if nf[i] <= 0:
                nf[i] = 1

        # Use Li-Petrasso:
        if nf[0] > 0:  # with sanity check
            model = StopPow_LP(self.__mt__, self.__Zt__, self.__mfGasMix__, self.__ZfGasMix__, self.__TfGasMix__, nf)
            # check limits:
            if model.get_Emin() < Ep < model.get_Emax():
                return model.Eout(Ep, x)

        return Ep

    def Eout_Shell(self, Ep, x, Rcm) -> float:
        """Calculate downshift in the shell.

        :param Ep: proton energy [MeV]
        :param x: path length [um]
        :param Rcm: shell radius at shock BT [cm]
        :returns: downshifted energy [MeV]
        """
        ni, ne = self.n_Shell(Rcm)
        nf = DoubleVector(1+len(self.__shell_A__[self.shell_mat]))
        nf[0] = ne
        for i in range(len(self.__shell_F__[self.shell_mat])):
            nf[1+i] = ni * self.__shell_F__[self.shell_mat][i]

        # Use Li-Petrasso:
        if ne > 0:
            model = StopPow_LP(self.__mt__, self.__Zt__, self.__mfShell__, self.__ZfShell__, self.__TfShell__, nf)
            # check limits:
            if model.get_Emin() < Ep < model.get_Emax():
                return model.Eout(Ep, x)

        return Ep

    def dEdr_Abl(self, Ep, r, Rcm):
        """Calculate stopping power for protons in the ablated mass.

        :param Ep: proton energy [MeV]
        :param r: radius [cm]
        :param Rcm: shell radius at shock BT [cm]
        :returns: stopping power [MeV/cm]
        """
        ni, ne = self.n_Abl(r, Rcm)
        nf = DoubleVector(1+len(self.__shell_A__[self.shell_mat]))
        nf[0] = ne
        for i in range(len(self.__shell_F__[self.shell_mat])):
            nf[1+i] = ni * self.__shell_F__[self.shell_mat][i]

        # Use Li-Petrasso:
        if ne > 0:
            model = StopPow_LP(self.__mt__, self.__Zt__, self.__mfAbl__, self.__ZfAbl__, self.__TfAbl__, nf)
            # check limits:
            if model.get_Emin() < Ep < model.get_Emax():
                return 1e4 * model.dEdx(Ep)

        return Ep