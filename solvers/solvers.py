from solvers.ecos import ECOSSolver
from solvers.gurobi import GUROBISolver
from solvers.mosek import MOSEKSolver
from solvers.osqp import OSQPSolver
from solvers.qpoases import qpOASESSolver

ECOS = 'ECOS'
ECOS_high = ECOS + "_high"
GUROBI = 'GUROBI'
GUROBI_high = GUROBI + "_high"
OSQP = 'OSQP'
OSQP_high = OSQP + '_high'
OSQP_polish = OSQP + '_polish'
OSQP_polish_high = OSQP_polish + '_high'
MOSEK = 'MOSEK'
MOSEK_high = MOSEK + "_high"
qpOASES = 'qpOASES'

# solvers = [ECOSSolver, GUROBISolver, MOSEKSolver, OSQPSolver]
# SOLVER_MAP = {solver.name(): solver for solver in solvers}


SOLVER_MAP = {OSQP: OSQPSolver,
              OSQP_high: OSQPSolver,
              OSQP_polish: OSQPSolver,
              OSQP_polish_high: OSQPSolver,
              GUROBI: GUROBISolver,
              GUROBI_high: GUROBISolver,
              MOSEK: MOSEKSolver,
              MOSEK_high: MOSEKSolver,
              ECOS: ECOSSolver,
              ECOS_high: ECOSSolver,
              qpOASES: qpOASESSolver}

time_limit = 1000. # Seconds
eps_low = 1e-03
eps_high = 1e-05

# Solver settings
settings = {
    OSQP: {'eps_abs': eps_low,
           'eps_rel': eps_low,
           'polish': False,
           'max_iter': int(1e09),
           'eps_prim_inf': 1e-15,  # Disable infeas check
           'eps_dual_inf': 1e-15,
    },
    OSQP_high: {'eps_abs': eps_high,
                'eps_rel': eps_high,
                'polish': False,
                'max_iter': int(1e09),
                'eps_prim_inf': 1e-15,  # Disable infeas check
                'eps_dual_inf': 1e-15
    },
    OSQP_polish: {'eps_abs': eps_low,
                  'eps_rel': eps_low,
                  'polish': True,
                  'max_iter': int(1e09),
                  'eps_prim_inf': 1e-15,  # Disable infeas check
                  'eps_dual_inf': 1e-15
    },
    OSQP_polish_high: {'eps_abs': eps_high,
                       'eps_rel': eps_high,
                       'polish': True,
                       'max_iter': int(1e09),
                       'eps_prim_inf': 1e-15,  # Disable infeas check
                       'eps_dual_inf': 1e-15
    },
    GUROBI: {'TimeLimit': time_limit,
             'FeasibilityTol': eps_low,
             'OptimalityTol': eps_low,
             'BarConvTol': 1e-2 * eps_low},
    GUROBI_high: {'TimeLimit': time_limit,
                  'FeasibilityTol': eps_high,
                  'OptimalityTol': eps_high,
                  'BarConvTol': 1e-2 * eps_high},
    MOSEK: {'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
            'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_low,   # Primal feasibility tolerance
            'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_low,   # Dual feasibility tolerance
            'MSK_DPAR_INTPNT_CO_TOL_REL_GAP': 1e-2 * eps_low,  # Complementary slackness
            'MSK_DPAR_INTPNT_CO_TOL_MU_RED': 1e-2 * eps_low,  # Relative complementary slackness tolerance
           },
    MOSEK_high: {'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
                 'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_high,   # Primal feasibility tolerance
                 'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_high,   # Dual feasibility tolerance
                 'MSK_DPAR_INTPNT_CO_TOL_REL_GAP': 1e-2 * eps_high,  # Complementary slackness
                 'MSK_DPAR_INTPNT_CO_TOL_MU_RED': 1e-2 * eps_high,  # Relative complementary slackness tolerance
                },
    ECOS: {'abstol': eps_low,
           'reltol': eps_low},
    ECOS_high: {'abstol': eps_high,
                'reltol': eps_high},
    qpOASES: {}
}

for key in settings:
    settings[key]['verbose'] = False
    settings[key]['time_limit'] = time_limit
