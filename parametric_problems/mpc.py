"""
Solve Lasso problem as parametric QP by updating iteratively lambda
"""

from problems.control import ControlExample


class MPC(object):
    def __init__(self, dimension, x0):
        self.dimension = dimension
        self.x0 = x0
