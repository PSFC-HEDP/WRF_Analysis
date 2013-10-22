from unittest import TestCase
import os

from NIF_WRF.DB import Database
from NIF_WRF.DB.Hohlraum_DB import *


__author__ = 'Alex Zylstra'


class TestHohlraum_DB(TestCase):
    """
    Unit testing of the Hohlraum_DB class.
    :author: Alex Zylstra
    :date: 2013/06/11
    """
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    h = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os
        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.h = Hohlraum_DB(Database.FILE_TEST)
        assert isinstance(self.h, Hohlraum_DB)
        self.h.clear()

        self.h.insert('AAA123',"Generic_Au_575",0,"Au",5,10)
        self.h.insert('AAA123',"Generic_Au_575",0,"Au",5,11)
        self.h.insert('AAA456',"Generic_U_575",0,"U",1,2)

        self.h.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.h.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.h.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print("Tearing down...")
        if isinstance(cls.h, Hohlraum_DB):
            if isinstance(cls.h.db, sqlite3.Connection):
                cls.s.db.commit()
                cls.s.db.close()

    def test_add_from_file(self):
        """Test the functionality for loading data from files"""
        fname = os.path.join(os.path.dirname(__file__), 'AAA12-119365_AA.csv')
        init_rows = self.h.num_rows()
        self.h.add_from_file(fname)
        self.assertEqual(self.h.num_rows(), init_rows+1120)

        # also verify that the data appears correct:
        self.assertTrue('AAA12-119365_AA' in self.h.get_drawings())
        self.assertListEqual(self.h.get_layers(drawing='AAA12-119365_AA'), [0,1,2,3])
        self.assertTrue('CONA2D_575.1013_AU_CH5.47S_T78_L337' in self.h.get_names())

    def test_get_names(self):
        """Test name retreival from the database"""
        # get names:
        names = self.h.get_names()
        expect = ['Generic_Au_575','Generic_U_575']

        testPass = (names == expect)

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.get_names")

    def test_get_drawings(self):
        """Test getting the unique drawing numbers from the database"""
        testPass = (self.h.get_drawings() == ['AAA123','AAA456'])

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.get_drawings")

    def test_get_drawing_name(self):
        """Test getting the unique drawing from a name"""
        testPass = ( self.h.get_drawing_name('AAA123') == ['Generic_Au_575'] )

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.get_drawing_name")

    def test_get_name_drawing(self):
        """Test getting the unique name from a drawing"""
        testPass = ( self.h.get_name_drawing('Generic_U_575') == ['AAA456'] )

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.get_name_drawing")

    def test_get_layers(self):
        """Test getting the available layers."""
        testPass = ( self.h.get_layers('Generic_U_575') == [0] )

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.get_layers")

    def test_insert(self):
        """Test the insertion mechanism of the Hohlraum database"""
        # should have three rows from the initialization:
        # add one more
        self.h.insert('AAA789',"Generic_U_575",0,"U",1,2)
        testPass = self.h.num_rows() == 4

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.insert")

    def test_drop(self):
        """Test dropping rows from the table."""
        self.h.drop('AAA456',0) # should remove one row
        testPass = self.h.num_rows() == 2

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.drop")

    def test_query_drawing(self):
        """Test querying by drawing number."""
        testPass = self.h.query_drawing('AAA123',0) == [['AAA123',"Generic_Au_575",0,"Au",5,10],['AAA123',"Generic_Au_575",0,"Au",5,11]]

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.query_drawing")

    def test_query_name(self):
        """Test querying by name."""
        testPass = self.h.query_name('Generic_Au_575',0) == [['AAA123',"Generic_Au_575",0,"Au",5,10],['AAA123',"Generic_Au_575",0,"Au",5,11]]
        testPass = testPass and (self.h.query_name('Generic_Au_575',1) == [])

        self.assertTrue(testPass,"Failed DB.Hohlraum_DB.query_name")

    def test_get_wall(self):
        """Test the method which retrieves all info for a given wall"""
        # load the data from test file:
        fname = os.path.join(os.path.dirname(__file__), 'AAA12-119365_AA.csv')
        self.h.add_from_file(fname)

        # get the wall by drawing, and test its dimensions:
        wall = self.h.get_wall(name='CONA2D_575.1013_AU_CH5.47S_T78_L337')
        self.assertEqual(len(wall), 1120)
        self.assertEqual(len(wall[0]), 6)

        # now try getting the wall via drawing number
        wall = self.h.get_wall(drawing='AAA12-119365_AA')
        self.assertEqual(len(wall), 1120)
        self.assertEqual(len(wall[0]), 6)
