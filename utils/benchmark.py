import os
import pandas as pd
import numpy as np
import solvers.statuses as statuses
from solvers.solvers import time_limit

MAX_TIMING = time_limit


def get_cumulative_data(solvers, problems, output_folder):
    for solver in solvers:

        # Path where solver results are stored
        path = os.path.join('.', 'results', output_folder, solver)

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


def compute_performance_profiles(solvers, problems_type):
    t = {}
    status = {}

    # Get time and status
    for solver in solvers:
        path = os.path.join('.', 'results', problems_type,
                            solver, 'results.csv')
        df = pd.read_csv(path)

        # Get total number of problems
        n_problems = len(df)

        t[solver] = df['run_time'].values
        status[solver] = df['status'].values

        # Set maximum time for solvers that did not succeed
        for idx in range(n_problems):
            if status[solver][idx] not in statuses.SOLUTION_PRESENT:
                t[solver][idx] = MAX_TIMING

    r = {}  # Dictionary of relative times for each solver/problem
    for s in solvers:
        r[s] = np.zeros(n_problems)

    # Iterate over all problems to find best timing between solvers
    for p in range(n_problems):

        # Get minimum time
        min_time = np.min([t[s][p] for s in solvers])

        # Normalize t for minimum time
        for s in solvers:
            r[s][p] = t[s][p]/min_time

    # Compute curve for all solvers
    n_tau = 1000
    tau_vec = np.logspace(0, 4, n_tau)
    rho = {'tau': tau_vec}  # Dictionary of all the curves

    for s in solvers:
        rho[s] = np.zeros(n_tau)
        for tau_idx in range(n_tau):
            count_problems = 0  # Count number of problems with t[p, s] <= tau
            for p in range(n_problems):
                if r[s][p] <= tau_vec[tau_idx]:
                    count_problems += 1
            rho[s][tau_idx] = count_problems / n_problems

    # Store final pandas dataframe
    df_performance_profiles = pd.DataFrame(rho)
    performance_profiles_file = os.path.join('.', 'results',
                                             problems_type,
                                             'performance_profiles.csv')
    df_performance_profiles.to_csv(performance_profiles_file, index=False)

    # Plot performance profiles
    # import matplotlib.pylab as plt
    # for s in solvers:
    #     plt.plot(tau_vec, rho[s], label=s)
    # plt.legend(loc='best')
    # plt.ylabel(r'$\rho_{s}$')
    # plt.xlabel(r'$\tau$')
    # plt.grid()
    # plt.xscale('log')
    # plt.show(block=False)

def geom_mean(t, shift=10.):
    return np.power(np.prod(t + shift), 1/len(t)) - shift


def compute_shifted_geometric_means(solvers, problems_type):
    t = {}
    status = {}
    g_mean = {}

    # Get time and status
    for solver in solvers:
        path = os.path.join('.', 'results', problems_type,
                            solver, 'results.csv')
        df = pd.read_csv(path)

        # Get total number of problems
        n_problems = len(df)

        t[solver] = df['run_time'].values
        status[solver] = df['status'].values

        # Set maximum time for solvers that did not succeed
        for idx in range(n_problems):
            if status[solver][idx] not in statuses.SOLUTION_PRESENT:
                t[solver][idx] = MAX_TIMING

        g_mean[solver] = geom_mean(t[solver])

    # Normalize geometric means by best solver
    best_g_mean = np.min([g_mean[s] for s in solvers])
    for s in solvers:
        g_mean[s] /= best_g_mean

    # Store final pandas dataframe
    df_g_mean = pd.Series(g_mean)
    g_mean_file = os.path.join('.', 'results',
                               problems_type,
                               'geom_mean.csv')
    df_g_mean.to_csv(g_mean_file, header=False, index=True)


    # r = {}  # Dictionary of relative times for each solver/problem
    # for s in solvers:
    #     r[s] = np.zeros(n_problems)

    # # Iterate over all problems to find best timing between solvers
    # for p in range(n_problems):

    #     # Get minimum time
    #     min_time = np.min([t[s][p] for s in solvers])

    #     # Normalize t for minimum time
    #     for s in solvers:
    #         r[s][p] = t[s][p]/min_time

    # # Compute curve for all solvers
    # n_tau = 1000
    # tau_vec = np.logspace(0, 4, n_tau)
    # rho = {'tau': tau_vec}  # Dictionary of all the curves

    # for s in solvers:
    #     rho[s] = np.zeros(n_tau)
    #     for tau_idx in range(n_tau):
    #         count_problems = 0  # Count number of problems with t[p, s] <= tau
    #         for p in range(n_problems):
    #             if r[s][p] <= tau_vec[tau_idx]:
    #                 count_problems += 1
    #         rho[s][tau_idx] = count_problems / n_problems

    # Store final pandas dataframe
    # df_performance_profiles = pd.DataFrame(rho)
    # performance_profiles_file = os.path.join('.', 'results',
    #                                          problems_type,
    #                                          'performance_profiles.csv')
    # df_performance_profiles.to_csv(performance_profiles_file, index=False)


