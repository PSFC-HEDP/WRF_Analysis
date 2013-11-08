# This file contains several functions aiding in the analysis of entire shots' worth of data
__author__ = 'Alex Zylstra'

from NIF_WRF.DB.WRF_Analysis_DB import WRF_Analysis_DB
import numpy

ERR_TOTAL = 'total'
ERR_RANDOM = 'random'
ERR_SYSTEMATIC = 'systematic'

def avg_rhoR(shot, dim, error=ERR_TOTAL):
    """Calculate the average rhoR and error bar for the given shot and DIM.

    :param shot: The shot number to use
    :param dim: The DIM to calculate the average for
    :param error: (optional) What type of error bar to return. Supply either:

        Shot_Analysis.ERR_TOTAL
        Shot_Analysis.ERR_RANDOM
        Shot_Analysis.ERR_SYSTEMATIC

    """
    try:
        rhoR = []
        ran = []
        sys = []
        db = WRF_Analysis_DB()

        for pos in db.get_pos(shot, dim):
            rhoR.append(db.get_value(shot, dim, pos, 'rhoR')[0])
            ran.append(db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0])
            sys.append(db.get_value(shot, dim, pos, 'rhoR_sys_unc')[0])


        if len(rhoR) > 0:
            Avg = numpy.dot(rhoR, ran)/numpy.sum(ran)
            if error == ERR_RANDOM:
                Avg_err = 1/numpy.sqrt(numpy.sum(1/numpy.power(ran,2)))
            elif error == ERR_SYSTEMATIC:
                Avg_err = numpy.average(sys)
            else:
                err1 = 1/numpy.sqrt(numpy.sum(1/numpy.power(ran,2)))
                err2 = numpy.average(sys)
                Avg_err = numpy.sqrt(err1**2 + err2**2)

            return Avg, Avg_err
        else:
            return None, None
    except:
        return None, None

def avg_Rcm(shot, dim, error=ERR_TOTAL):
    """Calculate the average Rcm and error bar for the given shot and DIM.

    :param shot: The shot number to use
    :param dim: The DIM to calculate the average for
    :param error: (optional) What type of error bar to return. Supply either:

        Shot_Analysis.ERR_TOTAL
        Shot_Analysis.ERR_RANDOM
        Shot_Analysis.ERR_SYSTEMATIC

    """
    try:
        Rcm = []
        ran = []
        sys = []
        db = WRF_Analysis_DB()

        for pos in db.get_pos(shot, dim):
            Rcm.append(db.get_value(shot, dim, pos, 'Rcm')[0])
            ran.append(db.get_value(shot, dim, pos, 'Rcm_ran_unc')[0])
            sys.append(db.get_value(shot, dim, pos, 'Rcm_sys_unc')[0])


        if len(Rcm) > 0:
            Avg = numpy.dot(Rcm, ran)/numpy.sum(ran)
            if error == ERR_RANDOM:
                Avg_err = 1/numpy.sqrt(numpy.sum(1/numpy.power(ran,2)))
            elif error == ERR_SYSTEMATIC:
                Avg_err = numpy.average(sys)
            else:
                err1 = 1/numpy.sqrt(numpy.sum(1/numpy.power(ran,2)))
                err2 = numpy.average(sys)
                Avg_err = numpy.sqrt(err1**2 + err2**2)

            return Avg, Avg_err
        else:
            return None, None
    except:
        return None, None

def avg_Yield(shot, dim):
    """Calculate the average yield and error bar for the given shot and DIM.

    :param shot: The shot number to use
    :param dim: The DIM on shot to calculate the average for
    """
    try:
        Yp = []
        err = []
        db = WRF_Analysis_DB()

        for pos in db.get_pos(shot, dim):
            Yp.append(db.get_value(shot, dim, pos, 'Yield')[0])
            err.append(db.get_value(shot, dim, pos, 'Yield_ran_unc')[0])

        if len(Yp) > 0:
            Avg = numpy.dot(Yp, err)/numpy.sum(err)
            Avg_err = 1/numpy.sqrt(numpy.sum(1/numpy.power(err,2)))
            return Avg, Avg_err
        else:
            return None, None
    except:
        return None, None