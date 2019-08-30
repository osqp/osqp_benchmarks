import numpy as np
import scipy.sparse as spa
import cvxpy


class HuberExample(object):
    '''
    Huber QP example
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
        self.x_true = np.random.randn(n) / np.sqrt(n)
        ind95 = (np.random.rand(self.m) < 0.95).astype(float)
        self.bd = self.Ad.dot(self.x_true) + \
            np.multiply(0.5*np.random.randn(self.m), ind95) \
            + np.multiply(10.*np.random.rand(self.m), 1. - ind95)

        self.qp_problem = self._generate_qp_problem()
        self.cvxpy_problem, self.cvxpy_variables = \
            self._generate_cvxpy_problem()

    @staticmethod
    def name():
        return 'Huber'

    def _generate_qp_problem(self):
        '''
        Generate QP problem
        '''
        # Construct the problem
        #       minimize    1/2 z.T * z + np.ones(m).T * (r + s)
        #       subject to  Ax - b - z = r - s
        #                   r >= 0
        #                   s >= 0
        # The problem reformulation follows from Eq. (24) of the following paper:
        # https://doi.org/10.1109/34.877518
        # x_solver = (x, z, r, s)
        Im = spa.eye(self.m)
        P = spa.block_diag((spa.csc_matrix((self.n, self.n)), Im,
                            spa.csc_matrix((2*self.m, 2*self.m))), format='csc')
        q = np.hstack([np.zeros(self.n + self.m), np.ones(2*self.m)])
        A = spa.bmat([[self.Ad, -Im,   -Im,   Im],
                      [None,     None,  Im,   None],
                      [None,     None,  None, Im]], format='csc')
        l = np.hstack([self.bd, np.zeros(2*self.m)])
        u = np.hstack([self.bd, np.inf*np.ones(2*self.m)])

        # Constraints without bounds
        A_nobounds = spa.hstack([self.Ad, -Im, -Im, Im], format='csc')
        l_nobounds = self.bd
        u_nobounds = self.bd

        # Bounds
        lx = np.hstack([-np.inf * np.ones(self.n + self.m),
                        np.zeros(2*self.m)])
        ux = np.inf*np.ones(self.n + 3*self.m)
        bounds_idx = np.arange(self.n + self.m, self.n + 3*self.m)

        problem = {}
        problem['P'] = P
        problem['q'] = q
        problem['A'] = A
        problem['l'] = l
        problem['u'] = u
        problem['m'] = A.shape[0]
        problem['n'] = A.shape[1]
        problem['A_nobounds'] = A_nobounds
        problem['l_nobounds'] = l_nobounds
        problem['u_nobounds'] = u_nobounds
        problem['bounds_idx'] = bounds_idx
        problem['lx'] = lx
        problem['ux'] = ux

        return problem

    def _generate_cvxpy_problem(self):
        '''
        Generate QP problem
        '''
        # Construct the problem
        #       minimize    1/2 z.T * z + np.ones(m).T * (r + s)
        #       subject to  Ax - b - z = r - s
        #                   r >= 0
        #                   s >= 0
        # The problem reformulation follows from Eq. (24) of the following paper:
        # https://doi.org/10.1109/34.877518
        x = cvxpy.Variable(self.n)
        z = cvxpy.Variable(self.m)
        r = cvxpy.Variable(self.m)
        s = cvxpy.Variable(self.m)

        objective = cvxpy.Minimize(.5 * cvxpy.sum_squares(z) + cvxpy.sum(r + s))
        constraints = [self.Ad@x - self.bd - z == r - s,
                       r >= 0, s >= 0]
        problem = cvxpy.Problem(objective, constraints)

        return problem, (x, z, r, s)

    def revert_cvxpy_solution(self):
        '''
        Get QP primal and duar variables from cvxpy solution
        '''

        (x_cvx, z_cvx, r_cvx, s_cvx) = self.cvxpy_variables
        constraints = self.cvxpy_problem.constraints

        # primal solution
        x = np.concatenate((x_cvx.value,
                            z_cvx.value,
                            r_cvx.value,
                            s_cvx.value))

        # dual solution
        y = np.concatenate((constraints[0].dual_value,
                            -constraints[1].dual_value,
                            -constraints[2].dual_value))

        return x, y
