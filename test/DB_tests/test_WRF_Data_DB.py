from unittest import TestCase
from DB.WRF_Data_DB import *
import DB.Database as Database
import numpy
import os

__author__ = 'Alex Zylstra'


class TestWRF_Data_DB(TestCase):
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    # the database object:
    db = 0

    def setUp(self):
        """Do initialization for the database tests."""
        import os
        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.db = WRF_Data_DB(Database.FILE_TEST)
        assert isinstance(self.db, WRF_Data_DB)

        shot = 'N130520-002-999'
        dim = '0-0'
        position = 1
        wrf_id = '13425888-g058'
        cr39_id = '13511794'
        date = '2013-06-10 08:32'
        hohl_corr = False
        data =     [[4.375, 8.274e+05, 2.294e+06],
                    [4.625, 6.173e+06, 2.990e+06],
                    [4.875, 3.159e+06, 2.192e+06],
                    [5.125, 1.187e+06, 1.675e+06]]
        image =    numpy.array([[0,1,2], [42,47,42], [0,0,0]])

        self.db.insert(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, data, image)

        shot2 = 'N123456-007-999'
        self.db.insert(shot2, dim, position, wrf_id, cr39_id, date, hohl_corr, data, image)

        self.db.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.db.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.db.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print("Tearing down...")
        if isinstance(cls.db, WRF_Data_DB):
            if isinstance(cls.db.db, sqlite3.Connection):
                cls.db.db.commit()
                cls.db.db.close()

    def test_add_data_from_file(self):
        """Test the method to add data from files"""
        rows = self.db.num_rows()
        path = os.path.dirname(__file__)
        csv_fname = os.path.join(path, 'N130711-002-999_WRF_Pos1_3_13425865_AL_13511088_S1_40x_5hr_ANALYSIS.CSV')
        img_fname_list = [os.path.join(path, 'Pos1.bmp'),
                          os.path.join(path, 'Pos1.jpg'),
                          os.path.join(path, 'Pos1.png')]

        for img_fname in img_fname_list:
            self.db.add_data_from_file(csv_fname, img_fname)

        self.assertEqual(self.db.num_rows(), rows+1)
        self.assertTrue('N130711-002-999' in self.db.get_shots())

    def test_get_shots(self):
        """Test retrieval of shots from database."""
        shots = self.db.get_shots()
        self.assertListEqual(shots, ['N123456-007-999', 'N130520-002-999'])

    def test_get_dims(self):
        """Test retrieval of DIMs for a given shot."""
        dim = self.db.get_dims('N130520-002-999')
        self.assertEqual(dim[0], '0-0')

    def test_get_positions(self):
        """Test retrieval of positions for given shot and DIM"""
        pos = self.db.get_positions('N130520-002-999', '0-0')
        self.assertEqual(1, pos[0])

    def test_get_dates(self):
        """Test retrieval of analysis date"""
        date = self.db.get_dates('N130520-002-999', '0-0', 1)
        self.assertEquals(date[0], '2013-06-10 08:32')

    def test_get_wrf_id(self):
        """Test retrieval of WRF ID from the DB"""
        WRF_ID = self.db.get_wrf_id('N130520-002-999', '0-0', 1)
        self.assertEqual(WRF_ID[0], '13425888-g058')

    def test_get_cr39_id(self):
        """Test retrieval of CR-39 ID from the DB"""
        CR39_ID = self.db.get_cr39_id('N130520-002-999', '0-0', 1)
        self.assertEqual(CR39_ID[0], '13511794')

    def test_get_corrected(self):
        """test retrieval of whether spectrum is corrected"""
        import datetime
        date = datetime.datetime.strptime('2013-06-10 08:32','%Y-%m-%d %H:%M')
        corr = self.db.get_corrected('N130520-002-999', '0-0', 1, '2013-06-10 08:32')
        self.assertEqual(corr[0], False)

    def test_insert(self):
        """Test insertion of additional rows"""
        # this one is basically tested implicitly, but let's try adding another row
        len_init = self.db.num_rows()

        shot = 'N474747-002-999'
        dim = '0-0'
        position = 1
        wrf_id = '13425888-g058'
        cr39_id = '13511794'
        date = '2013-06-10 08:32'
        hohl_corr = False
        data =     [[4.375, 8.274e+05, 2.294e+06],
                    [4.625, 6.173e+06, 2.990e+06],
                    [4.875, 3.159e+06, 2.192e+06],
                    [5.125, 1.187e+06, 1.675e+06]]

        self.db.insert(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, data)

        self.assertEqual(self.db.num_rows(), len_init+1)

    def test_get_spectrum(self):
        """Test functionality to retrieve a spectrum from the database."""
        # first try without specifying the date:
        data = self.db.get_spectrum('N130520-002-999', '0-0', 1, False)
        data = data.tolist()
        orig_data =     [[4.375, 8.274e+05, 2.294e+06],
                    [4.625, 6.173e+06, 2.990e+06],
                    [4.875, 3.159e+06, 2.192e+06],
                    [5.125, 1.187e+06, 1.675e+06]]
        self.assertListEqual(data, orig_data)

        # now try again with given date:
        data = self.db.get_spectrum('N130520-002-999', '0-0', 1, 0, '2013-06-10 08:32')
        data = data.tolist()
        self.assertListEqual(data, orig_data)

    def test_get_Nxy(self):
        """Test functionality for retrieving image data from the DB."""
        image = self.db.get_Nxy('N130520-002-999', '0-0', 1, 0)
        image = image.tolist()
        original = [[0,1,2], [42,47,42], [0,0,0]]
        self.assertListEqual(image, original)

        # try again with specified date:
        image = self.db.get_Nxy('N130520-002-999', '0-0', 1, 0, '2013-06-10 08:32')
        image = image.tolist()
        self.assertListEqual(image, original)

    def test_latest_date(self):
        """Test the method that infers the latest date"""
        date = self.db.__latest_date__('N130520-002-999', '0-0', 1)
        self.assertEqual(date, '2013-06-10 08:32')

        # add a new row with newer date
        shot = 'N130520-002-999'
        dim = '0-0'
        position = 1
        wrf_id = '13425888-g058'
        cr39_id = '13511794'
        date = '2013-06-10 08:47'
        hohl_corr = False
        data =     [[4.375, 8.274e+05, 2.294e+06],
                    [4.625, 6.173e+06, 2.990e+06],
                    [4.875, 3.159e+06, 2.192e+06],
                    [5.125, 1.187e+06, 1.675e+06]]
        image =    numpy.array([[0,1,2], [42,47,42], [0,0,0]])

        self.db.insert(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, data, image)

        # now try the date method again:
        date = self.db.__latest_date__(shot, dim, position)
        self.assertEqual(date, '2013-06-10 08:47')