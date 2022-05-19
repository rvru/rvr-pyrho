"""
Configuration (function selection) file creation and reading functions.

Author: Jennifer Hellar

"""


import importlib
import os
import re

from constants import save_restore_en

# import the class ParseRules from parser.py
ParseRules = getattr(importlib.import_module('parser'), 'ParseRules')


def create_config(compiler, assemblyfile, optfile):
    """
    Parses the input disassembly file to create the default master configuration
    file.

    Arguments:
        compiler        build to pass to the parser
        assemblyfile    disassembly file to parse for function names
        optfile         full filepath for output config file
    """
    # Configure the parser
    parse_rules = ParseRules(compiler)

    # Write out the header
    with open(optfile, 'w') as optf:
        optf.write('{:<50}{:<30}{:<30}\n'.format('function', 'parse (Y/N)', 'sub-function (Y/N)'))

    # Open the appropriate text file
    with open(assemblyfile, 'r') as f:
        for line in f:
            # Found the beginning of a function section
            if parse_rules.is_func_start(line):
                (func_name, wksheet_name) = parse_rules.get_func_data(line)
                sr_flag = save_restore_en \
                        and (wksheet_name.find('__riscv_save') != -1 or \
                             wksheet_name.find('__riscv_restore') != -1)
                if sr_flag:
                    parse = 'Y'
                else:
                    # By default, mark all functions as not selected to analyze
                    parse = 'N'
                # Sometimes, armclang puts code in subfunctions
                if (compiler == 'armclang') and func_name.find('__arm_cp.') != -1:
                    subfunc = 'Y'
                else:
                    subfunc = 'N'
                # Write out the default options for this function
                with open(optfile, 'a') as optf:
                    optf.write('{:<50}{:<30}{:<30}\n'.format(func_name, parse, subfunc))

    return


def create_subconfig(compiler, assemblyfile, optfile, masteropt):
    """
    Creates the sub-configuration file based on the master config file and input
    disassembly file.

    Arguments:
        compiler        build to pass to the parser
        assemblyfile    disassembly file to parse for function names
        optfile         full filepath for output config file
        masteropt       master config file, edited by the user
    """
    # Configure the parser
    parse_rules = ParseRules(compiler)

    # Write out the header
    with open(optfile, 'w') as optf:
        optf.write('{:<50}{:<30}{:<30}\n'.format('function', 'parse (Y/N)', 'sub-function (Y/N)'))

    # Read the master config file and get a list of user-selected functions
    opts = read_config(masteropt)
    funcs_to_parse = [opts[i][0] for i in opts.keys() if opts[i][1]]

    parse = 'N'

    # Open the appropriate text file
    with open(assemblyfile, 'r') as f:
        for line in f:
            # Found the beginning of a function section
            if parse_rules.is_func_start(line):
                (func_name, wksheet_name) = parse_rules.get_func_data(line)
                # Sometimes, armclang puts code in subfunctions
                if (compiler == 'armclang') and func_name.find('__arm_cp.') != -1:
                    subfunc = 'Y'
                else:
                    subfunc = 'N'
                # If this function selected, or previous function selected and
                #   current is a subfunction, then want to analyze it
                if (func_name in funcs_to_parse) \
                    or (parse == 'Y' and subfunc == 'Y'):
                    parse = 'Y'
                else:
                    parse = 'N'
                # Write out the options for this function
                with open(optfile, 'a') as optf:
                    optf.write('{:<50}{:<30}{:<30}\n'.format(func_name, parse, subfunc))

    return


def read_config(optfile):
    """
    Reads a configuration file.

    Arguments:
        optfile         full filepath for the config file

    Returns:
        opts: dictionary of function options
            * Key: function index (integer)
            * Value: list
                0th element: function name
                1st element: boolean indicator for function selected to analyze
                2nd element: boolean indicator for whether function is a subfunc
    """
    opts = {}
    fcnt = 0
    header = True
    # Open the appropriate text file
    with open(optfile, 'r') as f:
        for line in f:
            # First line is a header, so ignore it
            if header:
                header = False
                continue
            linsplit = re.split(' ', line)
            linsplit = [i.strip() for i in linsplit if i.strip() != '']
            # Get the options of the current line
            func_name, parse, subfunc = linsplit
            # Convert Y/N to boolean True/False
            parse = (parse == 'Y')
            subfunc = (subfunc == 'Y')
            opts[fcnt] = [func_name, parse, subfunc]
            fcnt += 1
    return opts


def create_configuration(benchmarkpath):
    """
    Creates the default master configuration file for the input benchmark (must
    provide full directory path).

    Arguments:
        benchmarkpath       full dirpath of requested benchmark
    """
    # Create the config directory if it does not already exist
    outdir = os.path.join(os.getcwd(), 'results')
    configdir = os.path.join(os.getcwd(), outdir, 'config')
    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    # Get the benchmark name
    if benchmarkpath[-1] != '/':
        benchmarkpath += '/'
    lin_split = re.split('/', benchmarkpath[::-1], maxsplit=2)
    benchmark = lin_split[-2][::-1]

    files = os.listdir(benchmarkpath)
    files = [i for i in files if i.find('disassembly') != -1]

    # Use the rvgcc build to create the master selection config file
    rvgccfile = [i for i in files if i.find('rvgcc') != -1][0]
    # Get the full filepath to the rvgcc disassembly and the masteropt
    assemblyfile = os.path.join(benchmarkpath, rvgccfile)
    masteropt = os.path.join(configdir, benchmark + '_' + 'master_selection.txt')
    create_config('rvgcc', assemblyfile, masteropt)


def create_configurations(benchmarkdir):
    """
    Creates the default master configuration files for all of the benchmarks in
    subdirectories of the input parent directory.

    Arguments:
        benchmarkdir       full dirpath of benchmark parent directory
    """
    # Get list of benchmarks as subdirectories of provides parent dir
    filedirs = os.listdir(benchmarkdir)
    benchmarks = [f for f in filedirs if os.path.isdir(os.path.join(benchmarkdir, f))]

    # Create the master config file for each benchmark
    for benchmark in benchmarks:
        print(benchmark)
        benchmarkpath = os.path.join(benchmarkdir, benchmark)
        create_configuration(benchmarkpath)
