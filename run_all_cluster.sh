#!/bin/bash

echo -n "Benchmark, parallel, low accuracy: "
sbatch run_cluster.sh run_benchmark_problems.py --parallel

echo -n "Benchmark, parallel, high accuracy: "
sbatch run_cluster.sh run_benchmark_problems.py --parallel --high_accuracy

echo -n "Maros Meszaros, parallel, low accuracy: "
sbatch run_cluster.sh run_maros_meszaros_problems.py --parallel

echo -n "Maros Meszaros, parallel, high accuracy: "
sbatch run_cluster.sh run_maros_meszaros_problems.py --parallel --high_accuracy

echo -n "Suitesparse, serial, low accuracy: "
sbatch run_cluster.sh run_suitesparse_problems.py

echo -n "Suitesparse, serial, high accuracy: "
sbatch run_cluster.sh run_suitesparse_problems.py --high_accuracy

# echo -n "QPLIB, serial, low accuracy: "
# sbatch run_cluster.sh run_qplib_problems.py
#
# echo -n "QPLIB, serial, high accuracy: "
# sbatch run_cluster.sh run_qplib_problems.py --high_accuracy


