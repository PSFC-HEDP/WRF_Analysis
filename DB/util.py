## Various utilities
# @author Alex Zylstra
# @date 2013/02/19

import collections

## Convert a database query to python array
# @param query The result of a database query
def array_convert(query):
	"""Convert a database query to python array"""
	# build a nice return array
	ret = []
	for row in query:
		temp = []
		for value in row:
			temp.append(value)
		ret.append(temp)

	return ret

## Flatten a list once (useful for processing results)
# @param x the list to flatten
def flatten(x):
	"""Flatten a list (useful for processing results)"""
	if isinstance(x, collections.Iterable):
		ret = []
		for i in x:
			for j in i:
				ret.append( j )
		return ret
	else:
		return x