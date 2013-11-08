__author__ = 'Alex Zylstra'

import scipy
import numpy as np
from NIF_WRF.Analysis.rhoR_Model import rhoR_Model
from NIF_WRF.DB.WRF_Analysis_DB import WRF_Analysis_DB
from NIF_WRF.DB.Snout_DB import Snout_DB

ANGLE_DEG = 'degrees'
ANGLE_RAD = 'radians'

def Rcm(theta, phi, r0, dr, l, m, angles=ANGLE_RAD):
    """Define the radius of an asymmetry mode, as function of polar/azimuthal angle.

        :param theta: Polar angle in radians or degrees. By default uses radians, specify with `angles`.
            Can be supplied as either a single number, list, or as np.ndarray
        :param phi: Azimuthal angle in radians or degrees. By default uses radians, specify with `angles.
            Can be supplied as either a single number, list, or as np.ndarray
        :param r0: Unperturbed radius
        :param dr: Fractional perturbation amplitude
        :param l: Spherical harmonic mode number l
        :param m: Spherical harmonic mode number m
        :param angles: (optional) Type of angle supplied, use Asymmetries.ANGLE_DEG or Asymmetries.ANGLE_RAD
        """

    # Convert theta and phi if necessary:
    if not isinstance(theta, np.ndarray):
        theta = np.asarray(theta)
    if not isinstance(phi, np.ndarray):
        phi = np.asarray(phi)

    # Convert angles if necessary:
    if angles is ANGLE_DEG:
        theta = np.multiply(theta , np.pi / 180.)
        phi = np.multiply(phi , np.pi / 180.)

    ret = np.empty_like(theta)  # return array
    # Loop to calculate each return value
    for i in range(len(ret)):
        temp, temp2 = scipy.special.lpmn(m, l, np.cos(theta[i]))  # note that scipy uses 'math' convention for l,m
        Plm = temp[m][l]
        imphi = np.complex(0, m*phi[i])
        # see http://mathworld.wolfram.com/SphericalHarmonic.html
        norm = np.sqrt( (2*l+1)/(4*np.pi) * scipy.misc.factorial(l-m)/scipy.misc.factorial(l+m) )

        ret[i] = r0 * (1 + dr * norm * np.real(np.exp(-imphi) * Plm))
    return ret

def rhoR(theta, phi, r0, dr, l, m, model=None, angles=ANGLE_RAD):
    """Define the rhoR of an asymmetry mode, as function of polar/azimuthal angle.

        :param theta: Polar angle in radians or degrees. By default uses radians, specify with `angles`.
            Can be supplied as either a single number, list, or as np.ndarray
        :param phi: Azimuthal angle in radians or degrees. By default uses radians, specify with `angles.
            Can be supplied as either a single number, list, or as np.ndarray
        :param r0: Unperturbed rhoR
        :param dr: Fractional perturbation amplitude
        :param l: Spherical harmonic mode number l
        :param m: Spherical harmonic mode number m
        :param model: (optional) The `rhoR_Model` to use in analysis. If none is supplied, default options are used.
        :param angles: (optional) Type of angle supplied, use Asymmetries.ANGLE_DEG or Asymmetries.ANGLE_RAD
        """
    # Set up rhoR model:
    if model is None:
        model = rhoR_Model()
    assert isinstance(model, rhoR_Model)

    # Get data from Rcm method:
    r = Rcm(theta, phi, r0, dr, l, m, angles=angles)

    # Convert each r to rhoR
    ret = np.empty_like(r)  # return array
    for i in range(len(r)):
        ret[i] = model.rhoR_Total(r[i])
    return np.multiply(ret, 1e3)

def fit_polar(theta, rR, rR_err, l, angles=ANGLE_RAD):
    """Fit a polar (m=0) asymmetry mode to data.

    :param theta: Polar angle in radians or degrees. By default uses radians, specify with `angles`.
        Can be supplied as either a list, or as np.ndarray
    :param rR: Areal density data in mg/cm2 corresponding to `theta`
        Can be supplied as either a list, or as np.ndarray
    :param rR_err: Error bars (1 sigma) on `rR`
    :param l: Spherical harmonic mode number l
    :param angles: (optional) Type of angle supplied, use Asymmetries.ANGLE_DEG or Asymmetries.ANGLE_RAD
    """
    model = rhoR_Model()
    # Convert angles if necessary:
    if angles is ANGLE_DEG:
        theta = np.multiply(theta , np.pi / 180.)

    phi = np.zeros_like(theta)
    m = 0.

    def asym(theta, r0, dr):
        # add sanity checking:
        if r0 < 100e-4 or dr > 1.:
            return np.zeros_like(theta)
        return rhoR(theta, phi, r0, dr, l, m, model=model)

    fit, pcov = scipy.optimize.curve_fit(asym,
                                         theta,
                                         rR,
                                         p0=[0.03, 0.],
                                         sigma=rR_err)
    # Correct for scipy weirdness:
    # see http://nbviewer.ipython.org/5030045
    perr_scaled = np.sqrt(np.diag(pcov))
    chi = (rR - asym(theta, *fit)) / rR_err
    chi2 = (chi**2).sum()
    dof = len(rR) - len(fit)
    perr = np.divide(perr_scaled, np.sqrt((chi2/dof)))
    if np.isnan(perr[0]) or np.isnan(perr[1]):
        raise ValueError

    # Fit parameters:
    r0 = fit[0]
    delta = fit[1]
    r0_unc =perr[0]
    delta_unc = perr[1]
    # Calculate 0 order rhoR and uncertainty:
    rhoR0 = rhoR([0.], [0.], r0, 0., 2, 0)[0]
    rhoR0_max = rhoR([0.], [0.], r0-r0_unc, 0., 2, 0)[0]
    rhoR0_min = rhoR([0.], [0.], r0+r0_unc, 0., 2, 0)[0]
    rhoR0_unc = (rhoR0_max-rhoR0_min)/2.

    return r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc

