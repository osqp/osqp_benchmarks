import osqp
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class OSQPSolver(object):

    m = osqp.OSQP()
    STATUS_MAP = {osqp.constant('OSQP_SOLVED'): s.OPTIMAL,
                  osqp.constant('OSQP_MAX_ITER_REACHED'): s.MAX_ITER_REACHED,
                  osqp.constant('OSQP_PRIMAL_INFEASIBLE'): s.PRIMAL_INFEASIBLE,
                  osqp.constant('OSQP_DUAL_INFEASIBLE'): s.DUAL_INFEASIBLE}

    def __init__(self, settings={}):
        '''
        Initialize solver object by setting require settings
        '''
        self._settings = settings

    @property
    def settings(self):
        """Solver settings"""
        return self._settings

    def solve(self, example):
        '''
        Solve problem

        Args:
            problem: problem structure with QP matrices

        Returns:
            Results structure
        '''
        problem = example.qp_problem
        settings = self._settings.copy()
        high_accuracy = settings.pop('high_accuracy', None)

        import ipdb; ipdb.set_trace()

        # Setup OSQP
        m = osqp.OSQP()
        m.setup(problem['P'], problem['q'], problem['A'], problem['l'],
                problem['u'],
                **settings)

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
            if results.info.run_time > time_limit:
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 results.info.obj_val,
                                 results.x,
                                 results.y,
                                 results.info.run_time,
                                 results.info.iter)

        return_results.status_polish = results.info.status_polish
        return_results.setup_time = results.info.setup_time
        return_results.solve_time = results.info.solve_time
        return_results.update_time = results.info.update_time

        return return_results
