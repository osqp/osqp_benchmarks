"""
Solve Portoflio problem for one year simulation
"""
import os
import numpy as np
from utils.general import make_sure_path_exists
import pandas as pd
from problems.portfolio import PortfolioExample
# import osqppurepy as osqp
import osqp


class PortfolioParametric(object):
    def __init__(self,
                 osqp_settings,
                 n_factors=100,
                 n_assets=3000,
                 n_months_per_risk_model_update=3,
                 n_years=4):
        """
        Generate Portfolio problem as parametric QP

        Args:
            osqp_settings: osqp solver settings
            n_factors: number of factors in risk model
            n_assets: number of assets to be optimized
            n_months_per_risk_model_update: number of months for every risk
                                            model update
            n_years: number of years to run the simulation
        """
        self.osqp_settings = osqp_settings
        self.n_factors = n_factors
        self.n_assets = n_assets
        self.n_qp_per_month = 20  # Number of trading days
        self.n_qp_per_update = self.n_qp_per_month * \
            n_months_per_risk_model_update
        self.n_problems = n_years * 240
        self.alpha = 0.1  # Relaxation parameter between new data nad old ones

    def solve(self):
        """
        Solve Portfolio problem
        """

        print("Solve Portfolio problem for dimension %i" % self.n_factors)

        # Create example instance
        instance = PortfolioExample(self.n_factors, n=self.n_assets)

        # Store number of nonzeros in F and D for updates
        nnzF = instance.F.nnz
        
        # Store alpha
        alpha = self.alpha

        '''
        Solve problem without warm start
        '''
        print("Solving without warm start")

        # Solution directory
        no_ws_path = os.path.join('.', 'results', 'parametric_problems',
                                  'OSQP no warmstart',
                                  'Portfolio',
                                  )

        # Create directory for the results
        make_sure_path_exists(no_ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(no_ws_path, 'n%i.csv' % self.n_factors)

        if not os.path.isfile(n_file_name):

            res_list_no_ws = []  # Initialize results
            for i in range(self.n_problems):
                qp = instance.qp_problem

                # Solve problem
                m = osqp.OSQP()
                m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                        **self.osqp_settings)
                r = m.solve()

                # DEBUG
                print("niter = %d" % r.info.iter)

                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter],
                                 'obj_val': [r.info.obj_val]}

                if r.info.status != "Solved":
                    print("OSQP no warmstart did not solve the problem")

                res_list_no_ws.append(pd.DataFrame(solution_dict))

                # Update model
                current_mu = instance.mu
                current_F_data = instance.F.data
                current_D_data = instance.D.data

                if i % self.n_qp_per_update == 0:
                    print("Update everything: mu, F, D") 
                    # Update everything
                    new_mu = alpha * np.random.randn(instance.n) + (1 - alpha) * current_mu
                    new_F = instance.F.copy()
                    new_F.data = alpha * np.random.randn(nnzF) + (1 - alpha) * current_F_data
                    new_D = instance.D.copy()
                    new_D.data = alpha * np.random.rand(instance.n) * \
                        np.sqrt(instance.k) + (1 - alpha) * current_D_data
                    instance.update_parameters(new_mu, new_F, new_D)
                else:
                    print("Update only mu") 
                    # Update only mu
                    new_mu = alpha * np.random.randn(instance.n) + (1 - alpha) * current_mu
                    instance.update_parameters(new_mu)

            # Get full warm-start
            res_no_ws = pd.concat(res_list_no_ws)

            # Store file
            res_no_ws.to_csv(n_file_name, index=False)

            # Plot results
            # import matplotlib.pylab as plt
            # plt.figure(0)
            # plt.plot(X_no_ws.T)
            # plt.title("No Warm Start")
            # plt.show(block=False)

        '''
        Solve problem with warm start
        '''
        print("Solving with warm start")

        # Solution directory
        ws_path = os.path.join('.', 'results', 'parametric_problems',
                               'OSQP warmstart',
                               'Portfolio',
                               )

        # Create directory for the results
        make_sure_path_exists(ws_path)

        # Check if solution already exists
        n_file_name = os.path.join(ws_path, 'n%i.csv' % self.n_factors)

        if not os.path.isfile(n_file_name):
            # Setup solver
            m = osqp.OSQP()
            m.setup(qp['P'], qp['q'], qp['A'], qp['l'], qp['u'],
                    **self.osqp_settings)

            res_list_ws = []  # Initialize results
            for i in range(self.n_problems):

                # Solve problem
                r = m.solve()

                # DEBUG
                print("niter = %d" % r.info.iter)

                if r.info.status != "Solved":
                    print("OSQP warmstart did not solve the problem")

                # Get results
                solution_dict = {'status': [r.info.status],
                                 'run_time': [r.info.run_time],
                                 'iter': [r.info.iter],
                                 'obj_val': [r.info.obj_val]}

                res_list_ws.append(pd.DataFrame(solution_dict))

                # Update model
                current_mu = instance.mu
                current_F_data = instance.F.data
                current_D_data = instance.D.data

                if i % self.n_qp_per_update == 0:
                    print("Update everything: mu, F, D") 
                    # Update everything
                    new_mu = alpha * np.random.randn(instance.n) + (1 - alpha) * current_mu
                    new_F = instance.F.copy()
                    new_F.data = alpha * np.random.randn(nnzF) + (1 - alpha) * current_F_data
                    new_D = instance.D.copy()
                    new_D.data = alpha * np.random.rand(instance.n) * \
                        np.sqrt(instance.k) + (1 - alpha) * current_D_data
                    instance.update_parameters(new_mu, new_F, new_D)
                    # Update solver
                    m.update(q=instance.qp_problem['q'],
                             Px=instance.qp_problem['P'].data,
                             Ax=instance.qp_problem['A'].data)
                else:
                    print("Update only mu") 
                    # Update only mu
                    new_mu = alpha * np.random.randn(instance.n) + (1 - alpha) * current_mu
                    instance.update_parameters(new_mu)

                    # Update solver
                    m.update(q=instance.qp_problem['q'])

            # Get full warm-start
            res_ws = pd.concat(res_list_ws)

            # Store file
            res_ws.to_csv(n_file_name, index=False)

            # Plot results
            # import matplotlib.pylab as plt
            # plt.figure(1)
            # plt.plot(X_ws.T)
            # plt.title("Warm Start")
            # plt.show(block=False)
