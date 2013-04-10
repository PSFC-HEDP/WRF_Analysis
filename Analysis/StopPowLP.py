# Stopping power calculator
# Reference: Li-Petrasso Phys. Rev. Lett. 70, 3059 (1993)
# Author: A Zylstra
# Date: 12/19/2012
# Code uses CGS units generally

import math
from Constants import *

# options
collective = 1

def test():
    mt = 1
    Zt = 1
    Et = 10
    Af = [9,me/mp]
    Zf = [4,1]
    Tf = [0.03,0.03]
    nf = [1.2e23,4*1.23e23]
    print(dEdr(mt,Zt,Et,Af,Zf,Tf,nf))
    
def dEdr(mt, Zt, Et, mf, Zf, Tf, nf):
    """Calculate stopping power for a multi component plasma. m and Z in atomic units; Et in MeV and Ti in keV. nf in 1/cc. Field inputs (mf, Zf, Tf, nf) are arrays. Returns MeV/cm."""
    if Et <= 0:
        return 0
    dEdr = 0 # return value
    for i in range(len(mf)):
        dEdr += dEdr_single( mt, Zt, Et, mf[i], Zf[i], Tf[i], nf[i] )
    return dEdr
    
def dEdr_single(mt, Zt, Et, mf, Zf, Tf, nf):
    """Calculate stopping power for a single field species. m and Z in atomic units; Et in MeV and Ti in keV. nf in 1/cc. Returns MeV/cm."""
    Et = Et * 1e3 # convert to keV
    xtf = (mf/mt)*(Et/Tf) # ratio of velocities
    LL = LogLambda(mt, Zt, Et, mf, Zf, Tf, nf) # Coulomb log
    dEdr = 0 # return value
    dEdr += LL*G(mt, Zt, Et, mf, Zf, Tf, nf, xtf, LL) # add standard stopping term
    if collective == 1 and xtf > 1/(1.261): # sanity check to keep arg of log > 1
        dEdr += 0.5 * math.log(1.261*xtf) # add collective effects
    # calculate prefactor:
    vt = c*math.sqrt(2*Et/(mt*mpc2))
    tmp = math.pow(Zt*e/vt,2)
    wpf = math.sqrt( 4*math.pi*nf*math.pow(Zf*e,2) / (mf*mp) )
    ret = -tmp*wpf*wpf*dEdr # erg/cm
    return ret*(1e-13)/(1.602e-19) # MeV/cm
    
def LogLambda(mt, Zt, Et, mf, Zf, Tf, nf):
    """ Coulomb logarithm. m and Z in atomic units; Et and Ti in keV. nf in 1/cc. """
    mr = mp*mt*mf/(mt+mf) # reduced mass
    u = math.sqrt(2*mt*mp*Et*keVtoeV)/((mt+mf)*mp) # relative velocity
    lD = math.sqrt( (kB*Tf*keVtoK) / (4 * math.pi * nf * math.pow(e*Zf,2)) ) # Debye length
    pperp = Zf*e*Zt*e / (mr*u*u) # classical b90
    pmin = math.sqrt( math.pow(pperp,2) + math.pow(hbar/(2*mr*u),2) ) # see L-P
    return 0.5*math.log(1 + math.pow(lD/pmin,2) )

def G(mt, Zt, Et, mf, Zf, Tf, nf, xtf, LL):
    """ Chandrasekhar function. m and Z in atomic units; Et and Ti in keV. nf in 1/cc."""
    # see L-P
    rat = mf / mt # mass ratio
    mu = 1.12838*math.sqrt(xtf)*math.exp(-xtf)
    erfunc = math.erf( math.sqrt(xtf) )
    return (erfunc  - mu) - rat*(mu - erfunc/LL)