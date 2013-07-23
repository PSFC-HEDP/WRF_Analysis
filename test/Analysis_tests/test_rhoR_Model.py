from unittest import TestCase
from Analysis.rhoR_Model import rhoR_Model
from numpy import arange

__author__ = 'alex'


class TestRhoR_Model(TestCase):
    """Test the rhoR model itself.
    :author: Alex Zylstra
    :date: 2013/06/15
    """

    # a model to play with
    model = rhoR_Model()  # using the default values for everything

    # try a few parameters:
    Ri = model.Ri
    Rcm = [Ri / 7., Ri / 6., Ri / 5., Ri / 4., Ri / 2.]
    Eout = [5.0, 7.5, 10.0, 12.5]

    def test_Eout(self):
        """Test the function which calculates Eout for given Rcm."""
        # try all:
        for R in self.Rcm:
            Eout = self.model.Eout(R)
            self.assertTrue(0 <= Eout <= 14.7, "Failed test of Eout for [Rcm=" + str(R)
                                               + ", E0=" + str(14.7) + "]" +
                                               "\n got Eout = " + str(Eout))

    def test_Calc_rhoR(self):
        """Test the rhoR calculator given measured & incident energy."""
        # try all:
        for E in self.Eout:
            rhoR = self.model.Calc_rhoR(E)[0]
            self.assertTrue(0 <= rhoR <= 1.0, "Failed test of Calc_rhoR for [E=" + str(E) + "]"
                                              + "\n got: " + str(rhoR))

    def test_rho_Gas(self):
        """Test getting the gas mass density."""
        # try all:
        for R in self.Rcm:
            rho = self.model.rho_Gas(R)
            self.assertTrue(0 <= rho <= 1e3, "Failed test of rho_Gas for [Rcm=" + str(R) + "]")

    def test_rhoR_Gas(self):
        """Test getting the gas areal density."""
        # try all:
        for R in self.Rcm:
            rhoR = self.model.rhoR_Gas(R)
            self.assertTrue(0 <= rhoR <= 0.3, "Failed test of rhoR_Gas for [Rcm=" + str(R) + "]")

    def test_n_Gas(self):
        """Test getting the gas number density."""
        # try all:
        for R in self.Rcm:
            ni, ne = self.model.n_Gas(R)
            self.assertTrue(1e20 <= ni <= 1e26, "Failed test of n_Gas for [Rcm=" + str(R) + "]" +
                                                "\n got ni,ne = " + str(ni) + "," + str(ne))
            self.assertTrue(ne >= ni, "Failed test of n_Gas for [Rcm=" + str(R) + "]")

    def test_rho_Mix(self):
        """Test getting the mix mass density."""
        # try all:
        for R in self.Rcm:
            rho = self.model.rho_Mix(R)
            self.assertTrue(0 <= rho <= 1e3, "Failed test of rho_Mix for [Rcm=" + str(R) + "]")

    def test_rhoR_Mix(self):
        """Test getting the mix areal density."""
        # try all:
        for R in self.Rcm:
            rhoR = self.model.rhoR_Mix(R)
            self.assertTrue(0 <= rhoR <= 0.3, "Failed test of rhoR_Mix for [Rcm=" + str(R) + "]")

    def test_n_Mix(self):
        """Test getting the mix number density."""
        # try all:
        for R in self.Rcm:
            ni, ne = self.model.n_Mix(R)
            self.assertTrue(0 <= ni <= 1e25, "Failed test of n_Mix for [Rcm=" + str(R) + "]")
            self.assertTrue(ne >= ni, "Failed test of n_Mix for [Rcm=" + str(R) + "]")

    def test_rho_Shell(self):
        """Test getting the shell density."""
        # try all:
        for R in self.Rcm:
            rho = self.model.rho_Shell(R)
            self.assertTrue(0 <= rho <= 1e3, "Failed test of rho_Shell for [Rcm=" + str(R) + "]")

    def test_rhoR_Shell(self):
        """Test getting the shell areal density."""
        # try all:
        for R in self.Rcm:
            rhoR = self.model.rhoR_Shell(R)
            self.assertTrue(0 <= rhoR <= 1, "Failed test of rhoR_Shell for [Rcm=" + str(R) + "]")

    def test_n_Shell(self):
        """Test getting the shell number density."""
        # try all:
        for R in self.Rcm:
            ni, ne = self.model.n_Shell(R)
            self.assertTrue(1e22 <= ni <= 1e26, "Failed test of n_Shell for [Rcm=" + str(R) + "]")
            self.assertTrue(ne >= ni, "Failed test of n_Shell for [Rcm=" + str(R) + "]")

    def test_get_Abl_radii(self):
        """Test getting the ablated radii"""
        # try all:
        for R in self.Rcm:
            r1, r2, r3 = self.model.get_Abl_radii(R)
            self.assertTrue(r3 > r2 > r1 > 0 and r3 < 3 * self.model.Ro,
                            "Failed test of ablated radii. Got: "
                            + str(r1) + "," + str(r2) + "," + str(r3) +
                            "; for params Rcm = " + str(R))

    def test_rho_Abl(self):
        """Test getting the ablated mass density."""
        # try all:
        for R in self.Rcm:
            r1, r2, r3 = self.model.get_Abl_radii(R)
            for r in arange(r1, r3, (r3 - r2) / 25.):
                rho = self.model.rho_Abl(r, R)
                self.assertTrue(self.model.rho_Abl_Min <= rho <= self.model.rho_Abl_Max,
                                "Failed ablated mass density at r,Rcm = " +
                                str(r) + "," + str(R) +
                                "\n got rho = " + str(rho))

    def test_rhoR_Abl(self):
        """Test getting the ablated mass areal density."""
        # try all:
        for R in self.Rcm:
            rhoR = self.model.rhoR_Abl(R)
            self.assertTrue(0 <= rhoR <= 1, "Failed test of rhoR_Abl for [Rcm=" + str(R) + "]")

    def test_n_Abl(self):
        """Test getting the ablated mass number density."""
        # try all:
        for R in self.Rcm:
            r1, r2, r3 = self.model.get_Abl_radii(R)
            for r in arange(r1, r3, (r3 - r1) / 25.):
                ni, ne = self.model.n_Abl(r, R)
                self.assertTrue(0 <= ni <= 1e24, "Failed test of n_Abl for [Rcm=" + str(R) + "]" +
                                                 "\n got ni,ne = " + str(ni) + "," + str(ne))
                self.assertTrue(ne >= ni, "Failed test of n_Abl for [Rcm=" + str(R) + "]")

    def test_rhoR_Total(self):
        """Test getting the total rhoR."""
        # try all:
        for R in self.Rcm:
            rhoR = self.model.rhoR_Total(R)
            self.assertTrue(0 <= rhoR <= 2, "Failed test of rhoR_Total for [Rcm=" + str(R) + "]")


    def test_rhoR_Parts(self):
        """Test getting the components of rhoR"""
        # try all:
        for R in self.Rcm:
            gas, shell, abl = self.model.rhoR_Parts(R)
            rhoR = self.model.rhoR_Total(R)
            self.assertTrue(rhoR == gas + shell + abl and gas > 0 and shell > 0 and abl > 0,
                            "Failed test of rhoR_Parts for [Rcm=" + str(R) + "]")

    def test_Eout_GasMix(self):
        """Test getting the gas mixture energy out."""
        EpList = [12.5, 15.0, 17.5]
        xList = [50, 100, 150, 200]
        for Ep in EpList:
            for x in xList:
                for R in self.Rcm:
                    Eout = self.model.Eout_GasMix(Ep, x, R)
                    self.assertTrue(0 <= Eout < Ep, "Failed Eout_GasMix at conditions Ep, x, R, T = " +
                                                    str(Ep) + "," + str(x) + "," + str(R))

    def test_Eout_Shell(self):
        """Test getting the downshift through the shell."""
        EpList = [10.0, 12.5, 15.0, 17.5]
        xList = [5, 10, 20, 30, 40]
        for Ep in EpList:
            for x in xList:
                for R in self.Rcm:
                    Eout = self.model.Eout_Shell(Ep, x, R)
                    self.assertTrue(0 <= Eout < Ep, "Failed Eout_Shell at conditions Ep, x, R, = " +
                                                    str(Ep) + "," + str(x) + "," + str(R))

    def test_dEdr_Abl(self):
        """Test getting the stopping power in the ablated material."""
        EpList = [10.0, 12.5, 15.0, 17.5]
        for Ep in EpList:
            for R in self.Rcm:
                for r in arange(R / 20., 0.9 * R, R / 50.):
                    Eout = self.model.dEdr_Abl(Ep, r, R)
                    self.assertTrue(0 <= Eout < Ep, "Failed dEdr_Abl at conditions Ep, r, R, = " +
                                                    str(Ep) + "," + str(r) + "," + str(R))