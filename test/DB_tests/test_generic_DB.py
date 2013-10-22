from unittest import TestCase
import string
import random
import os

from NIF_WRF.DB import Database
from NIF_WRF.DB.Generic_DB import *


__author__ = 'Alex Zylstra'


def rand_string(length=5, chr_set=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """
    Generate a random string
    :param length: The number of characters in the return string
    :param chr_set: The set of characters to use [default = ASCII uppercase + lowercase + digits
    :returns: a randomly generated string
    """
    output = ''
    for _ in range(length):
        output += random.choice(chr_set)
    return output


class TestGeneric_DB(TestCase):
    """
    Unit tests for the generic database functionality provided by DB.Generic_DB
    :author: Alex Zylstra
    :date: 2013/06/11
    """
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    s = 0

    def setUp(self):
        """Do initialization for the generic database tests."""
        import os

        try:
            os.makedirs(Database.TEST_DIR)
        except FileExistsError:
            if self.verbose == 2:
                print("Using existing directory")
        self.s = Generic_DB(Database.FILE_TEST)
        assert isinstance(self.s, Generic_DB)
        self.s.TABLE = 'test'

        # check to see if it exists already
        query = self.s.c.execute(
            '''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.s.TABLE)

        # create new table:
        if (query.fetchone()[0] != 0): # table exists
            self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)
            # table does not exist
        self.s.c.execute('''CREATE TABLE %s
            (test1 text, test2 int, test3 real)''' % self.s.TABLE)

        self.s.db.commit()

    def tearDown(self):
        """Do tear-down after a single unit test."""
        try:
            self.s.clear()
        except sqlite3.OperationalError:
            if self.verbose == 2:
                print("Oops: error occurred when tearing down test")
        self.s.db.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test class after the whole suite is complete."""
        if cls.verbose == 2:
            print("Tearing down...")
        if isinstance(cls.s, Generic_DB):
            if isinstance(cls.s.db, sqlite3.Connection):
                cls.s.db.commit()
                cls.s.db.close()

    def test_num_rows(self):
        """Test the Generic_DB.num_rows functionality"""
        # make sure the table is clean:
        self.s.clear()

        # add many: rows of random values:
        n = random.randint(10000, 50000)
        for i in range(n):
            a = rand_string(8)
            b = random.randint(-2 ** 31, 2 ** 31)
            c = random.random()
            self.s.sql_query('INSERT INTO %s values (?,?,?)' % self.s.TABLE, (a, b, c))

        # check that all rows were inserted correctly:
        self.assertEqual(self.s.num_rows(), n, "Failed test of Generic_DB.num_rows")

    def test_num_columns(self):
        """Test the Generic_DB.num_columns functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (''' % self.s.TABLE

        # add many columns:
        n = random.randint(100, 200)
        for i in range(n):
            # ith column is of random type
            val_type = random.choice(['text', 'int', 'real'])
            command += 'test' + str(i) + ' ' + val_type + ','
            # trim off last comma
        command = command[:-1]
        # add ending paren
        command += ')'

        # add the new table:
        self.s.c.execute(command)

        # check that we get the number of columns correctly
        self.assertEqual(self.s.num_columns(), n, "Failed test of Generic_DB.num_columns")

    def test_get_columns(self):
        """Test the Generic_DB.get_columns functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (''' % self.s.TABLE

        # add many columns:
        n = random.randint(100, 200)
        col_type = []
        col_name = []
        for i in range(n):
            # ith column is of random type
            val_type = random.choice(['text', 'int', 'real'])
            col_type.append(val_type)
            col_name.append('test' + str(i))
            command += 'test' + str(i) + ' ' + val_type + ','
            # trim off last comma
        command = command[:-1]
        # add ending paren
        command += ')'

        # add the new table:
        self.s.c.execute(command)

        # get the column info:
        result = self.s.get_columns()

        testPass = True
        for row in range(len(result)):
            testPass = testPass and (result[i][1] == col_name[i])
            testPass = testPass and (result[i][2] == col_type[i])

        self.assertTrue(testPass, "Failed test of Generic_DB.get_columns")

    def test_get_column_names(self):
        """Test the Generic_DB.get_column_names functionality"""

        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (''' % self.s.TABLE

        # add many columns:
        n = random.randint(100, 200)
        col_type = []
        col_name = []
        for i in range(n):
            # ith column is of random type
            val_type = random.choice(['text', 'int', 'real'])
            col_type.append(val_type)
            col_name.append('test' + str(i))
            command += 'test' + str(i) + ' ' + val_type + ','
            # trim off last comma
        command = command[:-1]
        # add ending paren
        command += ')'

        # add the new table:
        self.s.c.execute(command)

        # get the column info:
        result = self.s.get_column_names()

        testPass = True
        for row in range(len(result)):
            testPass = testPass and (result[i] == col_name[i])

        self.assertTrue(testPass, "Failed test of Generic_DB.get_column_names")

    def test_sql_query(self):
        """Test the Generic_DB.sql_query functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (test1 text)''' % self.s.TABLE
        # add the new table:
        self.s.sql_query(command)
        query = self.s.sql_query(
            '''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';''' % self.s.TABLE)

        result = query.fetchone()[0]

        self.assertEqual(result, 1, "Failed test of Generic_DB.sql_query")

    def test_clear(self):
        """Test the Generic_DB.clear functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (test1 text)''' % self.s.TABLE
        # add the new table:
        self.s.c.execute(command)
        # add many: rows of random values:
        n = random.randint(10000, 50000)
        for i in range(n):
            a = rand_string(8)
            self.s.sql_query('INSERT INTO %s values (?)' % self.s.TABLE, (a,))
        # clear:
        self.s.clear()

        # now it should be empty:
        self.assertEqual(self.s.num_rows(), 0, "Failed test of Generic_DB.clear")

    def test_add_column(self):
        """Does nothing, this is covered by other tests"""
        # covered by other column tests
        pass

    def test_csv_import(self):
        """Test the Generic_DB.csv_import functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (test1 text, test2 int, test3 real)''' % self.s.TABLE
        # add the new table:
        self.s.c.execute(command)

        # make a CSV file:
        file = open(Database.TEST_DIR + 'test_csv_import.csv', 'w')
        file.write(
            '''"(0, 'test1', 'text', 0, None, 0)","(1, 'test2', 'int', 0, None, 0)","(2, 'test3', 'real', 0, None, 0)"\n''')
        # add many: rows of random values:
        n = random.randint(1000, 5000)
        values = []
        for i in range(n):
            a = rand_string(8)
            b = random.randint(-2 ** 31, 2 ** 31)
            c = random.uniform(-1e9, 1e9)
            values.append([a, b, c])
            file.write(a + ',' + str(b) + ',' + str(c) + '\n')
        file.flush()

        # now import from the file:
        self.s.csv_import(Database.TEST_DIR + 'test_csv_import.csv')

        # compare:
        testPass = True
        for i in range(len(values)):
            values2 = self.s.sql_query('SELECT * from %s where test1=?' % self.s.TABLE, (values[i][0],))
            values2 = flatten(array_convert(values2))
            testPass = testPass and values[i] == values2

        # delete the file
        file.close()
        os.remove(Database.TEST_DIR + 'test_csv_import.csv')

        self.assertTrue(testPass, "Failed test of Generic_DB.csv_import")

    def test_csv_export(self):
        """Test the Generic_DB.csv_export functionality"""
        # get rid of the current table:
        self.s.c.execute('''DROP TABLE %s''' % self.s.TABLE)

        # start building a sql command to add a new table:
        command = '''CREATE TABLE %s (test1 text, test2 int, test3 real)''' % self.s.TABLE
        # add the new table:
        self.s.c.execute(command)

        # make a test table:
        # add many: rows of random values:
        n = random.randint(1000, 5000)
        values = []
        for i in range(n):
            a = rand_string(8)
            b = random.randint(-2 ** 31, 2 ** 31)
            c = random.uniform(-1e9, 1e9)
            values.append([a, b, c])
            # insert into the table:
            self.s.sql_query('''INSERT INTO %s values (?,?,?)''' % self.s.TABLE, (a, b, c,))

        # export to a file:
        self.s.csv_export(Database.TEST_DIR + 'test_csv_export.csv')

        # now import from the file:
        file = open(Database.TEST_DIR + 'test_csv_export.csv', 'r')
        header = []
        fileValues = []
        for row in csv.reader(file):
            if not header:
                header = row
            else:
                # do some conversions:
                a = row[0]
                b = int(row[1])
                c = float(row[2])
                fileValues.append([a, b, c])

        # compare:
        testPass = True
        for i in range(len(values)):
            testPass = testPass and values[i] == fileValues[i]

        # delete the file
        file.close()
        os.remove(Database.TEST_DIR + 'test_csv_export.csv')

        self.assertTrue(testPass, "Failed test of Generic_DB.csv_export")
