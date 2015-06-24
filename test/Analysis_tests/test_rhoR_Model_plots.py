from unittest import TestCase
import os

import NIF_WRF.Analysis.rhoR_model_plots as rhoR_Model_plots
import NIF_WRF.Analysis.rhoR_Model as rhoR_Model


__author__ = 'Alex Zylstra'


class TestPlot_rhoR_v_Energy(TestCase):
    """Test the plot of rhoR vs energy.
    :author: Alex Zylstra
    :date: 2013/06/15 """
    def test_plot_rhoR_v_Energy(self):
        # generate the model:
        model = rhoR_Model.rhoR_Model()  # use defaults
        path = os.path.dirname(__file__)
        filename = os.path.join(path,'rhoR_v_Energy.eps')
        rhoR_Model_plots.plot_rhoR_v_Energy(model, filename=filename)



class TestPlot_Rcm_v_Energy(TestCase):
    """Test the plot of Rcm vs energy.
    :author: Alex Zylstra
    :date: 2013/06/15 """
    def test_plot_Rcm_v_Energy(self):
        # generate the model:
        model = rhoR_Model.rhoR_Model()  # use defaults
        path = os.path.dirname(__file__)
        filename = os.path.join(path,'Rcm_v_Energy.eps')
        rhoR_Model_plots.plot_Rcm_v_Energy(model, filename=filename)


class TestPlot_rhoR_v_Rcm(TestCase):
    """Test the plot of rhoR vs Rcm.
    :author: Alex Zylstra
    :date: 2013/06/15 """
    def test_plot_rhoR_v_Rcm(self):
        # generate the model:
        model = rhoR_Model.rhoR_Model()  # use defaults
        path = os.path.dirname(__file__)
        filename = os.path.join(path,'rhoR_v_Rcm.eps')
        rhoR_Model_plots.plot_rhoR_v_Rcm(model, filename=filename)


class TestPlot_profile(TestCase):
    """Test the plot of rhoR model profiles.
    :author: Alex Zylstra
    :date: 2013/06/15 """
    def test_plot_profile(self):
        # generate the model:
        model = rhoR_Model.rhoR_Model()  # use defaults
        Rcm = model.Ri / 4.0
        path = os.path.dirname(__file__)
        filename = os.path.join(path,'rhoR_profile.eps')
        rhoR_Model_plots.plot_profile(model, Rcm, filename=filename)