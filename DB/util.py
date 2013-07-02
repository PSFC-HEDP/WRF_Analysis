import collections

def array_convert(query) -> list:
	"""Convert a database query to python array
	:param query: The result of a database query
	:returns: a list of converted values
	"""
	# build a nice return array
	ret = []
	for row in query:
		temp = []
		for value in row:
			temp.append(value)
		ret.append(temp)

	return ret

def flatten(x) -> list:
	"""Flatten a list (useful for processing results)
	:param x: the list to flatten
	:returns: The flattened list
	"""
	if isinstance(x, collections.Iterable):
		ret = []
		for i in x:
			for j in i:
				ret.append( j )
		return ret
	else:
		return x