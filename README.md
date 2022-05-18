## PyRho parses disassembly text files to analyze code size across toolchains.
----------------------------------------------------------------------------------------------------------------------------
# Features
	* Compares code size results across multiple ISA's and toolchains
		* RISC-V GCC, Arm GCC, Arm Compiler 5, Arm Compiler 6
	* Supports trial 16-bit RISC-V instructions for reducing code size (RVCX)
	* Identifies 32-bit RISC-V instructions replaceable by RVCX
	* Approximates potential RISC-V code size reduction
----------------------------------------------------------------------------------------------------------------------------
## General Information
**PROJECT NAME:** rvr-pyrho

**AUTHOR:** Jennifer Hellar

**DATE:**  05/18/2022

----------------------------------------------------------------------------------------------------------------------------
## Software Setup:

	1. (Optional) Install Excel 2007+
	2. Install Python 3
	3. pip3 install XlsxWriter
	4. Clone this project

----------------------------------------------------------------------------------------------------------------------------
## Software Execution:

	1. Set up the environment $PATH:
```console
source bin/setup_env.sh
```
	2. Create the default configuration files for all benchmarks:
```console
pyrho [path-to-benchmarks] --configure
```
	3. Open the configuration files in results/config/ and select the functions
	to analyze for code size.
	4. Select desired RVCX options in pyrho/constants.py
	5. Analyze single or all benchmarks as desired.

usage: pyrho [-h] [-c] [-a] [--armbuild ARMBUILD] [--rvbuild RVBUILD]
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

Examples:
```console
pyrho ../rvr-hydra/benchmarks/waterman/
pyrho ../rvr-hydra/benchmarks/fir_filter --armbuild armgcc --rvbuild rvgcc
pyrho ../rvr-hydra/benchmarks/ --all
```

----------------------------------------------------------------------------------------------------------------------------
## Script Descriptions:

* main.py
	* Main script; handles command line arguments and calls config or analyze.
* constants.py
	* Defines key constants and RVCX settings.

* config.py
	* Functions to create and read default configuration files per benchmark, as
	well as tool-specific subconfiguration files.
* analyze.py
	* Functions to parse, analyze, and create Excel workbooks for single or all
	benchmarks.

* arm.py
	* Functions to parse Arm disassembly files, extract code size data, and
	create/edit worksheets.
* riscv.py
	* Functions to parse RISC-V disassembly files, extract code size data, and
	create/edit worksheets.

* cx.py
	* Functions to determine compact instruction replacement.
* excel.py
	* Helper functions for Excel workbook/table management.
* summary_xlsx.py
	* Functions to create/modify the Summary worksheet.
* save_restore_xlsx.py
	* Functions to create/modify the riscv_save and riscv_restore worksheets.
* function_xlsx.py
	* Functions to create/modify function-specific worksheets.
* parser.py
	* Parser class for disassembly.

----------------------------------------------------------------------------------------------------------------------------
