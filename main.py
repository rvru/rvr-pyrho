
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
import importlib
import re

# Built-in library to create/write to Excel file
import xlsxwriter

# Supplementary python scripts
import summary_xlsx
import save_restore_xlsx
import function_xlsx
import cx
import excel
from constants import *

""" Command Line Inputs """

# Definition of expected command line inputs
parser = argparse.ArgumentParser(description='PyRho, A Code Density Analyzer')
parser.add_argument('rvgcc-file', help='filename of rvgcc disassembly')
parser.add_argument('output-file', nargs='?', const=None, default=None,
                    help='(optional) filename for the output excel file')

# Capture command line inputs
args = parser.parse_args()
args_dir = vars(args)
input_rvgcc = args_dir['rvgcc-file']
output_file = args_dir['output-file']

# Extract compilation source, benchmark name, and file name
lin_split = re.split('/', input_rvgcc[::-1], maxsplit=2)
src = lin_split[2][::-1]
benchmark = lin_split[1][::-1]
filename = lin_split[0][::-1]

# Check the inputs
# if (src not in '\t'.join(SOURCES)):
if not any(substring in src for substring in SOURCES):
    print('Unknown compilation source: ', src)
    exit()
if (benchmark not in BENCHMARKS):
    print('Unknown benchmark: ', benchmark)
    exit()
if filename[:5] != 'rvgcc' and filename[-15:] != 'disassembly.txt':
    print('Incorrect input file type.' +
          'Expected file beginning in \'rvgcc\'' +
          'and ending in \'disassembly.txt\'')
    exit()

# Find the corresponding arm file
path = input_rvgcc[:(input_rvgcc.rfind('/')+1)]
lin_split = re.split('_', filename)
input_arm = path + 'arm'
# input_arm = path + 'armclang'
for i in range(1, len(lin_split)):
    input_arm = input_arm + '_' + lin_split[i]
if (os.path.exists(input_arm) is False):
    print('Unable to find expected ARM disassembly: ', input_arm)
    exit()

# Find the corresponding IAR file
input_iar = path + 'iar'
for i in range(1, len(lin_split)):
    input_iar = input_iar + '_' + lin_split[i]
if (os.path.exists(input_iar) is False) and (IAR is True):
    print('Unable to find expected IAR disassembly: ', input_iar)
    exit()

# Import the appropriate parser class
if ('hydra' in src):
    txt_parser = 'parser'
ParseRules = getattr(importlib.import_module(txt_parser), 'ParseRules')

""" Excel Workbook Creation """

# Default to same directory as input
if output_file is None:
    output_file = input_rvgcc[:(input_rvgcc.rfind('/')+1)] + benchmark + \
        '_analysis.xlsx'
else:
    output_file = input_rvgcc[:(input_rvgcc.rfind('/')+1)] + output_file

excel.create_workbook(output_file)

parse_rules = ParseRules('RVGCC', benchmark)


