from unittest import TestCase
from DB.WRF_Spectrum_DB import *
import DB.Database as Database

__author__ = 'Alex Zylstra'


class TestWRF_Spectrum_DB(TestCase):
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    # the database object:
    db = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os
        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.db = WRF_Spectrum_DB(Database.FILE_TEST)
        assert isinstance(self.db, WRF_Spectrum_DB)

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
        energy = []
        Y = []
        err = []
        for row in data:
            energy.append(row[0])
            Y.append(row[1])
            err.append(row[2])

        self.db.insert(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, energy, Y, err)

        shot2 = 'N123456-007-999'
        self.db.insert(shot2, dim, position, wrf_id, cr39_id, date, hohl_corr, energy, Y, err)

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
        if isinstance(cls.db, WRF_Spectrum_DB):
            if isinstance(cls.db.db, sqlite3.Connection):
                cls.db.db.commit()
                cls.db.db.close()

    def test_get_shots(self):
        """Test retrieval of shots from database."""
        shots = self.db.get_shots()
        self.assertListEqual(shots, ['N123456-007-999', 'N130520-002-999'])

    def test_get_dims(self):
        """Test retrieval of DIMs for a given shot."""
        dim = self.db.get_dims('N130520-002-999')
        self.assertEqual(dim[0], '0-0')

    def test_get_positions(self):
        pos = self.db.get_positions('N130520-002-999', '0-0')
        self.assertEqual(1, pos[0])

    def test_get_dates(self):
        date = self.db.get_dates('N130520-002-999', '0-0', 1)
        self.assertEquals(date[0], '2013-06-10 08:32')

    def test_get_corrected(self):
        import datetime
        date = datetime.datetime.strptime('2013-06-10 08:32','%Y-%m-%d %H:%M')
        corr = self.db.get_corrected('N130520-002-999', '0-0', 1, '2013-06-10 08:32')
        self.assertEqual(corr[0], False)

    def test_insert(self):
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
        energy = []
        Y = []
        err = []
        for row in data:
            energy.append(row[0])
            Y.append(row[1])
            err.append(row[2])

        self.db.insert(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, energy, Y, err)

        self.assertEqual(self.db.num_rows(), len_init+len(data))