#!/bin/zsh
#SBATCH -n 12
#SBATCH -N 1
#SBATCH -c 1
#SBATCH --partition=normal
#SBATCH -o /home/gridsan/stellato/results/osqp/results_%j.txt
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=bartolomeo.stellato@gmail.com

# Activate environment
conda activate osqp

# Run script
python -u $1
