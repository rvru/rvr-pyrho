"""
Arm Disassembly Scanner Functions

Author: Jennifer Hellar (jenniferhellar@proton.me)

"""


import importlib
import os

# local scripts
import excel
import function_xlsx
import config
from constants import *

ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')


def scan_arm_file(compiler, armfile, optfile):
    """
    Opens and scans the ARM disassembly file to extract data and save to Excel
    workbook.

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

    optflag = os.path.exists(optfile)
    if not optflag:
        config.create_config(compiler, armfile, optfile)
        print('New function selection file(s) created. Please verify:')
        print('\t', optfile)
        exit(0)
    func_opts = config.read_config(optfile)

    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

    arm_results = {}
    arm_instr = {}

    parse_rules = ParseRules(compiler)

    parsing = False
    last_saved = False
    fcnt = 0
    with open(armfile, 'r') as f:
        for line in f:
            # found the start of a new function
            if parse_rules.is_func_start(line):
                (fname, wname) = parse_rules.get_func_data(line)
                nm, parse, subfunc = func_opts[fcnt]
                fcnt += 1
                if nm != fname:
                    raise Exception('Error: function name does not match func_opts record')
                # done w/current if new function is not a subfunction or not set
                # to parse
                if parsing and (not subfunc or not parse):
                    # record current function totals
                    function_xlsx.record_arm_totals(wksheet,
                                                    arm_results[func_name])
                    last_saved = True
                # a new function to parse and not a subfunction
                if parse and not subfunc:
                    # setup for the new function
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
                # a subfunction of the previous function
                elif parse and subfunc:
                    parsing = True
                    continue
                else:
                    parsing = False
                    continue
            if parsing:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instr info from text and record in worksheet
                res = parse_rules.scan_arm_instruction(line)
                (addr, instr, bytes, opcode, args, comments) = res
                if wksheet is None:
                    print(line)
                function_xlsx.record_instruction(wksheet, compiler, row, addr,
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

    if not last_saved:
        function_xlsx.record_arm_totals(wksheet, arm_results[func_name])

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


def scan_arm_file_data(compiler, armfile, optfile):
    """
    Opens and scans the ARM disassembly file to extract data.

    Data:
        - t_size: cumulative function code size (in bytes)

    Returns: t_size
    """
    func_opts = config.read_config(optfile)

    funcs_to_parse = [func_opts[i][0] for i in func_opts.keys() if func_opts[i][1]]
    if len(funcs_to_parse) == 0:
        raise Exception('Please select at least one function to parse in ' + optfile)

    arm_results = {}
    arm_instr = {}

    parse_rules = ParseRules(compiler)

    parsing = False
    last_saved = False
    fcnt = 0
    with open(armfile, 'r') as f:
        for line in f:
            # found the start of a new function
            if parse_rules.is_func_start(line):
                (fname, wname) = parse_rules.get_func_data(line)
                nm, parse, subfunc = func_opts[fcnt]
                fcnt += 1
                if nm != fname:
                    raise Exception('Error: function name does not match func_opts record')
                # a new function to parse and not a subfunction
                if parse and not subfunc:
                    # setup for the new function
                    func_name = fname
                    # Reset function variables
                    arm_results[func_name] = 0
                    last_saved = False
                    parsing = True
                    continue
                # a subfunction of the previous function
                elif parse and subfunc:
                    parsing = True
                    continue
                else:
                    parsing = False
                    continue
            if parsing:
                if parse_rules.is_skippable(line):
                    continue
                # Extract instr info from text and record in worksheet
                res = parse_rules.scan_arm_instruction(line)
                (addr, instr, bytes, opcode, args, comments) = res
                arm_results[func_name] += bytes

                if (opcode in arm_instr.keys()):
                    arm_instr[opcode][0] += 1
                    arm_instr[opcode][1].append(args)
                else:
                    arm_instr[opcode] = [1, [args]]
                continue

    t_size = 0
    for func in arm_results.keys():
        t_size += arm_results[func]

    return t_size