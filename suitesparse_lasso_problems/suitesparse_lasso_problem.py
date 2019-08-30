import os
from multiprocessing import Pool, cpu_count
from itertools import repeat
import pandas as pd

from solvers.solvers import SOLVER_MAP
from problem_classes.suitesparse_lasso import SuitesparseLasso
from utils.general import make_sure_path_exists

import numpy as np

PROBLEMS_FOLDER = "suitesparse_matrix_collection"


class SuitesparseLassoRunner(object):
    '''
    Examples runner
    '''
    def __init__(self,
                 solvers,
                 settings,
                 output_folder):
        self.solvers = solvers
        self.settings = settings
        self.output_folder = output_folder

        # Get problems list
        problems_dir = os.path.join(".", "problem_classes", PROBLEMS_FOLDER)
        # List of problems in .mat format
        lst_probs = [f for f in os.listdir(problems_dir) if \
            f.endswith('.mat')]
        self.problems = [f[:-4] for f in lst_probs]   # List of problem names


    def solve(self, parallel=True, cores=32):
        '''
        Solve problems of type example

        The results are stored as

            ./results/{self.output_folder}/{solver}/results.csv

        using a pandas table with fields
            - 'name': problem name
            - 'solver': solver name
            - 'status': solver status
            - 'run_time': execution time
            - 'iter': number of iterations
            - 'obj_val': objective value from solver
            - 'obj_opt': optimal objective value
            - 'n': leading dimension
            - 'N': nnz dimension (nnz(P) + nnz(A))
        '''

        print("Solving Suitesparse Lasso problems")
        print("----------------------------------")

        if parallel:
            pool = Pool(processes=min(cores, cpu_count()))

        # Iterate over all solvers
        for solver in self.solvers:
            settings = self.settings[solver]

            #  # Initialize solver results
            #  results_solver = []

            # Solution directory
            path = os.path.join('.', 'results', self.output_folder,
                                solver)

            # Create directory for the results
            make_sure_path_exists(path)

            # Get solver file name
            results_file_name = os.path.join(path, 'results.csv')

            # Check if file name already exists
            if not os.path.isfile(results_file_name):
                # Solve  problems
                if parallel:
                    results = pool.starmap(self.solve_single_example,
                                           zip(self.problems,
                                               repeat(solver),
                                               repeat(settings)))
                else:
                    results = []
                    for problem in self.problems:
                        results.append(self.solve_single_example(problem,
                                                                 solver,
                                                                 settings))
                # Create dataframe
                df = pd.concat(results)

                # Store results
                df.to_csv(results_file_name, index=False)

            #  else:
            #      # Load from file
            #      df = pd.read_csv(results_file_name)
            #
            #      # Combine list of dataframes
            #      results_solver.append(df)

        if parallel:
            pool.close()  # Not accepting any more jobs on this pool
            pool.join()   # Wait for all processes to finish

    def solve_single_example(self,
                             problem,
                             solver, settings):
        '''
        Solve Suitesparse Lasso 'problem' with 'solver'

        Args:
            dimension: problem leading dimension
            instance_number: number of the instance
            solver: solver name
            settings: settings dictionary for the solver

        '''
        # Create example instance
        full_name = os.path.join(".", "problem_classes",
                                 PROBLEMS_FOLDER, problem)
        instance = SuitesparseLasso(full_name)

        print(" - Solving %s with solver %s" % (problem, solver))

        # Solve problem
        s = SOLVER_MAP[solver](settings)
        results = s.solve(instance)

        # Create solution as pandas table
        P = instance.qp_problem['P']
        A = instance.qp_problem['A']
        N = P.nnz + A.nnz

        solution_dict = {'name': [problem],
                         'solver': [solver],
                         'status': [results.status],
                         'run_time': [results.run_time],
                         'iter': [results.niter],
                         'obj_val': [results.obj_val],
                         'n': [instance.qp_problem["n"]],
                         'm': [instance.qp_problem["m"]],
                         'N': [N]}

        # Add status polish if OSQP
        if solver[:4] == 'OSQP':
            solution_dict['status_polish'] = results.status_polish
            solution_dict['setup_time'] = results.setup_time
            solution_dict['solve_time'] = results.solve_time
            solution_dict['update_time'] = results.update_time

        print(" - Solved %s with solver %s" % (problem, solver))

        # Return solution
        return pd.DataFrame(solution_dict)
