'''
Run Maros-Meszaros problems for the OSQP paper

This code tests the solvers:
    - OSQP
    - GUROBI
    - MOSEK

'''
from maros_meszaros_problems.maros_meszaros_problem import MarosMeszarosRunner
import solvers.solvers as s
from utils.benchmark import compute_stats_info
import os, sys
import argparse


parser = argparse.ArgumentParser(description='Maros Meszaros Runner')
parser.add_argument('--high_accuracy', help='Test with high accuracy', default=False,
                    action='store_true')
parser.add_argument('--verbose', help='Verbose solvers', default=False,
                    action='store_true')
parser.add_argument('--parallel', help='Parallel solution', default=False,
                    action='store_true')
parser.add_argument('--codegen', help='code generation', default=None, action='store_true')
parser.add_argument('--restart_sufficient', type=float, default=0.2)
parser.add_argument('--restart_necessary', type=float, default=0.8)
parser.add_argument('--restart_artificial', type=float, default=0.36)

args = parser.parse_args()
high_accuracy = args.high_accuracy
verbose = args.verbose
parallel = args.parallel
codegen = args.codegen
restart_sufficient = args.restart_sufficient
restart_necessary = args.restart_necessary
restart_artificial = args.restart_artificial

print('high_accuracy', high_accuracy)
print('verbose', verbose)
print('parallel', parallel)
print('codegen', codegen)
print('restart_sufficient', restart_sufficient)
print('restart_necessary', restart_necessary)
print('restart_artificial', restart_artificial)


#Update restart parameters
for key in s.settings:
    s.settings[key]['restart_sufficient'] = restart_sufficient
    s.settings[key]['restart_necessary'] = restart_necessary
    s.settings[key]['restart_artificial'] = restart_artificial

# Add high accuracy solvers when accurazy
if high_accuracy:
    # solvers = [s.OSQP_high, s.OSQP_polish_high, s.GUROBI_high, s.MOSEK_high]
    # solvers = [s.OSQP_high, s.OSQP_polish_high, s.GUROBI_high]
    solvers = [s.OSQP_high]
    OUTPUT_FOLDER = 'maros_meszaros_problems_high_accuracy'
    for key in s.settings:
        s.settings[key]['high_accuracy'] = True
else:
    # solvers = [s.OSQP, s.OSQP_polish, s.GUROBI, s.MOSEK]
    solvers = [s.OSQP, s.OSQP_polish, s.GUROBI]
    OUTPUT_FOLDER = 'maros_meszaros_problems'

# Shut up solvers
if verbose:
    for key in s.settings:
        s.settings[key]['verbose'] = True

# Run all examples
maros_meszaros_runner = MarosMeszarosRunner(solvers,
                                            s.settings,
                                            OUTPUT_FOLDER)

# DEBUG only: Choose only 2 problems
# maros_meszaros_runner.problems = ["STADAT1", "BOYD1"]

maros_meszaros_runner.solve(parallel=parallel, cores=12, codegen=codegen)

if codegen:
    sys.exit()

# Compute results statistics
compute_stats_info(solvers, OUTPUT_FOLDER,
                   high_accuracy=high_accuracy)
