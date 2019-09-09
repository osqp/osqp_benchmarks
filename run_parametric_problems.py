'''
Run all parametric problems of the OSQP paper

This code compares OSQP with warm-start and factorization caching and without

'''


from parametric_problems.lasso import LassoParametric
from parametric_problems.mpc import MPCParametric
from parametric_problems.portfolio import PortfolioParametric
from utils.parametric import print_results_parametric, compute_results_parametric

PROBLEMS_MAP = {'Lasso': LassoParametric,
                'MPC': MPCParametric,
                'Portfolio': PortfolioParametric}

problems = [
            'Lasso',
            'MPC',
            'Portfolio'
            ]

# Problem dimensions
dimensions = {'Lasso': [50, 100, 150, 200],
              'MPC': [20, 40, 60, 80],
              'Portfolio': [100, 200, 300, 400]
              }

# OSQP solver settings
osqp_settings = {'verbose': False,
                 'polish': False,
                 'rho': 0.1}

# Solve all problems
for problem in problems:
    for dim in dimensions[problem]:
        problem_instance = PROBLEMS_MAP[problem](osqp_settings,
                                                 dim)
        problem_instance.solve()

# Compute results
compute_results_parametric(problems, dimensions)

#  # Extract results info
#  print("Results")
#  print("-------")
#  for problem in problems:
#      print_results_parametric(problem, dimensions[problem])
