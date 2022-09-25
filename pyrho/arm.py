"""
Arm Disassembly Scanner Functions

Author: Jennifer Hellar

"""


import importlib
import os

# local scripts
import excel
import function_xlsx
import config
from constants import *

# import the class ParseRules from parser.py
ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')


def scan_arm_file(compiler, assemblyfile, optfile):
    """
    Opens and scans the ARM disassembly file to extract data and save to Excel
    workbook.

    Arguments:
        - compiler          Arm toolchain used to compile the benchmark
        - assemblyfile      Arm disassembly file
        - optfile           Arm config file; selects the functions to parse

    Data:
        - arm_results
            * Key: function name
            * Val: function code size (in bytes)

    Returns: arm_results
    """
    # Read the config file to know which functions to analyze
    func_opts = config.read_config(optfile)

    # Check that at least one function has been selected for analysis
    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

    arm_results = {}
    # arm_instr = {}

    # Configure the parser
    parse_rules = ParseRules(compiler)

    parsing = False
    last_saved = False
    fcnt = 0    # function index
    with open(assemblyfile, 'r') as f:
        for line in f:
            # Found the start of a new function
            if parse_rules.is_func_start(line):
                (fname, wname) = parse_rules.get_func_data(line)
                nm, parse, subfunc = func_opts[fcnt]
                fcnt += 1
                if nm != fname:
                    raise Exception('Error: function name does not match func_opts record')
                # Done w/analysis of current function if the new function is not
                #   a subfunction or not set to parse
                if parsing and (not subfunc or not parse):
                    # Record current function totals
                    function_xlsx.record_arm_totals(wksheet,
                                                    arm_results[func_name])
                    last_saved = True
                # Beginning a new function to analyze and not a subfunction
                if parse and not subfunc:
                    # Setup for the new function
                    func_name = fname
                    wksheet_name = wname
                    wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                    # Reset function variables
                    arm_results[func_name] = 0
                    # Start data recording in 'ARM M0+' table below the header
                    row = excel.get_table_loc(ARM_TABLE)[0] + 3
                    last_saved = False
                    parsing = True
                    continue
                # Beginning to analyze a subfunction of the current function
                elif parse and subfunc:
                    parsing = True
                    continue
                # Beginning a function that is not selected to analyze
                else:
                    parsing = False
                    continue
            # Analyzing the current line (part of a selected function)
            if parsing:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instr info from text and record in worksheet
                res = parse_rules.scan_arm_instruction(line)
                (addr, instr, bytes, opcode, args, comments) = res
                function_xlsx.record_instruction(wksheet, compiler, row, addr,
                                                 instr, opcode, args, comments)
                arm_results[func_name] += bytes
                # Increment to the next Excel wksheet row
                row += 1
                # # Increment the counnter for this instruction
                # if (opcode in arm_instr.keys()):
                #     arm_instr[opcode][0] += 1
                #     arm_instr[opcode][1].append(args)
                # else:
                #     arm_instr[opcode] = [1, [args]]
                continue
    # Check that the last selected function's totals were saved to the wksheet
    if not last_saved:
        function_xlsx.record_arm_totals(wksheet, arm_results[func_name])

    return arm_results


def scan_arm_file_data(compiler, assemblyfile, optfile):
    """
    Opens and scans the ARM disassembly file to extract data.

    Arguments:
        - compiler          Arm toolchain used to compile the benchmark
        - assemblyfile      Arm disassembly file
        - optfile           Arm config file; selects the functions to parse

    Data:
        - t_size: cumulative function code size (in bytes)

    Returns: t_size
    """
    # Read the config file to know which functions to analyze
    func_opts = config.read_config(optfile)

    # Check that at least one function has been selected for analysis
    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

    arm_results = {}
    # arm_instr = {}

    # Configure the parser
    parse_rules = ParseRules(compiler)

    parsing = False
    fcnt = 0    # function index
    with open(assemblyfile, 'r') as f:
        for line in f:
            # Found the start of a new function
            if parse_rules.is_func_start(line):
                (fname, wname) = parse_rules.get_func_data(line)
                nm, parse, subfunc = func_opts[fcnt]
                fcnt += 1
                if nm != fname:
                    raise Exception('Error: function name does not match func_opts record')
                # Done w/analysis of current function if the new function is not
                #   a subfunction or not set to parse
                if parse and not subfunc:
                    # Setup for the new function
                    func_name = fname
                    # Reset function variables
                    arm_results[func_name] = 0
                    parsing = True
                    continue
                # Beginning to analyze a subfunction of the current function
                elif parse and subfunc:
                    parsing = True
                    continue
                # Beginning a function that is not selected to analyze
                else:
                    parsing = False
                    continue
            # Analyzing the current line (part of a selected function)
            if parsing:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instr info from text
                res = parse_rules.scan_arm_instruction(line)
                (addr, instr, bytes, opcode, args, comments) = res
                arm_results[func_name] += bytes
                # # Increment the counnter for this instruction
                # if (opcode in arm_instr.keys()):
                #     arm_instr[opcode][0] += 1
                #     arm_instr[opcode][1].append(args)
                # else:
                #     arm_instr[opcode] = [1, [args]]
                continue

    # Add up the function sizes for the whole benchmark
    t_size = 0
    for func in arm_results.keys():
        t_size += arm_results[func]

    return t_size
