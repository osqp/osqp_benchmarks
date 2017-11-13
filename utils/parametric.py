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

    # Store results
    results_file = os.path.join(".", "results", "parametric_problems",
                                "%s_results.txt" % problem.lower())
    print("Saving statistics to file %s" % results_file)
    f = open(results_file, "w")
    f.write('  OSQP (no warm start): \n')
    f.write('   - median time: %.4e sec\n' % no_ws_df['run_time'].median())
    f.write('   - mean time:   %.4e sec\n' % no_ws_df['run_time'].mean())
    f.write('   - median iter: %d\n' % no_ws_df['iter'].median())
    f.write('   - mean iter:   %d\n' % no_ws_df['iter'].mean())

    f.write('  OSQP (warm start): \n')
    f.write('   - median time: %.4e sec\n' % ws_df['run_time'].median())
    f.write('   - mean time:   %.4e sec\n' % ws_df['run_time'].mean())
    f.write('   - median iter: %d\n' % ws_df['iter'].median())
    f.write('   - mean iter:   %d\n' % ws_df['iter'].mean())

    f.write("  Speedups\n")
    f.write('   - median time: %.2f x\n' %
            (no_ws_df['run_time'].median() / ws_df['run_time'].median()))
    f.write('   - mean time:   %.2f x\n' %
            (no_ws_df['run_time'].mean() / ws_df['run_time'].mean()))
    f.close()

    print("")
