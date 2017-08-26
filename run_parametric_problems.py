'''
Run all parametric problems of the OSQP paper

This code compares OSQP with warm-start and factorization caching and without

'''
import os
import pandas as pd


from parametric_problems.lasso import LassoParametric

# OSQP solver settings
osqp_settings = {'verbose': False,
                 'polish': False,
                 'rho': 1.0}

dimensions = {'Lasso': 10}

# Solve Lasso example
lasso = LassoParametric(osqp_settings, dimensions['Lasso'])
lasso.solve()


# Generate statistics
problems = [
            'Lasso',
            # 'MPC',
            # 'Portoflio'
            ]

# Extract results info
print("Results")
print("-------")
for problem in problems:
    print('[Lasso]')
    ws_file = os.path.join('.', 'results', 'parametric_problems',
                           'OSQP warmstart',
                           problem,
                           'n%i.csv' % dimensions[problem]
                           )
    no_ws_file = os.path.join('.', 'results', 'parametric_problems',
                              'OSQP no warmstart',
                              problem,
                              'n%i.csv' % dimensions[problem]
                              )

    no_ws_df = pd.read_csv(no_ws_file)
    ws_df = pd.read_csv(ws_file)

    print('  OSQP (no warm start): ')
    print('   - median time: %.4e' % no_ws_df['run_time'].median())
    print('   - mean time:   %.4e' % no_ws_df['run_time'].mean())

    print('  OSQP (warm start): ')
    print('   - median time: %.4e' % ws_df['run_time'].median())
    print('   - mean time:   %.4e' % ws_df['run_time'].mean())

    print("  Speedups")
    print('   - median time: %.2f x' %
          (no_ws_df['run_time'].median() / ws_df['run_time'].median()))
    print('   - mean time:   %.2f x' %
          (no_ws_df['run_time'].mean() / ws_df['run_time'].mean()))
