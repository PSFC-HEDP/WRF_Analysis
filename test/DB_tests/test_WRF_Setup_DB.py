from unittest import TestCase
from DB.WRF_Setup_DB import *
import DB.Database as Database

__author__ = 'Alex Zylstra'


class TestWRF_Setup_DB(TestCase):
    """Test the WRF inventory database wrapper, DB.WRF_Setup_DB
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
        self.wrf = WRF_Setup_DB(Database.FILE_TEST)
        assert isinstance(self.wrf, WRF_Setup_DB)

        self.wrf.insert('N130227-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',1,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
        self.wrf.insert('N130228-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',2,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
        self.wrf.insert('N130229-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',3,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
        self.wrf.insert('N130229-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',3,'foo','13511730','13511716','',100,'','32:40:00','0:34:00')
        self.wrf.update('N130229-001-999','90-78','Generic',3,'wrf_id','12345')
        self.wrf.update('N130229-001-999','90-78','Generic',3,'cr39_1_id','12345')

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
            print("Tearing down...")
        if isinstance(cls.wrf, WRF_Setup_DB):
            if isinstance(cls.wrf.db, sqlite3.Connection):
                cls.wrf.db.commit()
                cls.wrf.db.close()

    def test_get_shots(self):
        """Test the method DB.WRF_Setup_DB.get_shots"""
        testPass = ( self.wrf.get_shots() == ['N130227-001-999', 'N130228-001-999', 'N130229-001-999'] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.get_shots")

    def test_insert(self):
        """Test the method DB.WRF_Setup_DB.insert"""
        self.wrf.insert('N123456-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',1,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
        testPass = (self.wrf.query('N123456-001-999') == [['N123456-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','AAA10-0123456_AA', '90-78',50,'Generic',1,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00']] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.insert")

    def test_update(self):
        """Test the method DB.WRF_Setup_DB.update"""
        self.wrf.update('N130229-001-999','90-78','Generic',3,'cr39_2_id','09876')
        testPass = (self.wrf.query_col('N130229-001-999','90-78',3,'cr39_2_id')[0] == '09876')
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.update")

    def test_query(self):
        """Test the method DB.WRF_Setup_DB.query"""
        testPass = ( self.wrf.query('N130229-001-999') == [['N130229-001-999', 'AAA10-108020-10', 'I_Shap_2DConA_Lgth_S05', 'AAA10-0123456_AA', '90-78', 50.0, 'Generic', 3, '12345', '12345', '13511716', '', 100.0, '', '32:40:00', '0:34:00']] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.query")

    def test_query_col(self):
        """Test the method DB.WRF_Setup_DB.query_col"""
        testPass = ( self.wrf.query_col('N130227-001-999', '90-78', 1, "wrf_id") == ['13425857'] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.query_col")

    def test_find_wrf(self):
        """Test the method DB.WRF_Setup_DB.find_wrf"""
        testPass = ( self.wrf.find_wrf('13425857') == ['N130227-001-999','N130228-001-999'] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.find_wrf")

    def test_find_cr39(self):
        """Test the method DB.WRF_Setup_DB.find_cr39"""
        testPass = ( self.wrf.find_cr39('13511730') == ['N130227-001-999','N130228-001-999'] )
        self.assertTrue(testPass, "Failed DB.WRF_Setup_DB.find_cr39")