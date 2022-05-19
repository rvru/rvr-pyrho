"""
RISC-V Disassembly Scanner Functions

Author: Jennifer Hellar (jenniferhellar@proton.me)

"""


import importlib
import os
import re

# local scripts
import excel
import cx
import function_xlsx
from constants import *
import config

ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')

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


def scan_riscv_file(compiler, assemblyfile, optfile):
    """
    Opens and scans the RISC-V disassembly file to extract data and update
    Excel workbook.

    Arguments:
        - compiler          RISC-V toolchain used to compile the benchmark
        - assemblyfile      RISC-V disassembly file
        - optfile           RISC-V config file; selects the functions to parse

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
    # Some available counters to aggregate details about specific instructions
    addioffsetcnt_en = False
    lwcnt_en = False
    sllicnt_en = False
    subcnt_en = False
    if addioffsetcnt_en:
        addioffset = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0}
    if lwcnt_en:
        lwcnt = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0}
    if sllicnt_en:
        sllicnt = {0: 0, 1:0, 2:0, 3:0, 4:0}
    if subcnt_en:
        subcnt = {0: 0, 1:0, 2:0, 3:0, 4:0}

    # Read the config file to know which functions to analyze
    func_opts = config.read_config(optfile)

    # Check that at least one function has been selected for analysis
    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

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
                    if (wksheet_name == '__riscv_save'):
                        # Increment total for save_0, save_1, etc.
                        if (f_size > 0):
                            curr = results['__riscv_save'][0]
                            results['__riscv_save'] = (curr + f_size, {}, {}, {}, 0)
                    elif (wksheet_name == '__riscv_restore'):
                        # Increment total for restore_0, restore_1, etc.
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
                            # If number of bits too high, not able to us cx.lwpc
                            if (res is False):
                                f_reductions['cx.lwpc'] = 0
                                # Revert back to original 32-bit LW
                                if 'lw' in f_instr.keys():
                                    f_instr['lw'] += f_instr['cx.lwpc']
                                else:
                                    f_instr['lw'] = f_instr['cx.lwpc']
                                f_instr['cx.lwpc'] = 0
                                lwpc_fail = True

                        # Add function totals to the overall benchmark totals
                        res = update_tot(t_reductions, t_pairs, t_instr,
                                         t_formats, f_reductions, f_pairs,
                                         f_instr, f_formats)
                        (t_reductions, t_pairs, t_instr, t_formats) = res
                        # Save the function results and record in Excel worksheet
                        results[func_name] = (f_size, f_reductions, f_instr,
                                                f_formats, f_bits)
                        function_xlsx.record_riscv_totals(wksheet, compiler,
                                                          f_size, f_reductions)
                        function_xlsx.add_tables_charts_marks(wksheet, compiler,
                                                              f_instr, f_formats,
                                                              replaced_loc,
                                                              not_repl_loc,
                                                              lwpc_fail,
                                                              pair_loc)
                    last_saved = True
                # Beginning a new function to analyze and not a subfunction
                if parse and not subfunc:
                    # Create and format new worksheet
                    (func_name, wksheet_name) = parse_rules.get_func_data(line)
                    if (wksheet_name == '__riscv_save'):
                        wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                        # Some functions grouped/have same definition in assembly
                        num = int(re.split('_', func_name)[-1])
                        if (num < 4):
                            tbl = SAVE_RVGCC_A_TABLE
                        elif (num < 8):
                            tbl = SAVE_RVGCC_B_TABLE
                        elif (num < 12):
                            tbl = SAVE_RVGCC_C_TABLE
                        else:
                            tbl = SAVE_RVGCC_D_TABLE

                        row = excel.get_table_loc(tbl)[0] + 3
                        f_size = 0
                    elif (wksheet_name == '__riscv_restore'):
                        wksheet = excel.wkbook.get_worksheet_by_name(wksheet_name)
                        num = int(re.split('_', func_name)[-1])
                        if (num < 4):
                            tbl = RESTORE_RVGCC_A_TABLE
                        elif (num < 8):
                            tbl = RESTORE_RVGCC_B_TABLE
                        elif (num < 12):
                            tbl = RESTORE_RVGCC_C_TABLE
                        else:
                            tbl = RESTORE_RVGCC_D_TABLE

                        row = excel.get_table_loc(tbl)[0] + 3
                        f_size = 0
                    elif (wksheet_name is not None):
                        wksheet = function_xlsx.create_sheet(func_name,
                                                             wksheet_name)
                        function_xlsx.record_func_name(wksheet, func_name)
                        # Place instruction data starting below the headers
                        row = excel.get_table_loc(RVGCC_TABLE)[0] + 3
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
                        results[func_name] = (f_size, f_reductions, f_instr,
                                              f_formats, f_bits)
                        # Reset offset trackers
                        lwpc_fail = False
                        max_offset = 0
                        min_offset = float("inf")
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
                # Extract instruction data from line of text and record
                if (compiler == 'rvgcc'):
                    ret = parse_rules.scan_rvgcc_instruction(line)
                    (addr, instr, bytes, opcode, args, comments) = ret
                    # Explicitly mark RVC instructions for readability
                    if (bytes == 2):
                        opcode = 'c.' + opcode
                    # GCC does not differentiate these sub-types
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
                elif (compiler == 'rviar'):
                    ret = parse_rules.scan_iar_instruction(line)
                    (addr, instr, bytes, opcode, args) = ret
                    comments = ''
                # __riscv_save and __riscv_restore functions are unique
                if (wksheet_name == '__riscv_save') \
                        or (wksheet_name == '__riscv_restore'):
                    save_restore_xlsx.record_instruction(wksheet, compiler,
                                                         tbl, row, addr, instr,
                                                         opcode, args, comments)
                else:
                    function_xlsx.record_instruction(wksheet, compiler,
                                                     row, addr, instr, opcode,
                                                     args, comments)

                # Increment function code size by this instruction size
                f_size += bytes

                # Parse for replaceable instructions
                if (wksheet_name != '__riscv_save') \
                        and (wksheet_name != '__riscv_restore'):
                    replaceable = False
                    # 32-bit instruction
                    if (bytes > 2):
                        # Increment appropriate instruction format label
                        instr_type = RV32_INSTR_FORMATS[opcode]
                        if (instr_type[0] not in RV32_FORMATS):
                            # Pseudoinstruction, get label of base instruction
                            for i in range(len(instr_type)):
                                lbl = RV32_INSTR_FORMATS[instr_type[i]][0]
                                f_formats[lbl][instr_type[i]] += 1
                        else:
                            f_formats[instr_type[0]][opcode] += 1
                        # Check if replaceable
                        res = cx.check_replaceable(opcode, args, comments,
                                                   max_offset, min_offset,
                                                   addr)
                        replaceable = res[0]
                        (r2, r1, offset) = res[1]
                        max_offset, min_offset, type_code = res[2:5]

                        # Record reduction in func_reductions and write comment
                        if (replaceable):
                            opcode = type_code
                            # Replacement by 16-bit instruction
                            if (opcode[:2] == 'c.') or (opcode[:2] == 'cx'):
                                f_reductions[opcode] += 2
                            function_xlsx.record_comments(wksheet, compiler,
                                                          row, opcode,
                                                          (r2, r1, offset))
                            replaced_loc[opcode].append(row)
                            f_instr[opcode] += 1
                        else:
                            if opcode in f_instr.keys():
                                f_instr[opcode] += 1
                            else:
                                f_instr[opcode] = 1
                    # 16-bit instruction
                    else:
                        # C.ADDI is unique since we are proposing to remove it
                        if (opcode == 'c.addi') and (addi_subi_en):
                            if (compiler == 'rviar'):
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

                if ((opcode == 'c.addi') or (opcode == 'addi')) \
                        and (compiler == 'rvgcc') and addioffsetcnt_en:
                    num = int(args[-1])
                    if (num <= -256):
                        addioffset[0] += 1
                    elif (num <= -32):
                        addioffset[1] += 1
                    elif (num < 0):
                        addioffset[2] += 1
                    elif (num < 32):
                        addioffset[3] += 1
                    elif (num < 256):
                        addioffset[4] += 1
                    else:
                        addioffset[5] += 1

                # if (opcode == 'addi') and addioffsetcnt_en:
                #     reg1 = args[0]
                #     reg2 = args[1]
                #     immed = abs(int(args[2], 16))
                #     if (reg1 != reg2) and (immed >= 32):
                #         addioffset[2] += 1
                #     elif (reg1 != reg2):
                #         addioffset[0] += 1
                #     elif (immed >= 32):
                #         addioffset[1] += 1
                #     else:
                #         addioffset[4] += 1
                #     print(func_name)
                #     print(args)

                if (opcode == 'lw') and lwcnt_en:
                    reg1 = args[0]
                    reg2 = args[1].split('(')[1][:-1]
                    off = int(args[1].split('(')[0], 16)
                    regs_okay = (reg1 in REG_LIST) and (reg2 in REG_LIST)
                    off_okay = (abs(off) < 128) and (off >= 0)
                    if (regs_okay is False) and (off_okay is False):
                        lwcnt[4] += 1
                    if (regs_okay is True) and (off_okay is False):
                        if (abs(off) >= 128) and (off > 0):
                            lwcnt[1] += 1
                        if (abs(off) < 128) and (off < 0):
                            lwcnt[2] += 1
                        if (abs(off) >= 128) and (off < 0):
                            lwcnt[3] += 1
                    if (regs_okay is False) and (off_okay is True):
                        if (reg1 not in REG_LIST) or (reg2 not in REG_LIST):
                            lwcnt[0] += 1
                elif (opcode == 'cx.lwpc'):
                    lwcnt[5] += 1

                if (opcode == 'slli') and sllicnt_en:
                    rd = args[0]
                    rs1 = args[1]
                    if (rd != rs1):
                        sllicnt[4] += 1
                    if (rd in REG_LIST) and (rs1 not in REG_LIST):
                        sllicnt[0] += 1
                    if (rs1 in REG_LIST) and (rd not in REG_LIST):
                        sllicnt[1] += 1
                    if (rd in REG_LIST) and (rs1 in REG_LIST):
                        sllicnt[2] += 1
                    if (rd not in REG_LIST) and (rs1 not in REG_LIST):
                        sllicnt[3] += 1

                if (opcode == 'sub') and subcnt_en:
                    subcnt[0] += 1
                    rd = args[0]
                    rs1 = args[1]
                    rs2 = args[2]
                    if (rd != rs1) and ((rd not in REG_LIST) or
                                        (rs1 not in REG_LIST) or
                                        (rs2 not in REG_LIST)):
                        subcnt[1] += 1
                    elif (rd != rs1):
                        subcnt[2] += 1
                    elif (rd not in REG_LIST) or (rs1 not in REG_LIST) or \
                            (rs2 not in REG_LIST):
                        subcnt[3] += 1
                    else:
                        subcnt[4] += 1

                # Move to next row of worksheet for next instruction
                row += 1
                continue

    # Check that the last selected function's totals were saved to the wksheet
    if not last_saved:
        if (wksheet_name == '__riscv_save'):
            # Increment total for save_0, save_1, etc.
            if (f_size > 0):
                curr = results['__riscv_save'][0]
                results['__riscv_save'] = (curr + f_size, {}, {}, {}, 0)
        elif (wksheet_name == '__riscv_restore'):
            # Increment total for restore_0, restore_1, etc.
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
                # If number of bits too high, not able to us cx.lwpc
                if (res is False):
                    f_reductions['cx.lwpc'] = 0
                    # Revert back to original 32-bit LW
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
        if record:
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


    if addioffsetcnt_en:
        print("\naddi offset counters:\n")
        print("{:<30s}{:<5d}".format(compiler + " data0", addioffset[0]))
        print("{:<30s}{:<5d}".format(compiler + " data1", addioffset[1]))
        print("{:<30s}{:<5d}".format(compiler + " data2", addioffset[2]))
        print("{:<30s}{:<5d}".format(compiler + " data3", addioffset[3]))
        print("{:<30s}{:<5d}".format(compiler + " data4", addioffset[4]))
        print("{:<30s}{:<5d}".format(compiler + " data5", addioffset[5]))
    if lwcnt_en:
        print("\nlw counters:\n")
        print("{:<30s}{:<5d}".format(compiler + " data0", lwcnt[0]))
        print("{:<30s}{:<5d}".format(compiler + " data1", lwcnt[1]))
        print("{:<30s}{:<5d}".format(compiler + " data2", lwcnt[2]))
        print("{:<30s}{:<5d}".format(compiler + " data3", lwcnt[3]))
        print("{:<30s}{:<5d}".format(compiler + " data4", lwcnt[4]))
        print("{:<30s}{:<5d}".format(compiler + " data5", lwcnt[5]))
    if sllicnt_en:
        print("\nslli counters:\n")
        print("{:<30s}{:<5d}".format(compiler + " data0", sllicnt[0]))
        print("{:<30s}{:<5d}".format(compiler + " data1", sllicnt[1]))
        print("{:<30s}{:<5d}".format(compiler + " data2", sllicnt[2]))
        print("{:<30s}{:<5d}".format(compiler + " data3", sllicnt[3]))
        print("{:<30s}{:<5d}".format(compiler + " data4", sllicnt[4]))
    if subcnt_en:
        print("\nsub counters:\n")
        print("{:<30s}{:<5d}".format(compiler + " data0", subcnt[0]))
        print("{:<30s}{:<5d}".format(compiler + " data1", subcnt[1]))
        print("{:<30s}{:<5d}".format(compiler + " data2", subcnt[2]))
        print("{:<30s}{:<5d}".format(compiler + " data3", subcnt[3]))
        print("{:<30s}{:<5d}".format(compiler + " data4", subcnt[4]))

    r = (results, t_reductions, t_pairs, t_instr, t_formats)
    return r


def scan_riscv_file_data(compiler, assemblyfile, optfile):
    """
    Opens and scans the RISC-V disassembly file to extract data.

    Arguments:
        - compiler          RISC-V toolchain used to compile the benchmark
        - assemblyfile      RISC-V disassembly file
        - optfile           RISC-V config file; selects the functions to parse

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
        - t_size:
            * Total code size of all parsed functions
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
    # Read the config file to know which functions to analyze
    func_opts = config.read_config(optfile)

    # Check that at least one function has been selected for analysis
    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

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
                    if (wksheet_name == '__riscv_save'):
                        # Increment total for save_0, save_1, etc.
                        if (f_size > 0):
                            curr = results['__riscv_save'][0]
                            results['__riscv_save'] = (curr + f_size, {}, {}, {}, 0)
                    elif (wksheet_name == '__riscv_restore'):
                        # Increment total for restore_0, restore_1, etc.
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
                            # If number of bits too high, not able to us cx.lwpc
                            if (res is False):
                                f_reductions['cx.lwpc'] = 0
                                # Revert back to original 32-bit LW
                                if 'lw' in f_instr.keys():
                                    f_instr['lw'] += f_instr['cx.lwpc']
                                else:
                                    f_instr['lw'] = f_instr['cx.lwpc']
                                f_instr['cx.lwpc'] = 0
                                lwpc_fail = True

                        # Add function totals to the overall benchmark totals
                        res = update_tot(t_reductions, t_pairs, t_instr,
                                         t_formats, f_reductions, f_pairs,
                                         f_instr, f_formats)
                        (t_reductions, t_pairs, t_instr, t_formats) = res
                        # Save the function results and record in Excel worksheet
                        results[func_name] = (f_size, f_reductions, f_instr, f_formats,
                                              f_bits)
                    last_saved = True
                # Beginning a new function to analyze and not a subfunction
                if parse and not subfunc:
                    # Create and format new worksheet
                    (func_name, wksheet_name) = parse_rules.get_func_data(line)
                    if (wksheet_name == '__riscv_save') or (wksheet_name == '__riscv_restore'):
                        f_size = 0
                        continue
                    elif (wksheet_name is not None):
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
                        results[func_name] = (f_size, f_reductions, f_instr,
                                              f_formats, f_bits)
                        # Reset offset trackers
                        lwpc_fail = False
                        max_offset = 0
                        min_offset = float("inf")
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
                # Extract instruction data from line of text and record
                if (compiler == 'rvgcc'):
                    ret = parse_rules.scan_rvgcc_instruction(line)
                    (addr, instr, bytes, opcode, args, comments) = ret
                    # Explicitly mark RVC instructions for readability
                    if (bytes == 2):
                        opcode = 'c.' + opcode
                    # GCC does not differentiate these sub-types
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
                elif (compiler == 'IAR'):
                    ret = parse_rules.scan_iar_instruction(line)
                    (addr, instr, bytes, opcode, args) = ret
                    comments = None
                # Increment function code size by this instruction size
                f_size += bytes

                # Parse for replaceable instructions
                if (wksheet_name != '__riscv_save') \
                        and (wksheet_name != '__riscv_restore'):
                    replaceable = False
                    # 32-bit instruction
                    if (bytes > 2):
                        # Increment appropriate instruction format label
                        instr_type = RV32_INSTR_FORMATS[opcode]
                        if (instr_type[0] not in RV32_FORMATS):
                            # Pseudoinstruction, get label of base instruction
                            for i in range(len(instr_type)):
                                lbl = RV32_INSTR_FORMATS[instr_type[i]][0]
                                f_formats[lbl][instr_type[i]] += 1
                        else:
                            f_formats[instr_type[0]][opcode] += 1
                        # Check if replaceable
                        res = cx.check_replaceable(opcode, args, comments,
                                                   max_offset, min_offset,
                                                   addr)
                        replaceable = res[0]
                        (r2, r1, offset) = res[1]
                        max_offset, min_offset, type_code = res[2:5]

                        # Record reduction in func_reductions and write comment
                        if (replaceable):
                            opcode = type_code
                            # Replacement by 16-bit instruction
                            if (opcode[:2] == 'c.') or (opcode[:2] == 'cx'):
                                f_reductions[opcode] += 2
                            f_instr[opcode] += 1
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

                prev_op = opcode
                prev_args = args
                continue

    # Check that the last selected function's totals were saved to the wksheet
    if not last_saved:
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

            # Add function totals to the overall benchmark totals
            res = update_tot(t_reductions, t_pairs, t_instr,
                             t_formats, f_reductions, f_pairs,
                             f_instr, f_formats)
            (t_reductions, t_pairs, t_instr, t_formats) = res
            # Save the function results and record in Excel worksheet
            results[func_name] = (f_size, f_reductions, f_instr, f_formats,
                                  f_bits)
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

    t_size = 0
    for func in results.keys():
        t_size += results[func][0]

    r = (t_size, t_reductions, t_pairs, t_instr, t_formats)
    return r
