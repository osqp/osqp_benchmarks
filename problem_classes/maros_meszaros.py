import numpy as np
import scipy.sparse as spa
import scipy.io as spio
import cvxpy


class MarosMeszaros(object):
    '''
    Maros Meszaros
    '''
    def __init__(self, file_name):
        '''
        Generate Maros problem in QP format and CVXPY format
        '''
        # Load problem from file
        self.P, self.q, self.A, self.l, self.u = \
            self._load_maros_meszaros_problem(file_name)

        self.n = self.A.shape[1]   # Number of variables
        self.m = self.A.shape[0]   # Number of constraints 
        
        self.qp_problem = self._generate_qp_problem()
        self.cvxpy_problem = self._generate_cvxpy_problem()

    @staticmethod
    def _load_maros_meszaros_problem(f):
        # Load file
        m = spio.loadmat(f)

        # Convert matrices
        P = m['Q'].astype(float).tocsc()
        n = P.shape[0]
        q = m['c'].T.flatten().astype(float)
        A = m['A'].astype(float)
        A = spa.vstack([A, spa.eye(n)]).tocsc()
        u = np.append(m['ru'].T.flatten().astype(float),
                      m['ub'].T.flatten().astype(float))
        l = np.append(m['rl'].T.flatten().astype(float),
                      m['lb'].T.flatten().astype(float))

        return P, q, A, l, u

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
        problem['A'] = self.A
        problem['l'] = self.l
        problem['u'] = self.u
        problem['m'] = self.m
        problem['n'] = self.n

        return problem

    def _generate_cvxpy_problem(self):
        '''
        Generate QP problem
        '''
        x_var = cvxpy.Variable(self.n)
        objective = .5 * cvxpy.quad_form(x_var, self.P) + self.q * x_var
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
        x = variables[0].value.A1

        # dual solution
        y = constraints[0].dual_value.A1 - constraints[1].dual_value.A1

        return x, y
