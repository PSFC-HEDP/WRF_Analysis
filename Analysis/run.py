from rhoR_Analysis import *

r = rhoR_Analysis()
Rcm=400e-4
E0=14.7
#print(r.Eout(Rcm))

Rcm=300e-4
#print(r.Eout(Rcm))

Rcm=150e-4
#print(r.Eout(Rcm))

print(r.rhoR_Total(Rcm))
print(r.Calc_rhoR(10.4,E0))
print(r.Calc_rhoR(11,E0))
print(r.Calc_Rcm(11,0.13,E0=14.7,ModelErr=True))
print(r.Calc_Rcm(11,0.13,E0=14.7,ModelErr=False))

from rhoR_model_plots import *

#plot_rhoR_v_Energy(r)
#plot_Rcm_v_Energy(r)
#plot_rhoR_v_Rcm(r)
#print("profile")
#Rcm=300e-4
#plot_profile(r,Rcm)
#print(r.Eout(Rcm))
#print(r.rhoR_Total(Rcm))
#print(r.rhoR_Parts(Rcm))

# Rcm analysis for 2D cona:
#print("2D ConA", "Pole", "PoleErr", "Eq", "EqErr")
#print("N121202", r.Calc_Rcm(11.03,0.26,ModelErr=True), r.Calc_Rcm((10.68+10.84+10.45+10.73)/4,0.14,ModelErr=True) )
#print("N121210", r.Calc_Rcm((11.02+10.88)/2,0.13,ModelErr=True), r.Calc_Rcm((10.68+10.59+10.45+10.43)/4,0.14,ModelErr=True) )
#print("N121218", r.Calc_Rcm((11.02+11.08)/2,0.13,ModelErr=True), r.Calc_Rcm((10.67+10.67+10.40+10.47)/4,0.14,ModelErr=True) )
#print("N121219", r.Calc_Rcm((10.79),0.14,ModelErr=True), r.Calc_Rcm((10.68+10.72+10.16)/3,0.14,ModelErr=True) )
#print("N130211", r.Calc_Rcm(10.34,0.26,ModelErr=True), r.Calc_Rcm((10.59+10.8+10.52+10.76)/4,0.14,ModelErr=True) )
#print("N130212", r.Calc_Rcm((11.45+11.21)/2,0.13,ModelErr=True), r.Calc_Rcm((10.8+11.03+10.67+10.59)/4,0.14,ModelErr=True) )
#print("N130213", r.Calc_Rcm((11.16+10.92)/2,0.26,ModelErr=True), r.Calc_Rcm((10.39+10.84+10.42+10.30)/4,0.14,ModelErr=True) )
#print("N130226", r.Calc_Rcm((11.28+11.41+11.45)/3,0.13,ModelErr=True), r.Calc_Rcm((10.80+10.90+10.63+10.78)/4,0.14,ModelErr=True) )
#print("N130227", r.Calc_Rcm(11.44,0.13,ModelErr=True), r.Calc_Rcm((11.01+10.87+10.80+10.69)/4,0.14,ModelErr=True) )
#print("N130303", r.Calc_Rcm(12.13,0.26,ModelErr=True), r.Calc_Rcm((11.7+11.4+11.27+11.66)/4,0.28,ModelErr=True) )
#print("N130313", r.Calc_Rcm(11.29,0.13,ModelErr=True), r.Calc_Rcm((10.98+11.07+11.20+11.34)/4,0.14,ModelErr=True) )

#print(r.rhoR_Parts(223e-4))
#print(r.rhoR_Parts(221.5e-4))
#print(r.rhoR_Parts(219e-4))
#print(r.rhoR_Parts(216e-4))