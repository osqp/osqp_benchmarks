# Benchmark examples for the OSQP solver

These are the scripts to compare the following Quadratic Program (QP) solvers

-   OSQP
-   GUROBI
-   MOSEK
-   ECOS (through CVXPY)
-   qpOASES

The detailed description of these tests is available in [this paper](https://arxiv.org/pdf/1711.08013.pdf).
To run these scripts you need `pandas` and `cvxpy` installed.

All the scripts (apart from the parametric examples) come with options (default to `False`)

- `--parallel` for parallel execution across instances
- `--verbose` for verbose solvers output (they  can be slower than necessary while printing)
- `--high_accuracy` for high accuracy `eps=1e-05` solver settings + optimality checks (default is `eps=1e-03`)


## Benchmark problems
The problems are all randomly generated as described in the OSQP paper.
They produce a benchmark library of `1400` problems with nonzeros ranging from `100` to `10'000'000`.
Problem instances include

-   Random QP
-   Equality constrained QP
-   Portfolio
-   Lasso
-   Huber fitting
-   Constrained optimal control

We generate the problems using the scripts in the `problem_classes` folder.

To execute these tests run
```python
python run_benchmark_problems.py
```

### Results
The resulting [shifted geometric means](http://plato.asu.edu/ftp/shgeom.html) are

| OSQP | GUROBI            | MOSEK           | ECOS               | qpOASES            |
| ---- | ----------------- | --------------- | ------------------ | ------------------ |
| 1.0  | 4.284628797377856 | 2.5222928639855 | 28.846675051894692 | 149.93199918447826 |


## Maros Meszaros problems
These are the hard problems from the [Maros Meszaros testset](http://www.cuter.rl.ac.uk/Problems/marmes.shtml) converted using [CUTEst](https://ccpforge.cse.rl.ac.uk/gf/project/cutest/wiki) and the scripts in the [maros_meszaros_data/](./problem_classes/maros_meszaros_data) folder.
In these benchmarks we compare OSQP with GUROBI and MOSEK.

To execute these tests run
```python
python run_maros_meszaros_problems.py
```

### Results
The resulting [shifted geometric means](http://plato.asu.edu/ftp/shgeom.html) are

| OSQP               | GUROBI | MOSEK             |
| ------------------ | ------ | ----------------- |
| 1.4644901303505107 | 1.0    | 6.121401985319734 |


## SuiteSparse Matrix Lasso and Huber Fitting problems
These are Lasso and Huber fitting problems generated from Least-Squares linear systems `Ax ~ b` from the [SuiteSparse Matrix Collection](https://sparse.tamu.edu/). They are downloaded and converted to mat using the [download.jl](./problem_classes/suitesparse_matrix_collection/download.jl) script. They are a total of 60 problems (30 Lasso and 30 Huber fitting).

To execute these tests run
```python
python run_suitesparse_problems.py
```

### Results
The resulting [shifted geometric means](http://plato.asu.edu/ftp/shgeom.html) are

| OSQP | GUROBI             | MOSEK              |
| ---- | ------------------ | ------------------ |
| 1.0  | 1.6298594688779335 | 1.7453455598793246 |

## Parametric problems
These tests apply only to the OSQP solver with and without warm-starting for three parametric examples of
-   Portfolio
-   Lasso
-   Constrained optimal control (MPC)

The problem construction is the same as for the same categories in the **Benchmark Problems**.

To execute these tests run
```python
python run_parametric_problems.py
```

## Citing

If you are using these benchmarks for your work, please cite the [OSQP paper](https://osqp.org/citing/).
