__author__ = 'Alex Zylstra'

import DB.Database as Database
from DB.Generic_DB import *
import datetime

# The table is arranged with columns:
# (shot text, dim text, position int, wrf_id text, cr39_id text, date datetime, hohl_corr bit,
#  energy real, yield real, error real)

# shot = a string describing the shot #, e.g. N130520-002-999
# dim = a string describing the DIM used, e.g. "0-0"
# position the position within a DIM used to field this piece, e.g. 1
# cr39_id CR-39 piece ID, e.g. 13511794
# date the date and time the analysis was generated
# hohl_corr if the spectrum is corrected for the hohlraum
# energy energy in MeV
# yield the yield per MeV
# error the statistical error bar


class WRF_Spectrum_DB(Generic_DB):
    """Provide a wrapper for WRF spectra.
    :author: Alex Zylstra
    :date: 2013/07/07
    """
    ## name of the table for the snout data
    TABLE = Database.WRF_SPECTRUM_TABLE

    def __init__(self, fname):
        """Initialize the WRF setup database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_Spectrum_DB, self).__init__(fname) # call super constructor
        self.__init_wrf_spectrum__()

    def __init_wrf_spectrum__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, wrf_id text, cr39_id text, date datetime, hohl_corr bit,
                 energy real, yield real, error real)''' % self.TABLE)
            self.c.execute('CREATE INDEX wrf_spectrum_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def get_shots(self) -> list:
        """Get a list of all shots available in the database."""
        query = self.c.execute('SELECT Distinct shot from %s' % self.TABLE)
        return flatten(array_convert(query))

    def get_dims(self, shot) -> list:
        """Get a list of all DIMs available for a given shot.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        """
        query = self.c.execute('SELECT Distinct dim from %s where shot=?' % self.TABLE, (shot,))
        return flatten(array_convert(query))

    def get_positions(self, shot, dim) -> list:
        """Get a list of all DIMs available for a given shot and DIM.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        """
        query = self.c.execute('SELECT Distinct position from %s where shot=? AND dim=?' % self.TABLE, (shot, dim,))
        return flatten(array_convert(query))

    def get_dates(self, shot, dim, position) -> list:
        """Get a list of all datetime stamps available for a given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        """
        # some sanity checking
        assert isinstance(shot, str)

        query = self.c.execute('SELECT Distinct date from %s where shot=? AND dim=? AND position=?' % self.TABLE,
                               (shot, dim, position,))
        return flatten(array_convert(query))

    def get_wrf_id(self, shot, dim, position) -> str:
        """Get the WRF ID used for the given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :returns: the WRF ID as a str
        """
        query = self.c.execute('SELECT wrf_id from %s where shot=? AND dim=? AND position=?' % self.TABLE,
                               (shot, dim, position,))
        return flatten(array_convert(query))

    def get_cr39_id(self, shot, dim, position) -> str:
        """Get the CR-39 ID used for the given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :returns: the CR-39 ID as a str
        """
        query = self.c.execute('SELECT cr39_id from %s where shot=? AND dim=? AND position=?' % self.TABLE,
                               (shot, dim, position,))
        return flatten(array_convert(query))

    def get_corrected(self, shot, dim, position, date) -> list:
        """Generally spectra can be available in either raw or corrected forms, or both. Return list contains False
           if the raw data is available, and True if the hohlraum-corrected data is.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param date: the date and time of analysis, in format YYYY-MM-DD HH:MM:SS
        """
        query = self.c.execute('SELECT Distinct hohl_corr from %s where shot=? AND dim=? AND position=? AND date=?'
                               % self.TABLE,
                               (shot, dim, position, date,))
        result = flatten(array_convert(query))

        # convert to boolean:
        ret = []
        for val in result:
            if val == 0:
                ret.append(False)
            elif val == 1:
                ret.append(True)

        return ret

    def get_spectrum(self, shot, dim, position, corr, date=None) -> list:
        """Get a spectrum.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param corr: boolean, whether the hohlraum was used or not
        :param date: (optional) the date and time of analysis, in format YYYY-MM-DD HH:MM:SS [default=None, get latest]
        """
        # get the latest date if one is not supplied:
        if date is None:
            query = self.c.execute('SELECT Distinct date from %s where shot=? AND dim=? AND position=? AND hohl_corr=?'
                                   % self.TABLE,
                                  (shot, dim, position, corr,))

            # array conversion:
            avail_date = flatten(array_convert(query))
            date = avail_date[0]

        # get the data:
        query = self.c.execute('SELECT energy,yield,error from %s where shot=? AND dim=? AND position=? AND hohl_corr=? AND date=?'
                               % self.TABLE,
                               (shot, dim, position, corr, date,))

        return array_convert(query)

    def insert(self, shot, dim, position, wrf_id, cr39_id, date, hohl_corr, energy, Y, error):
        """Insert a new row of data into the database.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param wrf_id: the WRF ID as a string
        :param cr39_id: the CR39 ID as a string
        :param date: the date and time the spectrum was generated, in form 'YYYY-MM-DD HH:MM' (24 hour clock)
        :param hohl_corr: boolean, whether the hohlraum was used or not
        :param energy: a list, tuple, or ndarray containing energy data in MeV
        :param Y: a list, tuple, or ndarray containing yield data in protons/MeV
        :param error: a list, tuple, or ndarray containing error bars for the previous
        """
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int)
        assert isinstance(wrf_id, str)
        assert isinstance(cr39_id, str)
        assert isinstance(date, str)
        assert isinstance(hohl_corr, bool)

        # spectrum columns must be iterable and contain floats
        # this looks funky but allows for list/tuple/numpy array args
        try:
            for val in energy:
                assert isinstance(val, float)
            for val in Y:
                assert isinstance(val, float)
            for val in error:
                assert isinstance(val, float)
        except TypeError:
            print('Invalid spectrum input to WRF_Spectrum_DB.insert')
            return

        # spectrum columns must have the same length:
        assert len(energy) == len(Y) == len(error)


        # now try to parse date:
        try:
            pytime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
        except ValueError:
            print('Could not parse time')
            return

        # for this table we don't try to maintain unique values for rows
        # this allows multiple versions of a spectrum
        # add to the database:
        for i in range(len(energy)):
            x = energy[i]
            y = Y[i]
            dy = error[i]
            newval = (shot, dim, position, wrf_id, cr39_id, date, hohl_corr, x, y, dy,)
            self.c.execute('INSERT INTO %s values (?,?,?,?,?,?,?,?,?,?)' % self.TABLE, newval)