def fit_shot(shot, l, error='random'):
    """Fit a l mode asymmetry to a given shot.

    :param shot: The shot number to fit (given as a str)
    :param l: The polar Legendre mode number to fit
    :param error: (optional) type of error bar to use: 'total' or 'random'
    """
    try:
        db = WRF_Analysis_DB()
        db_snout = Snout_DB()

        # Sanity check that 2 DIMs are available:
        if len(db.get_dims(shot)) < 2:
            raise ValueError

        # Retrieve data from the DB
        theta = []
        rhoR = []
        rhoR_err = []
        for dim in db.get_dims(shot):
            for pos in db.get_pos(shot, dim):
                val = db.get_value(shot, dim, pos, 'rhoR')[0]
                err_ran = db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0]
                err_sys = db.get_value(shot, dim, pos, 'rhoR_sys_unc')[0]

                angle = db_snout.get_theta('Generic', dim, pos)[0]
                if error == 'random':
                    err = err_ran
                else:
                    err = np.sqrt(err_sys**2 + err_ran**2)

                theta.append(angle)
                rhoR.append(val)
                rhoR_err.append(err)

        if len(theta) < 2:
            raise ValueError
        # if there are only 2 points scipy is silly and refuses to give pcov
        # fix by adding a third point with giant error bar so it doesn't affect fit
        if len(theta) == 2:
            theta.append(theta[0])
            rhoR.append(rhoR[0])
            rhoR_err.append(3*rhoR_err[0])
            theta.append(theta[1])
            rhoR.append(rhoR[1])
            rhoR_err.append(3*rhoR_err[1])

        # Convert to ndarray:
        theta = np.asarray(theta)
        rhoR = np.asarray(rhoR)
        rhoR_err = np.asarray(rhoR_err)

        return fit_polar(theta, rhoR, rhoR_err, l, angles=ANGLE_DEG)
    except Exception as inst:
        print('Cannot fit asymmetry: ' + shot)
        print(inst)
        ret = np.empty(6)
        ret.fill(np.nan)
        return ret

def Rcm_azi(theta, phi, r0, dr, dP2, dP4, m, mphi, angles=ANGLE_RAD):
    """Define the radius of an asymmetry mode, as function of polar/azimuthal angle."""
    # Convert theta and phi if necessary:
    if not isinstance(theta, np.ndarray):
        theta = np.asarray(theta)
    if not isinstance(phi, np.ndarray):
        phi = np.asarray(phi)

    # Convert angles if necessary:
    if angles is ANGLE_DEG:
        theta = np.multiply(theta , np.pi / 180.)
        phi = np.multiply(phi , np.pi / 180.)

    ret = r0*np.ones_like(theta)  # return array
    # Loop to calculate each return value
    for i in range(len(ret)):
        # P2:
        temp, temp2 = scipy.special.lpmn(m, 2, np.cos(theta[i]))  # note that scipy uses 'math' convention for l,m
        Plm = temp[m][2]
        imphi = np.complex(0, m*phi[i]+mphi)
        # see http://mathworld.wolfram.com/SphericalHarmonic.html
        norm = np.sqrt( (2*2+1)/(4*np.pi) * scipy.misc.factorial(2-m)/scipy.misc.factorial(2+m) )

        ret[i] += r0 * dr * norm * np.real(np.exp(-imphi) * Plm)

        # P4:
        temp, temp2 = scipy.special.lpmn(m, 4, np.cos(theta[i]))  # note that scipy uses 'math' convention for l,m
        Plm = temp[m][4]
        imphi = np.complex(0, m*phi[i]+mphi)
        # see http://mathworld.wolfram.com/SphericalHarmonic.html
        norm = np.sqrt( (2*4+1)/(4*np.pi) * scipy.misc.factorial(4-m)/scipy.misc.factorial(4+m) )

        ret[i] += r0 * dr * norm * np.real(np.exp(-imphi) * Plm)

        # m mode:
        imphi = np.complex(0, m*phi[i]+mphi)
        ret[i] += r0 * dr * np.real(np.exp(-imphi) * np.sin(theta[i]))

    return ret

