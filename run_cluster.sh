#!/bin/zsh
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 16
#SBATCH --partition=normal
#SBATCH -o /home/gridsan/stellato/results/osqp/results_%j.txt
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=bartolomeo.stellato@gmail.com

HDF5_USE_FILE_LOCKING=FALSE python -u $1 ${@:2}
