
"""
------------------------------------------------------------------------------
Script to analyze the disassembly of RISC-V and ARM-compiled benchmarks.
    - Compare code size results of all compilations
    - Identify 32-bit RISC-V instructions which could be replaced by 16-bit
        instructions
    - Approx. potential RISC-V code size reduction
------------------------------------------------------------------------------

@file   main.py
@author Jennifer Hellar <jennifer.hellar [at] rice.edu>
@date   10/01/2021

@brief Analyzes RISC-V code size.

------------------------------------------------------------------------------
Software Setup:

    * Install Python 3
    * pip3 install XlsxWriter
    * In same directory:
        * constants.py: Contains constants used by all scripts
        * parser.py: Normal class parser for RVA-compiled builds (or IAR)
        * summary_xlsx.py: Handles formatting/writing to the Summary worksheet
        * function_xlsx.py: Handles formatting/writing to function worksheets
        * save_restore_xlsx.py: Handles writing to __riscv_save/__riscv_restore
            worksheets
        * excel: Helper functions for summary_xlsx.py and function_xlsx.py
        * cx.py: Helper functions for instruction replacement

------------------------------------------------------------------------------
Software Execution:
    * Select desired options in constants.py
    * Execute on the command line:

usage: main.py [-h] rvgcc-file [output-file]

positional arguments:
  rvgcc-file   filename of rvgcc disassembly
  output-file  (optional) filename for the output excel file

optional arguments:
  -h, --help   show this help message and exit

"""
# Built-in libraries to handle command line inputs/outputs/execution results
import argparse
import os
import traceback
import re

# Built-in library to create/write to Excel file
import xlsxwriter

# Supplementary python scripts
import summary_xlsx
import save_restore_xlsx
import function_xlsx
import cx
import excel
import arm
import riscv
import analyze
import config
from constants import *

""" Command Line Inputs """

# Definition of expected command line inputs
parser = argparse.ArgumentParser(description='PyRho, A Code Density Analyzer')
parser.add_argument('benchmark', help='path to benchmark(s)')
parser.add_argument('-c', '--configure', nargs='?', const=True, default=False,
                    help='')
parser.add_argument('-a', '--all', nargs='?', const=True, default=False,
                    help='')
parser.add_argument('--arm', default='armcc', required=False, help='desired Arm build')
parser.add_argument('--riscv', default='rvgcc', required=False, help='desired RISC-V build')
parser.add_argument('-o', '--outfile', nargs='?', const=None, default=None,
                    help='(optional) filename for the output excel file')

# Capture command line inputs
args = parser.parse_args()
benchmarkpath = vars(args)['benchmark']
configureflag = vars(args)['configure']
allflag = vars(args)['all']
armbuild = vars(args)['arm']
rvbuild = vars(args)['riscv']
output_file = vars(args)['outfile']

""" Main Code """
failure = False
try:
    if configureflag:
        config.create_configurations(benchmarkpath)
        print('\nNew function selection files created for all benchmarks. Please review and select function(s) to parse.')
        exit(0)
    elif allflag:
        analyze.all_benchmarks(armbuild, rvbuild, benchmarkpath, output_file)
    else:
        analyze.single_benchmark(armbuild, rvbuild, benchmarkpath, output_file)
except Exception:
    failure = True
    print('\n\n')
    traceback.print_exc()
    print('\n\n')
finally:
    if (failure):
        print('Incomplete! See error or try again.')