def scan_arm_file():
    """
    Opens and scans the ARM disassembly file to extract data.

    Data:
        - arm_results
            * Key: function name
            * Val: function code size (in bytes)

    Returns: arm_results
    """
    data0 = 0
    data1 = 0
    data2 = 0
    data3 = 0
    data4 = 0
    data5 = 0
    data6 = 0
    data7 = 0
    data8 = 0
    data9 = 0
    data10 = 0
    data11 = 0
    data12 = 0
    data13 = 0

    compiler = 'ARM'

    arm_results = {}
    arm_instr = {}
    curr_state = S_INIT
    wksheet_name = None
    func_name = None
    last_flag = False

    f = open(input_arm)

    for line in f:
        if (curr_state == S_INIT):
            transition = parse_rules.is_first(line)
            if transition:
                end = parse_rules.is_last(line)
                if end:
                    last_flag = True
                curr_state = S_FUNC_START
            else:
                continue

        if (curr_state == S_WAIT):
            transition = parse_rules.is_func_start(line)
            if transition:
                end = parse_rules.is_last(line)
                if end:
                    last_flag = True
                curr_state = S_FUNC_START
            else:
                continue

        if (curr_state == S_FUNC_PARSE):
            transition = parse_rules.is_func_end(line)
            if transition:
                curr_state = S_FUNC_END
            else:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instr info from text and record in worksheet
                res = parse_rules.scan_arm_instruction(line)
                (addr, instr, bytes, opcode, args, comments) = res
                function_xlsx.record_instruction(wksheet, 'ARM', row, addr,
                                                 instr, opcode, args, comments)
                arm_results[func_name] += bytes
                row += 1

                if (opcode in arm_instr.keys()):
                    arm_instr[opcode][0] += 1
                    arm_instr[opcode][1].append(args)
                else:
                    arm_instr[opcode] = [1, [args]]

                # if (bytes > 2):
                #     data1 += 1
                # else:
                #     data0 += 1

                # if (opcode == 'ldr') and (line.find('pc') != -1):
                #     data0 += 1

                # if (opcode == 'push'):
                #     l = line
                #     all_regs = '{r0, r1, r2, r3, r4, r5, r6, r7, lr}'
                #     if (l.find('{lr}') != -1):
                #         data0 += 1
                #     elif (l.find('{r0, r4, r5, r6, r7, lr}') != -1):
                #         data1 += 1
                #     elif (l.find('{r0, r1, r4, r5, r6, r7, lr}') != -1):
                #         data2 += 1
                #     elif (l.find('{r0, r1, r2, r4, r5, r6, r7, lr}') != -1):
                #         data3 += 1
                #     elif l.find(all_regs) != -1:
                #         data4 += 1
                #     elif (l.find('{r1, r2, r3, r4, r5, r6, r7, lr}') != -1):
                #         data5 += 1
                #     elif (l.find('{r2, r3, r4, lr}') != -1):
                #         data6 += 1
                #     elif (l.find('{r2, r3, r4, r5, r6, lr}') != -1):
                #         data7 += 1
                #     elif (l.find('{r2, r3, r4, r5, r6, r7, lr}') != -1):
                #         data8 += 1
                #     elif (l.find('{r3, r4, r5, r6, r7, lr}') != -1):
                #         data9 += 1
                #     elif (l.find('{r4, lr}') != -1):
                #         data10 += 1
                #     elif (l.find('{r4, r5, lr}') != -1):
                #         data11 += 1
                #     elif (l.find('{r4, r5, r6, lr}') != -1):
                #         data12 += 1
                #     elif (l.find('{r4, r5, r6, r7, lr}') != -1):
                #         data13 += 1
                #     else:
                #         print(line)

                # if (opcode == 'pop'):
                #     l = line
                #     if (l.find('{pc}') != -1):
                #         data0 += 1
                #     elif (l.find('{r1, r2, r3, r4, r5, r6, r7, pc}') != -1):
                #         data1 += 1
                #     elif (l.find('{r2, r3, r4, pc}') != -1):
                #         data2 += 1
                #     elif (l.find('{r2, r3, r4, r5, r6, pc}') != -1):
                #         data3 += 1
                #     elif (l.find('{r2, r3, r4, r5, r6, r7, pc}') != -1):
                #         data4 += 1
                #     elif (l.find('{r3, r4, r5, r6, r7, pc}') != -1):
                #         data5 += 1
                #     elif (l.find('{r4, pc}') != -1):
                #         data6 += 1
                #     elif (l.find('{r4, r5, pc}') != -1):
                #         data7 += 1
                #     elif (l.find('{r4, r5, r6, pc}') != -1):
                #         data8 += 1
                #     elif (l.find('{r4, r5, r6, r7, pc}') != -1):
                #         data9 += 1
                #     else:
                #         print(line)
                continue

        if (curr_state == S_FUNC_END):
            function_xlsx.record_arm_totals(wksheet,
                                            arm_results[func_name])
            if (last_flag is False):
                if (parse_rules.is_func_start(line)):
                    curr_state = S_FUNC_START
                else:
                    curr_state = S_WAIT
                    continue
            else:
                curr_state = S_END
                break

        if (curr_state == S_FUNC_START):
            # Open worksheet for this function
            (func_name, wksheet_name) = parse_rules.get_func_data(line)
            if wksheet_name is not None:
                wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                # Reset function variables
                arm_results[func_name] = 0
                # Start data recording in 'ARM M0+' table below the header
                row = excel.get_table_loc(ARM_TABLE)[0] + 3
                curr_state = S_FUNC_PARSE
                continue
            else:
                curr_state = S_WAIT
    # Catch any function that occurs at the end of the file and save results
    if (curr_state != S_END) and (wksheet_name is not None) \
            and (func_name in arm_results.keys()):
        function_xlsx.record_arm_totals(wksheet, arm_results[func_name])

    f.close()

    # print("{:<30}{:<30}".format('ldr', arm_instr['ldr']))
    # for opcode in sorted(arm_instr.keys()):
    #     print("{:<30}{:<30}".format(opcode, arm_instr[opcode][0]))
    #     if (opcode == 'add'):
    #         for args in arm_instr[opcode][1]:
    #             if 'sp' == args[0]:
    #                 data0 += 1
    #             elif 'sp' == args[1]:
    #                 data1 += 1
    #             else:
    #                 data2 += 1
    #     if (opcode == 'adds'):
    #         for args in arm_instr[opcode][1]:
    #             if (len(args) <= 2):
    #                 if '#' in args[1]:
    #                     data0 += 1  # rd = rd + immed8
    #             elif ('#' in args[2]):
    #                 data1 += 1  # rd = rs1 + immed3 (rd may also be rs1)
    #             elif (args[0] == args[1]) or (args[0] == args[2]):
    #                 data2 += 1  # rd = rd + rs1
    #             elif (args[0] != args[1]) and (args[0] != args[2]):
    #                 data3 += 1  # rd = rs1 + rs2
    #     if (opcode == 'asrs'):
    #         for args in arm_instr[opcode][1]:
    #             if len(args) > 2:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'cmp'):
    #         for args in arm_instr[opcode][1]:
    #             if '#' not in args[1]:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'ldr'):
    #         for args in arm_instr[opcode][1]:
    #             if '[pc' in args:
    #                 data0 += 1
    #             elif '[sp' in args:
    #                 data1 += 1
    #             else:
    #                 test = False
    #                 for arg in args:
    #                     if '#' in arg:
    #                         data2 += 1
    #                         test = True
    #                 if test is False:
    #                     data3 += 1
    #     if (opcode == 'ldrb'):
    #         for args in arm_instr[opcode][1]:
    #             if '#' in args[2]:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'ldrh'):
    #         for args in arm_instr[opcode][1]:
    #             if '#' in args[2]:
    #                 data0 += 1
    #             else:
    #                 data1 += 1if (opcode == 'ldrb'):
    #     if (opcode == 'lsls'):
    #         for args in arm_instr[opcode][1]:
    #             if len(args) > 2:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'lsrs'):
    #         for args in arm_instr[opcode][1]:
    #             if len(args) > 2:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'movs') or (opcode == 'mov'):
    #         for args in arm_instr[opcode][1]:
    #             if '#' not in args[1]:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'str'):
    #         for args in arm_instr[opcode][1]:
    #             if '[sp' in args:
    #                 data0 += 1
    #             else:
    #                 test = False
    #                 for arg in args:
    #                     if "#" in arg:
    #                         data1 += 1
    #                         test = True
    #                 if test is False:
    #                     data2 += 1
    #     if (opcode == 'strb'):
    #         for args in arm_instr[opcode][1]:
    #             if '#' in args[2]:
    #                 data0 += 1
    #             else:
    #                 data1 += 1
    #     if (opcode == 'subs'):
    #         for args in arm_instr[opcode][1]:
    #             if len(args) > 2:
    #                 if '#' not in args[2]:
    #                     data0 += 1
    #                 elif int(args[2][1:]) < 8:
    #                     data1 += 1
    #             else:
    #                 data2 += 1
    # print()
    # print("{:<30s}{:<5d}".format(compiler + " data0", data0))
    # print("{:<30s}{:<5d}".format(compiler + " data1", data1))
    # print("{:<30s}{:<5d}".format(compiler + " data2", data2))
    # print("{:<30s}{:<5d}".format(compiler + " data3", data3))
    # print("{:<30s}{:<5d}".format(compiler + " data4", data4))
    # print("{:<30s}{:<5d}".format(compiler + " data5", data5))
    # print("{:<30s}{:<5d}".format(compiler + " data6", data6))
    # print("{:<30s}{:<5d}".format(compiler + " data7", data7))
    # print("{:<30s}{:<5d}".format(compiler + " data8", data8))
    # print("{:<30s}{:<5d}".format(compiler + " data9", data9))
    # print("{:<30s}{:<5d}".format(compiler + " data10", data10))
    # print("{:<30s}{:<5d}".format(compiler + " data11", data11))
    # print("{:<30s}{:<5d}".format(compiler + " data12", data12))
    # print("{:<30s}{:<5d}".format(compiler + " data13", data13))
    # print()
    return arm_results


