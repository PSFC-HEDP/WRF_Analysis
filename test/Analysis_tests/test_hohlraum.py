from unittest import TestCase
import math

from WRF_Analysis.util.CSV import *
import WRF_Analysis.Analysis.Hohlraum as Hohlraum


__author__ = 'Alex Zylstra'


class TestHohlraum(TestCase):
    """Test various aspects of the hohlraum correction functionality."""
    # where the test data is:
    path = os.path.dirname(__file__)

    # test data:
    data = read_csv(os.path.join(path, 'TestData.csv'), 3)
    # test hohlraum info:
    hohl_wall = read_csv(os.path.join(path, 'AAA12-119365_AA.csv'), crop=0, cols=[2, 4, 5])
    theta = 76.371
    dtheta = (180 / math.pi) * math.asin(1 / 50)
    angles = [theta - dtheta, theta + dtheta]

    # a test hohlraum:
    hohl = Hohlraum.Hohlraum(data, wall=hohl_wall, angles=angles)

    def test_shift_energy(self):
        """Test energy shifts through the hohlraum."""
        # first make sure that 0 thickness doesn't change energy:
        Energies = [10, 11, 12, 13, 14, 15, 16, 17]
        for E in Energies:
            Eout = self.hohl.shift_energy(E, 0, 0, 0)
            self.assertAlmostEqual(E, Eout, places=3, msg="Failed test of energy shift with 0 thickness")

        # also test calculation stability for a variety of thicknesses:
        E0 = 14.7
        for Al in [20, 40, 60, 80, 100, 200, 300]:
            for DU in [5, 10, 20, 30, 40]:
                for Au in [5, 10, 20, 30, 40, 50, 60, 70]:
                    Ein = self.hohl.shift_energy(E0, Al, DU, Au)
                    self.assertTrue(Ein > E0, "Failed test of hohlraum energy shift for Al, DU, Au = "
                                              + str(Al) + "," + str(DU) + "," + str(Au)
                                              + "\n got E0->Ein: " + str(E0) + "->" + str(Ein))

        # test a specific case:
        self.assertAlmostEqual(self.hohl.shift_energy(10.0, 72, 20, 20), 11.885, places=2)

    def test_get_fit_raw(self):
        """Test the raw fit to the data."""
        fit = self.hohl.get_fit_raw()
        # compare to expected values from the test data:
        self.assertAlmostEqual(fit[0], 4.93e7, delta=1e5)
        self.assertAlmostEqual(fit[1], 9.2551, places=3)
        self.assertAlmostEqual(fit[2], 0.6984, places=3)

    def test_get_fit_corr(self):
        """Test the fit to the corrected data."""
        fit = self.hohl.get_fit_corr()
        # compare to expected values from the test data:
        self.assertAlmostEqual(fit[0], 4.94e7, delta=1e5)
        self.assertAlmostEqual(fit[1], 11.06, places=2)
        self.assertAlmostEqual(fit[2], 0.6189, places=3)

    def test_get_data_raw(self):
        """Test retrieval of the raw data from the Hohlraum object."""
        hData = self.hohl.get_data_raw()
        # compare to what we gave the Hohlraum:
        for i in range(len(self.data)):
            self.assertTrue(all(self.data[i][j] == hData[i][j] for j in range(len(hData[i]))),
                            msg="Failed raw data comparison.")

    def test_get_data_corr(self):
        """Test retrieval of the corrected data from the Hohlraum object."""
        hData = self.hohl.get_data_corr()
        # compare to what we gave the Hohlraum plus shift:
        for i in range(len(self.data)):
            energy = self.hohl.shift_energy(self.data[i][0])
            self.assertAlmostEqual(energy, hData[i][0], places=2, msg="Failed raw data comparison.")

    def test_get_E_shift(self):
        """Test retrieval of the peak energy shift from the hohlraum."""
        deltaE = self.hohl.get_E_shift()
        # compare to what we expect from the test data and hohlraum:
        self.assertAlmostEqual(deltaE, 1.800, places=3)

    def test_get_unc(self):
        """Test uncertainties due to the hohlraum for the test data."""
        unc = self.hohl.get_unc()
        # compare to expected values for the test data:
        self.assertAlmostEqual(unc[0][0], 4592, delta=1)
        self.assertAlmostEqual(unc[0][1], 3997, delta=1)
        self.assertAlmostEqual(unc[1][0], 0.05847, places=3)
        self.assertAlmostEqual(unc[1][1], 0.05827, places=3)
        self.assertAlmostEqual(unc[2][0], 0.00232, places=4)
        self.assertAlmostEqual(unc[2][1], 0.00231, places=4)

    def test_plot_file(self):
        """Generate a plot of the hohlraum correction and save it to file."""
        fname = os.path.join(self.path, 'hohlraum.eps')
        self.hohl.plot_file(fname)

    def test_plot_window(self):
        """Generate a plot of the hohlraum correction and display it."""
        self.hohl.plot_window(interactive=True)

    def test_plot_hohlraum_file(self):
        """Generate a plot of the hohlraum profile and save it to a file."""
        fname = os.path.join(self.path, 'hohlraum_profile.eps')
        self.hohl.plot_hohlraum_file(fname)

    def test_plot_hohlraum_window(self):
        """Generate a plot of the hohlraum profile and display it."""
        self.hohl.plot_hohlraum_window(interactive=True)