'''
Run Suitesparse Lasso problems for the OSQP paper

This code tests the solvers:
    - OSQP
    - GUROBI
    - MOSEK
    - ECOS 

'''
from suitesparse_lasso_problems.suitesparse_lasso_problem import SuitesparseLassoRunner
import solvers.solvers as s
from utils.general import plot_performance_profiles
from utils.benchmark import \
    compute_performance_profiles, \
    compute_shifted_geometric_means, \
    compute_failure_rates, \
    compute_polish_statistics
import os

# Define solvers to benchmark
solvers = [
            s.OSQP,
            s.OSQP_high,
            s.OSQP_polish,
            s.OSQP_polish_high,
            s.GUROBI,
            s.MOSEK,
             s.ECOS,
            #  s.qpOASES
           ]

time_limit = 1000.  # Seconds
settings = {
             s.OSQP: {'polish': False,
                      'time_limit': time_limit,
                      'max_iter': int(1e09),
                      'eps_prim_inf': 1e-15,  # Disable infeas check
                      'eps_dual_inf': 1e-15
                     },
             s.OSQP_high: {'eps_abs': 1e-05,
                           'eps_rel': 1e-05,
                           'polish': False,
                           'time_limit': time_limit,
                           'max_iter': int(1e09),
                           'eps_prim_inf': 1e-15,  # Disable infeas check
                           'eps_dual_inf': 1e-15
                           },
             s.OSQP_polish: {'polish': True,
                             'time_limit': time_limit,
                             'max_iter': int(1e09),
                             'eps_prim_inf': 1e-15,  # Disable infeas check
                             'eps_dual_inf': 1e-15
                            },
             s.OSQP_polish_high: {'eps_abs': 1e-05,
                                  'eps_rel': 1e-05,
                                  'polish': True,
                                  'time_limit': time_limit,
                                  'max_iter': int(1e09),
                                  'eps_prim_inf': 1e-15,  # Disable infeas check 
                                  'eps_dual_inf': 1e-15
                             },
             s.GUROBI: {'time_limit': time_limit},
             s.MOSEK: {'time_limit': time_limit},
             s.ECOS: {'time_limit': time_limit},
             s.qpOASES: {'time_limit': time_limit}
            }

# Shut up solvers
for key in settings:
    settings[key]['verbose'] = False

# Run all examples
suitesparse_lasso_runner = SuitesparseLassoRunner(solvers,
                                                  settings)

# DEBUG only: Choose only 2 problems
# suitesparse_lasso.problems = ["HS52"]

suitesparse_lasso_runner.solve(parallel=True, cores=12)

statistics_file = os.path.join(".", "results", "suitesparse_lasso_problems",
                               "statistics.txt")
print("Saving statistics to %s" % statistics_file)

# Compute failure rates
compute_failure_rates(solvers, 'suitesparse_lasso_problems')

# Compute performance profiles
compute_performance_profiles(solvers, 'suitesparse_lasso_problems')

# Compute performance profiles
compute_shifted_geometric_means(solvers, 'suitesparse_lasso_problems')

# Compute polish statistics
if 'OSQP' in solvers and 'OSQP_polish' in solvers:
    compute_polish_statistics('suitesparse_lasso_problems')

# Plot performance profiles
plot_performance_profiles('suitesparse_lasso_problems',
                          ["OSQP", "GUROBI",  "MOSEK"])
