__author__ = 'Alex Zylstra'

import datetime

import numpy

import NIF_WRF.DB.Database as Database
from NIF_WRF.DB.Generic_DB import *
from NIF_WRF.util.Import_WRF_CSV import WRF_CSV
from NIF_WRF.util.Import_Nxy import load_image


# The table is arranged with columns:
# (shot text, dim text, position int, wrf_id text, cr39_id text, date datetime, hohl_corr bit,
#  energy real, yield real, error real)

# shot = a string describing the shot #, e.g. N130520-002-999
# dim = a string describing the DIM used, e.g. "0-0"
# position the position within a DIM used to field this piece, e.g. 1
# cr39_id CR-39 piece ID, e.g. 13511794
# date the date and time the data was generated
# hohl_corr if the spectrum is corrected for the hohlraum
# spectrum as blob (pickled numpy array)
# Nxy as blob (pickled numpy array)


class WRF_Data_DB(Generic_DB):
    """Provide a wrapper for WRF spectra.
    :author: Alex Zylstra
    :date: 2013/08/05
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF setup database wrapper and connect to the database.
        :param fname: the file location/name for the database
        """
        super(WRF_Data_DB, self).__init__(fname) # call super constructor
        # name of the table for the snout data
        self.TABLE = Database.WRF_DATA_TABLE
        self.__init_wrf_data__()

    def __init_wrf_data__(self):
        """initialize the table."""
        # check to see if it exists already
        query = self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.TABLE)

        # create new table:
        if query.fetchone()[0] == 0: # table does not exist
            self.c.execute('''CREATE TABLE %s
                (shot text, dim text, position int, wrf_id text, cr39_id text, date datetime, hohl_corr bit,
                 spectrum blob, nxy blob)''' % self.TABLE)
            self.c.execute('CREATE INDEX wrf_spectrum_index on %s(shot)' % self.TABLE)

        # finish changes:
        self.db.commit()

    def add_data(self, raw, image=None, hohl=False):
        """Add to the data DB from a raw CSV import and image import.
        :param raw: An imported WRF CSV file, as WRF_CSV object
        :param image: (optional) An imported N(x,y) image data array as numpy.ndarray [default=None]
        :param hohl: (optional) If the spectrum is corrected for the hohlraum [default=False]
        """
        assert isinstance(raw, WRF_CSV)
        assert isinstance(image, numpy.ndarray) or image is None
        datetime = raw.date + ' ' + raw.time
        self.insert(raw.shot, raw.dim, raw.pos, raw.WRF_ID, raw.CR39_ID, datetime, hohl, raw.spectrum, image)

    def add_data_from_file(self, csv_file, image_file=None, hohl=False):
        """Import data from file(s) and add it to the database.
        :param csv_file: Location of the CSV file to import
        :param image_file: (optional) Location of the image file to import [default=None]
        :param hohl: (optional) If the spectrum is corrected for the hohlraum [default=False]
        """
        raw = WRF_CSV(csv_file)
        if image_file is not None:
            Nxy = load_image(image_file)
        else:
            Nxy = None

        # call previous method:
        self.add_data(raw, Nxy, hohl)

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
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)

        # SQL query:
        query = self.c.execute('SELECT wrf_id from %s where shot=? AND dim=? AND position=?' % self.TABLE,
                               (shot, dim, position,))
        return flatten(array_convert(query))

    def get_cr39_id(self, shot, dim, position) -> str:
        """Get the CR-39 ID used for the given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :returns: the CR-39 ID as a str
        :rtype: str
        """
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)

        # SQL query:
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
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(date, str)

        # SQL query:
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
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(corr, int) or isinstance(corr, bool)

        # get the latest date if one is not supplied:
        if date is None:
            date = self.__latest_date__(shot, dim, position, corr)

        # get the data:
        query = self.c.execute('SELECT spectrum from %s where shot=? AND dim=? AND position=? AND hohl_corr=? AND date=?'
                               % self.TABLE,
                               (shot, dim, position, corr, date,))

        query = array_convert(query)

        if len(query) > 0:
            bin_str = query[0][0]
            return numpy.loads(bin_str)
        else:
            return None

    def get_Nxy(self, shot, dim, position, corr, date=None) -> list:
        """Get N(x,y) image data.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param corr: boolean, whether the hohlraum was used or not
        :param date: (optional) the date and time of analysis, in format YYYY-MM-DD HH:MM:SS [default=None, get latest]
        """
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, str) or isinstance(position, int)
        assert isinstance(corr, int) or isinstance(corr, bool)

        # get the latest date if one is not supplied:
        if date is None:
            date = self.__latest_date__(shot, dim, position)

        # get the data:
        query = self.c.execute('SELECT nxy from %s where shot=? AND dim=? AND position=? AND hohl_corr=? AND date=?'
                               % self.TABLE,
                               (shot, dim, position, corr, date,))

        query = array_convert(query)

        if len(query) > 0:
            bin_str = query[0][0]
            return numpy.loads(bin_str)
        else:
            return None

    def insert(self, shot, dim, position, wrf_id, cr39_id, date, hohl_corr, spectrum, image=None):
        """Insert a new row of data into the database.
        :param shot: the shot number as a string, e.g. 'N130520-002-999'
        :param dim: the DIM as a string, e.g. '0-0'
        :param position: the position as an integer, e.g. 1
        :param wrf_id: the WRF ID as a string
        :param cr39_id: the CR39 ID as a string
        :param date: the date and time the spectrum was generated, in form 'YYYY-MM-DD HH:MM' (24 hour clock)
        :param hohl_corr: boolean, whether the hohlraum was used or not
        :param spectrum: The spectrum to save, as a numpy ndarray
        :param image: (optional) the N(x,y) image data to save, as a numpy ndarray [default=None]
        """
        # some sanity checking
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)
        assert isinstance(wrf_id, str)
        assert isinstance(cr39_id, str)
        assert isinstance(date, str)
        assert isinstance(hohl_corr, bool)

        # spectrum columns must be numpy arrays or lists:
        assert isinstance(spectrum, numpy.ndarray) or isinstance(spectrum, list)
        if not isinstance(spectrum, numpy.ndarray):
            spectrum = numpy.array(spectrum, dtype='float')
        assert isinstance(image, numpy.ndarray) or image is None

        # create binary blobs:
        bin_spectrum = spectrum.dumps()
        bin_image = ''
        if image is not None:
            bin_image = image.dumps()

        # now try to parse date:
        try:
            date.replace('/','-')
            pytime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
        except ValueError:
            print('Could not parse time: ' + date)
            return

        # check for duplicates, shot/dim/position/date should be unique:
        query = self.c.execute('SELECT * from %s where shot=? AND dim=? AND position=? AND date=? AND hohl_corr=?'
                                % self.TABLE, (shot, dim, position, date,hohl_corr,))

        # not found:
        if len(query.fetchall()) <= 0:
            # add to the database:
            if image is not None:
                newval = (shot, dim, position, wrf_id, cr39_id, date, hohl_corr, bin_spectrum, bin_image,)
                self.c.execute('INSERT INTO %s values (?,?,?,?,?,?,?,?,?)' % self.TABLE, newval)
            else:
                newval =(shot, dim, position, wrf_id, cr39_id, date, hohl_corr, bin_spectrum, None)
                self.c.execute('INSERT INTO %s values (?,?,?,?,?,?,?,?,?)' % self.TABLE, newval)

        # otherwise, update existing row:
        else:
            # update the spectrum:
            command = 'UPDATE %s set [spectrum]=? WHERE shot=? AND dim=? AND position=? AND date=? AND hohl_corr=?' % self.TABLE
            self.c.execute(command, (shot, dim, position, date, hohl_corr, bin_spectrum,))
            # update the image if appropriate:
            if image is not None:
                command = 'UPDATE %s set [nxy]=? WHERE shot=? AND dim=? AND position=? AND date=? AND hohl_corr=?' % self.TABLE
                self.c.execute(command, (shot, dim, position, date, hohl_corr, bin_image,))

        self.db.commit()

    def __latest_date__(self, shot, dim, position, corr=None):
        """Get the latest (i.e. most recent) date available for the given shot, DIM, and position.
        :param shot: the shot number as a string, e.g. 'N130520-002-999' (as str)
        :param dim: the DIM as a string, e.g. '0-0' (as str)
        :param position: the position as an integer or str, e.g. 1
        :param corr: If we want corrected or uncorrected spectrum (optional)
        """
        # sanity checks:
        assert isinstance(shot, str)
        assert isinstance(dim, str)
        assert isinstance(position, int) or isinstance(position, str)

        # result without specified corr:
        if corr is None:
            query = self.c.execute('SELECT Distinct date from %s where shot=? AND dim=? AND position=?'
                                   % self.TABLE,
                                  (shot, dim, position,))
        else:
            # sanity check:
            assert isinstance(corr, bool)
            query = self.c.execute('SELECT Distinct date from %s where shot=? AND dim=? AND position=? AND hohl_corr=?'
                                   % self.TABLE,
                                  (shot, dim, position,corr,))

        # array conversion:
        avail_date = flatten(array_convert(query))
        avail_date.sort()
        return avail_date[-1]