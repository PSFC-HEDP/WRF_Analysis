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
from DB.WRF_Analysis_DB import *
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
    WRF_Analysis_DB(Database.FILE)


def export_all(export_dir=os.path.join(Database.DIR,'csv')):
    """Export all tables as CSV.
    :param export_dir: (optional) where to export CSV files to [default=Database.DIR+'csv']
    """
    os.makedirs(export_dir, exist_ok=True)

    s = Shot_DB(Database.FILE)
    s.csv_export(os.path.join(export_dir, 'shot.csv'))

    s2 = Snout_DB(Database.FILE)
    s2.csv_export(os.path.join(export_dir, 'snout.csv'))

    h = Hohlraum_DB(Database.FILE)
    h.csv_export(os.path.join(export_dir, 'hohlraum.csv'))

    wi = WRF_Inventory_DB(Database.FILE)
    wi.csv_export(os.path.join(export_dir, 'wrf_inventory.csv'))

    ws = WRF_Setup_DB(Database.FILE)
    ws.csv_export(os.path.join(export_dir, 'wrf_setup.csv'))

    wspec = WRF_Spectrum_DB(Database.FILE)
    wspec.csv_export(os.path.join(export_dir, 'wrf_spectrum.csv'))

    winit = WRF_InitAnalysis_DB(Database.FILE)
    winit.csv_export(os.path.join(export_dir, 'wrf_init_analysis.csv'))

    DB = WRF_Analysis_DB(Database.FILE)
    DB.csv_export(os.path.join(export_dir, 'wrf_analysis.csv'))


def import_all(import_dir=os.path.join(Database.DIR,'csv')):
    """Import all tables from CSV files.
    :param import_dir: (optional) where to import CSV files from [default=Database.DIR]
    """
    os.makedirs(import_dir, exist_ok=True)

    s = Shot_DB(Database.FILE)
    s.csv_import(os.path.join(import_dir, 'shot.csv'))

    s2 = Snout_DB(Database.FILE)
    s2.csv_import(os.path.join(import_dir, 'snout.csv'))

    h = Hohlraum_DB(Database.FILE)
    h.csv_import(os.path.join(import_dir, 'hohlraum.csv'))

    wi = WRF_Inventory_DB(Database.FILE)
    wi.csv_import(os.path.join(import_dir, 'wrf_inventory.csv'))

    ws = WRF_Setup_DB(Database.FILE)
    ws.csv_import(os.path.join(import_dir, 'wrf_setup.csv'))

    wspec = WRF_Spectrum_DB(Database.FILE)
    wspec.csv_import(os.path.join(import_dir, 'wrf_spectrum.csv'))

    winit = WRF_InitAnalysis_DB(Database.FILE)
    winit.csv_import(os.path.join(import_dir, 'wrf_init_analysis.csv'))

    DB = WRF_Analysis_DB(Database.FILE)
    DB.csv_import(os.path.join(import_dir, 'wrf_analysis.csv'))