def rhoR_azi(theta, phi, r0, dr, dP2, dP4, m, mphi, model=None, angles=ANGLE_RAD):
    """Define the rhoR of an azimuthal asymmetry mode, as function of polar/azimuthal angle."""
    # Set up rhoR model:
    if model is None:
        model = rhoR_Model()
    assert isinstance(model, rhoR_Model)

    # Get data from Rcm method:
    r = Rcm_azi(theta, phi, r0, dr, dP2, dP4, m, mphi, angles=angles)

    # Convert each r to rhoR
    ret = np.empty_like(r)  # return array
    for i in range(len(r)):
        ret[i] = model.rhoR_Total(r[i])
    return np.multiply(ret, 1e3)

def fit_azimuthal(theta, phi, rR, rR_err, dP2, dP4, m, mphi, angles=ANGLE_RAD):
    """Fit a azimuthal asymmetry mode to data.

    :param theta: Polar angle in radians or degrees. By default uses radians, specify with `angles`.
        Can be supplied as either a list, or as np.ndarray
    :param phi: Azimuthal angle in radians or degrees. By default uses radians, specify with `angles`.
        Can be supplied as either a list, or as np.ndarray
    :param rR: Areal density data in mg/cm2 corresponding to `theta`
        Can be supplied as either a list, or as np.ndarray
    :param rR_err: Error bars (1 sigma) on `rR`
    :param dP2: P2 mode amplitude
    :param dP4: P4 mode amplitude
    :param m: Spherical harmonic mode number m
    :param angles: (optional) Type of angle supplied, use Asymmetries.ANGLE_DEG or Asymmetries.ANGLE_RAD
    """
    model = rhoR_Model()
    # Convert angles if necessary:
    if angles is ANGLE_DEG:
        theta = np.multiply(theta , np.pi / 180.)
        phi = np.multiply(phi, np.pi / 180.)

    def asym(theta, r0, dr):
        # add sanity checking:
        if r0 < 100e-4 or dr > 1.:
            return np.zeros_like(theta)
        return rhoR_azi(theta, phi, r0, dr, dP2, dP4, m, mphi, model=model)

    fit, pcov = scipy.optimize.curve_fit(asym,
                                         theta,
                                         rR,
                                         p0=[0.03, 0.],
                                         sigma=rR_err)
    # Correct for scipy weirdness:
    # see http://nbviewer.ipython.org/5030045
    perr_scaled = np.sqrt(np.diag(pcov))
    chi = (rR - asym(theta, *fit)) / rR_err
    chi2 = (chi**2).sum()
    dof = len(rR) - len(fit)
    perr = np.divide(perr_scaled, np.sqrt((chi2/dof)))
    if np.isnan(perr[0]) or np.isnan(perr[1]):
        raise ValueError

    # Fit parameters:
    r0 = fit[0]
    delta = fit[1]
    r0_unc =perr[0]
    delta_unc = perr[1]
    # Calculate 0 order rhoR and uncertainty:
    rhoR0 = rhoR([0.], [0.], r0, 0., 2, 0)[0]
    rhoR0_max = rhoR([0.], [0.], r0-r0_unc, 0., 2, 0)[0]
    rhoR0_min = rhoR([0.], [0.], r0+r0_unc, 0., 2, 0)[0]
    rhoR0_unc = (rhoR0_max-rhoR0_min)/2.

    return r0, r0_unc, delta, delta_unc, rhoR0, rhoR0_unc

def fit_shot_azimuthal(shot, m, mphi, dP2, dP4):
    """Fit a m mode asymmetry to a given shot."""
    try:
        # Sanity check that 2 DIMs are available:
        db = WRF_Analysis_DB()
        db_snout = Snout_DB()
        if len(db.get_dims(shot)) < 2:
            raise ValueError

        # Retrieve data from the DB
        theta = []
        phi = []
        rhoR = []
        rhoR_err = []
        for dim in db.get_dims(shot):
            for pos in db.get_pos(shot, dim):
                val = db.get_value(shot, dim, pos, 'rhoR')[0]
                err_ran = db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0]

                shotTheta = db_snout.get_theta('Generic', dim, pos)[0]
                shotPhi = db_snout.get_phi('Generic', dim, pos)[0]
                err = err_ran

                theta.append(shotTheta)
                phi.append(shotPhi)
                rhoR.append(val)
                rhoR_err.append(err)

        if len(theta) < 2:
            raise ValueError
        # if there are only 2 points scipy is silly and refuses to give pcov
        # fix by adding a third point with giant error bar so it doesn't affect fit
        if len(theta) == 2:
            theta.append(theta[0])
            rhoR.append(rhoR[0])
            rhoR_err.append(3*rhoR_err[0])
            theta.append(theta[1])
            rhoR.append(rhoR[1])
            rhoR_err.append(3*rhoR_err[1])

        # Convert to ndarray:
        theta = np.asarray(theta)
        rhoR = np.asarray(rhoR)
        rhoR_err = np.asarray(rhoR_err)

        return fit_azimuthal(theta, phi, rhoR, rhoR_err,  dP2, dP4, m, mphi, angles=ANGLE_DEG)
    except Exception as inst:
        print('Cannot fit asymmetry: ' + shot)
        print(inst)
        ret = np.empty(6)
        ret.fill(np.nan)
        return ret