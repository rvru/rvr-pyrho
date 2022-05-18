
"""
Excel Save/Restore Functions Worksheet

This file contains functions for creating/modifying save/restore worksheets.

Author: Jennifer Hellar (jennifer.hellar@rice.edu)

"""

import xlsxwriter

import excel
from constants import *


def create_sheet(name):
    """
    Adds a new worksheet to an open Excel workbook and formats it.

        - Formats the column sizes
        - Creates tables for __riscv_save/__riscv_restore function groups
            - Writes out headers
            - Adds formulas for some automatic data analysis
        - Returns the worksheet
    """
    wksheet = excel.wkbook.add_worksheet(name)
    # Add link to return to Summary
    formula = '=HYPERLINK("#Summary!A1", "Return to Summary")'
    wksheet.write_formula('A1', formula, excel.header_format)
    # Format column sizes
    col_sizes = {
                 0: 30, 1: 20, 2: 20, 3: 20, 4: 50,
                 5: 20
                 }
    for col in col_sizes:
        wksheet.set_column(col, col, col_sizes[col])

    # 'RISC-V (RVGCC) [Save or Restore] Totals'
    add_riscv_totals_table(wksheet, 'RVGCC', name)
    # 'save_12 (RVGCC)', etc.
    add_riscv_tables(wksheet, 'RVGCC', name)

    return wksheet


""" Functions to add specific tables/charts to the worksheet """


def add_riscv_totals_table(wksheet, compiler, func):
    """ Adds the 'RISC-V [compiler] [func] Totals' table to the worksheet. """
    if (compiler == 'IAR'):
        row = 2
        col = 0
        if (func == '__riscv_save'):
            table = SAVE_IAR_TOTALS_TABLE
        elif (func == '__riscv_restore'):
            table = RESTORE_IAR_TOTALS_TABLE
    elif (compiler == 'RVGCC'):
        row = 2
        col = 0
        if (func == '__riscv_save'):
            # row = excel.get_table_loc(SAVE_IAR_TOTALS_TABLE)[0]
            # col = excel.get_table_loc(SAVE_IAR_A_TABLE)[3] + 2
            table = SAVE_RVGCC_TOTALS_TABLE
        elif (func == '__riscv_restore'):
            # row = excel.get_table_loc(RESTORE_IAR_TOTALS_TABLE)[0]
            # col = excel.get_table_loc(RESTORE_IAR_A_TABLE)[3] + 2
            table = RESTORE_RVGCC_TOTALS_TABLE
    headers = ['', 'Bytes']
    row_labels = ['Total']
    end_row = row + len(row_labels) + 1     # includes header row, etc.
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)
    excel.add_row_labels(wksheet, table, row_labels)


def add_riscv_tables(wksheet, compiler, func):
    """ Adds individual save_x or restore_x function tables. """
    if (func == '__riscv_save'):
        row = excel.get_table_loc(SAVE_RVGCC_TOTALS_TABLE)[2] + 8
        if (compiler == 'RVGCC'):
            col = excel.get_table_loc(SAVE_RVGCC_TOTALS_TABLE)[1]
            tables = rvgcc_save_tables
        # elif (compiler == 'IAR'):
        #     col = excel.get_table_loc(SAVE_IAR_TOTALS_TABLE)[1]
        #     tables = iar_save_tables
    elif (func == '__riscv_restore'):
        row = excel.get_table_loc(RESTORE_RVGCC_TOTALS_TABLE)[2] + 8
        if (compiler == 'RVGCC'):
            col = excel.get_table_loc(RESTORE_RVGCC_TOTALS_TABLE)[1]
            tables = rvgcc_restore_tables
        # elif (compiler == 'IAR'):
        #     col = excel.get_table_loc(RESTORE_IAR_TOTALS_TABLE)[1]
        #     tables = iar_restore_tables

    headers = ['Address',
               'Instruction',
               'Opcode',
               'Arguments',
               'Comments']
    tables.reverse()
    for table in tables:
        end_row = row + 20
        end_col = col + len(headers) - 1
        excel.create_table(wksheet, row, col, end_row, end_col,
                           table, headers, False)
        row = row + 28


""" Functions to record data to the worksheet """


def record_instruction(wksheet, compiler, table, curr_row, addr, instr, opcode,
                       args, comments):
    """ Write out info for a single instruction. """

    col = excel.get_table_col(table, 'Address')
    wksheet.write_string(curr_row, col, addr)

    col = excel.get_table_col(table, 'Instruction')
    wksheet.write_string(curr_row, col, instr)

    col = excel.get_table_col(table, 'Opcode')
    wksheet.write_string(curr_row, col, opcode)

    col = excel.get_table_col(table, 'Arguments')
    arguments = ''
    for i in range(len(args)):
        if i != 0:
            arguments = arguments + ', ' + args[i]
        else:
            arguments = args[i]
    wksheet.write_string(curr_row, col, arguments)

    col = excel.get_table_col(table, 'Comments')
    wksheet.write_string(curr_row, col, comments)

    if (len(instr) > 4):
        start = excel.get_table_loc(table)[1]
        end = excel.get_table_loc(table)[3]
        cell_range = CELL_NAME[(curr_row, start)] + ':' \
            + CELL_NAME[(curr_row, end)]
        format_dict = {'type': 'no_errors', 'format': excel.red_format}
        wksheet.conditional_format(cell_range, format_dict)


def record_totals(wksheet, compiler, func, bytes):
    """ Write out the function totals to the totals table. """
    if (func == '__riscv_save'):
        if (compiler == 'IAR'):
            table = SAVE_IAR_TOTALS_TABLE
        elif (compiler == 'RVGCC'):
            table = SAVE_RVGCC_TOTALS_TABLE
    elif (func == '__riscv_restore'):
        if (compiler == 'IAR'):
            table = RESTORE_IAR_TOTALS_TABLE
        elif (compiler == 'RVGCC'):
            table = RESTORE_RVGCC_TOTALS_TABLE
    cell = excel.get_table_cell(table, 'Bytes', 'Total')
    wksheet.write_number(cell, bytes, excel.bold_light_format)
