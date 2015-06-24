from unittest import TestCase
from numpy import arange
from NIF_WRF.Analysis import rhoR_Analysis

__author__ = 'Alex Zylstra'


class TestRhoR_Analysis(TestCase):
    """Unit tests for the rhoR analysis module.
    :author: Alex Zylstra
    :date: 2013/06/16 """

    # class variable for analysis object
    a = rhoR_Analysis.rhoR_Analysis()  # use default values

    # for varying the center of mass radius in test methods:
    Ri = a.Ri[1]
    Rcm = [0.9*Ri, Ri/2, Ri/4, Ri/5, Ri/6]

    def test_Eout(self):
        """Test getting the energy out from a rhoR analysis."""
        # vary parameters for Rcm and E0:
        for R in self.Rcm:
            Eout = self.a.Eout(R)[0]
            self.assertTrue(0<=Eout<14.7, "Failed test of Eout for Rcm, E0 = " + str(R) + "," + str(14.7)
                            + "\n got Eout = " + str(Eout))

    def test_Calc_rhoR(self):
        """Test rhoR calculator from a rhoR analysis."""
        # vary initial energy:
        E0 = 14.7
        for E1 in arange(E0/3, E0/1.5, 10.):
            rhoR = self.a.Calc_rhoR(E1)[0]
            self.assertTrue(0<=rhoR<1, "Failed test of Calc_rhoR for E0, E1 = " + str(E0) + "," + str(E1)
                            + "\n got rhoR = " + str(rhoR))

    def test_rhoR_Total(self):
        """Test calculations of total rhoR with error bars."""
        for Rcm in self.Rcm:
            rhoR, err = self.a.rhoR_Total(Rcm)
            self.assertTrue(0<err<rhoR, "Failed test of rhoR_Total, got nonsense error bar for Rcm = " + str(Rcm)
                            + "\n got rhoR, err = " + str(rhoR) + "," + str(err))


    def test_rhoR_Parts(self):
        """Test calculation of rhoR components."""
        for Rcm in self.Rcm:
            rhoR, err = self.a.rhoR_Total(Rcm)
            fuel, shell, abl = self.a.rhoR_Parts(Rcm)

            self.assertTrue(rhoR==fuel+shell+abl, "Failed test of rhoR_Parts, does not add up for Rcm = " + str(Rcm)
                            + "\n got rhoR, err = " + str(rhoR) + "," + str(err)
                            + "\n got fuel, shell, abl mass rhoRs = " + str(fuel) + "," + str(shell) + "," + str(abl))


    def test_Calc_Rcm(self):
        """Test calculations of the center-of-mass radius."""
        dE = 0.15  # test error bar
        E0 = 14.7
        for E1 in arange(13, 5, -1):
            Rcm, err = self.a.Calc_Rcm(E1, dE)
            Ri = self.a.Ri[1]
            self.assertTrue(0<Rcm<Ri, "Failed test of Calc_Rcm, got nonsense Rcm for E1, dE, E0 = "
                            + str(E1) + "," + str(dE) + "," + str(E0)
                            + "\n got Rcm, err = " + str(Rcm) + "," + str(err))
            self.assertTrue(0<err<Rcm, "Failed test of Calc_Rcm, got invalid error bar for E1, dE, E0 = "
                            + str(E1) + "," + str(dE) + "," + str(E0)
                            + "\n got Rcm, err = " + str(Rcm) + "," + str(err))
