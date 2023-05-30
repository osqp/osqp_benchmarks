import numpy as np
import scipy.sparse as spa
import cvxpy


class PortfolioExample(object):
    '''
    Portfolio QP example
    '''
    def __init__(self, k, seed=1, n=None):
        '''
        Generate problem in QP format and CVXPY format
        '''
        # Set random seed
        np.random.seed(seed)

        self.k = int(k)               # Number of factors
        if n is None:                 # Number of assets
            self.n = int(k * 100)
        else:
            self.n = int(n)

        # Generate data
        self.F = spa.random(self.n, self.k, density=0.5,
                            data_rvs=np.random.randn, format='csc')
        self.D = spa.diags(np.random.rand(self.n) *
                           np.sqrt(self.k), format='csc')
        self.mu = np.random.randn(self.n)
        self.gamma = 1.0

        self.qp_problem = self._generate_qp_problem()
        self.cvxpy_problem, self.cvxpy_param = \
            self._generate_cvxpy_problem()

    @staticmethod
    def name():
        return 'Portfolio'

    def _generate_qp_problem(self):
        '''
        Generate QP problem
        '''

        # Construct the problem
        #       minimize	x' D x + y' I y - (1/gamma) * mu' x
        #       subject to  1' x = 1
        #                   F' x = y
        #                   0 <= x <= 1
        P = spa.block_diag((2 * self.D, 2 * spa.eye(self.k)), format='csc')
        q = np.append(- self.mu / self.gamma, np.zeros(self.k))
        A = spa.vstack([
                spa.hstack([spa.csc_matrix(np.ones((1, self.n))),
                           spa.csc_matrix((1, self.k))]),
                spa.hstack([self.F.T, -spa.eye(self.k)]),
                spa.hstack((spa.eye(self.n), spa.csc_matrix((self.n, self.k))))
            ]).tocsc()
        l = np.hstack([1., np.zeros(self.k), np.zeros(self.n)])
        u = np.hstack([1., np.zeros(self.k), np.ones(self.n)])

        # Constraints without bounds
        A_nobounds = spa.vstack([
                spa.hstack([spa.csc_matrix(np.ones((1, self.n))),
                            spa.csc_matrix((1, self.k))]),
                spa.hstack([self.F.T, -spa.eye(self.k)]),
                ]).tocsc()
        l_nobounds = np.hstack([1., np.zeros(self.k)])
        u_nobounds = np.hstack([1., np.zeros(self.k)])
        bounds_idx = np.arange(self.n)

        # Separate bounds
        lx = np.hstack([np.zeros(self.n), -np.inf * np.ones(self.k)])
        ux = np.hstack([np.ones(self.n), np.inf * np.ones(self.k)])

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

        x = cvxpy.Variable(self.n)
        y = cvxpy.Variable(self.k)

        # Create parameters m
        mu = cvxpy.Parameter(self.n)
        mu.value = self.mu

        objective = cvxpy.Minimize(cvxpy.quad_form(x, cvxpy.psd_wrap(self.D)) +
                                   cvxpy.quad_form(y, cvxpy.psd_wrap(spa.eye(self.k))) +
                                   - 1 / self.gamma * (mu.T * x))
        constraints = [np.ones(self.n) * x == 1,
                       self.F.T * x == y,
                       0 <= x, x <= 1]
        problem = cvxpy.Problem(objective, constraints)

        return problem, mu

    def revert_cvxpy_solution(self):
        '''
        Get QP primal and duar variables from cvxpy solution
        '''

        variables = self.cvxpy_problem.variables()
        constraints = self.cvxpy_problem.constraints

        # primal solution
        x = np.concatenate((variables[0].value,
                            variables[1].value))

        # dual solution
        y = np.concatenate(([constraints[0].dual_value],
                            constraints[1].dual_value,
                            constraints[3].dual_value -
                            constraints[2].dual_value))

        return x, y

    def update_parameters(self, mu, F=None, D=None):
        """
        Update problem parameters with new mu, F, D
        """

        # Update internal parameters
        self.mu = mu
        if F is not None:
            if F.shape == self.F.shape and \
                    all(F.indptr == self.F.indptr) and \
                    all(F.indices == self.F.indices):
                # Check if F has same sparsity pattern as self.D
                self.F = F
            else:
                raise ValueError("F sparsity pattern changed")
        if D is not None:
            if D.shape == self.D.shape and \
                    all(D.indptr == self.D.indptr) and \
                    all(D.indices == self.D.indices):
                # Check if D has same sparsity pattern as self.D
                self.D = D
            else:
                raise ValueError("D sparsity pattern changed")

        # Update parameters in QP problem
        if F is None and D is None:
            # Update only q
            self.qp_problem['q'] = np.append(- self.mu / self.gamma,
                                             np.zeros(self.k))
            # Update parameter in CVXPY problem
            self.cvxpy_param.value = self.mu
        else:
            # Generate problem from scratch
            self.qp_problem = self._generate_qp_problem()
            self.cvxpy_problem, self.cvxpy_param = \
                self._generate_cvxpy_problem()
