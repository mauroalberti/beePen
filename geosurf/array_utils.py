from __future__ import division

from numpy import *  # general import for compatibility with formula input
from numpy.linalg import svd

from .errors import AnaliticSurfaceCalcException


def point_solution(a_array, b_array):
    """
    finds a non-unique solution
    for a set of linear equations
    """

    try:
        return linalg.lstsq(a_array, b_array)[0]
    except:
        return None, None, None


def xyz_svd(xyz_array):
    # modified after: 
    # http://stackoverflow.com/questions/15959411/best-fit-plane-algorithms-why-different-results-solved

    try:
        return dict(result=svd(xyz_array))
    except:
        return dict(result=None)

