import sys
from cx_Freeze import setup, Executable
import scipy
import scipy.interpolate
import platform

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
# Dependencies are automatically detected, but it might need fine tuning.
if platform.system() == 'Darwin':
    build_exe_options = {"packages": ["os","scipy","scipy.interpolate","NIF_WRF","NIF_WRF.DB","NIF_WRF.Analysis","NIF_WRF.util","NIF_WRF.GUI","NIF_WRF.GUI.widgets"], 
                                            "includes": ["numpy","scipy","scipy.interpolate","scipy.optimize","scipy.stats","matplotlib","matplotlib.pyplot","matplotlib.backends.backend_macosx","matplotlib.backends.backend_tkagg"],
                                            "excludes": [],
                                            "include_files": [('NIF_WRF/util/_StopPow.so','_StopPow.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_csr.so','_csr.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_csc.so','_csc.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_coo.so','_coo.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_dia.so','_dia.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_bsr.so','_bsr.so'),
                                                                                    ('/usr/local/lib/python3.3/site-packages/scipy/sparse/sparsetools/_csgraph.so','_csgraph.so')],
                                            "optimize": 2
                                            }
    scripts = []
    
if platform.system() == 'Windows':
    build_exe_options = {"packages": ["os","scipy","scipy.interpolate","NIF_WRF","NIF_WRF.DB","NIF_WRF.Analysis","NIF_WRF.util","NIF_WRF.GUI","NIF_WRF.GUI.widgets"], 
                                            "includes": ["numpy","scipy","scipy.interpolate","scipy.optimize","scipy.stats","matplotlib","matplotlib.pyplot","matplotlib.backends.backend_macosx","matplotlib.backends.backend_tkagg"],
                                            "excludes": [],
                                            "include_files": [('NIF_WRF/util/_StopPow.pyd','_StopPow.pyd'),
                                                              ('logo/WRF_logo.ico','favicon.ico'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_csr.pyd','_csr.pyd'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_csc.pyd','_csc.pyd'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_coo.pyd','_coo.pyd'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_dia.pyd','_dia.pyd'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_bsr.pyd','_bsr.pyd'),
                                                                                    ('C:\Python33\Lib\site-packages\scipy\sparse\sparsetools\_csgraph.pyd','_csgraph.pyd')],
                                            "optimize": 2,
                                             "include_msvcr": True,
                                             "icon": "logo/WRF_logo.ico"
                                            }
    scripts = ['win_postinst.py']

mac_options = {"iconfile": "logo/WRF_logo.icns"}
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "NIF WRF",                # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]main.exe",    # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None, # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
msi_options = {'data': msi_data}


setup(  name = "NIF_WRF",
        version = "0.1.2",
        description = "NIF WRF database and analysis code",
    	packages=['NIF_WRF', 'NIF_WRF.DB', 'NIF_WRF.GUI', 'NIF_WRF.GUI.widgets', 'NIF_WRF.util', 'NIF_WRF.Analysis'],
        options = {"build_exe": build_exe_options, "bdist_mac": mac_options, "bdist_msi": msi_options},
        scripts = scripts,
        executables = [Executable("NIF_WRF/main.py", base=base, copyDependentFiles=True, compress=True)])
