'''
Run all benchmarks for the OSQP paper

This code tests the solvers:
    - OSQP
    - GUROBI
    - MOSEK
    - ECOS
    - qpOASES

'''
from benchmark_problems.example import Example
import solvers.solvers as s
from utils.general import gen_int_log_space, plot_performance_profiles
from utils.benchmark import get_cumulative_data, \
    compute_performance_profiles, \
    compute_failure_rates, \
    compute_polish_statistics, \
    compute_shifted_geometric_means
import os
import argparse


parser = argparse.ArgumentParser(description='Benchmark Problems Runner')
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
    solvers = [s.OSQP_high, s.OSQP_polish_high, s.GUROBI, s.MOSEK, s.qpOASES]
    OUTPUT_FOLDER = 'benchmark_problems_high_accuracy'
    for key in s.settings:
        s.settings[key]['high_accuracy'] = True
else:
    solvers = [s.OSQP, s.OSQP_polish, s.GUROBI, s.MOSEK, s.ECOS, s.qpOASES]
    OUTPUT_FOLDER = 'benchmark_problems'


if verbose:
    for key in s.settings:
        s.settings[key]['verbose'] = True


# Number of instances per different dimension
n_instances = 10
n_dim = 20


# Run benchmark problems
problems = [
            'Random QP',
            'Eq QP',
            'Portfolio',
            'Lasso',
            'SVM',
            'Huber',
            'Control'
            ]

problem_dimensions = {'Random QP': gen_int_log_space(10, 2000, n_dim),
                      'Eq QP': gen_int_log_space(10, 2000, n_dim),
                      'Portfolio': gen_int_log_space(5, 150, n_dim),
                      'Lasso': gen_int_log_space(10, 200, n_dim),
                      'SVM': gen_int_log_space(10, 200, n_dim),
                      'Huber': gen_int_log_space(10, 200, n_dim),
                      'Control': gen_int_log_space(10, 100, n_dim)}

# Some problems become too big to be executed in parallel and we solve them
# serially
problem_parallel = {'Random QP': parallel,
                    'Eq QP': parallel,
                    'Portfolio': parallel,
                    'Lasso': parallel,
                    'SVM': parallel,
                    'Huber': parallel,
                    'Control': parallel}

# Small dimensions (to comment when running on the server)
#  for key in problem_dimensions:
   #  problem_dimensions[key] = [4, 5]

# Run all examples
for problem in problems:
    example = Example(problem,
                      problem_dimensions[problem],
                      solvers,
                      s.settings,
                      OUTPUT_FOLDER,
                      n_instances)
    example.solve(parallel=problem_parallel[problem])


# Collect cumulative data for each solver
get_cumulative_data(solvers, problems, OUTPUT_FOLDER)

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
