
import os, sys, inspect
# add util folder to path
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"util")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from CSV import *
from Hohlraum import *
import numpy

data = read_csv('TestData.csv',3)
name = 'N123456'

#hohl_wall = read_csv('AAA12-119365_AA.csv')

h = Hohlraum(data,61,0,74)
print(h.get_E_shift())
h.plot_file('plot.eps')