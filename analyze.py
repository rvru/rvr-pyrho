"""
Single benchmark or benchmark suite-level analysis functions.

Author: Jennifer Hellar (jenniferhellar@proton.me)

"""


# Built-in libraries to handle command line inputs/outputs/execution results
import os
import re

# Supplementary python scripts
import summary_xlsx
import save_restore_xlsx
import excel
import arm
import riscv
from constants import *


def single_benchmark(armbuild, rvbuild, benchmarkpath, output_file):
    # Extract compilation source and benchmark name
    if benchmarkpath[-1] != '/':
        benchmarkpath += '/'
    lin_split = re.split('/', benchmarkpath[::-1], maxsplit=2)
    benchmark = lin_split[-2][::-1]

    # Check the inputs
    if (benchmark not in BENCHMARKS):
        raise Exception('Unknown benchmark ' + benchmark + '. Please choose from:\n\t[' + ', '.join(BENCHMARKS) + ']')

    files = os.listdir(benchmarkpath)
    files = [i for i in files if i.find('disassembly') != -1]

    rvfiles = [i for i in files if i[:i.index('_')].find('rv') != -1]
    armfiles = [i for i in files if i[:i.index('_')].find('arm') != -1]

    rvbuilds = [i[:i.index('_')] for i in rvfiles]
    armbuilds = [i[:i.index('_')] for i in armfiles]

    if rvbuild not in rvbuilds:
        raise Exception('RISC-V disassembly for \'' + rvbuild + '\' unavailable. Please compile or choose from:\n\t[' + ', '.join(rvbuilds) + ']')
    if armbuild not in armbuilds:
        raise Exception('ARM disassembly for \'' + armbuild + '\' unavailable. Please compile or choose from:\n\t[' + ', '.join(armbuilds) + ']')

    rvfile = os.path.join(benchmarkpath, rvbuild + '_' + benchmark + '_disassembly.txt')
    armfile = os.path.join(benchmarkpath, armbuild + '_' + benchmark + '_disassembly.txt')
    if (os.path.exists(rvfile) is False):
        raise Exception('Unable to find expected RISC-V disassembly:\n\t' + rvfile)
    if (os.path.exists(armfile) is False):
        raise Exception('Unable to find expected Arm disassembly:\n\t' + armfile)

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

    # Create Summary worksheet; write input files to A1, A2; set column sizes
    # Do this first so that it shows up as the first sheet in the workbook
    sum_wksheet = summary_xlsx.create_summary(False, rvfile, armfile)

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

    configdir = os.path.join(os.getcwd(), outdir, 'config')
    if not os.path.isdir(configdir):
        os.makedirs(configdir)
    rvoptfile = os.path.join(configdir, benchmark + '_' + rvbuild + '_function_selection.txt')
    armoptfile = os.path.join(configdir, benchmark + '_' + armbuild + '_function_selection.txt')

    # Parse the input files
    res = riscv.scan_riscv_file(rvbuild, rvfile, rvoptfile)
    (riscv_results, riscv_reductions, riscv_pairs, riscv_instr, riscv_formats) = res

    # for instr in sorted(riscv_instr.keys()):
    #     print("{:<30}{:<30}".format(instr, riscv_instr[instr]))

    arm_results = arm.scan_arm_file(armbuild, armfile, armoptfile)

    # Add the main table to record individual function totals
    row = 18
    col = 1
    summary_xlsx.add_main_table(row, col, False, rvbuild, armbuild)

    # Add the totals table to record overall benchmark totals
    row = 3
    col = 1
    summary_xlsx.add_totals_table(row, col, False, rvbuild, armbuild)

    # Write out the results to the Summary worksheet
    summary_xlsx.record_rvgcc_data(riscv_results, riscv_reductions, rvbuild)
    summary_xlsx.record_arm_data(riscv_results, arm_results, rvbuild, armbuild)

    # Record replaced instruction performance
    reductions = [riscv_reductions]
    summary_xlsx.add_replaced_instr_table(reductions, rvbuild, armbuild)

    # Add a chart to visualize the replaced instruction performance
    compilers = [rvbuild]
    summary_xlsx.add_replaced_instr_chart(compilers)

    # Record the rules used to implement new replaced instructions
    summary_xlsx.add_replacement_rules_table()

    # Record the frequency of instructions
    summary_xlsx.add_total_instr_table(riscv_instr, 20, rvbuild)

    # Record the frequency of instruction pairs
    summary_xlsx.add_pairs_table(riscv_pairs, 20, rvbuild, armbuild)

    # Record the frequency of instruction formats to 'tmp' worksheet
    formats = [riscv_formats]
    summary_xlsx.add_instr_formats_tables(formats, compilers)

    # Add a chart to visualize the instruction format frequency distribution
    summary_xlsx.add_instr_formats_radar(rvbuild)

    # Record function contribution to overshooting ARM code size
    summary_xlsx.add_overshoot_table(riscv_results, arm_results, 5, rvbuild)

    # Add a chart to visualize the function overshoot over ARM code size
    summary_xlsx.add_overshoot_chart(rvbuild)

    excel.close_workbook()
    print('\nComplete! See Excel workbook: ')
    print('\t' + output_file)


