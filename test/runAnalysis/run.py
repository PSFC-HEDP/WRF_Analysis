
import os, sys, inspect
# add util folder to path
#cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"util")))
#if cmd_subfolder not in sys.path:
#    sys.path.insert(0, cmd_subfolder)

from util.CSV import *
from Analysis.Analyze_Spectrum import *
from Analysis.Hohlraum import *
import numpy

# read in the raw data:
data = read_csv('TestData.csv',3)
name = 'N123456'

hohl_wall = read_csv('AAA12-119365_AA.csv',crop=0,cols=[2,4,5])
theta=76.371
dtheta=(180/math.pi)*math.asin(1/50)
angles = [theta-dtheta,theta+dtheta]

random = [1e7,0.085,0.05]
systematic = [1e7,0.075,0.05]

result = Analyze_Spectrum(data,random,systematic,name=name,hohl_wall=hohl_wall,LOS=angles, rhoR_plots=True)

print(result)