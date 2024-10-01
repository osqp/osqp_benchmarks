class Results(object):
    '''
    Results class from QP solution
    '''
    def __init__(self, status, obj_val, x, y, run_time, niter, dual_obj_val=None, duality_gap=None, restarts=None):
        self.status = status
        self.obj_val = obj_val
        self.x = x
        self.y = y
        self.run_time = run_time
        self.niter = niter
        self.dual_obj_val = dual_obj_val
        self.duality_gap = duality_gap
        self.restarts = restarts
