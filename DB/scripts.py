## Various scripts for NIF DB actions
# @author Alex Zylstra
# @date 2013/07/05

import DB.Database as Database
from DB.Shot_DB import *
from DB.Hohlraum_DB import *
from DB.Snout_DB import *
from DB.WRF_Inventory_DB import *
from DB.WRF_Setup_DB import *
from DB.WRF_Spectrum_DB import *
from DB.WRF_InitAnalysis_DB import *
import os


def initialize():
    """Initialize all database tables, if they are not already."""
    Shot_DB(Database.FILE)
    Snout_DB(Database.FILE)
    Hohlraum_DB(Database.FILE)
    WRF_Inventory_DB(Database.FILE)
    WRF_Setup_DB(Database.FILE)
    WRF_Spectrum_DB(Database.FILE)
    WRF_InitAnalysis_DB(Database.FILE)


def export_all():
    """Export all tables as CSV."""
    os.makedirs(Database.DIR, exist_ok=True)

    s = Shot_DB(Database.FILE)
    s.csv_export(Database.DIR + 'csv/shot.csv')

    s2 = Snout_DB(Database.FILE)
    s2.csv_export(Database.DIR + 'csv/snout.csv')

    h = Hohlraum_DB(Database.FILE)
    h.csv_export(Database.DIR + 'csv/hohlraum.csv')

    wi = WRF_Inventory_DB(Database.FILE)
    wi.csv_export(Database.DIR + 'csv/wrf_inventory.csv')

    ws = WRF_Setup_DB(Database.FILE)
    ws.csv_export(Database.DIR + 'csv/wrf_setup.csv')

    wspec = WRF_Spectrum_DB(Database.FILE)
    wspec.csv_export(Database.DIR + 'csv/wrf_spectrum.csv')

    winit = WRF_InitAnalysis_DB(Database.FILE)
    winit.csv_excport(Database.DIR + 'csv/wrf_init_analysis.csv')


def import_all():
    """Import all tables from CSV files."""
    os.makedirs(Database.DIR, exist_ok=True)

    s = Shot_DB(Database.FILE)
    s.csv_import(Database.DIR + 'csv/shot.csv')

    s2 = Snout_DB(Database.FILE)
    s2.csv_import(Database.DIR + 'csv/snout.csv')

    h = Hohlraum_DB(Database.FILE)
    h.csv_import(Database.DIR + 'csv/hohlraum.csv')

    wi = WRF_Inventory_DB(Database.FILE)
    wi.csv_import(Database.DIR + 'csv/wrf_inventory.csv')

    ws = WRF_Setup_DB(Database.FILE)
    ws.csv_import(Database.DIR + 'csv/wrf_setup.csv')

    wspec = WRF_Spectrum_DB(Database.FILE)
    wspec.csv_import(Database.DIR + 'csv/wrf_spectrum.csv')

    winit = WRF_InitAnalysis_DB(Database.FILE)
    winit.csv_export(Database.DIR + 'csv/wrf_init_analysis.csv')