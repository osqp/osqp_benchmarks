import numpy as np
import numpy.linalg as la
import solvers.solvers as s
import errno
import os

import sys
from contextlib import contextmanager


@contextmanager
def stdout_redirected(to=os.devnull):
    """
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    """
    fd = sys.stdout.fileno()

    # assert that Python and C stdio write using the same file descriptor
    # assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

    def _redirect_stdout(to):
        sys.stdout.close()  # + implicit flush()
        os.dup2(to.fileno(), fd)  # fd writes to 'to' file
        sys.stdout = os.fdopen(fd, "w")  # Python writes to fd

    with os.fdopen(os.dup(fd), "w") as old_stdout:
        with open(to, "w") as file:
            _redirect_stdout(to=file)
        try:
            yield  # allow code to be run with the redirected stdout
        finally:
            # restore stdout.
            # buffering and flags such as
            # CLOEXEC may be different
            _redirect_stdout(to=old_stdout)


# Function to create directories
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        # Catch exception if directory created in between
        if exception.errno != errno.EEXIST:
            raise


def gen_int_log_space(min_val, limit, n):
    result = [1]
    if n > 1:  # just a check to avoid ZeroDivisionError
        ratio = (float(limit) / result[-1]) ** (1.0 / (n - len(result)))
    while len(result) < n:
        next_value = result[-1] * ratio
        if next_value - result[-1] >= 1:
            # safe zone. next_value will be a different integer
            result.append(next_value)
        else:
            # problem! same integer. we need to find next_value
            # by artificially incrementing previous value
            result.append(result[-1] + 1)
            # recalculate the ratio so that the remaining values will scale
            # correctly
            ratio = (float(limit) / result[-1]) ** (1.0 / (n - len(result)))
    # round, re-adjust to 0 indexing (i.e. minus 1) and return np.uint64 array
    return np.array(list(map(lambda x: round(x) - 1 + min_val, result)), dtype=int)


def is_qp_solution_optimal(qp_problem, x, y, high_accuracy=False):
    """
    Check optimality condition of the QP given the
    primal-dual solution (x, y) and the tolerance eps
    """
    if high_accuracy:
        eps_abs = s.eps_high
        eps_rel = s.eps_high
    else:
        eps_abs = s.eps_low
        eps_rel = s.eps_low

    # Get problem matrices
    P = qp_problem["P"]
    q = qp_problem["q"]
    A = qp_problem["A"]
    l = qp_problem["l"]
    u = qp_problem["u"]

    # Set infinity values (1e20)
    l[l > +9e19] = +np.inf
    u[u > +9e19] = +np.inf
    l[l < -9e19] = -np.inf
    u[u < -9e19] = -np.inf

    # Check primal feasibility
    Ax = A.dot(x)
    eps_pri = eps_abs + eps_rel * la.norm(Ax, np.inf)
    pri_res = np.minimum(Ax - l, 0) + np.maximum(Ax - u, 0)

    if la.norm(pri_res, np.inf) > eps_pri:
        print(
            "Error in primal residual: %.4e > %.4e"
            % (la.norm(pri_res, np.inf), eps_pri)
        )
        return False

    # Check dual feasibility
    Px = P.dot(x)
    Aty = A.T.dot(y)
    eps_dua = eps_abs + eps_rel * np.max(
        [la.norm(Px, np.inf), la.norm(q, np.inf), la.norm(Aty, np.inf)]
    )
    dua_res = Px + q + Aty

    if la.norm(dua_res, np.inf) > eps_dua:
        print(
            "Error in dual residual: %.4e > %.4e" % (la.norm(dua_res, np.inf), eps_dua)
        )
        return False

    # Check duality gap
    # Find index of infinity values in u and l
    u_inf = np.isinf(u)
    l_inf = np.isinf(l)

    # select non infinity values in u and l and y
    u_notinf = u[~u_inf]
    l_notinf = l[~l_inf]
    y_notinf_u = y[~u_inf]
    y_notinf_l = y[~l_inf]

    y_plus = np.maximum(y_notinf_u, 0)
    y_minus = np.minimum(y_notinf_l, 0)

    supp_func = u_notinf.dot(y_plus) + l_notinf.dot(y_minus)
    xPx = x.dot(Px)
    qx = q.dot(x)
    dua_gap = np.abs(xPx + qx + supp_func)
    eps_dua_gap = eps_abs + eps_rel * np.max(
        [np.abs(xPx), np.abs(qx), np.abs(supp_func)]
    )

    if dua_gap > eps_dua_gap:
        print("Error in duality gap residual: %.4e > %.4e" % (dua_gap, eps_dua_gap))
        return False

    # If we arrived until here, the solution is optimal
    return True
