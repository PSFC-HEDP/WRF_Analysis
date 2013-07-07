from unittest import TestCase
from DB.WRF_InitAnalysis_DB import *
import DB.Database as Database

__author__ = 'Alex Zylstra'


class TestWRF_InitAnalysis_DB(TestCase):
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
        self.db = WRF_InitAnalysis_DB(Database.FILE_TEST)
        assert isinstance(self.db, WRF_InitAnalysis_DB)

        # make two rows in the new database
        self.db.insert('N123456', '0-0', 1, '2013-07-07 01:23')
        self.db.insert('N130520', '90-78', 3, '2013-07-07 13:47')
        # add a value
        self.db.set_column('N130520', '90-78', 3, 'distance', 50)

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
        if isinstance(cls.db, WRF_InitAnalysis_DB):
            if isinstance(cls.db.db, sqlite3.Connection):
                cls.db.db.commit()
                cls.db.db.close()

    def test_insert(self):
        """Test insertion of a new row."""
        n0 = self.db.num_rows()
        self.db.insert('N010203', '90-315', 2, '2013-01-02 03:04')
        n1 = self.db.num_rows()

        # basic test, did # of rows increase by 1?
        self.assertEqual(n1, n0+1)

    def test_set_column(self):
        """Test setting a specific column in the table."""
        val0 = 0
        self.db.set_column('N123456', '0-0', 1, 'back1_region_x0', val0)

        val1 = self.db.get_value('N123456', '0-0', 1, 'back1_region_x0')

        # check that we got back what we put in
        self.assertEqual(val0, val1[0])

    def test_get_value(self):
        """Test retrieval of a value that is already set in the table."""
        val = self.db.get_value('N130520', '90-78', 3, 'distance')
        self.assertEqual(val[0], 50)

    def test_get_row(self):
        """Test the functionality to get a whole row."""
        row = self.db.get_row('N130520', '90-78', 3)
        # also try with specified analysis
        row2 = self.db.get_row('N130520', '90-78', 3, '2013-07-07 13:47')

        # two queries should be equal:
        self.assertListEqual(row, row2)

        print(len(row))

        # make sure trying with a bogus list gives nothing:
        row3 = self.db.get_row('N130520', '90-78', 3, '2013-03-04 13:47')
        self.assertEqual(len(row3), 0)