__author__ = 'Alex Zylstra'

from NIF_WRF.GUI.WRF_Analyzer import WRF_Analyzer
from NIF_WRF.DB import Database
from NIF_WRF.DB.WRF_Analysis_DB import WRF_Analysis_DB
from NIF_WRF.DB.WRF_Data_DB import WRF_Data_DB
from NIF_WRF.DB.WRF_InitAnalysis_DB import WRF_InitAnalysis_DB
from NIF_WRF.DB.WRF_Setup_DB import WRF_Setup_DB
from NIF_WRF.DB.Hohlraum_DB import Hohlraum_DB
from NIF_WRF.DB.Snout_DB import Snout_DB
from NIF_WRF.DB.WRF_rhoR_Model_DB import WRF_rhoR_Model_DB
from NIF_WRF.DB.WRF_Analysis_Param_DB import WRF_Analysis_Param_DB
from NIF_WRF.GUI.widgets.Option_Prompt import Option_Prompt
from NIF_WRF.GUI.widgets.Model_Frame import Model_Frame
from NIF_WRF.GUI.WRF_Progress_Dialog import WRF_Progress_Dialog
from NIF_WRF.Analysis.rhoR_Analysis import rhoR_Analysis
from NIF_WRF.Analysis.Analyze_Spectrum import Analyze_Spectrum

import matplotlib
import math