def compute_failure_rates(solvers, problems_type):
    """
    Compute and show failure rates
    """

    # Check if results file already exists
    results_file = os.path.join(".", "results", problems_type,
                                "statistics.txt")

    # Always overwrite file
    f = open(results_file, "w")

    f.write('[Failure rates]\n')
    for solver in solvers:
        results_file = os.path.join('.', 'results', problems_type,
                                    solver, 'results.csv')
        df = pd.read_csv(results_file)

        n_problems = len(df)

        failed_statuses = np.logical_and(*[df['status'].values != s
                                           for s in statuses.SOLUTION_PRESENT])
        n_failed_problems = np.sum(failed_statuses)
        failure_rate = n_failed_problems / n_problems

        f.write(" - %s = %.4f %%\n" % (solver, 100 * failure_rate))
    f.write("\n")

    f.close()


def compute_polish_statistics(problems_type, high_accuracy=False):
    name_high = "_high" if high_accuracy else ""

    # Check if results file already exists
    results_file = os.path.join(".", "results", problems_type,
                                "statistics.txt")
    if os.path.exists(results_file):
        f = open(results_file, "a")
    else:
        f = open(results_file, "w")

    # Path where solver results are stored
    path_osqp = os.path.join('.', 'results', problems_type,
                             "OSQP" + name_high, 'results.csv')
    path_osqp_polish = os.path.join('.', 'results', problems_type,
                                    'OSQP_polish' + name_high, 'results.csv')

    # Load data frames
    df_osqp = pd.read_csv(path_osqp)
    df_osqp_polish = pd.read_csv(path_osqp_polish)

    # Take only problems where osqp has success
    successful_problems = df_osqp['status'] == statuses.OPTIMAL
    df_osqp = df_osqp.loc[successful_problems]
    df_osqp_polish = df_osqp_polish.loc[successful_problems]
    n_problems = len(df_osqp)

    # Compute time increase
    osqp_time = df_osqp['run_time'].values
    osqp_polish_time = df_osqp_polish['run_time'].values
    time_increase = np.zeros(n_problems)

    for i in range(n_problems):
        time_increase = osqp_polish_time / osqp_time

    polish_successs = np.sum(df_osqp_polish['status_polish'] == 1) \
        / n_problems

    # Print results
    f.write("\n[OSQP Polish benchmarks]\n")
    f.write("  - Median time increase:  %.2fx\n" % np.median(time_increase))
    f.write("  - Percentage of success: %.2f %%\n" % (polish_successs * 100))
    f.write("\n")
    f.close()


#  def constrain_execution_time(solvers, problems,
#                               problem_dimensions, time_limit):
#      """
#      Change status to solver_error when execution time exceeds time_limit
#      """
#
#      for solver in solvers:
#          for problem in problems:
#              for dim in problem_dimensions[problem]:
#                  file_to_read = os.path.join('.', 'results',
#                                              'benchmark_problems',
#                                              solver,
#                                              problem,
#                                              'n%i.csv' % dim)
#                  df = pd.read_csv(file_to_read)
#                  n_instances = len(df)
#                  status_list = []
#                  for i in range(n_instances):
#                      if df['run_time'].values[i] > time_limit:
#                          status_list.append(statuses.SOLVER_ERROR)
#                      else:
#                          status_list.append(df['status'].values[i])
#
#                  df['status'] = status_list
#                  df.to_csv(file_to_read, index=False)