def scan_riscv_file(compiler):
    """
    Opens and scans the RISC-V disassembly files to extract data.

    Function-Level Data Structures:
        - f_size: function size (in bytes)
        - f_reductions:
            * Key: replaced instruction name (e.g. 'cx.lwpc')
            * Val: size reduction by that instruction
        - f_instr:
            * Key: instruction
            * Val: # of Occurrences
        - f_formats:
            * Key: RV32 Instruction Format (R, U, etc.)
            * Val:
                * Key: RV32 Base Instruction
                * Val: # of Occurrences
        - f_bits: number of bits to encode LW offsets
        - f_pairs
            * Key: (instruction #1, instruction #2)
            * Val: # of Occurrences
        - replaced_loc
            * Key: replaced instruction name
            * Val: [list of row locations in that function]
        - pair_loc
            * Key: (instruction #1, instruction #2)
            * Val: [list of row locations in that function]
    Benchmark-Level Data Structures:
        - results:
            * Key: function name
            * Val: (f_size, f_reductions, f_instr, f_formats, f_bits)
        - t_reductions
            * Benchmark accumulator for f_reductions
        - t_pairs
            * Benchmark accumulator for f_pairs
        - t_instr
            * Benchmark accumulator for f_instr
        - t_formats
            * Benchmark accumulator for f_formats

    Returns: (results, t_reductions, t_pairs, t_instr, t_formats)
    """
    data0 = 0
    data1 = 0
    data2 = 0
    data3 = 0
    data4 = 0
    data5 = 0
    data6 = 0
    data7 = 0
    data8 = 0
    data9 = 0
    data10 = 0
    data11 = 0
    data12 = 0

    # Initialize high-level data structures
    results = {}
    if (save_restore_en):
        results['__riscv_save'] = (0, {}, {}, {}, 0)
        results['__riscv_restore'] = (0, {}, {}, {}, 0)
    t_reductions = {}
    t_pairs = {}
    t_instr = {}
    t_formats = {}
    for i in range(len(ENABLED)):
        t_reductions[ENABLED[i]] = 0
    for lbl in RV32_FORMATS:
        t_formats[lbl] = {}
        for instr in RV32_INSTR_FORMATS.keys():
            instr_lbl = RV32_INSTR_FORMATS[instr][0]
            if (instr_lbl == lbl):
                t_formats[lbl][instr] = 0

    # Open the appropriate text file
    if (compiler == 'RVGCC'):
        f = open(input_rvgcc)
    elif (compiler == 'IAR'):
        f = open(input_iar)

    wksheet_name = None
    last_flag = False

    state = S_INIT
    for line in f:
        if (state == S_INIT):
            transition = parse_rules.is_first(line)
            if transition:
                end = parse_rules.is_last(line)
                if end:
                    last_flag = True
                # print("First function found.\n")
                state = S_FUNC_START
            else:
                continue

        if (state == S_WAIT):
            # waiting for next function to start
            transition = parse_rules.is_func_start(line)
            if transition:
                # check if it is the last function
                end = parse_rules.is_last(line)
                if end:
                    last_flag = True
                state = S_FUNC_START
            else:
                continue

        if (state == S_FUNC_PARSE):
            transition = parse_rules.is_func_end(line)
            if transition:
                # reached end of current function
                state = S_FUNC_END
            else:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instruction data from line of text and record
                if (compiler == 'RVGCC'):
                    ret = parse_rules.scan_rvgcc_instruction(line)
                    (addr, instr, bytes, opcode, args, comments) = ret
                    # Explicitly mark RVC instructions for readability
                    if (bytes == 2):
                        opcode = 'c.' + opcode
                    # RVGCC does not differentiate these sub-types
                    if (opcode == 'c.addi'):
                        if (args[1] == 'sp'):
                            if args[0] == 'sp':
                                opcode = 'c.addi16sp'
                                args = args[2:]
                            else:
                                opcode = 'c.addi4spn'
                                args.pop(1)
                    if (opcode == 'c.sw') and ('sp' in args[1]):
                        opcode = 'c.swsp'
                        idx = args[1].index('(')
                        args = [args[0], args[1][:idx]]
                    if (opcode == 'c.lw') and ('sp' in args[1]):
                        opcode = 'c.lwsp'
                        idx = args[1].index('(')
                        args = [args[0], args[1][:idx]]
                    # __riscv_save and __riscv_restore functions are unique
                    if (wksheet_name == '__riscv_save') \
                            or (wksheet_name == '__riscv_restore'):
                        save_restore_xlsx.record_instruction(wksheet, compiler,
                                                             tbl, row, addr,
                                                             instr, opcode,
                                                             args, comments)
                    else:
                        function_xlsx.record_instruction(wksheet, compiler,
                                                         row, addr, instr,
                                                         opcode, args,
                                                         comments)
                elif (compiler == 'IAR'):
                    ret = parse_rules.scan_iar_instruction(line)
                    (addr, instr, bytes, opcode, args) = ret
                    # __riscv_save and __riscv_restore functions are unique
                    if (wksheet_name == '__riscv_save') \
                            or (wksheet_name == '__riscv_restore'):
                        save_restore_xlsx.record_instruction(wksheet, compiler,
                                                             tbl, row, addr,
                                                             instr, opcode,
                                                             args, '')
                    else:
                        function_xlsx.record_instruction(wksheet, compiler,
                                                         row, addr, instr,
                                                         opcode, args, '')
                    comments = None
                # Increment function code size by this instruction size
                f_size += bytes
                # if (bytes > 2):
                #     data1 += 1
                # else:
                #     data0 += 1

                # Parse for replaceable instructions
                if (wksheet_name != '__riscv_save') \
                        and (wksheet_name != '__riscv_restore'):
                    replaceable = False
                    # 32-bit instruction
                    if (bytes > 2):
                        # increment appropriate instruction format label
                        instr_type = RV32_INSTR_FORMATS[opcode]
                        if (instr_type[0] not in RV32_FORMATS):
                            # pseudoinstruction, get label of base instruction
                            for i in range(len(instr_type)):
                                lbl = RV32_INSTR_FORMATS[instr_type[i]][0]
                                f_formats[lbl][instr_type[i]] += 1
                        else:
                            f_formats[instr_type[0]][opcode] += 1
                        # check if replaceable
                        res = cx.check_replaceable(opcode, args, comments,
                                                   max_offset, min_offset,
                                                   addr)
                        replaceable = res[0]
                        (r2, r1, offset) = res[1]
                        max_offset, min_offset, type_code = res[2:5]

                        # Record reduction in func_reductions and write comment
                        if (replaceable):
                            opcode = type_code
                            # replacement by 16-bit instruction
                            if (opcode[:2] == 'c.') or (opcode[:2] == 'cx'):
                                f_reductions[opcode] += 2
                            function_xlsx.record_comments(wksheet, compiler,
                                                          row, opcode,
                                                          (r2, r1, offset))
                            f_instr[opcode] += 1
                            replaced_loc[opcode].append(row)
                        else:
                            if opcode in f_instr.keys():
                                f_instr[opcode] += 1
                            else:
                                f_instr[opcode] = 1
                    # 16-bit instruction
                    else:
                        # C.ADDI is unique since we are proposing to remove it
                        if (opcode == 'c.addi') and (addi_subi_en):
                            if (compiler == 'IAR'):
                                args = [args[0], args[0], args[1]]
                            res = cx.check_replaceable('c.addi', args,
                                                       comments,
                                                       max_offset,
                                                       min_offset,
                                                       addr)
                            replaceable = res[0]
                            (r2, r1, offset) = res[1]
                            type_code = res[4]
                            if (replaceable):
                                opcode = type_code
                                function_xlsx.record_comments(wksheet,
                                                              compiler,
                                                              row, opcode,
                                                              res[1])
                                replaced_loc[opcode].append(row)
                            else:
                                if (opcode not in not_repl_loc.keys()):
                                    not_repl_loc[opcode] = [row]
                                else:
                                    not_repl_loc[opcode].append(row)
                        if opcode in f_instr.keys():
                            f_instr[opcode] += 1
                        else:
                            f_instr[opcode] = 1

                    # Increment instruction pair occurence
                    pair = (prev_op, opcode)
                    if pair in f_pairs.keys():
                        f_pairs[pair] += 1
                    else:
                        if (prev_op != ''):
                            f_pairs[pair] = 1
                    if (pair in PAIRS_ENABLED):
                        pair_loc[pair].append(row - 1)

                prev_op = opcode
                prev_args = args

                # if ((opcode == 'c.addi') or (opcode == 'addi')) \
                #         and (compiler == 'RVGCC'):
                #     num = int(args[-1])
                #     if (num <= -256):
                #         data0 += 1
                #     elif (num <= -32):
                #         data1 += 1
                #     elif (num < 0):
                #         data2 += 1
                #     elif (num < 32):
                #         data3 += 1
                #     elif (num < 256):
                #         data4 += 1
                #     else:
                #         data5 += 1

                # if (opcode == 'addi'):
                #     reg1 = args[0]
                #     reg2 = args[1]
                #     immed = abs(int(args[2], 16))
                #     if (reg1 != reg2) and (immed >= 32):
                #         data2 += 1
                #     elif (reg1 != reg2):
                #         data0 += 1
                #     elif (immed >= 32):
                #         data1 += 1
                #     else:
                #         data4 += 1
                #     print(func_name)
                #     print(args)

                # if (opcode == 'lw'):
                #     # IMPORTANT: Must also uncomment data3 line in S_FUNC_END
                #     reg1 = args[0]
                #     reg2 = args[1].split('(')[1][:-1]
                #     off = int(args[1].split('(')[0], 16)
                #     regs_okay = (reg1 in REG_LIST) and (reg2 in REG_LIST)
                #     off_okay = (abs(off) < 128) and (off >= 0)
                #     if (regs_okay is False) and (off_okay is False):
                #         data4 += 1
                #     if (regs_okay is True) and (off_okay is False):
                #         if (abs(off) >= 128) and (off > 0):
                #             data1 += 1
                #         if (abs(off) < 128) and (off < 0):
                #             data2 += 1
                #         if (abs(off) >= 128) and (off < 0):
                #             data3 += 1
                #     if (regs_okay is False) and (off_okay is True):
                #         if (reg1 not in REG_LIST) or (reg2 not in REG_LIST):
                #             data0 += 1
                # elif (opcode == 'cx.lwpc'):
                #     data5 += 1

                # if (opcode == 'slli'):
                #     rd = args[0]
                #     rs1 = args[1]
                #     if (rd != rs1):
                #         data4 += 1
                #     if (rd in REG_LIST) and (rs1 not in REG_LIST):
                #         data0 += 1
                #     if (rs1 in REG_LIST) and (rd not in REG_LIST):
                #         data1 += 1
                #     if (rd in REG_LIST) and (rs1 in REG_LIST):
                #         data2 += 1
                #     if (rd not in REG_LIST) and (rs1 not in REG_LIST):
                #         data3 += 1

                # if (opcode == 'jal'):
                #     print(args)
                #     print(int(args[1], 16) - int(addr, 16))

                # if (opcode == 'add'):
                #     data0 += 1
                #     rd = args[0]
                #     rs1 = args[1]
                #     if (rd != rs1):
                #         data1 += 1
                #     else:
                #         print(args)
                # if (opcode == 'sub'):
                #     data0 += 1
                #     rd = args[0]
                #     rs1 = args[1]
                #     rs2 = args[2]
                #     if (rd != rs1) and ((rd not in REG_LIST) or
                #                         (rs1 not in REG_LIST) or
                #                         (rs2 not in REG_LIST)):
                #         data1 += 1
                #     elif (rd != rs1):
                #         data2 += 1
                #     elif (rd not in REG_LIST) or (rs1 not in REG_LIST) or \
                #             (rs2 not in REG_LIST):
                #         data3 += 1
                #     else:
                #         data4 += 1

                # if (line.find('__riscv_save') != -1):
                #     if (line.find('__riscv_save_12') != -1):
                #         data12 += 1
                #     elif (line.find('__riscv_save_11') != -1):
                #         data11 += 1
                #     elif (line.find('__riscv_save_10') != -1):
                #         data10 += 1
                #     elif (line.find('__riscv_save_9') != -1):
                #         data9 += 1
                #     elif (line.find('__riscv_save_8') != -1):
                #         data8 += 1
                #     elif (line.find('__riscv_save_7') != -1):
                #         data7 += 1
                #     elif (line.find('__riscv_save_6') != -1):
                #         data6 += 1
                #     elif (line.find('__riscv_save_5') != -1):
                #         data5 += 1
                #     elif (line.find('__riscv_save_4') != -1):
                #         data4 += 1
                #     elif (line.find('__riscv_save_3') != -1):
                #         data3 += 1
                #     elif (line.find('__riscv_save_2') != -1):
                #         data2 += 1
                #     elif (line.find('__riscv_save_1') != -1):
                #         data1 += 1
                #     elif (line.find('__riscv_save_0') != -1):
                #         data0 += 1
                #     else:
                #         print(line)

                # if (line.find('__riscv_restore') != -1):
                #     if (line.find('__riscv_restore_12') != -1):
                #         data12 += 1
                #     elif (line.find('__riscv_restore_11') != -1):
                #         data11 += 1
                #     elif (line.find('__riscv_restore_10') != -1):
                #         data10 += 1
                #     elif (line.find('__riscv_restore_9') != -1):
                #         data9 += 1
                #     elif (line.find('__riscv_restore_8') != -1):
                #         data8 += 1
                #     elif (line.find('__riscv_restore_7') != -1):
                #         data7 += 1
                #     elif (line.find('__riscv_restore_6') != -1):
                #         data6 += 1
                #     elif (line.find('__riscv_restore_5') != -1):
                #         data5 += 1
                #     elif (line.find('__riscv_restore_4') != -1):
                #         data4 += 1
                #     elif (line.find('__riscv_restore_3') != -1):
                #         data3 += 1
                #     elif (line.find('__riscv_restore_2') != -1):
                #         data2 += 1
                #     elif (line.find('__riscv_restore_1') != -1):
                #         data1 += 1
                #     elif (line.find('__riscv_restore_0') != -1):
                #         data0 += 1
                #     else:
                #         print(line)

                # Move to next row of worksheet for next instruction
                row += 1
                continue

        if (state == S_FUNC_END):
            if (wksheet_name == '__riscv_save'):
                # increment total for save_0, save_1, etc.
                if (f_size > 0):
                    curr = results['__riscv_save'][0]
                    results['__riscv_save'] = (curr + f_size, {}, {}, {}, 0)
            elif (wksheet_name == '__riscv_restore'):
                # increment total for restore_0, restore_1, etc.
                if (f_size > 0):
                    curr = results['__riscv_restore'][0]
                    results['__riscv_restore'] = (curr + f_size, {}, {}, {}, 0)
            else:
                # If using cx.lwpc, need to check if offset width exceeded
                if lwpc_en[1]:
                    (res, min_offset, f_bits) = cx.check_offsets(f_size,
                                                                 f_reductions,
                                                                 max_offset,
                                                                 min_offset)
                    # if number of bits too high, not able to us cx.lwpc
                    if (res is False):
                        f_reductions['cx.lwpc'] = 0
                        # revert back to original 32-bit LW
                        if 'lw' in f_instr.keys():
                            f_instr['lw'] += f_instr['cx.lwpc']
                        else:
                            f_instr['lw'] = f_instr['cx.lwpc']
                        f_instr['cx.lwpc'] = 0
                        lwpc_fail = True

                    # else:
                    #     data5 -= f_instr['cx.lwpc']

                # Add function totals to the overall benchmark totals
                res = update_tot(t_reductions, t_pairs, t_instr,
                                 t_formats, f_reductions, f_pairs,
                                 f_instr, f_formats)
                (t_reductions, t_pairs, t_instr, t_formats) = res
                # Save the function results and record in Excel worksheet
                results[func_name] = (f_size, f_reductions, f_instr, f_formats,
                                      f_bits)
                function_xlsx.record_riscv_totals(wksheet, compiler, f_size,
                                                  f_reductions)
                function_xlsx.add_tables_charts_marks(wksheet, compiler,
                                                      f_instr, f_formats,
                                                      replaced_loc,
                                                      not_repl_loc, lwpc_fail,
                                                      pair_loc)
            # Indicate successful completion of last function
            if (last_flag is True):
                state = S_END
                break
            # Or continue to next function
            else:
                if parse_rules.is_func_start(line):
                    end = parse_rules.is_last(line)
                    if end:
                        last_flag = True
                    state = S_FUNC_START
                else:
                    state = S_WAIT
                    continue

        if (state == S_FUNC_START):
            # Create and format new worksheet
            (func_name, wksheet_name) = parse_rules.get_func_data(line)
            if (wksheet_name == '__riscv_save'):
                wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                # Some functions grouped/have same definition in assembly
                num = int(re.split('_', func_name)[-1])
                if (num < 4):
                    if (compiler == 'IAR'):
                        tbl = SAVE_IAR_A_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = SAVE_RVGCC_A_TABLE
                elif (num < 8):
                    if (compiler == 'IAR'):
                        tbl = SAVE_IAR_B_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = SAVE_RVGCC_B_TABLE
                elif (num < 12):
                    if (compiler == 'IAR'):
                        tbl = SAVE_IAR_C_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = SAVE_RVGCC_C_TABLE
                else:
                    if (compiler == 'IAR'):
                        tbl = SAVE_IAR_D_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = SAVE_RVGCC_D_TABLE

                row = excel.get_table_loc(tbl)[0] + 3
                f_size = 0
                state = S_FUNC_PARSE
                continue
            elif (wksheet_name == '__riscv_restore'):
                wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                num = int(re.split('_', func_name)[-1])
                if (num < 4):
                    if (compiler == 'IAR'):
                        tbl = RESTORE_IAR_A_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = RESTORE_RVGCC_A_TABLE
                elif (num < 8):
                    if (compiler == 'IAR'):
                        tbl = RESTORE_IAR_B_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = RESTORE_RVGCC_B_TABLE
                elif (num < 12):
                    if (compiler == 'IAR'):
                        tbl = RESTORE_IAR_C_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = RESTORE_RVGCC_C_TABLE
                else:
                    if (compiler == 'IAR'):
                        tbl = RESTORE_IAR_D_TABLE
                    elif (compiler == 'RVGCC'):
                        tbl = RESTORE_RVGCC_D_TABLE

                row = excel.get_table_loc(tbl)[0] + 3
                f_size = 0
                state = S_FUNC_PARSE
                continue
            elif (wksheet_name is not None):
                if (compiler == 'RVGCC'):
                    # print("New function: " + func_name)
                    wksheet = function_xlsx.create_sheet(func_name,
                                                         wksheet_name)
                    function_xlsx.record_func_name(wksheet, func_name)
                    # Place instruction data starting below the headers
                    row = excel.get_table_loc(RVGCC_TABLE)[0] + 3
                elif (compiler == 'IAR'):
                    wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                    row = excel.get_table_loc(IAR_TABLE)[0] + 3
                # Reset current function totals
                f_size = 0
                f_reductions = {}
                f_instr = {}
                f_formats = {}
                replaced_loc = {}
                not_repl_loc = {}
                f_pairs = {}
                pair_loc = {}
                prev_op = ''
                prev_args = []
                for instr in ENABLED:
                    f_reductions[instr] = 0
                    f_instr[instr] = 0
                    replaced_loc[instr] = []
                for pair in PAIRS_ENABLED:
                    pair_loc[pair] = []
                f_bits = 0
                for lbl in RV32_FORMATS:
                    f_formats[lbl] = {}
                    for instr in RV32_INSTR_FORMATS.keys():
                        instr_lbl = RV32_INSTR_FORMATS[instr][0]
                        if (instr_lbl == lbl):
                            f_formats[lbl][instr] = 0
                # Add entry for new function with default values
                results[func_name] = (f_size, f_reductions, f_instr, f_formats,
                                      f_bits)
                # Reset offset trackers
                lwpc_fail = False
                max_offset = 0
                min_offset = float("inf")
                state = S_FUNC_PARSE
                continue
            else:
                state = S_WAIT
                continue
    # Catch any function that occurs at the end of the file and save results
    if (state != S_END) and (wksheet_name is not None):
        if (wksheet_name == '__riscv_save'):
            # increment total for save_0, save_1, etc.
            if (f_size > 0):
                curr = results['__riscv_save'][0]
                results['__riscv_save'] = (curr + f_size, {}, {}, {}, 0)
        elif (wksheet_name == '__riscv_restore'):
            # increment total for restore_0, restore_1, etc.
            if (f_size > 0):
                curr = results['__riscv_restore'][0]
                results['__riscv_restore'] = (curr + f_size, {}, {}, {}, 0)
        else:
            # If using cx.lwpc, need to check if offset width exceeded
            if lwpc_en[1]:
                (res, min_offset, f_bits) = cx.check_offsets(f_size,
                                                             f_reductions,
                                                             max_offset,
                                                             min_offset)
                # if number of bits too high, not able to us cx.lwpc
                if (res is False):
                    f_reductions['cx.lwpc'] = 0
                    # revert back to original 32-bit LW
                    if 'lw' in f_instr.keys():
                        f_instr['lw'] += f_instr['cx.lwpc']
                    else:
                        f_instr['lw'] = f_instr['cx.lwpc']
                    f_instr['cx.lwpc'] = 0
                    lwpc_fail = True

                # else:
                #     data5 -= f_instr['cx.lwpc']

            # Add function totals to the overall benchmark totals
            res = update_tot(t_reductions, t_pairs, t_instr,
                             t_formats, f_reductions, f_pairs,
                             f_instr, f_formats)
            (t_reductions, t_pairs, t_instr, t_formats) = res
            # Save the function results and record in Excel worksheet
            results[func_name] = (f_size, f_reductions, f_instr, f_formats,
                                  f_bits)
            function_xlsx.record_riscv_totals(wksheet, compiler, f_size,
                                              f_reductions)
            function_xlsx.add_tables_charts_marks(wksheet, compiler,
                                                  f_instr, f_formats,
                                                  replaced_loc,
                                                  not_repl_loc, lwpc_fail,
                                                  pair_loc)

    # Only allow the first BR_KEEP (%) of each type of branch to be compressed
    for br_instr in BR_ENABLED:
        if br_instr in t_instr.keys():
            orig_br = br_instr[3:]
            keep = round(t_instr[br_instr]*BR_KEEP)
            # Update the totals (# of occurrences & reduction amt)
            t_instr[orig_br] = t_instr[br_instr] - keep
            t_instr[br_instr] = keep
            t_reductions[br_instr] = 2*keep

        # Go through the functions until reach limit of branches to keep
        count = 0
        zero = False
        for func in results.keys():
            (f_size, f_reductions, f_instr, f_formats, f_bits) = results[func]
            # Number of compressed branches in this function
            left = f_instr[br_instr]
            # Count through until reach max to keep
            while (zero is False) and (left > 0):
                count += 1
                left -= 1
                if (count == keep):
                    zero = True
            # Zero out the rest, undoing the compression
            if (zero):
                f_instr[orig_br] = left
                f_instr[br_instr] -= left
                f_reductions[br_instr] -= left*2
                # f_size += left*2
                results[func] = (f_size, f_reductions, f_instr, f_formats,
                                 f_bits)

    if (save_restore_en):
        # Add __riscv_save and __riscv_restore totals to corresponding wksheet
        nm = '__riscv_save'
        wksheet = excel.wkbook.get_worksheet_by_name(nm)
        save_restore_xlsx.record_totals(wksheet, compiler, nm, results[nm][0])
        nm = '__riscv_restore'
        wksheet = excel.wkbook.get_worksheet_by_name(nm)
        save_restore_xlsx.record_totals(wksheet, compiler, nm, results[nm][0])
        # Add push/pop reductions to totals if enabled
        if ('push (save)' in ENABLED):
            size = results['__riscv_save'][0]
            results['__riscv_save'] = (size, {'push (save)': size}, {}, {}, 0)
            # Add function totals to the overall benchmark totals
            res = update_tot(t_reductions, t_pairs, t_instr, t_formats,
                             results['__riscv_save'][1], {}, {}, {})
            (t_reductions, t_pairs, t_instr, t_formats) = res
        if ('pop (restore)' in ENABLED):
            size = results['__riscv_restore'][0]
            results['__riscv_restore'] = (size, {'pop (restore)': size}, {}, {}, 0)
            res = update_tot(t_reductions, t_pairs, t_instr, t_formats,
                             results['__riscv_restore'][1], {}, {}, {})
            (t_reductions, t_pairs, t_instr, t_formats) = res

    f.close()
    # print("{:<30s}{:<5d}".format(compiler + " data0", data0))
    # print("{:<30s}{:<5d}".format(compiler + " data1", data1))
    # print("{:<30s}{:<5d}".format(compiler + " data2", data2))
    # print("{:<30s}{:<5d}".format(compiler + " data3", data3))
    # print("{:<30s}{:<5d}".format(compiler + " data4", data4))
    # print("{:<30s}{:<5d}".format(compiler + " data5", data5))
    # print("{:<30s}{:<5d}".format(compiler + " data6", data6))
    # print("{:<30s}{:<5d}".format(compiler + " data7", data7))
    # print("{:<30s}{:<5d}".format(compiler + " data8", data8))
    # print("{:<30s}{:<5d}".format(compiler + " data9", data9))
    # print("{:<30s}{:<5d}".format(compiler + " data10", data10))
    # print("{:<30s}{:<5d}".format(compiler + " data11", data11))
    # print("{:<30s}{:<5d}".format(compiler + " data12", data12))
    # print()

    r = (results, t_reductions, t_pairs, t_instr, t_formats)
    return r


