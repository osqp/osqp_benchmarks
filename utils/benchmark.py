import os
import pandas as pd
import numpy as np
import solvers.statuses as statuses
from solvers.solvers import time_limit

# Plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt

MAX_TIMING = time_limit

def plot_performance_profiles(problems, solvers):
    """
    Plot performance profiles in matplotlib for specified problems and solvers
    """
    df = pd.read_csv('./results/%s/performance_profiles.csv' % problems)
    plt.figure(0)
    for solver in solvers:
        plt.plot(df["tau"], df[solver], label=solver)
    plt.xlim(1., 10000.)
    plt.ylim(0., 1.)
    plt.xlabel(r'Performance ratio $\tau$')
    plt.ylabel('Ratio of problems solved')
    plt.xscale('log')
    plt.legend()
    plt.grid()
    plt.show(block=False)
    results_file = './results/%s/%s.png' % (problems, problems)
    print("Saving plots to %s" % results_file)
    plt.savefig(results_file)


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
    """Compute the shifted geometric mean using formula from
    http://plato.asu.edu/ftp/shgeom.html

    NB. Use logarithms to avoid numeric overflows
    """
    return np.exp(np.sum(np.log(np.maximum(1, t + shift))/len(t))) - shift


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

        # NB. Normalize to avoid overflow. They get normalized back anyway.
        t[solver] = df['run_time'].values * 1e-03
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
    df_g_mean.to_frame().transpose().to_csv(g_mean_file, index=False)


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
    failure_rates = {}

    # Check if results file already exists
    failure_rates_file = os.path.join(".", "results", problems_type, "failure_rates.csv")
    for solver in solvers:
        results_file = os.path.join('.', 'results', problems_type,
                                    solver, 'results.csv')
        df = pd.read_csv(results_file)

        n_problems = len(df)

        failed_statuses = np.logical_and(*[df['status'].values != s
                                           for s in statuses.SOLUTION_PRESENT])
        n_failed_problems = np.sum(failed_statuses)
        failure_rates[solver] = n_failed_problems / n_problems

    # Write csv file
    df_failure_rates = pd.Series(failure_rates)
    df_failure_rates.to_frame().transpose().to_csv(failure_rates_file, index=False)


def compute_polish_statistics(problems_type, high_accuracy=False):
    name_high = "_high" if high_accuracy else ""

    # Check if results file already exists
    polish_file = os.path.join(".", "results", problems_type,
            "polish_statistics.csv")
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
    time_increase = osqp_polish_time / osqp_time

    polish_success = np.sum(df_osqp_polish['status_polish'] == 1) \
        / n_problems

    # Print results
    polish_statistics = {'median_time_increase': np.median(time_increase),
                         'percentage_of_success': (polish_success * 100)}

    df_polish = pd.Series(polish_statistics)
    df_polish.to_frame().transpose().to_csv(polish_file, index=False)


def compute_ratio_setup_solve(problems_type, high_accuracy=False):
    name_high = "_high" if high_accuracy else ""

    # Check if results file already exists
    ratio_file = os.path.join(".", "results", problems_type,
            "ratio_setup_solve.csv")
    # Path where solver results are stored
    path_osqp = os.path.join('.', 'results', problems_type,
                             "OSQP" + name_high, 'results.csv')
    # Load data frames
    df_osqp = pd.read_csv(path_osqp)

    # Take only problems where osqp has success
    successful_problems = df_osqp['status'] == statuses.OPTIMAL
    df_osqp = df_osqp.loc[successful_problems]
    n_problems = len(df_osqp)

    # Compute time increase
    osqp_setup_time = df_osqp['setup_time'].values
    osqp_solve_time = df_osqp['solve_time'].values
    ratios = np.divide(osqp_setup_time, osqp_solve_time)

    # Print results
    ratio_stats = {'mean_ratio': np.mean(ratios),
                   'median_ratio': np.median(ratios)}

    df_ratio = pd.Series(ratio_stats)
    df_ratio.to_frame().transpose().to_csv(ratio_file, index=False)


def compute_stats_info(solvers, benchmark_type,
                       problems=None,
                       high_accuracy=False,
                       performance_profiles=True):

    if problems is not None:
        # Collect cumulative data for each solver
        # If there are multiple problems defined
        get_cumulative_data(solvers, problems, benchmark_type)

    # Compute failure rates
    compute_failure_rates(solvers, benchmark_type)

    # Compute performance profiles
    compute_performance_profiles(solvers, benchmark_type)

    # Compute performance profiles
    compute_shifted_geometric_means(solvers, benchmark_type)

    # Compute polish statistics
    if any(s.startswith('OSQP') for s in solvers):
        compute_polish_statistics(benchmark_type, high_accuracy=high_accuracy)
        compute_ratio_setup_solve(benchmark_type, high_accuracy=high_accuracy)

    # Plot performance profiles
    if performance_profiles:
        plot_performance_profiles(benchmark_type, solvers)
