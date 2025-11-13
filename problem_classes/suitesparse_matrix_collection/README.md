# SuiteSparse Matrix Collection Problems

This folder contains scripts to download least squares problems from the SuiteSparse Matrix Collection.

## Downloading the Problems

To download the problems, follow these steps:

1. Navigate to this directory:
   ```bash
   cd problem_classes/suitesparse_matrix_collection
   ```

2. Open Julia:
   ```bash
   julia
   ```

3. Activate the project environment:
   ```julia
   using Pkg
   Pkg.activate(".")
   ```

4. Install dependencies (first time only):
   ```julia
   Pkg.instantiate()
   ```

5. Run the download script:
   ```julia
   include("download.jl")
   ```

The script will download and process problems from the SuiteSparse Matrix Collection, filtering for least squares problems. The total number of problems should be **26**.

Each problem is saved as a `.mat` file containing the matrix `A` and vector `b`.
