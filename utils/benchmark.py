import os
import pandas as pd
import numpy as np
import solvers.statuses as solver_statuses

MAX_TIMING = 1e8


def get_cumulative_data(solvers, problems):
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


def compute_performance_profiles(solvers):
    timings = {}
    statuses = {}

    # Get timings and statuses
    for solver in solvers:
        path = os.path.join('.', 'results', 'benchmark_problems',
                            solver, 'results.csv')
        df = pd.read_csv(path)
        timings[solver] = df['run_time'].values
        statuses[solver] = df['status'].values

        # Set maximum timing for solvers that did not succeed
        for idx in range(len(timings['solver'])):
            if statuses[solver][idx] != solver_statuses.OPTIMAL:
                timings[solver][idx] = MAX_TIMING

    # Get total number of problems
    n_problems = len(df)

    t = {}  # Dictionary relative timings for each solver/problem
    for s in solvers:
        t[s] = np.array(n_problems)

    # Iterate over all problems to find best timing between solvers
    for p in range(n_problems):

        # Get minimum time
        min_time = np.min([timings[s][p] for s in solvers])

        # Normalize timings for minimum time
        for s in solvers:
            t[s][p] /= min_time

    # Compute curve for all solvers
    tau = np.logspace(0, 4, 1000)
    r = {}  # Dictionary of all the curves

    for s in solvers:


        #

            # CONTINUE
