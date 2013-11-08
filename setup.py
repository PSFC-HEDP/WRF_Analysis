import sys
from cx_Freeze import setup, Executable
import scipy
import scipy.interpolate

# Dependencies are automatically detected, but it might need fine tuning.
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

mac_options = {"iconfile": "logo/WRF_logo.icns"}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "NIF_WRF",
        version = "0.1.2",
        description = "NIF WRF database and analysis code",
    	packages=['NIF_WRF', 'NIF_WRF.DB', 'NIF_WRF.GUI', 'NIF_WRF.GUI.widgets', 'NIF_WRF.util', 'NIF_WRF.Analysis'],
        options = {"build_exe": build_exe_options, "bdist_mac": mac_options},
        executables = [Executable("NIF_WRF/main.py", base=base, copyDependentFiles=True, compress=True)])