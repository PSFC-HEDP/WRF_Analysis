from CSV import *
from GaussFit import *
import numpy

data = read_csv('TestData.csv',3)

FitObj = GaussFit(data,name='N123456')

print(FitObj.get_fit())
print(FitObj.red_chi2())
print(FitObj.chi2_fit_unc())
FitObj.plot_file('plot.eps')
#FitObj.plot_window()