def update_tot(t_red, t_pair, t_instr, t_lbl, f_red, f_pair, f_instr, f_lbl):
    """ Updates the benchmark totals as each function is completed. """
    # New replaced instruction reductions
    for instr in f_red.keys():
        t_red[instr] += f_red[instr]
    # Instruction pairs
    for pair in f_pair.keys():
        if pair in t_pair.keys():
            t_pair[pair] += f_pair[pair]
        else:
            t_pair[pair] = f_pair[pair]
    # Instruction occurrences
    for instr in f_instr.keys():
        if instr in t_instr.keys():
            t_instr[instr] += f_instr[instr]
        else:
            t_instr[instr] = f_instr[instr]
    # Instruction formats
    for lbl in f_lbl.keys():
        for instr in f_lbl[lbl]:
            t_lbl[lbl][instr] += f_lbl[lbl][instr]
    return (t_red, t_pair, t_instr, t_lbl)


""" Main Code """

failure = False
try:
    # Create Summary worksheet; write input files to A1, A2; set column sizes
    # Do this first so that it shows up as the first sheet in the workbook
    sum_wksheet = summary_xlsx.create_summary(input_rvgcc, input_arm)

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
    parse_rules.compiler = 'RVGCC'
    res = scan_riscv_file('RVGCC')
    (gcc_results, gcc_reductions, gcc_pairs, gcc_instr, gcc_formats) = res

    # for instr in sorted(gcc_instr.keys()):
    #     print("{:<30}{:<30}".format(instr, gcc_instr[instr]))

    parse_rules.compiler = 'ARM'
    arm_results = scan_arm_file()

    if (IAR is True):
        parse_rules.compiler = 'IAR'
        res = scan_riscv_file('IAR')
        (iar_results, iar_reductions, iar_pairs, iar_instr, iar_formats) = res

        # for instr in sorted(iar_instr.keys()):
        #     print("{:<30}{:<30}".format(instr, iar_instr[instr]))

    # Add the main table to record individual function totals
    row = 18
    col = 1
    summary_xlsx.add_main_table(row, col)

    # Add the totals table to record overall benchmark totals
    row = 3
    col = 1
    summary_xlsx.add_totals_table(row, col)

    # Write out the results to the Summary worksheet
    summary_xlsx.record_rvgcc_data(gcc_results, gcc_reductions)
    summary_xlsx.record_arm_data(gcc_results, arm_results)
    if (IAR is True):
        summary_xlsx.record_iar_data(gcc_results, iar_results)

    # Record replaced instruction performance
    reductions = [gcc_reductions]
    if (IAR is True):
        reductions.append(iar_reductions)
    summary_xlsx.add_replaced_instr_table(reductions)

    # Add a chart to visualize the replaced instruction performance
    compilers = ['RVGCC']
    if (IAR is True):
        compilers.append('IAR')
    summary_xlsx.add_replaced_instr_chart(compilers)

    # Record the rules used to implement new replaced instructions
    summary_xlsx.add_replacement_rules_table()

    # Record the frequency of instructions
    summary_xlsx.add_total_instr_table(gcc_instr, 20, 'RVGCC')
    if (IAR is True):
        summary_xlsx.add_total_instr_table(iar_instr, 20, 'IAR')

    # Record the frequency of instruction pairs
    summary_xlsx.add_pairs_table(gcc_pairs, 20, 'RVGCC')
    if (IAR is True):
        summary_xlsx.add_pairs_table(iar_pairs, 20, 'IAR')

    # Record the frequency of instruction formats to 'tmp' worksheet
    formats = [gcc_formats]
    if (IAR is True):
        formats.append(iar_formats)
    summary_xlsx.add_instr_formats_tables(formats, compilers)

    # Add a chart to visualize the instruction format frequency distribution
    summary_xlsx.add_instr_formats_radar('RVGCC')
    if (IAR is True):
        summary_xlsx.add_instr_formats_radar('IAR')

    # Record function contribution to overshooting ARM code size
    summary_xlsx.add_overshoot_table(gcc_results, arm_results, 5, 'RVGCC')
    if (IAR is True):
        summary_xlsx.add_overshoot_table(iar_results, arm_results, 5, 'IAR')

    # Add a chart to visualize the function overshoot over ARM code size
    summary_xlsx.add_overshoot_chart('RVGCC')
    if (IAR is True):
        summary_xlsx.add_overshoot_chart('IAR')


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
