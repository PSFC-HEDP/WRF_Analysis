__author__ = 'Alex Zylstra'

from NIF_WRF.DB.Generic_Analysis_DB import *


class Generic_Param_DB(Generic_Analysis_DB):
    """Provide a wrapper for storing analysis parameters in databases.

    :param fname: the file location/name for the database
    :author: Alex Zylstra
    """

    def __init__(self, fname=Database.FILE):
        """Initialize the WRF analysis database wrapper and connect to the database."""
        super(Generic_Param_DB, self).__init__(fname)  # call super constructor

    def load_results(self, shot, dim, position, results):
        """Load the rhoR model parameters used in the analysis.

        :param shot: The shot number
        :param dim: the DIM
        :param position: The position
        :param results: The result of `Analysis.Analyze_Spectrum.Analyze_Spectrum`, which is a `dict`
        """
        # get the date and time:
        import datetime
        now = datetime.datetime.now()
        analysis_date = now.strftime('%Y-%m-%d %H:%M')

        # get a list of columns to update:
        columns = self.get_column_names()
        # remove ones that are not in the dict:
        columns.remove('shot')
        columns.remove('dim')
        columns.remove('position')
        columns.remove('analysis_date')

        # insert a new row into the table:
        self.insert(shot, dim, position, analysis_date)

        # set values from the dict:
        for col in columns:
            self.set_column(shot, dim, position, col, results[col], analysis_date=analysis_date)

        self.db.commit()

    def get_results(self, shot, dim, position):
        """Get the rhoR model parameters used in the analysis.

        :param shot: The shot number
        :param dim: the DIM
        :param position: The position
        :returns: a `dict` of the parameters
        """
        analysis_date = self.__latest_date__(shot, dim, position)

        # get a list of columns to retrieve:
        columns = self.get_column_names()
        # remove ones that are not relevant (ie metadata):
        columns.remove('shot')
        columns.remove('dim')
        columns.remove('position')
        columns.remove('analysis_date')

        # get values:
        ret = dict()
        for col in columns:
            ret[col] = self.get_value(shot, dim, position, col, analysis_date=analysis_date)[0]
        return ret