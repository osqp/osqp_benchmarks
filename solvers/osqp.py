import osqp
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class OSQPSolver(object):

    m = osqp.OSQP()
    STATUS_MAP = {osqp.constant('OSQP_SOLVED', algebra=s.ALGEBRA): s.OPTIMAL,
                  osqp.constant('OSQP_MAX_ITER_REACHED', algebra=s.ALGEBRA): s.MAX_ITER_REACHED,
                  osqp.constant('OSQP_PRIMAL_INFEASIBLE', algebra=s.ALGEBRA): s.PRIMAL_INFEASIBLE,
                  osqp.constant('OSQP_DUAL_INFEASIBLE', algebra=s.ALGEBRA): s.DUAL_INFEASIBLE}

    def __init__(self, settings={}):
        '''
        Initialize solver object by setting require settings
        '''
        self._settings = settings

    @property
    def settings(self):
        """Solver settings"""
        return self._settings

    def solve(self, example, codegen=None):
        '''
        Solve problem

        Args:
            problem: problem structure with QP matrices

            codegen_path: Path for codegen directory.

        Returns:
            Results structure
        '''
        problem = example.qp_problem
        settings = self._settings.copy()
        high_accuracy = settings.pop('high_accuracy', None)

        settings['adaptive_rho_interval'] = 0
        settings['adaptive_rho_tolerance'] = 5.0

        algebra = self.settings.get('algebra', 'builtin')
        # Setup OSQP
        m = osqp.OSQP(algebra=algebra)

        m.setup(problem['P'], problem['q'], problem['A'], problem['l'],
                problem['u'],
                **settings)
        
        if codegen:
            m.codegen(codegen, force_rewrite=True)
            return None

        # Solve
        results = m.solve()
        status = self.STATUS_MAP.get(results.info.status_val, s.SOLVER_ERROR)

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          results.x,
                                          results.y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        # Verify solver time
        if settings.get('time_limit') is not None:
            if results.info.run_time > settings.get('time_limit'):
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 results.info.obj_val,
                                 results.x,
                                 results.y,
                                 results.info.run_time,
                                 results.info.iter,
                                 results.info.dual_obj_val,
                                 results.info.duality_gap,
                                 results.info.restarts,
                                 )

        return_results.status_polish = results.info.status_polish
        return_results.setup_time = results.info.setup_time
        return_results.solve_time = results.info.solve_time
        return_results.update_time = results.info.update_time
        return_results.rho_updates = results.info.rho_updates
        return_results.dual_obj_val = results.info.dual_obj_val
        return_results.duality_gap = results.info.duality_gap
        return_results.restarts = results.info.restarts

        return return_results
