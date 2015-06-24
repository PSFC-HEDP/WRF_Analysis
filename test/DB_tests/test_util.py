from unittest import TestCase
import random
import sqlite3
import string

from NIF_WRF.DB.util import *


__author__ = 'Alex Zylstra'


class TestUtil(TestCase):
    """
    Unit tests for the misc utilities provided by DB.util
    :author: Alex Zylstra
    :date: 2013/06/11
    """
    # verbosity
    # 0 = no output
    # 1 = moderate output
    # 2 = lots of output
    verbose = 1

    def test_array_convert(self):
        """Test the DB.util.array_convert method"""
        def char_generator():
            for c in string.ascii_lowercase:
                yield (c,)

        con = sqlite3.connect(":memory:")
        cur = con.cursor()
        cur.execute("create table characters(c)")

        cur.executemany("insert into characters(c) values (?)", char_generator())

        cur.execute("select c from characters")
        sql_values = cur.fetchall()
        values = array_convert(sql_values)

        assert isinstance(values,list)

        # check values:
        testPass = True
        for x in sql_values:
            # get and remove first element:
            conv_x = values[0][0]
            values = values[1:]

            # output if requested:
            if self.verbose == 2:
                print(x,conv_x)

            # compare to result from SQL:
            testPass = testPass and x[0] == conv_x

        self.assertTrue(testPass,"Failed test of DB.util.array_convert")

    def test_flatten(self):
        """Test the DB.util.flatten method"""
        test_arr = []
        values = []
        # make a horrible nested list thing:
        for i in range(random.randint(10,20)):
            test_arr.append([])
            for j in range(random.randint(10,20)):
                test_arr[i].append([])
                for k in range(random.randint(10,20)):
                    test_arr[i][j].append([])
                    for l in range(random.randint(10,20)):
                        val = random.uniform(-1e9,1e9)
                        test_arr[i][j][k].append(val)
                        values.append(val)

        # apply flatten thrice:
        test_arr = flatten(flatten(flatten(test_arr)))

        testPass = True
        for i in range(len(values)):
            # output if requested:
            if self.verbose == 2:
                print(values[i],test_arr[i])
            testPass = testPass and values[i] == test_arr[i]

        self.assertTrue(testPass,"Failed test of DB.util.flatten")