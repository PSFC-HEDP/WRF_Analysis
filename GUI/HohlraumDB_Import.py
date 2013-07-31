__author__ = 'Alex Zylstra'

from DB import Database
from DB.Hohlraum_DB import *

def HohlraumDB_Import():
    """Import a hohlraum definition file from CSV."""
    # get an existing filename:
    from tkinter.filedialog import askopenfilename
    FILEOPENOPTIONS = dict(defaultextension='.csv',
                   filetypes=[('Comma Separated Values','*.csv'), ('All files','*.*')],
                   multiple=False,
                   initialdir=Database.DIR)
    filename = askopenfilename(**FILEOPENOPTIONS)
    print(filename)
    # open the database
    db = Hohlraum_DB(Database.FILE)
    db.add_from_file(filename)