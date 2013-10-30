#from distutils.core import setup
import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includefiles = ['NIF_WRF/util/_StopPow.so', 'NIF_WRF/util/SRIM/Hydrogen in Aluminum.txt']
includes = []
excludes = []
packages = []

setup(
    name='NIF_WRF',
    version='0.1',
    packages=['NIF_WRF', 'NIF_WRF.DB', 'NIF_WRF.GUI', 'NIF_WRF.GUI.widgets', 'NIF_WRF.util', 'NIF_WRF.Analysis'],
    url='',
    license='MIT',
    author='Alex Zylstra',
    author_email='azylstra@psfc.mit.edu',
    description='NIF WRF analysis and database code',
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}},
    executables = [Executable("NIF_WRF/main.py", base=base)]
)