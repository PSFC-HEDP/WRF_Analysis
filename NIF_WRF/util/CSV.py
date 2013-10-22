## Read CSV data

import numpy
import csv
import os

def read_csv(fname,crop=0,cols=[]) -> list:
    """Read CSV data from a file and do conversions.
    :param fname: the file name to read
    :param crop: the number of rows of header to drop
    :param cols: the columns to convert to float (default [] -> all columns)
    :returns: a python list of the values, converted to floating point values
    """
    temp = []

    fileReader = csv.reader(open(fname,'r'),delimiter=',')

    # read in data:
    for row in fileReader:
        temp.append(row)

    # crop:
    temp = temp[crop:]

    # convert to float:
    for i in range(len(temp)):
        for j in range(len(temp[i])):
            if len(cols) == 0: # convert all columns
                temp[i][j] = float(temp[i][j])
            if j in cols:
                temp[i][j] = float(temp[i][j])

    # return temp
    return temp

def unique_vals(in_arr) -> list:
    """Remove duplicates from an array
    :param in_arr: the raw (1-D) array to remove duplicates from
    :returns: a list containing the unique values from in_arr
    """
    out_arr = []
    for i in in_arr:
        if i not in out_arr:
            out_arr.append(i)
    return out_arr
