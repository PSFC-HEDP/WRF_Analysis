from unittest import TestCase
from DB.WRF_Analysis_DB import *
import DB.Database as Database

__author__ = 'Alex Zylstra'


class TestWRF_Analysis_DB(TestCase):
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
        self.db = WRF_Analysis_DB(Database.FILE_TEST)
        assert isinstance(self.db, WRF_Analysis_DB)

        # make two rows in the new database
        self.db.insert('N123456', '0-0', 1, '2013-07-07 01:23')
        self.db.insert('N130520', '90-78', 3, '2013-07-07 13:47')

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
        if isinstance(cls.db, WRF_Analysis_DB):
            if isinstance(cls.db.db, sqlite3.Connection):
                cls.db.db.commit()
                cls.db.db.close()

    def test_set_column(self):
        # add a value
        self.db.set_column('N130520', '90-78', 3, 'E_raw', 9.5)
        pass

    def test_get_value(self):
        # add a value
        self.db.set_column('N130520', '90-78', 3, 'E_raw', 9.5)
        self.assertEqual(self.db.get_value('N130520', '90-78', 3, 'E_raw')[0], 9.5)

    def test_get_row(self):
        row = self.db.get_row('N130520', '90-78', 3)
        self.assertGreater(len(row), 0)

