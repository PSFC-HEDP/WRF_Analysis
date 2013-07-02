from unittest import TestCase
from util.GaussFit import *
from datetime import *
import timeit
import os
from util.CSV import *
import numpy

__author__ = 'Alex Zylstra'


class TestGaussFit(TestCase):
    """Test the Gaussian fitting utility."""
    # where the test data is:
    path = os.path.dirname(__file__)

    # test data:
    data = read_csv(os.path.join(path,'TestData.csv'),3)

    # fit:
    fit = GaussFit(data)

    def test_Gaussian(self):
        """Test the Gaussian method implemented in the other function."""
        # test cases, calculated in Mathematica via A*PDF[NormalDistribution[\[Mu], \[Sigma]], x]
        self.assertAlmostEqual(Gaussian(0.3, 2., 0., 0.1), 0.088637, places=4)
        self.assertAlmostEqual(Gaussian(-0.8, 1., 2., 0.5), 1.2365e-7, delta=1e-9)
        self.assertAlmostEqual(Gaussian(11., 5e7, 9.5, 0.5), 4.432e5, delta=1e3)

        # speed test
        t = timeit.timeit(stmt="Gaussian(0,1,1,1)",  setup="from util.GaussFit import Gaussian", number=int(1e3))
        print("Evaluating Gaussian: " + '{:.2f}'.format(1e3*t) + " us per call")

    def test_do_fit(self):
        """Test the fit itself."""
        fit_val = self.fit.do_fit()[0]
        # compare to an expected value:
        self.assertAlmostEqual(fit_val[0], 4.92e7, delta=1e5)
        self.assertAlmostEqual(fit_val[1], 9.255, delta=0.01)
        self.assertAlmostEqual(fit_val[2], 0.698, delta=0.01)

        # compare two fit methods to each other:
        fit_1 = self.fit.do_fit(method='fmin')[0]
        fit_2 = self.fit.do_fit(method='chi^2')[0]
        self.assertAlmostEqual(fit_1[0], fit_2[0], delta=1e6)
        self.assertAlmostEqual(fit_1[1], fit_2[1], delta=0.05)
        self.assertAlmostEqual(fit_1[2], fit_2[2], delta=0.05)

        # speed test
        t0 = datetime.now()
        for i in range(100):
            self.fit.do_fit()
        t1 = datetime.now()
        print('{:.2f}'.format(10*(t1 - t0).total_seconds()) + "ms per fit call")

    def test_eval_fit(self):
        """Test evaluation of the fit."""
        B = self.fit.do_fit()[0]
        for x in numpy.arange(0,15,0.1):
            # evaluate it ourselves:
            eval1 = B[0]/(B[2]*numpy.sqrt(2*numpy.pi))*numpy.exp(-((x-B[1])**2/(2*B[2]**2)))
            eval2 = self.fit.eval_fit(x)
            self.assertAlmostEqual(eval1, eval2, delta=max(1e-6, eval1/1e3))

    def test_chi2(self):
        """Test the overall chi^2 value for the fit."""
        # compare to known value for this test case:
        self.assertAlmostEqual(self.fit.chi2(), 77.58, places=1)

    def test_red_chi2(self):
        """Test the reduced chi^2 value."""
        # compare to known value for this test case:
        self.assertAlmostEqual(self.fit.red_chi2(), 1.293, places=2)

    def test_chi2_fit_unc(self):
        """Test the fit uncertainties for this test data."""
        # compare to known values for this test case:
        unc = self.fit.chi2_fit_unc()
        self.assertAlmostEqual(unc[0][0], -3.11e6, delta=1e4)
        self.assertAlmostEqual(unc[0][1], 3.13e6, delta=1e4)
        self.assertAlmostEqual(unc[1][0], -0.052, delta=1e-3)
        self.assertAlmostEqual(unc[1][1], 0.051, delta=1e-3)
        self.assertAlmostEqual(unc[2][0], -0.053, delta=1e-3)
        self.assertAlmostEqual(unc[2][1], 0.059, delta=1e-3)

    def test_plot_file(self):
        """Test the generation of a plot and saving it to file."""
        fname = os.path.join(self.path, 'gaussFit_plot.eps')
        self.fit.plot_file(fname)

    def test_plot_window(self):
        """Test generating and displaying a plot window."""
        self.fit.plot_window(True)
