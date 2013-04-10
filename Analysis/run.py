
import os, sys, inspect
# add util folder to path
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"util")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from CSV import *
from Analyze_Spectrum import *
import numpy

data = read_csv('TestData.csv',3)
name = 'N123456'

random = [1e7,0.1,0.05]
systematic = [1e7,0.05,0.05]
Analyze_Spectrum(data,random,systematic,name)