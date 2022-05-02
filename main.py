
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
from constants import *

""" Command Line Inputs """

# Definition of expected command line inputs
parser = argparse.ArgumentParser(description='PyRho, A Code Density Analyzer')
parser.add_argument('--arm', required=True, help='desired Arm build')
parser.add_argument('--riscv', required=True, help='desired RISC-V build')
parser.add_argument('benchmark', help='path to benchmark')
parser.add_argument('-o', '--outfile', nargs='?', const=None, default=None,
                    help='(optional) filename for the output excel file')

# Capture command line inputs
args = parser.parse_args()
args_dir = vars(args)
armbuild = args_dir['arm']
rvbuild = args_dir['riscv']
benchmarkpath = args_dir['benchmark']
output_file = args_dir['outfile']

# Extract compilation source and benchmark name
if benchmarkpath[-1] != '/':
    benchmarkpath += '/'
lin_split = re.split('/', benchmarkpath[::-1], maxsplit=2)
src = lin_split[-1][::-1]
benchmark = lin_split[-2][::-1]

# Check the inputs
# if (src not in '\t'.join(SOURCES)):
if not any(substring in src for substring in SOURCES):
    print('Unknown compilation source: ', src)
    exit()
if (benchmark not in BENCHMARKS):
    print('Unknown benchmark: ', benchmark)
    exit()
# if filename[:5] != 'rvgcc' and filename[-15:] != 'disassembly.txt':
#     print('Incorrect input file type.' +
#           'Expected file beginning in \'rvgcc\'' +
#           'and ending in \'disassembly.txt\'')
#     exit()
files = os.listdir(benchmarkpath)
files = [i for i in files if i.find('disassembly') != -1]

rvfiles = [i for i in files if i[:i.index('_')].find('rv') != -1]
armfiles = [i for i in files if i[:i.index('_')].find('arm') != -1]

rvbuilds = [i[:i.index('_')] for i in rvfiles]
armbuilds = [i[:i.index('_')] for i in armfiles]

if rvbuild not in rvbuilds:
    print('\nRISC-V disassembly for \'' + rvbuild + '\' unavailable. Please compile or choose from:')
    print('\t', rvbuilds, '\n')
    exit()
if armbuild not in armbuilds:
    print('\nARM disassembly for \'' + armbuild + '\' unavailable. Please compile or choose from:')
    print('\t', armbuilds, '\n')
    exit()

rvfile = os.path.join(benchmarkpath, rvbuild + '_' + benchmark + '_disassembly.txt')
armfile = os.path.join(benchmarkpath, armbuild + '_' + benchmark + '_disassembly.txt')
if (os.path.exists(rvfile) is False):
    print('\nUnable to find expected RISC-V disassembly:\n\t', rvfile, '\n')
    exit()
if (os.path.exists(armfile) is False):
    print('\nUnable to find expected ARM disassembly:\n\t', armfile, '\n')
    exit()

""" Excel Workbook Creation """

# Default to same directory as input
outdir = os.path.join(os.getcwd(), 'results')
if not os.path.isdir(outdir):
    os.makedirs(outdir)
if output_file is None:
	output_file = benchmark + '_analysis.xlsx'
if output_file[-5:] != '.xlsx':
    output_file += '.xlsx'
output_file = os.path.join(outdir, output_file)
excel.create_workbook(output_file)


""" Main Code """

