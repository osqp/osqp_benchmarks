'''
Run Maros-Meszaros problems for the OSQP paper

This code tests the solvers:
    - OSQP
    - GUROBI
    - MOSEK
    - ECOS
    - qpOASES

'''
from maros_meszaros_problems.maros_meszaros_problem import MarosMeszarosRunner
import solvers.solvers as s
from utils.benchmark import \
    compute_performance_profiles, \
    compute_failure_rates, \
    compute_polish_statistics

# Define solvers to benchmark
solvers = [
            s.OSQP,
            s.OSQP_polish,
            s.GUROBI,
            s.MOSEK,
            #  s.ECOS,
            #  s.qpOASES
           ]

time_limit = 1000.  # Seconds
settings = {
             s.OSQP: {'polish': False,
                      'time_limit': time_limit,
                      'eps_prim_inf': 1e-15,  # Disable infeas check
                      'eps_dual_inf': 1e-15
                      },
             s.OSQP_polish: {'polish': True,
                             'time_limit': time_limit,
                             'eps_prim_inf': 1e-15,  # Disable infeas check
                             'eps_dual_inf': 1e-15
                             },
             s.GUROBI: {'time_limit': time_limit},
             s.MOSEK: {'time_limit': time_limit},
             s.ECOS: {'time_limit': time_limit},
             s.qpOASES: {'time_limit': time_limit}
            }

# Shut up solvers
for key in settings:
    settings[key]['verbose'] = False

# Run all examples
maros_meszaros_runner = MarosMeszarosRunner(solvers,
                                            settings)

# DEBUG only: Choose only 2 problems
#  maros_meszaros_runner.problems = ["HS52", "HS53"]

maros_meszaros_runner.solve(parallel=False, cores=10)


# Compute failure rates
compute_failure_rates(solvers, 'maros_meszaros_problems')

# Compute performance profiles
compute_performance_profiles(solvers, 'maros_meszaros_problems')

# Compute polish statistics
if 'OSQP' in solvers and 'OSQP_polish' in solvers:
    compute_polish_statistics('maros_meszaros_problems')
