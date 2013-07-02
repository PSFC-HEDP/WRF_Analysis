from unittest import TestCase
from util.GaussFit import *
from util.CSV import *
from Analysis.Hohlraum import *
import Analysis.SlideGenerator as SlideGenerator
import sys, imp

__author__ = 'Alex Zylstra'


class TestShow_slide(TestCase):
    """Test class for the Analysis.SlideGenerator.show_slide method.
    :author: Alex Zylstra
    :date: 2013/06/15 """

    def test_show_slide(self):
        """Test the Analysis.SlideGenerator.show_slide method."""
        if 'matplotlib' in sys.modules:
            imp.reload(matplotlib)

        path = os.path.dirname(__file__)
        # read in some test data:
        data = read_csv(os.path.join(path,'TestData.csv'), crop=5, cols=[0,1,2])
        # create a Gauss Fit object:
        fit = GaussFit(data, guess=[4e7,10,1])

        hohl_wall = read_csv(os.path.join(path,'AAA12-119365_AA.csv'), crop=0, cols=[2,4,5])
        theta=76.371
        dtheta=(180/math.pi)*math.asin(1/50)
        angles = [theta-dtheta,theta+dtheta]
        hohl = Hohlraum(data, wall=hohl_wall, angles=angles)

        name = r'foo'
        summary = r'bar'
        results = r'47'

        import matplotlib.image as mpimg
        img = mpimg.imread(os.path.join(path,'Pos1.png'))

        SlideGenerator.show_slide(Fit=fit, Hohl=hohl, Nxy=img, name=name, summary=summary, results=results, interactive=True)

class TestSave_slide(TestCase):
    """Test class for the Analysis.SlideGenerator.show_slide method.
    :author: Alex Zylstra
    :date: 2013/06/15 """

    def test_save_slide(self):
        """Test the Analysis.SlideGenerator.save_slide method."""
        path = os.path.dirname(__file__)
        # read in some test data:
        data = read_csv(os.path.join(path,'TestData.csv'), crop=5, cols=[0,1,2])
        # create a Gauss Fit object:
        fit = GaussFit(data, guess=[4e7,10,1])

        hohl_wall = read_csv(os.path.join(path,'AAA12-119365_AA.csv'), crop=0, cols=[2,4,5])
        theta=76.371
        dtheta=(180/math.pi)*math.asin(1/50)
        angles = [theta-dtheta,theta+dtheta]
        hohl = Hohlraum(data, wall=hohl_wall, angles=angles)

        name = 'foo'
        summary = 'bar'
        results = '47'

        import matplotlib.image as mpimg
        img = mpimg.imread(os.path.join(path,'Pos1.png'))

        SlideGenerator.save_slide(os.path.join(path, 'test_slide.eps'), Fit=fit, Hohl=hohl, Nxy=img, name=name, summary=summary, results=results)
