"""
Configuration (function selection) file creation and reading functions.

Author: Jennifer Hellar (jenniferhellar@proton.me)

"""


import importlib
import os
import re

from constants import save_restore_en

ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')

def create_config(compiler, assemblyfile, optfile):
    parse_rules = ParseRules(compiler)

    with open(optfile, 'w') as optf:
        optf.write('{:<50}{:<30}{:<30}\n'.format('function', 'parse (Y/N)', 'sub-function (Y/N)'))

    # Open the appropriate text file
    with open(assemblyfile, 'r') as f:
        for line in f:
            if parse_rules.is_func_start(line):
                (func_name, wksheet_name) = parse_rules.get_func_data(line)
                sr_flag = save_restore_en and (wksheet_name.find('__riscv_save') != -1 \
                        or wksheet_name.find('__riscv_restore') != -1)
                if sr_flag:
                    parse = 'Y'
                else:
                    parse = 'N'
                if (compiler == 'armclang') and func_name.find('__arm_cp.') != -1:
                    subfunc = 'Y'
                else:
                    subfunc = 'N'
                with open(optfile, 'a') as optf:
                    optf.write('{:<50}{:<30}{:<30}\n'.format(func_name, parse, subfunc))

    return


def create_subconfig(compiler, assemblyfile, optfile, masteropt):
    parse_rules = ParseRules(compiler)

    with open(optfile, 'w') as optf:
        optf.write('{:<50}{:<30}{:<30}\n'.format('function', 'parse (Y/N)', 'sub-function (Y/N)'))

    opts = read_config(masteropt)
    funcs_to_parse = [opts[i][0] for i in opts.keys() if opts[i][1]]

    parse = 'N'

    # Open the appropriate text file
    with open(assemblyfile, 'r') as f:
        for line in f:
            if parse_rules.is_func_start(line):
                (func_name, wksheet_name) = parse_rules.get_func_data(line)
                if (compiler == 'armclang') and func_name.find('__arm_cp.') != -1:
                    subfunc = 'Y'
                else:
                    subfunc = 'N'
                if (func_name in funcs_to_parse) \
                    or (parse == 'Y' and subfunc == 'Y'):
                    parse = 'Y'
                else:
                    parse = 'N'
                with open(optfile, 'a') as optf:
                    optf.write('{:<50}{:<30}{:<30}\n'.format(func_name, parse, subfunc))

    return


def read_config(optfile):
    opts = {}
    fcnt = 0
    header = True
    with open(optfile, 'r') as f:
        for line in f:
            if header:
                header = False
                continue
            linsplit = re.split(' ', line)
            linsplit = [i.strip() for i in linsplit if i.strip() != '']
            func_name, parse, subfunc = linsplit
            parse = (parse == 'Y')
            subfunc = (subfunc == 'Y')
            opts[fcnt] = [func_name, parse, subfunc]
            fcnt += 1
    return opts


def create_configuration(benchmarkpath):
    # Default to same directory as input
    outdir = os.path.join(os.getcwd(), 'results')
    configdir = os.path.join(os.getcwd(), outdir, 'config')
    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    if benchmarkpath[-1] != '/':
        benchmarkpath += '/'
    lin_split = re.split('/', benchmarkpath[::-1], maxsplit=2)
    benchmark = lin_split[-2][::-1]

    files = os.listdir(benchmarkpath)
    files = [i for i in files if i.find('disassembly') != -1]

    builds = [i[:i.index('_')] for i in files]

    rvgccfile = [i for i in files if i.find('rvgcc') != -1][0]
    assemblyfile = os.path.join(benchmarkpath, rvgccfile)
    masteropt = os.path.join(configdir, benchmark + '_' + 'master_selection.txt')
    create_config('rvgcc', assemblyfile, masteropt)


def create_configurations(benchmarkdir):

    filedirs = os.listdir(benchmarkdir)
    benchmarks = [f for f in filedirs if os.path.isdir(os.path.join(benchmarkdir, f))]

    for benchmark in benchmarks:
        print(benchmark)
        benchmarkpath = os.path.join(benchmarkdir, benchmark)
        create_configuration(benchmarkpath)
