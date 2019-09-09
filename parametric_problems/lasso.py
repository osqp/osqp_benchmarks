"""
Solve Lasso problem as parametric QP by updating iteratively lambda
"""
import numpy as np
import pandas as pd
import os
from solvers.solvers import SOLVER_MAP  # AVOID CIRCULAR DEPENDENCY
from problem_classes.lasso import LassoExample
from utils.general import make_sure_path_exists
# import osqppurepy as osqp
import osqp


class LassoParametric(object):
    def __init__(self,
                 osqp_settings,
                 dimension,
                 minimum_lambda_over_max=0.01,
                 n_problems=100):
        """
        Generate Parametric Lasso object

        Args:
            osqp_settings: osqp solver settings
            dimension: leading dimension for the problem
            minimum_lambda_over_max: min ratio between lambda and lambda_max
            n_problem: number of lasso problems to solve
        """
        self.osqp_settings = osqp_settings
        self.dimension = dimension
        self.minimum_lambda_over_max = minimum_lambda_over_max
        self.n_problems = n_problems

    def solve(self):
        """
        Solve Lasso problem
        """

        print("Solve Lasso problem for dimension %i" % self.dimension)

        # Create example instance
        instance = LassoExample(self.dimension)
        qp = instance.qp_problem

        # Create lambda array
        lambda_array = np.logspace(np.log10(self.minimum_lambda_over_max *
                                            instance.lambda_max),
                                   np.log10(instance.lambda_max),
                                   self.n_problems)[::-1]   # From max to min

        '''
        Solve problem without warm start
        '''
        #  print("Solving without warm start")
        # Solution directory
        no_ws_path = os.path.join('.', 'results', 'parametric_problems',
                                  'OSQP no warmstart',
                                  'Lasso',
                                  )

        # Create directory for the results
        make_sure_path_exists(no_ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(no_ws_path, 'n%i.csv' % self.dimension)

        if not os.path.isfile(n_file_name):

            res_list_no_ws = []  # Initialize results
            for lambda_val in lambda_array:
                # Update lambda
                instance.update_lambda(lambda_val)

                # Solve problem
                m = osqp.OSQP()
                m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                        **self.osqp_settings)
                r = m.solve()

                # DEBUG
                #  print("Lambda = %.4e,\t niter = %d" % (lambda_val, r.info.iter))

                if r.info.status != "solved":
                    print("OSQP no warmstart did not solve the problem")

                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter]}

                res_list_no_ws.append(pd.DataFrame(solution_dict))

            # Get full warm-start
            res_no_ws = pd.concat(res_list_no_ws)

            # Store file
            res_no_ws.to_csv(n_file_name, index=False)

        '''
        Solve problem with warm start
        '''

        #  print("Solving with warm start")
        # Solution directory
        ws_path = os.path.join('.', 'results', 'parametric_problems',
                               'OSQP warmstart',
                               'Lasso',
                               )

        # Create directory for the results
        make_sure_path_exists(ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(ws_path, 'n%i.csv' % self.dimension)

        # Reset problem to first instance
        instance.update_lambda(lambda_array[0])

        # Setup solver
        qp = instance.qp_problem
        m = osqp.OSQP()
        m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                **self.osqp_settings)

        if not os.path.isfile(n_file_name):

            res_list_ws = []  # Initialize results
            for lambda_val in lambda_array:

                # Update lambda
                instance.update_lambda(lambda_val)
                m.update(q=qp['q'])

                # Solve problem
                r = m.solve()

                # DEBUG
                #  print("Lambda = %.4e,\t niter = %d" % (lambda_val, r.info.iter))

                if r.info.status != "solved":
                    print("OSQP warmstart did not solve the problem")

                # Get results
                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter]}

                res_list_ws.append(pd.DataFrame(solution_dict))

            # Get full warm-start
            res_ws = pd.concat(res_list_ws)

            # Store file
            res_ws.to_csv(n_file_name, index=False)

        else:
            res_ws = pd.read_csv(n_file_name)
