from unittest import TestCase
import os

from WRF_Analysis.util.Import_Nxy import load_image


__author__ = 'Alex Zylstra'

class TestLoad_image(TestCase):
    def test_load_image(self):
        """Test image loading capabilities."""
        # test three files:
        path = os.path.dirname(__file__)
        filenames = [os.path.join(path, 'Pos1.bmp'),
                          os.path.join(path, 'Pos1.jpg'),
                          os.path.join(path, 'Pos1.png')]

        images = []
        for fname in filenames:
            images.append(load_image(fname))

        self.assertImagesEqualSize(images[0], images[1])
        self.assertImagesEqualSize(images[0], images[2])

    def assertImagesEqualSize(self, img1, img2):
        """Assert that two numpy.ndarrays are equal in size"""
        self.assertTupleEqual(img1.shape, img2.shape)