import numpy as np
import scipy.sparse as spa
import scipy.io as spio
import cvxpy
import tables


class SuitesparseLasso(object):
    '''
    SuiteSparse Lasso
    '''
    def __init__(self, file_name, create_cvxpy_problem=False):
        '''
        Suitesparse Matrix collection Ax = b lasso problem.

        NB. By default, the CVXPY problem is not created
        '''
        self._load_suitesparse_lasso_data(file_name)
        
        self.qp_problem = self._generate_qp_problem()

        if create_cvxpy_problem:
            self.cvxpy_problem = self._generate_cvxpy_problem()

    def _load_suitesparse_lasso_data(self, file):
        # Import with pytables
        f = tables.open_file(file + '.mat')
        self.bd = f.root['b'][:].flatten()
        A_indices = f.root['A']['ir'][:]
        A_pointers = f.root['A']['jc'][:]
        A_data = f.root['A']['data'][:]
        self.n = len(A_pointers) - 1
        self.m = len(self.bd)
        self.Ad = spa.csc_matrix((A_data, A_indices, A_pointers), shape=(self.m, self.n))

        # Construct Lasso problem
        self.lambda_max = np.linalg.norm(self.Ad.T.dot(self.bd), np.inf)
        self.lambda_param = (1./5.) * self.lambda_max

    @staticmethod
    def name():
        return 'Suitesparse Lasso'

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

        objective = cvxpy.Minimize(cvxpy.quad_form(y, spa.eye(self.m))
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