failure = False
try:
    # Create Summary worksheet; write input files to A1, A2; set column sizes
    # Do this first so that it shows up as the first sheet in the workbook
    sum_wksheet = summary_xlsx.create_summary(rvfile, armfile)

    # Use an empty worksheet to calculate the pie segments for radar plots
    tmp_wksheet = excel.wkbook.add_worksheet('tmp')
    segments = [0] * len(RV32_FORMATS)
    for instr in RV32_INSTR_FORMATS.keys():
        lbl = RV32_INSTR_FORMATS[instr][0]
        if lbl in RV32_FORMATS:
            idx = RV32_FORMATS.index(lbl)
            segments[idx] += 1
    data = [RV32_FORMATS, segments]
    tmp_wksheet.write_column('A1', data[0])
    tmp_wksheet.write_column('B1', data[1])

    # Create the __riscv_save and __riscv_restore worksheets
    save_wksheet = save_restore_xlsx.create_sheet('__riscv_save')
    restore_wksheet = save_restore_xlsx.create_sheet('__riscv_restore')

    # Parse the input files
    res = riscv.scan_riscv_file(rvbuild, benchmark, rvfile)
    (gcc_results, gcc_reductions, gcc_pairs, gcc_instr, gcc_formats) = res

    # for instr in sorted(gcc_instr.keys()):
    #     print("{:<30}{:<30}".format(instr, gcc_instr[instr]))

    arm_results = arm.scan_arm_file(armbuild, benchmark, armfile)

    # if (IAR is True):
    #     parse_rules.compiler = 'IAR'
    #     res = scan_riscv_file('IAR')
    #     (iar_results, iar_reductions, iar_pairs, iar_instr, iar_formats) = res

        # for instr in sorted(iar_instr.keys()):
        #     print("{:<30}{:<30}".format(instr, iar_instr[instr]))

    # Add the main table to record individual function totals
    row = 18
    col = 1
    summary_xlsx.add_main_table(row, col, rvbuild, armbuild)

    # Add the totals table to record overall benchmark totals
    row = 3
    col = 1
    summary_xlsx.add_totals_table(row, col, rvbuild, armbuild)

    # Write out the results to the Summary worksheet
    summary_xlsx.record_rvgcc_data(gcc_results, gcc_reductions, rvbuild)
    summary_xlsx.record_arm_data(gcc_results, arm_results, rvbuild, armbuild)
    # if (IAR is True):
    #     summary_xlsx.record_iar_data(gcc_results, iar_results)

    # Record replaced instruction performance
    reductions = [gcc_reductions]
    if (IAR is True):
        reductions.append(iar_reductions)
    summary_xlsx.add_replaced_instr_table(reductions, rvbuild, armbuild)

    # Add a chart to visualize the replaced instruction performance
    compilers = [rvbuild]
    # if (IAR is True):
    #     compilers.append('IAR')
    summary_xlsx.add_replaced_instr_chart(compilers)

    # Record the rules used to implement new replaced instructions
    summary_xlsx.add_replacement_rules_table()

    # Record the frequency of instructions
    summary_xlsx.add_total_instr_table(gcc_instr, 20, rvbuild)
    # if (IAR is True):
    #     summary_xlsx.add_total_instr_table(iar_instr, 20, 'IAR')

    # Record the frequency of instruction pairs
    summary_xlsx.add_pairs_table(gcc_pairs, 20, rvbuild, armbuild)
    # if (IAR is True):
    #     summary_xlsx.add_pairs_table(iar_pairs, 20, 'IAR')

    # Record the frequency of instruction formats to 'tmp' worksheet
    formats = [gcc_formats]
    # if (IAR is True):
    #     formats.append(iar_formats)
    summary_xlsx.add_instr_formats_tables(formats, compilers)

    # Add a chart to visualize the instruction format frequency distribution
    summary_xlsx.add_instr_formats_radar(rvbuild)
    # if (IAR is True):
    #     summary_xlsx.add_instr_formats_radar('IAR')

    # Record function contribution to overshooting ARM code size
    summary_xlsx.add_overshoot_table(gcc_results, arm_results, 5, rvbuild)
    # if (IAR is True):
    #     summary_xlsx.add_overshoot_table(iar_results, arm_results, 5, 'IAR')

    # Add a chart to visualize the function overshoot over ARM code size
    summary_xlsx.add_overshoot_chart(rvbuild)
    # if (IAR is True):
    #     summary_xlsx.add_overshoot_chart('IAR')


except Exception:
    failure = True
    print('\n\n')
    traceback.print_exc()
    print('\n\n')


finally:
    excel.close_workbook()
    if (failure):
        print('Incomplete! See error or try again.')
    else:
        if not os.path.isdir('results'):
            os.makedirs('results')
        os.system("cp " + output_file + " results/.")
        print('\nComplete! See Excel workbook: ')
        print('\t' + output_file)
        print('\t' + 'results/' + benchmark + '_analysis.xlsx')
        # os.system("open " + output_file)
