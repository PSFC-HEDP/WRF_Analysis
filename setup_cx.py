import sys
from cx_Freeze import setup, Executable
import scipy
import platform

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
# Dependencies are automatically detected, but it might need fine tuning.
if platform.system() == 'Darwin':
    build_exe_options = {"packages": ["os","scipy","WRF_Analysis","WRF_Analysis.Analysis","WRF_Analysis.util","WRF_Analysis.GUI","WRF_Analysis.GUI.widgets"],
                                            "includes": ["numpy","scipy","scipy.interpolate","scipy.linalg","scipy.optimize","scipy.stats","matplotlib","matplotlib.pyplot","matplotlib.backends.backend_macosx","matplotlib.backends.backend_tkagg"],
                                            "excludes": [],
                                            "include_files": [('WRF_Analysis/util/_StopPow.so','_StopPow.so')],
                                            "optimize": 2
                                            }
    scripts = []
# 
                                                                                    # ('/usr/local/lib/python3.4/site-packages/scipy/sparse/_csparsetools.so','_csparsetools.so'),
                                                                                    # ('/usr/local/lib/python3.4/site-packages/scipy/sparse/_sparsetools.so','_sparsetools.so'),
                                                                                    # ('/usr/local/lib/python3.4/site-packages/scipy/linalg/_fblas.so','_fblas.so')
if platform.system() == 'Windows':
    build_exe_options = {"packages": ["os","scipy","scipy.interpolate","WRF_Analysis","WRF_Analysis.Analysis","WRF_Analysis.util","WRF_Analysis.GUI","WRF_Analysis.GUI.widgets"],
                                            "includes": ["numpy","scipy","scipy.interpolate","scipy.optimize","scipy.stats","matplotlib","matplotlib.pyplot","matplotlib.backends.backend_macosx","matplotlib.backends.backend_tkagg"],
                                            "excludes": [],
                                            "include_files": [('WRF_Analysis/util/_StopPow.pyd','_StopPow.pyd'),
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
     "WRF Analysis",                # Name
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


setup(  name = "WRF_Analysis",
        version = "0.1",
        description = "WRF analysis utilities",
    	packages=['WRF_Analysis', 'WRF_Analysis.GUI', 'WRF_Analysis.GUI.widgets', 'WRF_Analysis.util', 'WRF_Analysis.Analysis'],
        options = {"build_exe": build_exe_options, "bdist_mac": mac_options, "bdist_msi": msi_options},
        scripts = scripts,
        executables = [Executable("WRF_Analysis/main.py", base=base, copyDependentFiles=True, compress=True)])
