import importlib

import excel
import function_xlsx
from constants import *

ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')

def scan_arm_file(compiler, benchmark, armfile):
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

    arm_results = {}
    arm_instr = {}
    curr_state = S_INIT
    wksheet_name = None
    func_name = None
    last_flag = False

    parse_rules = ParseRules(compiler, benchmark)
    f = open(armfile)

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


def scan_arm_file_data(compiler, benchmark, armfile):
    """
    Opens and scans the ARM disassembly file to extract data.

    Data:
        - arm_results
            * Key: function name
            * Val: function code size (in bytes)

    Returns: arm_results
    """

    arm_results = {}
    arm_instr = {}
    curr_state = S_INIT
    wksheet_name = None
    func_name = None
    last_flag = False

    parse_rules = ParseRules(compiler, benchmark)
    f = open(armfile)

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
                arm_results[func_name] += bytes

                if (opcode in arm_instr.keys()):
                    arm_instr[opcode][0] += 1
                    arm_instr[opcode][1].append(args)
                else:
                    arm_instr[opcode] = [1, [args]]

                continue

        if (curr_state == S_FUNC_END):
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
                # Reset function variables
                arm_results[func_name] = 0
                curr_state = S_FUNC_PARSE
                continue
            else:
                curr_state = S_WAIT

    f.close()

    t_size = 0
    for func in arm_results.keys():
        t_size += arm_results[func]

    return t_size
