'''
Run all parametric problems of the OSQP paper

This code compares OSQP with warm-start and factorization caching and without

'''

from utils.parametric import print_results_parametric

from parametric_problems.lasso import LassoParametric
from parametric_problems.mpc import MPCParametric
from parametric_problems.portfolio import PortfolioParametric


PROBLEMS_MAP = {'Lasso': LassoParametric,
                'MPC': MPCParametric,
                'Portfolio': PortfolioParametric}

problems = [
            # 'Lasso',
            # 'MPC',
            'Portfolio'
            ]

# Problem dimensions
dimensions = {'Lasso': 50,
              'MPC': 50,
              'Portfolio': 100
              }

# OSQP solver settings
osqp_settings = {'verbose': False,
                 'polish': False,
                 'rho': 10.}

# Solve all problems
for problem in problems:
    problem_instance = PROBLEMS_MAP[problem](osqp_settings,
                                             dimensions[problem])
    problem_instance.solve()

# Extract results info
print("Results")
print("-------")
for problem in problems:
    print_results_parametric(problem, dimensions[problem])
