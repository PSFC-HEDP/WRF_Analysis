__author__ = 'Alex Zylstra'

import numpy

def load_image(filename) -> numpy.ndarray:
    """Load an image from file to a ndarray.
    :param filename: The file name of the image to load
    """
    import matplotlib.image as mpimg

    # read in the file:
    Nxy = mpimg.imread(filename)

    # check for mono bitmap:
    if len(Nxy.shape) == 2:
        # convert to RGB:
        raw = numpy.array(Nxy)
        Nxy = numpy.ndarray((raw.shape[0], raw.shape[1], 3), dtype=raw.dtype)
        for i in range(raw.shape[0]):
            for j in range(raw.shape[1]):
                Nxy[i][j][0] = raw[i][j]
                Nxy[i][j][1] = raw[i][j]
                Nxy[i][j][2] = raw[i][j]

    return Nxy