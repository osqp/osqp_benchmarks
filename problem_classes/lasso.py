import numpy as np
import scipy.sparse as spa
import cvxpy


class LassoExample(object):
    '''
    Lasso QP example
    '''
    def __init__(self, n, seed=1):
        '''
        Generate problem in QP format and CVXPY format
        '''
        # Set random seed
        np.random.seed(seed)

        self.n = int(n)               # Number of features
        self.m = int(self.n * 100)    # Number of data-points

        self.Ad = spa.random(self.m, self.n, density=0.15,
                             data_rvs=np.random.randn)
        self.x_true = np.multiply((np.random.rand(self.n) >
                                   0.5).astype(float),
                                  np.random.randn(self.n)) / np.sqrt(self.n)
        self.bd = self.Ad.dot(self.x_true) + np.random.randn(self.m)
        self.lambda_max = np.linalg.norm(self.Ad.T.dot(self.bd), np.inf)
        self.lambda_param = (1./5.) * self.lambda_max

        self.qp_problem = self._generate_qp_problem()
        self.cvxpy_problem, self.cvxpy_variables, self.cvxpy_param = \
            self._generate_cvxpy_problem()

    @staticmethod
    def name():
        return 'Lasso'

    def _generate_qp_problem(self):
        '''
        Generate QP problem
        '''

        # Construct the problem
        #       minimize	y' * y + lambda * 1' * t
        #       subject to  y = Ax - b
        #                   -t <= x <= t
        P = spa.block_diag((spa.csc_matrix((self.n, self.n)),
                            2*spa.eye(self.m),
                            spa.csc_matrix((self.n, self.n))), format='csc')
        q = np.append(np.zeros(self.m + self.n),
                      self.lambda_param * np.ones(self.n))
        In = spa.eye(self.n)
        Onm = spa.csc_matrix((self.n, self.m))
        A = spa.vstack([spa.hstack([self.Ad, -spa.eye(self.m),
                                    spa.csc_matrix((self.m, self.n))]),
                        spa.hstack([In, Onm, -In]),
                        spa.hstack([In, Onm, In])]).tocsc()
        l = np.hstack([self.bd, -np.inf * np.ones(self.n), np.zeros(self.n)])
        u = np.hstack([self.bd, np.zeros(self.n), np.inf * np.ones(self.n)])

        problem = {}
        problem['P'] = P
        problem['q'] = q
        problem['A'] = A
        problem['l'] = l
        problem['u'] = u
        problem['m'] = A.shape[0]
        problem['n'] = A.shape[1]

        return problem

    def _generate_cvxpy_problem(self):
        '''
        Generate QP problem
        '''

        x = cvxpy.Variable(self.n)
        y = cvxpy.Variable(self.m)
        t = cvxpy.Variable(self.n)

        # Create parameeter and assign value
        lambda_cvxpy = cvxpy.Parameter()
        lambda_cvxpy.value = self.lambda_param

        objective = cvxpy.Minimize(cvxpy.quad_form(y, cvxpy.psd_wrap(spa.eye(self.m)))
                                   + self.lambda_param * (np.ones(self.n) * t))
        constraints = [y == self.Ad * x - self.bd,
                       -t <= x, x <= t]
        problem = cvxpy.Problem(objective, constraints)

        return problem, (x, y, t), lambda_cvxpy

    def revert_cvxpy_solution(self):
        '''
        Get QP primal and duar variables from cvxpy solution
        '''

        (x_cvx, y_cvx, t_cvx) = self.cvxpy_variables
        constraints = self.cvxpy_problem.constraints

        # primal solution
        x = np.concatenate((x_cvx.value,
                            y_cvx.value,
                            t_cvx.value))

        # dual solution
        y = np.concatenate((-constraints[0].dual_value,
                            constraints[2].dual_value,
                            -constraints[1].dual_value))

        return x, y

    def update_lambda(self, lambda_new):
        """
        Update lambda value in inner problems
        """
        # Update internal lambda parameter
        self.lambda_param = lambda_new

        # Update q in QP problem
        self.qp_problem['q'] = np.append(np.zeros(self.m + self.n),
                                         self.lambda_param * np.ones(self.n))

        # Update parameter in CVXPY problem
        self.cvxpy_param.value = self.lambda_param
