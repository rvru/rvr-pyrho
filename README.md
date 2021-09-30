## PyRho parses disassembly text files to analyze code size across toolchains.
----------------------------------------------------------------------------------------------------------------------------
# Features
	* Compares code size results across multiple ISA's and toolchains
		* RVGCC, IAR, ARM
	* Supports trial 16-bit RISC-V instructions for reducing code size (RVCX)
	* Identifies 32-bit RISC-V instructions replaceable by RVCX
	* Approximates potential RISC-V code size reduction
----------------------------------------------------------------------------------------------------------------------------
## General Information
**PROJECT NAME:** rvr-pyrho

**AUTHOR:** Jennifer Hellar <jennifer.hellar [at] rice.edu>

**DATE:**  10/01/2021

----------------------------------------------------------------------------------------------------------------------------
## Software Setup:

	1. (Optional) Install Excel 2007+
	2. Install Python 3
	3. pip3 install XlsxWriter
	4. Clone this project

----------------------------------------------------------------------------------------------------------------------------
## Software Execution:

	1. Select desired options in constants.py
	2. Execute on the command line:

usage: main.py [-h] rvgcc-file [output-file]

PyRho, A Code Density Analyzer

positional arguments:
* rvgcc-file  
	* rvgcc disassembly text file
* output-file       
	* (optional) filename for the output excel file

Example:

* python3 main.py ../rvr-hydra/benchmarks/fir_filter/rvgcc_fir_filter_disassembly.txt

----------------------------------------------------------------------------------------------------------------------------
## Script Descriptions:

* main.py													 
	* Main script; state machine for parsing input files
* constants.py									
	* Defines constants used by multiple scripts
* cx.py													
	* Functions to determine compact instruction replacement
* excel.py											
	* Helper functions for Excel workbook/table management
* summary_xlsx.py								
	* Functions to create/modify the Summary worksheet
* save_restore_xlsx.py
	* Functions to create/modify the riscv_save and riscv_restore worksheets
* function_xlsx.py							
	* Functions to create/modify function-specific worksheets
* parser.py					
	* Parser class for RVA-compiled or IAR-compiled disassembly

----------------------------------------------------------------------------------------------------------------------------
## Script Dependencies:

* main.py
	* constants.py
	* cx.py
	* excel.py
	* summary_xlsx.py
	* save_restore_xlsx.py
	* function_xlsx.py
	* parser.py
* constants.py
* cx.py
	* constants.py
* excel.py
	* constants.py
* summary_xlsx.py
	* constants.py
	* excel.py
* save_restore_xlsx.py
	* constants.py
	* excel.py
* function_xlsx.py
	* constants.py
	* excel.py
* parser.py
	* constants.py
	* excel.py

----------------------------------------------------------------------------------------------------------------------------
