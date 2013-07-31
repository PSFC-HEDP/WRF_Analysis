# Define parameters for the sqlite3 database
__author__ = 'Alex Zylstra'
import sys

# Directory where the main database is stored
# OS dependent
if sys.platform.startswith('linux'):
    # where the database is stored
    DIR = '/home/alex'
    # Directory where the tests are stored
    TEST_DIR = '/home/alex/test/'
elif sys.platform.startswith('darwin'):
    # where the database is stored
    DIR = '/Users/alex'
    # Directory where the tests are stored
    TEST_DIR = '/Users/alex/test/'

import os

# Database file
FILE = os.path.join(DIR, 'NIF.db')
# Test database file
FILE_TEST = os.path.join(TEST_DIR, 'test.db')

# Define table names:
SNOUT_TABLE = 'snout'
HOHLRAUM_TABLE = 'hohlraum'
SHOT_TABLE = 'shot'
WRF_INVENTORY_TABLE = 'wrf_inventory'
WRF_SETUP_TABLE = 'wrf_setup'
WRF_SPECTRUM_TABLE = 'wrf_spectrum'
WRF_INITANALYSIS_TABLE = 'wrf_init_analysis'
WRF_ANALYSIS_TABLE = 'wrf_analysis'