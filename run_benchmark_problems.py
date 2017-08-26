'''
Run all benchmarks for the OSQP paper

This code tests the solvers:
    - OSQP
    - GUROBI
    - MOSEK
    - ECOS
    - qpOASES

'''
import os
import pandas as pd
from benchmark_problems.example import Example
import solvers.solvers as s
from benchmark_problems.utils import gen_int_log_space

# Define solvers to benchmark
solvers = [
            # s.OSQP,
            # s.OSQP_polish,
            s.GUROBI,
            s.MOSEK,
            s.ECOS,
            s.qpOASES
           ]

settings = {
             # s.OSQP: {'polish': False},
             # s.OSQP_polish: {'polish': True},
             s.GUROBI: {},
             s.MOSEK: {},
             s.ECOS: {},
             s.qpOASES: {'nWSR': 1000000,    # Number of working set recalcs
                         'cputime': 1000.     # Seconds (N.B. Must be float!)
                         }
            }

# Number of instances per different dimension
n_instances = 10

# Shut up solvers
for key in settings:
    settings[key]['verbose'] = False

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

problem_dimensions = {'Random QP': gen_int_log_space(10, 2000, 20),
                      'Eq QP': gen_int_log_space(10, 2000, 20),
                      'Portfolio': gen_int_log_space(5, 150, 20),
                      'Lasso': gen_int_log_space(10, 1000, 20),
                      'SVM': gen_int_log_space(10, 1000, 20),
                      'Huber': gen_int_log_space(10, 1000, 20),
                      'Control': gen_int_log_space(4, 100, 20)}

# Small dimensions (to check)
for key in problem_dimensions:
    problem_dimensions[key] = [4, 5]

# Run all examples
for problem in problems:
    example = Example(problem,
                      problem_dimensions[problem],
                      solvers,
                      settings,
                      n_instances)
    example.solve()


# Collect cumulative data for each solver
for solver in solvers:
    # Path where solver results are stored
    path = os.path.join('.', 'results', 'benchmark_problems', solver)
    # Initialize cumulative results

    results = []
    for problem in problems:
        file_name = os.path.join(path, problem, 'full.csv')
        results.append(pd.read_csv(file_name))

    # Create cumulative dataframe
    df = pd.concat(results)

    # Store dataframe into results
    solver_file_name = os.path.join(path, 'results.csv')
    df.to_csv(solver_file_name, index=False)
