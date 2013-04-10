## Various scripts for NIF DB actions
# @author Alex Zylstra
# @date 2013/02/28

import Database
from Shot_DB import *
from Hohlraum_DB import *
from Snout_DB import *
from WRF_Inventory_DB import *
from WRF_Setup_DB import *

def initialize():
	s = Shot_DB(Database.FILE)
	s2 = Snout_DB(Database.FILE)
	h = Hohlraum_DB(Database.FILE)
	wi = WRF_Inventory_DB(Database.FILE)
	ws = WRF_Setup_DB(Database.FILE)

def export_all():
	s = Shot_DB(Database.FILE)
	s.csv_export('csv/shot.csv')

	s2 = Snout_DB(Database.FILE)
	s2.csv_export('csv/snout.csv')

	h = Hohlraum_DB(Database.FILE)
	h.csv_export('csv/hohlraum.csv')

	wi = WRF_Inventory_DB(Database.FILE)
	wi.csv_export('csv/wrf_inventory.csv')

	ws = WRF_Setup_DB(Database.FILE)
	ws.csv_export('csv/wrf_setup.csv')

def import_all():
	s = Shot_DB(Database.FILE)
	s.csv_import('csv/shot.csv')

	s2 = Snout_DB(Database.FILE)
	s2.csv_import('csv/snout.csv')

	h = Hohlraum_DB(Database.FILE)
	h.csv_import('csv/hohlraum.csv')

	wi = WRF_Inventory_DB(Database.FILE)
	wi.csv_import('csv/wrf_inventory.csv')

	ws = WRF_Setup_DB(Database.FILE)
	ws.csv_import('csv/wrf_setup.csv')