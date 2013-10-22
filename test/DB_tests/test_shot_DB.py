import sqlite3
from unittest import TestCase
from NIF_WRF.DB import Database
from NIF_WRF.DB.Shot_DB import *

__author__ = 'Alex Zylstra'


class TestShot_DB(TestCase):
    """
    Unit testing of the Shot_DB class.
    :author: Alex Zylstra
    :date: 2013/06/11
    """

    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    # the database object:
    shot = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os
        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.shot = Shot_DB(Database.FILE_TEST)
        assert isinstance(self.shot, Shot_DB)

        self.shot.clear()
        self.shot.add_column('Yn','real')
        self.shot.add_column("Yn Unc",'real')
        self.shot.add_column('Ti','real')
        self.shot.insert('N010203')
        self.shot.update('N010203','Yn',5)
        self.shot.update('N010203','Yn Unc',2)
        self.shot.update('N010203','Ti',18)

        self.shot.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.shot.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.shot.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print("Tearing down...")
        if isinstance(cls.shot, Shot_DB):
            if isinstance(cls.shot.db, sqlite3.Connection):
                cls.shot.db.commit()
                cls.shot.db.close()

    def test_get_shots(self):
        """Testing retrieval of a list of shots"""
        testPass = (self.shot.get_columns() == [[0, 'shot', 'text', 0, None, 0], [1, 'Yn', 'real', 0, None, 0], [2, 'Yn Unc', 'real', 0, None, 0], [3, 'Ti', 'real', 0, None, 0]])

        self.assertTrue(testPass,"Failed DB.Shot_DB.")

    def test_insert(self):
        """Test inserting rows into the database."""
        self.shot.insert("N123456")
        # should now have one more row:
        testPass = self.shot.num_rows() == 2
        # also should contain the new name:
        testPass = testPass and ( "N123456" in flatten(self.shot.get_shots()) )

        self.assertTrue(testPass,"Failed DB.Shot_DB.insert")

    def test_update(self):
        """Test updating a row in the table."""
        self.shot.update('N010203','Yn',12345.6)
        # check:
        testPass = self.shot.query_col('N010203','Yn')[0] == 12345.6

        self.assertTrue(testPass,"Failed DB.Shot_DB.update")

    def test_query(self):
        """Test querying the table."""
        testPass =  (self.shot.query('N010203') == ['N010203', 5.0, 2.0, 18.0])

        self.assertTrue(testPass,"Failed DB.Shot_DB.")

    def test_query_col(self):
        """Test querying a specific column."""
        testPass = (self.shot.query_col('N010203','Yn') == (5,2))
        testPass = testPass and (self.shot.query_col('N010203','Ti') == 18)

        self.assertTrue(testPass,"Failed DB.Shot_DB.")