def rerun(shot, dim, pos, OutputDir=None, usePrevParam=False, usePrevModel=True):
    """Rerun a single given analysis.

    :param shot: The shot number
    :param dim: The DIM
    :param pos: The WRF position #
    :param OutputDir: (optional) the directory to save output to. If `None`, then the user will be prompted.
    :param usePrevParam: Set to `True` to load previous analysis parameters (if available) from database
    :param usePrevModel: Set to `True` to load previous rhoR model parameters (if available) from database
    """
    # Database:
    analysis_db = WRF_Analysis_DB()

    # Sanity checks:
    assert shot in analysis_db.get_shots()
    assert dim in analysis_db.get_dims(shot)
    assert pos in analysis_db.get_pos(shot, dim)

    # Rerun:
    print(shot, dim, pos)

    # More database access:
    init_db = WRF_InitAnalysis_DB()
    data_db = WRF_Data_DB()
    setup_db = WRF_Setup_DB()
    hohl_db = Hohlraum_DB()
    snout_db = Snout_DB()
    model_db = WRF_rhoR_Model_DB()
    param_db = WRF_Analysis_Param_DB()

    # get the spectrum and image:
    spectrum = data_db.get_spectrum(shot, dim, pos, False)
    # sanity check:
    if spectrum is None:
        from tkinter.messagebox import showerror
        showerror('Error', 'Could not load spectrum from database')
        return
    try:
        Nxy = data_db.get_Nxy(shot, dim, pos, False)
    except TypeError:  # data not found
        Nxy = None

    # get uncertainties
    random = [0, 0, 0]
    random[0] = init_db.get_value(shot, dim, pos, 'unc_yield_random')[0]
    random[1] = init_db.get_value(shot, dim, pos, 'unc_mean_random')[0]
    random[2] = init_db.get_value(shot, dim, pos, 'unc_sigma_random')[0]
    systematic = [0, 0, 0]
    systematic[0] = init_db.get_value(shot, dim, pos, 'unc_yield_sys')[0]
    systematic[1] = init_db.get_value(shot, dim, pos, 'unc_mean_sys')[0]
    systematic[2] = init_db.get_value(shot, dim, pos, 'unc_sigma_sys')[0]

    # get a name and summary
    name = shot + '_' + dim + '_Pos' + str(pos)
    # Get the shot title/name description thing
    shot_name_query = setup_db.query_col(shot, dim, pos, 'shot_name')

    # check for errors
    if shot_name_query is None or len(shot_name_query) is 0:
        summary = shot
    else:
        summary = shot + ' , ' + shot_name_query[0]
    # if we are using TeX for rendering, then fix underscores:
    if matplotlib.rcParams['text.usetex'] == True:
        summary = summary.replace('_',r'$\textunderscore$')

    # get snout info:
    snout = setup_db.query_col(shot, dim, pos, 'snout')[0]

    # Figure out if we need a hohlraum correction.
    # Set by whether one was used before:
    try:
        prev_Au = analysis_db.get_value(shot, dim, pos, 'Au')[0]
        prev_DU = analysis_db.get_value(shot, dim, pos, 'DU')[0]
        prev_Al = analysis_db.get_value(shot, dim, pos, 'Al')[0]
        do_hohl_corr = math.fabs(prev_Au) > 0 or math.fabs(prev_DU) > 0 or math.fabs(prev_Al) > 0
    except:
        do_hohl_corr = False

    # get the hohlraum wall:
    if do_hohl_corr:
        hohl_drawing = setup_db.query_col(shot, dim, pos, 'hohl_drawing')[0]
        while ' ' in hohl_drawing:
            hohl_drawing = hohl_drawing.replace(' ', '')
        wall = hohl_db.get_wall(drawing=hohl_drawing)
        hohl_thick = None

        if wall is None or len(wall) == 0:
            from tkinter.messagebox import askyesnocancel

            # First, lets try to pick hohlraum from a list:
            msgstr = shot + ', ' + dim + ', ' + str(pos)
            response = askyesnocancel('Warning '+msgstr, 'Could not load hohlraum definition for ' + hohl_drawing
                                                 + '. Choose from list?')
            if response:
                dialog = Option_Prompt(None, title='Choose hohlraum for '+msgstr, text='Pre-existing hohlraums',
                                       options=hohl_db.get_drawings())
                wall = hohl_db.get_wall(drawing=dialog.result)
            elif not response:
                response = askyesnocancel('Warning '+msgstr, 'Could not load hohlraum definition for ' + hohl_drawing
                                                     + '. Specify manually?')
                if response:
                    from NIF_WRF.GUI.widgets.Value_Prompt import Value_Prompt
                    dialog = Value_Prompt(None, title='Hohlraum for '+msgstr, text='Input Au thickness in um', default=0.)
                    Au = dialog.result
                    dialog = Value_Prompt(None, title='Hohlraum for '+msgstr, text='Input DU thickness in um', default=0.)
                    DU = dialog.result
                    dialog = Value_Prompt(None, title='Hohlraum for '+msgstr, text='Input Al thickness in um', default=0.)
                    Al = dialog.result

                    hohl_thick = [Au, DU, Al]
                    wall = None
                else:
                    wall = None

            elif response is None:
                return
            else:
                wall = None

        # get the bump info from the database
        temp = hohl_db.get_bump(hohl_drawing)
        # Stuff for the bump correction:
        if hohl_drawing is not None and hohl_drawing != '' \
                and temp is not None:
            use_bump_corr = temp[1]
            bump_corr = temp[2]
        else:
            use_bump_corr = False
            bump_corr = 0.
    else:
        wall = None
        hohl_thick = None
        use_bump_corr = False
        bump_corr = 0

    # calculate angles:
    theta = snout_db.get_theta(snout, dim, pos)[0]
    r = snout_db.get_r(snout, dim, pos)[0]
    dtheta = math.atan2(1., r)*180./math.pi
    angles = [theta-dtheta, theta+dtheta]

    # Get a guess to help the fitting routine from the numbers in the initial analysis
    guess_Y = init_db.get_value(shot, dim, pos, 'fit_yield')
    guess_E = init_db.get_value(shot, dim, pos, 'fit_mean')
    guess_s = init_db.get_value(shot, dim, pos, 'fit_sigma')
    if len(guess_Y) > 0 and len(guess_E) > 0 and len(guess_s) > 0:
        fit_guess = [guess_Y[0], guess_E[0], guess_s[0]]
    else:
        fit_guess = None

    # energy limits based on default window
    fit_mean = init_db.get_value(shot, dim, pos, 'fit_mean')[0]
    min_energy = fit_mean - 2
    max_energy = fit_mean + 2
    limits = [min_energy, max_energy]

    # get the rhoR model
    mp = model_db.get_results(shot, dim, pos)
    model = None
    if usePrevModel:
        try:
            model = rhoR_Analysis(shell_mat=mp['shell_mat'],
                          Ri=mp['Ri'],
                          Ro=mp['Ro'],
                          fD=mp['fD'],
                          f3He=mp['f3He'],
                          P0=mp['P0'],
                          Te_Gas=mp['Te_Gas'],
                          Te_Shell=mp['Te_Shell'],
                          Te_Abl=mp['Te_Abl'],
                          Te_Mix=mp['Te_Mix'],
                          rho_Abl_Max=mp['rho_Abl_Max'],
                          rho_Abl_Min=mp['rho_Abl_Min'],
                          rho_Abl_Scale=mp['rho_Abl_Scale'],
                          MixF=mp['MixF'],
                          Tshell=mp['Tshell'],
                          Mrem=mp['Mrem'],
                          E0=mp['E0'],
                          Ri_Err=mp['Ri_Err'],
                          Ro_Err=mp['Ro_Err'],
                          P0_Err=mp['P0_Err'],
                          fD_Err=mp['fD_Err'],
                          f3He_Err=mp['f3He_Err'],
                          Te_Gas_Err=mp['Te_Gas_Err'],
                          Te_Shell_Err=mp['Te_Shell_Err'],
                          Te_Abl_Err=mp['Te_Abl_Err'],
                          Te_Mix_Err=mp['Te_Mix_Err'],
                          rho_Abl_Max_Err=mp['rho_Abl_Max_Err'],
                          rho_Abl_Min_Err=mp['rho_Abl_Min_Err'],
                          rho_Abl_Scale_Err=mp['rho_Abl_Scale_Err'],
                          MixF_Err=mp['MixF_Err'],
                          Tshell_Err=mp['Tshell_Err'],
                          Mrem_Err=mp['Mrem_Err'])
        except:
            pass
    if model is None:
        adv_frame = Model_Frame(None, shot=shot)
        model = adv_frame.get_rhoR_Analysis()

    # if no directory was provided, then prompt for one:
    if OutputDir is None or OutputDir == '':
        from tkinter.filedialog import askdirectory
        opts = dict(mustexist='False',
                       initialdir=Database.DIR,
                       title='Save files to')
        OutputDir = askdirectory(**opts)
        # sanity check:
        if OutputDir == '':  # user cancelled
            return

    # If the user requested using previous analysis parameters:
    if usePrevParam:
        try:
            prev_param = param_db.get_results(shot, dim, pos)
            if prev_param['use_hohl_corr'] == False and do_hohl_corr == True:
                wall = None
                hohl_thick = None
            name = prev_param['name']
            summary = prev_param['summary']
            limits = [prev_param['min_E'], prev_param['max_E']]
            use_bump_corr = prev_param['use_bump_corr']
            bump_corr = prev_param['bump_corr']
        except:
            pass

    # do the actual analysis:
    result, corr_spec = Analyze_Spectrum(spectrum,
                              random,
                              systematic,
                              angles,
                              hohl_wall=wall,
                              hohl_thick=hohl_thick,
                              name=name,
                              summary=summary,
                              plots=True,
                              verbose=True,
                              rhoR_plots=False,
                              OutputDir=OutputDir,
                              Nxy=Nxy,
                              ProgressBar=None,
                              ShowSlide=False,
                              model=model,
                              fit_guess=fit_guess,
                              limits=limits,
                              use_bump_corr=use_bump_corr,
                              bump_corr=bump_corr)

    # add to DB:
    print(result)
    analysis_db.load_results(shot, dim, pos, result)
    analysis_param = {'use_hohl_corr': do_hohl_corr,
                      'name': name,
                      'summary': summary,
                      'min_E': limits[0],
                      'max_E': limits[1],
                      'use_bump_corr': use_bump_corr,
                      'bump_corr': bump_corr}
    param_db.load_results(shot, dim, pos, analysis_param)
    model_db.load_from_model(shot, dim, pos, model)

    # Add hohlraum-corrected spectrum to the database if necessary:
    if corr_spec is not None:
        wrf_id = data_db.get_wrf_id(shot, dim, pos)[0]
        cr39_id = data_db.get_cr39_id(shot, dim, pos)[0]
        # get the date and time:
        import datetime
        now = datetime.datetime.now()
        analysis_date = now.strftime('%Y-%m-%d %H:%M')
        print(wrf_id, cr39_id)
        data_db.insert(shot, dim, pos, wrf_id, cr39_id, analysis_date, True, corr_spec)

