# Define parameters for the sqlite3 database
__author__ = 'Alex Zylstra'
import os

# Directory where the main database is stored
# where the database is stored
DIR = os.path.expanduser('~')
# Directory where the tests are stored
TEST_DIR = os.path.join(os.path.expanduser('~'),'test')

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
WRF_DATA_TABLE = 'wrf_data'
WRF_INITANALYSIS_TABLE = 'wrf_init_analysis'
WRF_ANALYSIS_TABLE = 'wrf_analysis'
WRF_RHOR_MODEL_TABLE = 'wrf_rhor_model'