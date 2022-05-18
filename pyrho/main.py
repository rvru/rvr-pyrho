
"""
------------------------------------------------------------------------------
Script to analyze the disassembly of RISC-V and ARM-compiled benchmarks.
    - Compare code size results of all compilations
    - Identify 32-bit RISC-V instructions which could be replaced by 16-bit
        instructions
    - Approx. potential RISC-V code size reduction
------------------------------------------------------------------------------

@file   main.py
@author Jennifer Hellar
@date   05/18/2022

@brief Analyzes RISC-V code size.

------------------------------------------------------------------------------
Software Execution:
    * Select desired options in constants.py
    * Create the default configuration files for all benchmarks (see below)
        * Edit these files to select desired functions to analyze for code size
    * Execute on the command line:

usage: main.py [-h] [-c] [-a] [--armbuild ARMBUILD] [--rvbuild RVBUILD]
               [-o OUTFILE]
               benchmark

PyRho, A Code Density Analyzer

positional arguments:
  benchmark             path to benchmark(s)

optional arguments:
  -h, --help            show this help message and exit
  -c, --configure       create the default configuration files for function
                        selection per benchmark
  -a, --all             analyze all supported benchmarks
  --armbuild ARMBUILD   (optional, default: armcc) input the desired Arm build
                        for individual or baseline analysis
  --rvbuild RVBUILD     (optional, default: rvgcc) input the desired RISC-V
                        build for individual or baseline analysis
  -o OUTFILE, --outfile OUTFILE
                        (optional) filename for the output excel file

"""
# Built-in libraries to handle command line inputs/outputs/execution results
import argparse
import os
import traceback
import re

# Supplementary python scripts
import analyze
import config
from constants import *

""" Command Line Inputs """

# Definition of expected command line inputs
parser = argparse.ArgumentParser(description='PyRho, A Code Density Analyzer')
parser.add_argument('benchmark', help='path to benchmark(s)')
parser.add_argument('-c', '--configure', action='store_true', default=False,
                    help='create the default configuration files for function selection per benchmark')
parser.add_argument('-a', '--all', action='store_true', default=False,
                    help='analyze all supported benchmarks')
parser.add_argument('--armbuild', default='armcc', required=False, help='(optional, default: armcc) input the desired Arm build for individual or baseline analysis')
parser.add_argument('--rvbuild', default='rvgcc', required=False, help='(optional, default: rvgcc) input the desired RISC-V build for individual or baseline analysis')
parser.add_argument('-o', '--outfile', required=False, default=None,
                    help='(optional) filename for the output excel file')

# Capture command line inputs
args = parser.parse_args()
benchmarkpath = vars(args)['benchmark']
configureflag = vars(args)['configure']
allflag = vars(args)['all']
armbuild = vars(args)['armbuild']
rvbuild = vars(args)['rvbuild']
output_file = vars(args)['outfile']

""" Main Code """
failure = False
try:
    if configureflag:
        # create default configuration files for all benchmarks
        # user MUST edit these to enable function(s) for code size analysis
        config.create_configurations(benchmarkpath)
        print('\nNew function selection files created for all benchmarks. Please review and select function(s) to parse.')
        exit(0)
    else:
        # create the results directory if it does not already exist
        outdir = os.path.join(os.getcwd(), 'results')
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        # create the config directory within the results dir also
        configdir = os.path.join(os.getcwd(), outdir, 'config')
        if not os.path.isdir(configdir):
            os.makedirs(configdir)

        if allflag:
            # if analyzing all benchmarks, get a list (all subdirs of benchmarkpath)
            filedirs = os.listdir(benchmarkpath)
            benchmarks = [f for f in filedirs if os.path.isdir(os.path.join(benchmarkpath, f))]
            benchmarks.sort()
            # check if any benchmarks are missing configuration files
            configmissing = []
            for benchmark in benchmarks:
                masteropt = os.path.join(configdir, benchmark + '_master_selection.txt')
                if not os.path.exists(masteropt):
                    configmissing.append(benchmark)
            # if so, create the missing ones and prompt the user to edit them
            if len(configmissing) > 0:
                for benchmark in configmissing:
                    config.create_configuration(os.path.join(benchmarkpath, benchmark))
                print('\nNew function selection file(s) created for [' + ','.join(configmissing) + ']. Please review and select function(s) to parse.')
                exit(0)
            # otherwise, analyze all and create the summary workbook
            analyze.all_benchmarks(armbuild, rvbuild, benchmarkpath, output_file)
            # also, analyze each individually
            for benchmark in benchmarks:
                pth = os.path.join(benchmarkpath, benchmark)
                analyze.single_benchmark(armbuild, rvbuild, pth, None)
        else:
            # for a single benchmark...
            # Extract benchmark name
            if benchmarkpath[-1] != '/':
                benchmarkpath += '/'
            lin_split = re.split('/', benchmarkpath[::-1], maxsplit=2)
            benchmark = lin_split[-2][::-1]
            # check if the configuration file exists
            masteropt = os.path.join(configdir, benchmark + '_master_selection.txt')
            # if not, create it and prompt the user to edit
            if not os.path.exists(masteropt):
                config.create_configuration(benchmarkpath)
                print('\nNew function selection file created for ' + benchmark + '. Please review and select function(s) to parse.')
                exit(0)
            # otherwise, analyze the benchmark
            analyze.single_benchmark(armbuild, rvbuild, benchmarkpath, output_file)

except Exception:
    failure = True
    print('\n\n')
    traceback.print_exc()
    print('\n\n')

finally:
    if (failure):
        print('Incomplete! See error or try again.')
