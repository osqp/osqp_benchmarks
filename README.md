# Benchmark examples for the OSQP solver

These are the scripts to compare the OSQP solver to many other QP solvers.
At the moment the supported solvers are:

-   GUROBI
-   MOSEK
-   ECOS (through CVXPY)
-   qpOASES


To run these scripts you need `pandas` and `cvxpy` installed.

# Problems
The problems are all randomly generated as described in the OSQP paper.
They include
-   Random QP
-   Equality constrained QP
-   Portfolio
-   Lasso
-   Huber fitting
-   Constrained optimal control

We generate the problems using the scripts in the `problems/` folder.

# Scripts
The script `run_benchmark_problems.py` runs all the examples for the specified dimensions and reports the data of each solver in the folder `results/benchmark_problems/SOLVER_NAME/results.csv`.

The script `run_parametric_problems.py` runs the OSQP solver with and without warm-starting for three parametric examples of
-   Portfolio
-   Lasso
-   Constrained optimal control (MPC)

It prints the result of the speed improvements using warm-starting and factorization caching.
