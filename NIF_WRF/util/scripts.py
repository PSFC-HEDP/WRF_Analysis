__author__ = 'Alex Zylstra'

from NIF_WRF.DB.WRF_Analysis_DB import WRF_Analysis_DB
from NIF_WRF.Analysis import Shot_Analysis
import numpy
import csv
import os

def generate_shot_dim_summary(shot, dim, fname=None):
    """Generate summary info for a single shot and dim.

    :param shot: The shot number to use
    :param dim: The DIM
    :param fname: (optional) The file name to write out to. Defaults to:

        summary_SHOT_DIM.csv

    """
    db = WRF_Analysis_DB()
    if fname is None:
        fname = 'summary_' + shot + '_' + dim + '.csv'
    file = csv.writer(open(fname,'w'), delimiter=',')
    file.writerow([shot])
    file.writerow([dim])

    for pos in db.get_pos(shot, dim):
        file.writerow(['Position',pos])
        file.writerow(['Field', 'Value', 'SysUnc', 'StatUnc', 'TotUnc'])

        # Shock proton yield:
        Yp = db.get_value(shot, dim, pos, 'Yield')[0]
        Yp_ran = db.get_value(shot, dim, pos, 'Yield_ran_unc')[0]
        Yp_sys = db.get_value(shot, dim, pos, 'Yield_sys_unc')[0]
        Yp_tot = numpy.sqrt(Yp_ran**2 + Yp_sys**2)
        file.writerow(['Yield',
                      '{:.2e}'.format(Yp),
                      '{:.1f}'.format(100*Yp_ran/Yp)+'%',
                      '{:.1f}'.format(100*Yp_sys/Yp)+'%',
                      '{:.1f}'.format(100*Yp_tot/Yp)+'%'])

        # Shock rhoR
        rhoR = db.get_value(shot, dim, pos, 'rhoR')[0]
        rhoR_ran = db.get_value(shot, dim, pos, 'rhoR_ran_unc')[0]
        rhoR_sys = db.get_value(shot, dim, pos, 'rhoR_sys_unc')[0]
        rhoR_tot = numpy.sqrt(rhoR_ran**2 + rhoR_sys**2)
        file.writerow(['rhoR',
                      '{:.1f}'.format(rhoR)+'\t',
                      '{:.1f}'.format(rhoR_ran),
                      '{:.1f}'.format(rhoR_sys),
                      '{:.1f}'.format(rhoR_tot)])

def all_shot_dim_summary(dir='', use_shot_dirs=False):
    """Generate all of the individual shot/dim summary files.

    :param dir: (optional) Where to write out to. If the directory doesn't exist it will be created.
    Default is present working directory.
    :param use_shot_dirs: (optional) Whether to split output files into directories based on shot #
    """
    db = WRF_Analysis_DB()

    if not os.path.exists(dir):
        os.makedirs(dir)

    # loop over all shots and DIMs:
    for shot in db.get_shots():
        if use_shot_dirs:
            shot_dir = os.path.join(dir, shot)
            os.makedirs(shot_dir, exist_ok=True)
        else:
            shot_dir = dir

        for dim in db.get_dims(shot):
            fname = os.path.join(shot_dir, 'summary_' + shot + '_' + dim + '.csv')
            generate_shot_dim_summary(shot, dim, fname=fname)

def generate_allshot_summary(fname=None):
    """Generate a single summary CSV of all shots. Columns contain polar and equatorial rhoR, and equatorial yield,
    plus associated error bars.

    :param fname: (optional) The file name to write out to.
    """
    db = WRF_Analysis_DB()

    # get the file:
    if fname is None:
        fname = 'WRF_Summary.csv'
    file = csv.writer(open(fname,'w'), delimiter=',')

    # write the header info:
    file.writerow(['Shot',
                   '0-0 rhoR (mg/cm2)', 'ran unc (mg/cm2)', 'tot unc (mg/cm2)',
                   '90-78 rhoR (mg/cm2)', 'ran unc (mg/cm2)', 'tot unc (mg/cm2)',
                   'Yield', 'Tot Unc'])

    # write a row for each shot:
    for shot in db.get_shots():
        row = [shot, '', '', '', '', '', '', '', '']

        # get all the info:
        for dim in db.get_dims(shot):
            if dim == '90-78':
                Yp, Yp_err = Shot_Analysis.avg_Yield(shot, dim)
                row[7] = '{:.2e}'.format(Yp)
                row[8] = '{:.2e}'.format(Yp_err)
            rhoR, rhoR_tot_err = Shot_Analysis.avg_rhoR(shot, dim)
            rhoR_ran_err = Shot_Analysis.avg_rhoR(shot, dim, Shot_Analysis.ERR_RANDOM)[1]
            if dim == '0-0':
                i = 1
            elif dim == '90-78':
                i =4
            if i is not None:
                row[i] = '{:.1f}'.format(rhoR)
                row[i+1] = '{:.1f}'.format(rhoR_ran_err)
                row[i+2] = '{:.1f}'.format(rhoR_tot_err)

        # write the row to file:
        file.writerow(row)