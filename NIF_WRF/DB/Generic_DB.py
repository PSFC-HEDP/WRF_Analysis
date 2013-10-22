__author__ = 'Alex Zylstra'

import sqlite3
import csv
import shlex
from NIF_WRF.DB.util import *


class Generic_DB:
    """Python-based database utility for a generic database wrapper.
    :author: Alex Zylstra
    :date: 2013/06/11
    """

    def __init__(self, fname):
        """Class constructor, which connects to the database
        :param fname: the file location/name for the database
        """
        import os

        if not os.path.exists(fname):
            file = open(fname, 'w+')
            file.close()

        # check if the file exists:
        try:
            # database connector
            self.db = sqlite3.connect(fname)
            # database cursor
            self.c = self.db.cursor()
        except sqlite3.OperationalError:
            print("Error opening database file.")

        # name of the table for the data
        self.TABLE = ''

    def __del__(self):
        """Properly close database objects."""
        self.db.commit()
        self.db.close()

    def num_rows(self) -> int:
        """Get the number of rows in the database table associated with this object.
        :returns: the number of rows in the table
        """
        query = self.c.execute('SELECT count(*) from %s' % self.TABLE)

        return query.fetchone()[0]

    def num_columns(self):
        """Get the number of columns in the table.
        :returns: the number of columns in the table
        """
        return len(self.get_columns())

    def get_columns(self) -> list:
        """Get a list of columns in the table.
        :returns: a list where each element is the column metainfo (name, type, etc).
        """
        query = self.c.execute('PRAGMA table_info(%s)' % self.TABLE)
        return array_convert(query)

    def get_column_names(self) -> list:
        """Get a list of columns in the table.
        :returns: a list where each element is the column name
        """
        query = self.c.execute('PRAGMA table_info(%s)' % self.TABLE)
        # get an array of column info:
        columns = array_convert(query)

        # The default SQL result contains other metainfo (data type, etc)
        # Cut it down to just the column names:
        ret = []
        for i in columns:
            ret.append(i[1])
        return ret

    def sql_query(self, query, values=()):
        """Execute a generic SQL query. Be careful!
        :param query: the query to execute, i.e. a string in SQL syntax
        :returns: the result of the query
        """
        return self.c.execute(query, values)

    def clear(self):
        """Clear all data from the table."""
        self.c.execute('DELETE from %s' % self.TABLE)
        self.db.commit()

    def add_column(self, name, col_type):
        """Add a new column to the table.
        :param name: the name of the column you want to add
        :param col_type: a string defining the type of data for this column
        """
        # First, check for existing column to avoid duplicates:
        if name not in self.get_column_names():
            # add the column and commit changes to DB:
            self.c.execute("ALTER TABLE %s ADD [%s] %s" % (self.TABLE, name, col_type))
            self.db.commit()

    def csv_import(self, fname):
        """Read all data from a csv file into the table.
        :param fname: The CSV file to import from
        """
        # drop the existing table
        self.c.execute('DROP TABLE %s' % self.TABLE)
        table_created = False

        # try to open the file:
        with open(fname) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header = next(csvreader)  # read header

            # add columns to the table from the header info:
            for col in header:
                # use the shlex to split the header text into list:
                splitter = shlex.shlex(col, posix=True)
                splitter.whitespace += ','
                splitter.whitespace_split = True
                h = list(splitter)  # temporary list

                # if the table hasn't been remade yet:
                if not table_created:
                    # create a new table with the first column:
                    self.c.execute('CREATE TABLE %s ([%s] %s)' % (self.TABLE, h[1], h[2]))
                    # automatically index by the first column:
                    self.c.execute('CREATE INDEX %s_index on %s([%s])' % (self.TABLE, self.TABLE, h[1]))
                    table_created = True
                # otherwise just add a column:
                else:
                    self.c.execute("ALTER TABLE %s ADD [%s] %s" % (self.TABLE, h[1], h[2]))

            # iterate over each row in the CSV file:
            for row in csvreader:
                # create a command string and array of values to insert:
                command = 'INSERT INTO %s values(' % self.TABLE
                values = []
                for val in row:
                    values.append(val)
                    command += '?,'
                    # remove trailing ',' and then add a close paren to command:
                command = command[:-1]
                command += ')'
                # execute the operation:
                self.c.execute(command, values)

        # finalize changes to database:
        self.db.commit()

    def csv_export(self, fname):
        """Write all data from the table to a csv file
        :param fname: The file to write out to
        """
        with open(fname, 'w', newline='\n') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')

            # write header:
            query = self.c.execute("PRAGMA table_info(%s)" % self.TABLE)
            csvwriter.writerow(query.fetchall())

            # query all rows from the DB:
            query = self.c.execute('SELECT * from %s' % self.TABLE)
            for row in query:
                csvwriter.writerow(row)