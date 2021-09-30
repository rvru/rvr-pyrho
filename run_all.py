"""

A quick and dirty script to run PyRho on all benchmarks in the
../rvr-hydra/benchmarks directory.

Author: Jennifer Hellar (jennifer.hellar@rice.edu)

"""

import os
import sys

from constants import BENCHMARKS

cwd = '../rvr-hydra/benchmarks'
# cwd = os.getcwd()
sub_directories = [x[0] for x in os.walk(cwd)]

cwd_parts = cwd.split('/')

for sub_path in sub_directories:
    # print(sub_path)
    sub_split = sub_path.split('/')
    if sub_split[len(sub_split) - 1] not in BENCHMARKS:
        continue

    benchmark_name = sub_split[len(sub_split) - 1]
    # print(benchmark_name)

    base_cmd = 'python3 main.py ../rvr-hydra/benchmarks/'
    filename = '/rvgcc_' + benchmark_name + '_disassembly.txt'

    print(base_cmd + benchmark_name + filename + '\n')
    os.system(base_cmd + benchmark_name + filename)
