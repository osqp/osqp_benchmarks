# from solvers.ecos import ECOSSolver
from solvers.gurobi import GUROBISolver
# from solvers.mosek import MOSEKSolver
from solvers.osqp import OSQPSolver
# from solvers.qpoases import qpOASESSolver
from solvers.clarabel import ClarabelSolver

ECOS = 'ECOS'
ECOS_high = ECOS + "_high"
GUROBI = 'GUROBI'
GUROBI_high = GUROBI + "_high"
OSQP = 'OSQP'
OSQP_high = OSQP + '_high'
OSQP_polish = OSQP + '_polish'
OSQP_polish_high = OSQP_polish + '_high'
OSQP_MKL_INDIRECT = 'OSQP_MKL_INDIRECT'
OSQP_MKL_DIRECT = 'OSQP_MKL_DIRECT'
OSQP_CUDA = 'OSQP_CUDA'
MOSEK = 'MOSEK'
MOSEK_high = MOSEK + "_high"
qpOASES = 'qpOASES'
CLARABEL = 'Clarabel'
CLARABEL_high = CLARABEL + "_high"

# solvers = [ECOSSolver, GUROBISolver, MOSEKSolver, OSQPSolver]
# SOLVER_MAP = {solver.name(): solver for solver in solvers}

SOLVER_MAP = {OSQP: OSQPSolver,
              OSQP_high: OSQPSolver,
              OSQP_polish: OSQPSolver,
              OSQP_polish_high: OSQPSolver,
              OSQP_MKL_INDIRECT: OSQPSolver,
              OSQP_MKL_DIRECT: OSQPSolver,
			  OSQP_CUDA: OSQPSolver,
              GUROBI: GUROBISolver,
              GUROBI_high: GUROBISolver,
              # MOSEK: MOSEKSolver,
              # MOSEK_high: MOSEKSolver,
              # ECOS: ECOSSolver,
              # ECOS_high: ECOSSolver,
              # qpOASES: qpOASESSolver,
              CLARABEL: ClarabelSolver,
              CLARABEL_high: ClarabelSolver}

time_limit = 1000. # Seconds
eps_low = 1e-03
eps_high = 1e-06

# Solver settings
settings = {
    OSQP: {'eps_abs': eps_low,
           'eps_rel': eps_low,
           'polish': False,
           'max_iter': int(1e09),
           'eps_prim_inf': 1e-15,  # Disable infeas check
           'eps_dual_inf': 1e-15,
           'check_dualgap': True,
           'restart_enable': True,
           'restart_sufficient': 0.3875,
           'restart_necessary': 0.825,
           'restart_artificial': 0.5,
    },
    OSQP_high: {'eps_abs': eps_high,
                'eps_rel': eps_high,
                'polish': False,
                'max_iter': int(1e09),
                'eps_prim_inf': 1e-15,  # Disable infeas check
                'eps_dual_inf': 1e-15,
                'check_dualgap': True,
                'restart_enable': True,
                'restart_sufficient': 0.3875,
                'restart_necessary': 0.825,
                'restart_artificial': 0.5,
    },
    OSQP_polish: {'eps_abs': eps_low,
                  'eps_rel': eps_low,
                  'polish': True,
                  'max_iter': int(1e09),
                  'eps_prim_inf': 1e-15,  # Disable infeas check
                  'eps_dual_inf': 1e-15,
                  'check_dualgap': True,
                  'restart_enable': True,
                  'restart_sufficient': 0.3875,
                  'restart_necessary': 0.825,
                  'restart_artificial': 0.5,
    },
    OSQP_polish_high: {'eps_abs': eps_high,
                       'eps_rel': eps_high,
                       'polish': True,
                       'max_iter': int(1e09),
                       'eps_prim_inf': 1e-15,  # Disable infeas check
                       'eps_dual_inf': 1e-15,
                       'check_dualgap': True,
                       'restart_enable': True,
                       'restart_sufficient': 0.3875,
                       'restart_necessary': 0.825,
                       'restart_artificial': 0.5,
    },
    OSQP_MKL_INDIRECT: {'eps_abs': eps_low,
           'eps_rel': eps_low,
           'polish': False,
           'max_iter': int(1e09),
           'eps_prim_inf': 1e-15,  # Disable infeas check
           'eps_dual_inf': 1e-15,
           'algebra': 'mkl',
           'solver_type': 'indirect',
           'check_dualgap': True,
           'restart_enable': True,
           'restart_sufficient': 0.3875,
           'restart_necessary': 0.825,
           'restart_artificial': 0.5,
           },
    OSQP_MKL_DIRECT: {'eps_abs': eps_low,
                        'eps_rel': eps_low,
                        'polish': False,
                        'max_iter': int(1e09),
                        'eps_prim_inf': 1e-15,  # Disable infeas check
                        'eps_dual_inf': 1e-15,
                        'algebra': 'mkl',
                        'solver_type': 'direct',
                        'check_dualgap': True,
                        'restart_enable': True,
                        'restart_sufficient': 0.3875,
                        'restart_necessary': 0.825,
                        'restart_artificial': 0.5,
                        },
    OSQP_CUDA: {'eps_abs': eps_low,
                        'eps_rel': eps_low,
                        'polish': False,
                        'max_iter': int(1e09),
                        'eps_prim_inf': 1e-15,  # Disable infeas check
                        'eps_dual_inf': 1e-15,
                        'algebra': 'cuda',
                        'check_dualgap': True,
                        'restart_enable': True,
                        'restart_sufficient': 0.3875,
                        'restart_necessary': 0.825,
                        'restart_artificial': 0.5,
                        },						
    GUROBI: {'TimeLimit': time_limit,
             'FeasibilityTol': eps_low,
             'OptimalityTol': eps_low,
             },
    GUROBI_high: {'TimeLimit': time_limit,
                  'FeasibilityTol': eps_high,
                  'OptimalityTol': eps_high,
                  },
    MOSEK: {'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
            'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_low,   # Primal feasibility tolerance
            'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_low,   # Dual feasibility tolerance
           },
    MOSEK_high: {'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
                 'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_high,   # Primal feasibility tolerance
                 'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_high,   # Dual feasibility tolerance
                },
    ECOS: {'abstol': eps_low,
           'reltol': eps_low},
    ECOS_high: {'abstol': eps_high,
                'reltol': eps_high},
    qpOASES: {},
    CLARABEL: {'abstol': eps_low,
               'reltol': eps_low},
    CLARABEL_high: {'abstol': eps_high,
                    'reltol': eps_high}
}

for key in settings:
    settings[key]['verbose'] = False
    settings[key]['time_limit'] = time_limit
