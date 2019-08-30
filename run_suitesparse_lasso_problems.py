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
import argparse


parser = argparse.ArgumentParser(description='Suitesparse Lasso Runner')
parser.add_argument('--high_accuracy', help='Test with high accuracy', default=False,
                    action='store_true')
parser.add_argument('--verbose', help='Verbose solvers', default=False,
                    action='store_true')
parser.add_argument('--parallel', help='Parallel solution', default=False,
                    action='store_true')
args = parser.parse_args()
high_accuracy = args.high_accuracy
verbose = args.verbose
parallel = args.parallel

print('high_accuracy', high_accuracy)
print('verbose', verbose)
print('parallel', parallel)


# Add high accuracy solvers when accurazy
if high_accuracy:
    solvers = [s.OSQP_high, s.OSQP_polish_high, s.GUROBI, s.MOSEK]
    OUTPUT_FOLDER = 'suitesparse_lasso_problems_high_accuracy'
    for key in s.settings:
        s.settings[key]['high_accuracy'] = True
else:
    solvers = [s.OSQP, s.OSQP_polish, s.GUROBI, s.MOSEK]
    OUTPUT_FOLDER = 'suitesparse_lasso_problems'

if verbose:
    for key in s.settings:
        s.settings[key]['verbose'] = True

# Run all examples
suitesparse_lasso_runner = SuitesparseLassoRunner(solvers,
                                                  s.settings,
                                                  OUTPUT_FOLDER)

# DEBUG Only two problems
#  suitesparse_lasso_runner.problems = ['Springer_ESOC']  # ['HB_abb313', 'HB_ash331']

suitesparse_lasso_runner.solve(parallel=parallel, cores=12)



statistics_file = os.path.join(".", "results", OUTPUT_FOLDER, "statistics.txt")
print("Saving statistics to %s" % statistics_file)

# Compute failure rates
compute_failure_rates(solvers, OUTPUT_FOLDER)

# Compute performance profiles
compute_performance_profiles(solvers, OUTPUT_FOLDER)

# Compute performance profiles
compute_shifted_geometric_means(solvers, OUTPUT_FOLDER)

# Compute polish statistics
compute_polish_statistics(OUTPUT_FOLDER, high_accuracy=high_accuracy)

# Plot performance profiles
plot_performance_profiles(OUTPUT_FOLDER, solvers)
