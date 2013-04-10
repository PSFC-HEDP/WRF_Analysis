## Read CSV data

import numpy
import csv
import os

def read_csv(fname,crop=0):
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
			temp[i][j] = float(temp[i][j])

	# return temp convered to ndarray:
	return numpy.array(temp)
