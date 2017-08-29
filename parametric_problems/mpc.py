"""
Solve Lasso problem as parametric QP by updating iteratively lambda
"""
import numpy as np
import pandas as pd
import os
from problems.control import ControlExample
from utils.general import make_sure_path_exists
import osqp


class MPCParametric(object):
    def __init__(self,
                 osqp_settings,
                 dimension,
                 n_simulation=100):
        """
        Generate MPC problem as parametric QP

        Args:
            osqp_settings: osqp solver settings
            dimension: leading dimension for the problem
            minimum_lambda_over_max: min ratio between lambda and lambda_max
            n_simulation: number of MPC problems to solve
        """
        self.osqp_settings = osqp_settings
        self.dimension = dimension
        self.n_simulation = n_simulation

    def solve(self):
        """
        Solve MPC problem
        """

        print("Solve MPC problem for dimension %i" % self.dimension)

        # Create example instance
        instance = ControlExample(self.dimension)
        qp = instance.qp_problem
        x0 = np.copy(instance.x0)

        '''
        Solve problem without warm start
        '''
        # Solution directory
        no_ws_path = os.path.join('.', 'results', 'parametric_problems',
                                  'OSQP no warmstart',
                                  'MPC',
                                  )

        # Create directory for the results
        make_sure_path_exists(no_ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(no_ws_path, 'n%i.csv' % self.dimension)

        if not os.path.isfile(n_file_name):
            # Initialize states and inputs for the whole simulation
            X_no_ws = np.zeros((instance.nx, self.n_simulation + 1))
            U_no_ws = np.zeros((instance.nu, self.n_simulation))
            X_no_ws[:, 0] = x0

            res_list_no_ws = []  # Initialize results
            for i in range(self.n_simulation):

                # Solve problem
                m = osqp.OSQP()
                m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                        **self.osqp_settings)
                r = m.solve()

                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter]}

                if r.info.status != "Solved":
                    print("OSQP no warmstart did not solve the problem")

                res_list_no_ws.append(pd.DataFrame(solution_dict))

                # Get input
                U_no_ws[:, i] = r.x[instance.nx * (instance.T + 1):
                                    instance.nx * (instance.T + 1)+instance.nu]

                # Propagate state
                X_no_ws[:, i + 1] = instance.A.dot(X_no_ws[:, i]) + \
                    instance.B.dot(U_no_ws[:, i])

                # Update initial state
                instance.update_x0(X_no_ws[:, i + 1])

            # Get full warm-start
            res_no_ws = pd.concat(res_list_no_ws)

            # Store file
            res_no_ws.to_csv(n_file_name, index=False)

            # Plot results
            # import matplotlib.pylab as plt
            # plt.figure(1)
            # plt.plot(X_no_ws.T)
            # plt.title("No Warm Start")
            # plt.show(block=False)

        '''
        Solve problem with warm start
        '''
        # Solution directory
        ws_path = os.path.join('.', 'results', 'parametric_problems',
                               'OSQP warmstart',
                               'MPC',
                               )

        # Create directory for the results
        make_sure_path_exists(ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(ws_path, 'n%i.csv' % self.dimension)

        if not os.path.isfile(n_file_name):
            # Setup solver
            m = osqp.OSQP()
            m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                    **self.osqp_settings)

            # Initialize states and inputs for the whole simulation
            X_ws = np.zeros((instance.nx, self.n_simulation + 1))
            U_ws = np.zeros((instance.nu, self.n_simulation))
            X_ws[:, 0] = x0

            res_list_ws = []  # Initialize results
            for i in range(self.n_simulation):

                # Solve problem
                r = m.solve()

                if r.info.status != "Solved":
                    print("OSQP no warmstart did not solve the problem")

                # Get results
                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter]}

                res_list_ws.append(pd.DataFrame(solution_dict))

                # Get input
                U_ws[:, i] = r.x[instance.nx * (instance.T + 1):
                                 instance.nx * (instance.T + 1)+instance.nu]

                # Propagate state
                X_ws[:, i + 1] = instance.A.dot(X_ws[:, i]) + \
                    instance.B.dot(U_ws[:, i])

                # Update initial state
                instance.update_x0(X_ws[:, i + 1])

                # Update solver
                m.update(l=instance.qp_problem['l'],
                         u=instance.qp_problem['u'])

            # Get full warm-start
            res_ws = pd.concat(res_list_ws)

            # Store file
            res_ws.to_csv(n_file_name, index=False)

            # # Plot results
            # import matplotlib.pylab as plt
            # plt.figure(3)
            # plt.plot(X_ws.T)
            # plt.title("X Warm Start")
            # plt.show(block=False)
            #
            # plt.figure(4)
            # plt.plot(U_ws.T)
            # plt.title("U Warm Start")
            # plt.show()
