'''
Run all parametric problems of the OSQP paper

This code compares OSQP with warm-start and factorization caching and without

'''

from problems.problems.lasso import LassoExample
from problems.problems.portfolio import PortfolioExample
from problems.problems.control import ControlExample
