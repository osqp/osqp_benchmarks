import linecache
import pandas as pd
import numpy as np
import scipy.sparse as spa
import scipy.io as spio
import cvxpy


class QPLIB(object):
    '''
    QPLIB
    '''
    def __init__(self, file_name, create_cvxpy_problem=False):
        '''
        Generate Maros problem in QP format and CVXPY format

        NB. By default, the CVXPY problem is not created
        '''
        # Load problem from file
        self._load_qplib_problem(file_name)

        self.qp_problem = self._generate_qp_problem()

        if create_cvxpy_problem:
            self.cvxpy_problem = self._generate_cvxpy_problem()

    def _load_qplib_problem(self, filename, verbose=False):
        # minimize or maximize
        head = 3                                    # 3
        line = linecache.getline(filename, head)
        if 'minimize' in line:
            obj_type = 'min'
        else:
            obj_type = 'max'

        # number of variables
        head += 1                                   # 4
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        if 'variables\n' in parts:
            n = int(parts[0])
            if verbose:
                print(line)
        else:
            raise ValueError("No number of variables recognized")

        # number of constraints
        head += 1                                   # 5
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        if 'constraints\n' in parts:
            m = int(parts[0])
            if verbose:
                print(line)
        else:
            m = 0  # No constraints
            head -= 1

        # nnz in Ptriu
        head += 1                                   # 6
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        if ('quadratic' in parts) and ('objective\n' in parts):
            nnz_Ptriu = int(parts[0])
            if verbose:
                print(line)
        else:
            nnz_Ptriu = 0
            head -= 1

        # Extract upper triangular part of P
        head += 1                                   # 7
        if (nnz_Ptriu > 0):
            P_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=nnz_Ptriu, header=None)

            # Replace the order of rows and columns since QPLIB stores P as a lower triangular matrix
            P = spa.csc_matrix((P_df[2].values, (P_df[1].values-1, P_df[0].values-1)), shape=(n, n))
            P = (P + spa.triu(P, 1).T).tocsc()
        else:
            P = spa.csc_matrix((n, n))

        # Default value of q
        head += nnz_Ptriu
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        q_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for q
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        q_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract q
        head += 1
        q = q_dflt * np.ones(n)
        if (q_non_dflt_numel > 0):
            q_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=q_non_dflt_numel, header=None)
            q[q_df[0] - 1] = q_df[1]

        # Objective constant
        head += q_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        r = float(parts[0])
        if verbose:
            print(line)

        # Extract constraints only if present
        if m > 0:
            # nnz in A
            head += 1
            line = linecache.getline(filename, head)
            parts = line.split(' ')
            nnz_A = int(parts[0])
            if verbose:
                print(line)

            # Extract A
            head += 1
            if (nnz_A > 0):
                A_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=nnz_A, header=None)
                A = spa.csc_matrix((A_df[2].values, (A_df[0].values-1, A_df[1].values-1)), shape=(m, n))
            else:
                A = None
        else:
            head += 1
            nnz_A = 0
            A = spa.csc_matrix((0, n))

        # Value for infinity
        head += nnz_A
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        infty = float(parts[0])
        if verbose:
            print(line)

        # Extract constraints if present
        if m > 0:
            # Default value of l
            head += 1
            line = linecache.getline(filename, head)
            parts = line.split(' ')
            l_dflt = float(parts[0])
            if verbose:
                print(line)

            # Number of non-default values for l
            head += 1
            line = linecache.getline(filename, head)
            parts = line.split(' ')
            l_non_dflt_numel = int(parts[0])
            if verbose:
                print(line)

            # Extract l
            head += 1
            l = l_dflt * np.ones(m)
            if (l_non_dflt_numel > 0):
                l_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=l_non_dflt_numel, header=None)
                l[l_df[0] - 1] = l_df[1]

            # Default values for u
            head += l_non_dflt_numel
            line = linecache.getline(filename, head)
            parts = line.split(' ')
            u_dflt = float(parts[0])
            if verbose:
                print(line)

            # Number of non-default values for u
            head += 1
            line = linecache.getline(filename, head)
            parts = line.split(' ')
            u_non_dflt_numel = int(parts[0])
            if verbose:
                print(line)

            # Extract u
            head += 1
            u = u_dflt * np.ones(m)
            if (u_non_dflt_numel > 0):
                u_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=u_non_dflt_numel, header=None)
                u[u_df[0] - 1] = u_df[1]
        else:
            head += 1
            l = np.array([])
            u = np.array([])
            u_non_dflt_numel = 0  # To continue processing

        # Default value of lx
        head += u_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        lx_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for lx
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        lx_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract lx
        head += 1
        lx = lx_dflt * np.ones(n)
        if (lx_non_dflt_numel > 0):
            lx_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=lx_non_dflt_numel, header=None)
            lx[lx_df[0] - 1] = lx_df[1]

        # Default value of ux
        head += lx_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        ux_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for ux
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        ux_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract ux
        head += 1
        ux = ux_dflt * np.ones(n)
        if (ux_non_dflt_numel > 0):
            ux_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=ux_non_dflt_numel, header=None)
            ux[ux_df[0] - 1] = ux_df[1]


        # Default value of x0
        head += ux_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        x0_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for x0
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        x0_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract x0
        head += 1
        x0 = x0_dflt * np.ones(n)
        if (x0_non_dflt_numel > 0):
            x0_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=x0_non_dflt_numel, header=None)
            x0[x0_df[0] - 1] = x0_df[1]

        # Default value of y0
        head += x0_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        y0_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for y0
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        y0_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract y0
        head += 1
        y0 = y0_dflt * np.ones(m)
        if (y0_non_dflt_numel > 0):
            y0_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=y0_non_dflt_numel, header=None)
            y0[y0_df[0] - 1] = y0_df[1]

        # Default value of w0
        head += y0_non_dflt_numel
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        w0_dflt = float(parts[0])
        if verbose:
            print(line)

        # Number of non-default values for w0
        head += 1
        line = linecache.getline(filename, head)
        parts = line.split(' ')
        w0_non_dflt_numel = int(parts[0])
        if verbose:
            print(line)

        # Extract w0
        head += 1
        w0 = w0_dflt * np.ones(n)
        if (w0_non_dflt_numel > 0):
            w0_df = pd.read_csv(filename, sep=' ', skiprows=head-1, nrows=w0_non_dflt_numel, header=None)
            w0[w0_df[0] - 1] = w0_df[1]

        # Assign final values to problem
        self.n = n
        self.m = m + n  # Combine bounds in constraints
        self.A = spa.vstack([A, spa.eye(n)]).tocsc()
        self.l = np.hstack([l, lx])
        self.u = np.hstack([u, ux])
        self.P = P
        self.q = q
        self.r = r
        self.obj_type = obj_type
        if self.obj_type == 'max':
            self.P *= -1
            self.q *= -1
            self.r *= -1

    @staticmethod
    def name():
        return 'QPLIB'

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
        objective = .5 * cvxpy.quad_form(x_var, cvxpy.psd_wrap(self.P)) + self.q * x_var + \
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
