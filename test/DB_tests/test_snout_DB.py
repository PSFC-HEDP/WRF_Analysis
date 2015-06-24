from unittest import TestCase
from NIF_WRF.DB import Database
from NIF_WRF.DB.Snout_DB import *

__author__ = 'Alex Zylstra'


class TestSnout_DB(TestCase):
    """
    Unit testing of the Snout_DB class.
    :author: Alex Zylstra
    :date: 2013/06/11
    """
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    # the database object:
    snout = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os
        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.snout = Snout_DB(Database.FILE_TEST)
        assert isinstance(self.snout, Snout_DB)

        self.snout.insert("Generic",'90-78',1,76.371,82.329,49.91)
        self.snout.insert("Generic",'90-78',2,76.371,75.171,49.91)
        self.snout.insert("Generic",'90-78',3,103.629,82.329,49.91)
        self.snout.insert("Generic2",'90-78',4,103.629,75.171,49.91)
        self.snout.update("Generic",'90-78',1,'theta',1)

        self.snout.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.snout.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.snout.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print("Tearing down...")
        if isinstance(cls.snout, Snout_DB):
            if isinstance(cls.snout.db, sqlite3.Connection):
                cls.snout.db.commit()
                cls.snout.db.close()
    
    def test_get_names(self):
        """Test retreiving names from the database."""
        testPass = (self.snout.get_names() == ['Generic','Generic2'])
        self.assertTrue(testPass, "Failed test of DB.Snout_DB.get_names")

    def test_get_pos(self):
        """Test getting the positions available for a given snout name and DIM."""
        testPass = (self.snout.get_pos("Generic","90-78") == [1,2,3])
        self.assertTrue(testPass, "Failed test of DB.Snout_DB.get_pos")

    def test_get_DIM(self):
        """Test querying for available DIMs for a given name."""
        testPass = ( self.snout.get_DIM("Generic") == ['90-78'] )
        self.assertTrue(testPass, "Failed test of DB.Snout_DB.get_DIM")

    def test_insert(self):
        """Test inserting a row into the table."""
        # do the insertion:
        self.snout.insert("Test","TestDIM",1,42,47,47)
        # do some checks:
        testPass = (self.snout.num_rows() == 5)
        testPass = testPass and ("Test" in self.snout.get_names())
        testPass = testPass and ("TestDIM" in self.snout.get_DIM("Test"))

        self.assertTrue(testPass, "Failed test of DB.Snout_DB.insert")

    def test_update(self):
        """Test updating of a single row."""
        # update an existing row:
        self.snout.update("Generic",'90-78',1,'theta',47)
        testPass = (self.snout.query("Generic","90-78",1)[0][3] == 47)
        self.assertTrue(testPass, "Failed DB.Snout_DB.update")

    def test_query(self):
        """Test a query of existing data."""
        testPass = (self.snout.query("Generic","90-78",2)[0] == ["Generic",'90-78',2,76.371,75.171,49.91] )
        self.assertTrue(testPass, "Failed DB.Snout_DB.query")

    def test_get_r(self):
        """Test method that gets the radius"""
        # first test
        r = self.snout.get_r('Generic', '90-78', 1)[0]
        self.assertEqual(r, 49.91)

        # second test:
        r = self.snout.get_r('Generic2', '90-78', 4)[0]
        self.assertEqual(r, 49.91)

        # add a new row:
        self.snout.insert("Generic2",'90-78',5,103.629,75.171,47.47)
        # and test it:
        r = self.snout.get_r('Generic2', '90-78', 5)[0]
        self.assertEqual(r, 47.47)

    def test_get_theta(self):
        """Test method that gets the polar angle"""
        theta = self.snout.get_theta('Generic', '90-78', 1)[0]
        self.assertEqual(theta, 1.0)

        # try a second one:
        theta = self.snout.get_theta('Generic', '90-78', 3)[0]
        self.assertEqual(theta, 103.629)

    def test_get_phi(self):
        """Test method that gets the azimuthal angle"""
        phi = self.snout.get_phi('Generic', '90-78', 1)[0]
        self.assertEqual(phi, 82.329)

        phi = self.snout.get_phi('Generic', '90-78', 2)[0]
        self.assertEqual(phi, 75.171)