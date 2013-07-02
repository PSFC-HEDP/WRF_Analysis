from unittest import TestCase
from DB.WRF_Inventory_DB import *
import DB.Database as Database

__author__ = 'Alex Zylstra'


class TestWRF_Inventory_DB(TestCase):
    """Test the WRF inventory database wrapper, DB.WRF_Inventory_DB.
    :author: Alex Zylstra
    :date: 2013/06/12
    """
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    # the database object:
    wrf = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os

        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.wrf = WRF_Inventory_DB(Database.FILE_TEST)
        assert isinstance(self.wrf, WRF_Inventory_DB)

        self.wrf.insert('1', 3, 'active')
        self.wrf.insert('2', 0, 'active')
        self.wrf.insert('3', -1, 'retired')

        self.wrf.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.wrf.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.wrf.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print('Tearing down...')
        if isinstance(cls.wrf, WRF_Inventory_DB) and isinstance(cls.wrf.db, sqlite3.Connection):
            cls.wrf.db.commit()
            cls.wrf.db.close()

    def test_get_ids(self):
        """Test the method DB.WRF_Inventory_DB.get_ids"""
        testPass = (self.wrf.get_ids() == ['1', '2', '3'])
        self.assertTrue(testPass, "Failed DB.WRF_Inventory_DB.get_ids")

    def test_get_shots(self):
        """Test the method DB.WRF_Inventory_DB.get_shots"""
        testPass = not (self.wrf.get_shots('3') == 5)
        testPass = testPass and (self.wrf.get_shots('3') == -1)
        self.assertTrue(testPass, "Failed DB.WRF_Inventory_DB.get_shots")

    def test_get_status(self):
        """Test the method DB.WRF_Inventory_DB.get_status"""
        testPass = (self.wrf.get_status('2') == 'active')
        self.assertTrue(testPass, "Failed DB.WRF_Inventory_DB.status")

    def test_insert(self):
        """Test the method DB.WRF_Inventory_DB.insert"""
        self.wrf.insert("foo", 5, "bar")
        testPass = ("foo" in self.wrf.get_ids())
        testPass = testPass and ("bar" == self.wrf.get_status("foo"))
        testPass = testPass and (5 == self.wrf.get_shots("foo"))
        self.assertTrue(testPass, "Failed DB.WRF_Inventory_DB.insert")

    def test_update(self):
        """Test the method DB.WRF_Inventory_DB.update"""
        self.wrf.update('3', 42, '47')
        testPass = (42 == self.wrf.get_shots('3'))
        testPass = testPass and ('47' == self.wrf.get_status('3'))
        self.assertTrue(testPass, "Failed DB.WRF_Inventory_DB.update")