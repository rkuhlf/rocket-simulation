# Stores the fitted polynomials that are outputted from fitPolynomial.py
# They have to be transferred manually

import numpy as np

# cheb([ 0.68555263 -0.47346114  0.06083131 -0.00668305])


def get_density(altitude):
    # return np.polyval(cheb([0.68555263 - 0.47346114  0.06083131)], altitude)

    # Not technically the fastest way ^, but fast enough
    return 0.68555263 - 0.47346114 * altitude + 0.06083131 * altitude ** 2
