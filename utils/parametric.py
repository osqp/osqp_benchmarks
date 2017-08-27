import os
import pandas as pd


def print_results_parametric(problem, dimension):
    """
    Print parametric problem results
    """
    print('[%s]' % problem)
    ws_file = os.path.join('.', 'results', 'parametric_problems',
                           'OSQP warmstart',
                           problem,
                           'n%i.csv' % dimension
                           )
    no_ws_file = os.path.join('.', 'results', 'parametric_problems',
                              'OSQP no warmstart',
                              problem,
                              'n%i.csv' % dimension
                              )

    no_ws_df = pd.read_csv(no_ws_file)
    ws_df = pd.read_csv(ws_file)

    print('  OSQP (no warm start): ')
    print('   - median time: %.4e sec' % no_ws_df['run_time'].median())
    print('   - mean time:   %.4e sec' % no_ws_df['run_time'].mean())

    print('  OSQP (warm start): ')
    print('   - median time: %.4e sec' % ws_df['run_time'].median())
    print('   - mean time:   %.4e sec' % ws_df['run_time'].mean())

    print("  Speedups")
    print('   - median time: %.2f x' %
          (no_ws_df['run_time'].median() / ws_df['run_time'].median()))
    print('   - mean time:   %.2f x' %
          (no_ws_df['run_time'].mean() / ws_df['run_time'].mean()))
    print("")
