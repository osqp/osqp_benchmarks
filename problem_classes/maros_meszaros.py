import numpy as np
import scipy.sparse as spa
import scipy.io as spio
import cvxpy


class MarosMeszaros(object):
    '''
    Maros Meszaros
    '''
    def __init__(self, file_name, create_cvxpy_problem=False):
        '''
        Generate Maros problem in QP format and CVXPY format

        NB. By default, the CVXPY problem is not created
        '''
        # Load problem from file
        self.P, self.q, self.r, self.A, self.l, self.u, self.n, self.m = \
            self._load_maros_meszaros_problem(file_name)

        self.qp_problem = self._generate_qp_problem()

        if create_cvxpy_problem:
            self.cvxpy_problem = self._generate_cvxpy_problem()

    @staticmethod
    def _load_maros_meszaros_problem(f):
        # Load file
        m = spio.loadmat(f)

        # Convert matrices
        P = m['P'].astype(float).tocsc()
        q = m['q'].T.flatten().astype(float)
        r = m['r'].T.flatten().astype(float)[0]
        A = m['A'].astype(float).tocsc()
        l = m['l'].T.flatten().astype(float)
        u = m['u'].T.flatten().astype(float)
        n = m['n'].T.flatten().astype(int)[0]
        m = m['m'].T.flatten().astype(int)[0]

        return P, q, r, A, l, u, n, m

    @staticmethod
    def name():
        return 'Maros Meszaros'

    def _generate_qp_problem(self):
        '''
        Generate QP problem
        '''
        problem = {}
        problem['P'] = self.P
        problem['q'] = self.q
        problem['r'] = self.r
        problem['A'] = self.A
        problem['l'] = self.l
        problem['u'] = self.u
        problem['n'] = self.n
        problem['m'] = self.m

        return problem

    def _generate_cvxpy_problem(self):
        '''
        Generate QP problem
        '''
        x_var = cvxpy.Variable(self.n)
        objective = .5 * cvxpy.quad_form(x_var, self.P) + self.q * x_var + \
            self.r
        constraints = [self.A * x_var <= self.u, self.A * x_var >= self.l]
        problem = cvxpy.Problem(cvxpy.Minimize(objective), constraints)

        return problem

    def revert_cvxpy_solution(self):
        '''
        Get QP primal and duar variables from cvxpy solution
        '''

        variables = self.cvxpy_problem.variables()
        constraints = self.cvxpy_problem.constraints

        # primal solution
        x = variables[0].value

        # dual solution
        y = constraints[0].dual_value - constraints[1].dual_value

        return x, y