def rerun_all():
    """A script to re-run all WRF analysis."""
    db = WRF_Analysis_DB()

    # Get a directory for all output
    # ask if we should generate rhoR plots
    from tkinter.filedialog import askdirectory
    opts = dict(mustexist='False',
                   initialdir=Database.DIR,
                   title='Save files to')
    OutputDir = askdirectory(**opts)
    # sanity check:
    if OutputDir == '':  # user cancelled
        return

    # Prompt for which shot to start at
    prompt = Option_Prompt(None, title='Start at shot', options=db.get_shots(), width=16)
    startShot = prompt.result
    if startShot is '' or startShot is None:
        return

    # get the index where this shot starts
    startIndex = db.get_shots().index(startShot)

    # Total number that need to be rerun:
    n = 0
    for shot in db.get_shots()[startIndex:]:
        #for dim in db.get_dims(shot):
        n += len(db.get_pos(shot, '90-78'))

    prog = WRF_Progress_Dialog()
    prog.set_text('Running...0/'+str(n))

    i = 1
    for shot in db.get_shots()[startIndex:]:
        dim = '90-78'
        #for dim in db.get_dims(shot):
        for pos in db.get_pos(shot, dim):
            prog.set_text('Running...'+str(i)+'/'+str(n))
            rerun(shot, dim, pos, OutputDir=OutputDir)
            prog.step(100./float(n))
            prog.update_idletasks()
            i += 1

            if prog.cancelled:
                return
    prog.cancel()