def all_benchmarks(armbuild, rvbuild, benchmarkdir, output_file):


    """ Excel Workbook Creation """

    # Default to same directory as input
    outdir = os.path.join(os.getcwd(), 'results')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if output_file is None:
    	output_file = 'all_benchmarks_analysis.xlsx'
    if output_file[-5:] != '.xlsx':
        output_file += '.xlsx'
    output_file = os.path.join(outdir, output_file)
    excel.create_workbook(output_file)

    configdir = os.path.join(os.getcwd(), outdir, 'config')
    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    # Create Summary worksheet; write input files to A1, A2; set column sizes
    # Do this first so that it shows up as the first sheet in the workbook
    sum_wksheet = summary_xlsx.create_summary(True)

    # Add the main table to record individual function totals
    row = 18
    col = 1
    summary_xlsx.add_main_table(row, col, True)

    # Add the totals table to record overall benchmark totals
    row = 3
    col = 1
    summary_xlsx.add_totals_table(row, col, True)

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

    filedirs = os.listdir(benchmarkdir)
    benchmarks = [f for f in filedirs if os.path.isdir(os.path.join(benchmarkdir, f))]

    results = {}
    for build in BUILDS:
        results[build] = {}

    for benchmark in benchmarks:
        print('\n' + benchmark)
        benchmarkpath = os.path.join(benchmarkdir, benchmark)
        files = os.listdir(benchmarkpath)
        files = [i for i in files if i.find('disassembly') != -1]

        rvfiles = [i for i in files if i[:i.index('_')].find('rv') != -1]
        armfiles = [i for i in files if i[:i.index('_')].find('arm') != -1]

        rvbuilds = [i[:i.index('_')] for i in rvfiles]
        armbuilds = [i[:i.index('_')] for i in armfiles]

        for i in range(len(rvbuilds)):
            build = rvbuilds[i]
            # print('\t' + build)
            rvfile = os.path.join(benchmarkpath, rvfiles[i])
            rvoptfile = os.path.join(configdir, benchmark + '_' + build + '_function_selection.txt')
            # Parse the input files
            res = riscv.scan_riscv_file_data(build, rvfile, rvoptfile)
            # (size, reductions, pairs, instr, formats) = res
            results[build][benchmark] = res

        for i in range(len(armbuilds)):
            build = armbuilds[i]
            # print('\t' + build)
            armfile = os.path.join(benchmarkpath, armfiles[i])
            armoptfile = os.path.join(configdir, benchmark + '_' + build + '_function_selection.txt')
            res = arm.scan_arm_file_data(build, armfile, armoptfile)
            results[build][benchmark] = res

        # print('\n')
    summary_xlsx.record_all_main(results, benchmarks)
    excel.close_workbook()
    print('\nComplete! See Excel workbook: ')
    print('\t' + output_file)
