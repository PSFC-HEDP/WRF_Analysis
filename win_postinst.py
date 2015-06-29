import os
import sys
import shutil
import WRF_Analysis

DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
APP_FOLDER = os.path.join(sys.prefix,'Program Files','WRF_Analysis')
NAME = 'NIF WRF.lnk'

if sys.argv[1] == '-install':
    create_shortcut(
        os.path.join(APP_FOLDER, 'main.exe'), # program
        'WRF Analysis', # description
        NAME, # filename
        WRF_Analysis.__file__, # parameters
        APP_FOLDER, # workdir
        os.path.join(APP_FOLDER, 'favicon.ico'), # iconpath
    )
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(), NAME),
                os.path.join(DESKTOP_FOLDER, NAME))
    # tell windows installer that we created another
    # file which should be deleted on uninstallation
    file_created(os.path.join(DESKTOP_FOLDER, NAME))

if sys.argv[1] == '-remove':
    pass
    # This will be run on uninstallation. Nothing to do.
