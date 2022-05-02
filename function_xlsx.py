"""
Excel Function Worksheet

This file contains functions for creating/modifying function worksheets.

Author: Jennifer Hellar (jennifer.hellar@rice.edu)

"""

import xlsxwriter

import excel
from constants import *


def create_sheet(func_name, name):
    """
    Adds a new worksheet to an open Excel workbook and formats it.

        - Adds an Excel worksheet with the name of the function
        - Formats the column sizes
        - Creates tables for ARM/RISC-V data
            - Writes out headers
            - Adds formulas for some automatic data analysis
        - Returns the worksheet
    """
    wksheet = excel.wkbook.add_worksheet(name)
    # Add link to return to Summary
    formula = '=HYPERLINK("#Summary!A1", "Return to Summary")'
    wksheet.write_formula('A1', formula, excel.header_format)
    # Format column sizes
    col_sizes = {  # ARM table
                 0: 20, 1: 20, 2: 20, 3: 30, 4: 50,
                 5: 20,
                   # RISC-V table
                 6: 20, 7: 20, 8: 20, 9: 20, 10: 20, 11: 30, 12: 20, 13: 50,
                 14: 20,
                 #   # RVGCC table
                 # 15: 20, 16: 20, 17: 20, 18: 20, 19: 20, 20: 30, 21: 20,
                 # 22: 50,
                 # 23: 20,
                   # Instruction format tables
                 15: 20, 16: 20, 17: 20, 18: 20, 19: 20, 20: 20, 21: 20,
                 22: 20, 23: 20, 24: 20, 25: 20, 26: 20, 27: 20, 28: 20,
                 29: 20, 30: 20, 31: 20, 32: 20, 33: 20, 34: 20, 35: 20,
                 36: 20, 37: 20, 38: 20, 39: 20, 40: 20, 41: 20, 42: 20
                 }
    for col in col_sizes:
        wksheet.set_column(col, col, col_sizes[col])

    # 'ARM M0+ Totals'
    row = 2
    col = 0
    add_arm_totals_table(wksheet, row, col)
    # 'ARM M0+'
    add_arm_table(wksheet)
    # # 'RISC-V (IAR) Totals'
    # add_riscv_totals_table(wksheet, 'IAR')
    # # 'RISC-V (IAR)'
    # add_riscv_table(wksheet, 'IAR')
    # 'RISC-V (GCC) Totals'
    add_riscv_totals_table(wksheet, 'rvgcc')
    # 'RISC-V (GCC)'
    add_riscv_table(wksheet, 'rvgcc')

    return wksheet


""" Functions to add specific tables/charts to the worksheet """


def add_arm_totals_table(wksheet, row, col):
    """ Adds the 'ARM M0+ Totals' table to the worksheet. """
    headers = ['', 'Bytes']
    row_labels = ['Total']
    end_row = row + len(row_labels) + 1     # includes header row, etc.
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       ARM_TOTALS_TABLE, headers, True)
    excel.add_row_labels(wksheet, ARM_TOTALS_TABLE, row_labels)


def add_arm_table(wksheet):
    """ Adds the 'ARM M0+' table to the worksheet. """
    # Location: Directly below 'ARM M0+ Totals' table
    #   At same row as RISC-V table, so pushed down by listing of enabled instr
    row = excel.get_table_loc(ARM_TOTALS_TABLE)[0] + max(len(ENABLED), 7) + 34
    col = excel.get_table_loc(ARM_TOTALS_TABLE)[1]
    headers = ['Address',
               'Instruction',
               'Opcode',
               'Arguments',
               'Comments']
    end_row = 200   # this will be updated when data is filled in
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       ARM_TABLE, headers, False)


def add_riscv_totals_table(wksheet, compiler):
    """ Adds a RISC-V Totals for the given compiler table to the worksheet. """
    # if (compiler == 'IAR'):
    #     row = excel.get_table_loc(ARM_TOTALS_TABLE)[0]
    #     col = excel.get_table_loc(ARM_TABLE)[3] + 2
    #     table = IAR_TOTALS_TABLE
    # elif (compiler == 'rvgcc'):
    row = excel.get_table_loc(ARM_TOTALS_TABLE)[0]
    col = excel.get_table_loc(ARM_TABLE)[3] + 2
    table = RVGCC_TOTALS_TABLE

    headers = ['', 'Instruction', 'Bytes']
    row_labels = ['Total', 'Reduction']
    # Empty spaces to hold compact instruction reduction data
    for i in range(len(ENABLED)):
        row_labels.append('')
    row_labels.append('Final Estimate')
    end_row = row + len(row_labels) + 2
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)
    excel.add_row_labels(wksheet, table, row_labels)

    # Add compact instruction locations to table map (will fill in later)
    # (Table title location + 2 = Table header row) + # rows to Reductions lbl
    row = excel.get_table_loc(table)[0] + 2\
        + row_labels.index('Reduction') + 1

    for i in range(len(ENABLED)):
        row += 1
        excel.update_table_map(table, 'Instruction',
                               ENABLED[i], row)
        excel.update_table_map(table, 'Bytes', ENABLED[i], row)


def add_riscv_table(wksheet, compiler):
    """ Adds a RISC-V table to the worksheet for the given compiler. """
    # Location: Directly below the corresponding Totals table
    row = excel.get_table_loc(ARM_TABLE)[0]
    if (compiler == 'rvgcc'):
        col = excel.get_table_loc(RVGCC_TOTALS_TABLE)[1]
        table = RVGCC_TABLE
    # elif (compiler == 'IAR'):
    #     col = excel.get_table_loc(IAR_TOTALS_TABLE)[1]
    #     table = IAR_TABLE
    rv_headers = ['Address',
                  'Instruction',
                  'Opcode',
                  'Arguments',
                  'Compact version',
                  'Implementation',
                  'Offset size',
                  'Comments']
    end_row = 200
    end_col = col + len(rv_headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, rv_headers, False)


def add_instr_freq_table(wksheet, compiler, instr_freq):
    """ Add the 'Instruction Occurrence' table to the current worksheet. """
    names = []
    vals = []
    for instr in instr_freq.keys():
        # Mark instruction names based on size
        freq = instr_freq[instr]
        names.append(instr)
        vals.append(freq)
    # Sort by the number of occurrences
    vlnm = sorted(zip(vals, names))
    vals = [val for val, nm in vlnm if val > 0]
    names = [nm for val, nm in vlnm if val > 0]
    # Keep at most the top 10 most common
    keep = min(10, len(names))
    other = sum(vals[:-keep])
    vals = vals[-keep:]
    names = names[-keep:]
    vals.reverse()
    names.reverse()
    if (other != 0):
        vals.append(other)
        names.append('other')

    # Location: Directly to below 'xxx Totals' table
    headers = ['', '# Occurrences']
    if (compiler == 'rvgcc'):
        table = RVGCC_INSTR_TABLE
        row = excel.get_table_loc(RVGCC_TOTALS_TABLE)[2] + 2
        col = excel.get_table_loc(RVGCC_TOTALS_TABLE)[1]
    # elif (compiler == 'IAR'):
    #     table = IAR_INSTR_TABLE
    #     row = excel.get_table_loc(IAR_TOTALS_TABLE)[2] + 2
    #     col = excel.get_table_loc(IAR_TOTALS_TABLE)[1]
    end_row = row + len(names) + 2
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, False)

    row = row + 3

    for i in range(len(names)):
        instr = names[i]
        # Mark 'cx' instructions with gold text
        if (instr in ENABLED):
            name_format = excel.gold_header_format
            val_format = excel.light_bg_format
        # Mark 32-bit instructions with red text
        elif (instr.find('c.') == -1) and (instr != 'other'):
            name_format = excel.red_header_format
            val_format = excel.red_light_format
        else:
            name_format = excel.header_format
            val_format = excel.light_bg_format
        # Vertical labels are instruction names
        col = excel.get_table_col(table, '')
        wksheet.write_string(row, col, names[i], name_format)
        # Update the table map to include the occurrence cells
        excel.update_table_map(table, '# Occurrences',
                               names[i], row)
        # Record the occurrence value
        col = excel.get_table_col(table, '# Occurrences')
        wksheet.write_number(row, col, vals[i], val_format)

        row += 1


def add_instr_freq_chart(wksheet, compiler):
    """ Add chart to visualize most frequent instructions. """
    if (compiler == 'rvgcc'):
        data_table = RVGCC_INSTR_TABLE
        loc_table = RVGCC_TOTALS_TABLE
    # elif (compiler == 'IAR'):
    #     data_table = IAR_INSTR_TABLE
    #     loc_table = IAR_TOTALS_TABLE
    # Location of data table
    coord = excel.get_table_loc(data_table)
    (first_row, first_col, last_row, last_col) = coord
    first_row = first_row + 3
    # Location of instruction names
    name_col = excel.get_table_col(data_table, '')
    start_name = CELL_NAME[(first_row, name_col)]
    end_name = CELL_NAME[(last_row, name_col)]
    # Location of occurrence values
    val_col = excel.get_table_col(data_table, '# Occurrences')
    start_val = CELL_NAME[(first_row, val_col)]
    end_val = CELL_NAME[(last_row, val_col)]
    # Location of chart
    coord = excel.get_table_loc(loc_table)
    row = max(coord[2] + 12, coord[0] + 25)
    col = coord[3] + 2
    chart_loc_cell = CELL_NAME[(row, col)]
    chart = excel.wkbook.add_chart({'type': 'pie'})
    categories = '=' + wksheet.get_name() + '!' + start_name + ':' + end_name
    values = '=' + wksheet.get_name() + '!' + start_val + ':' + end_val
    chart.add_series({
        'name':         'Distribution of Instructions',
        'categories':   categories,
        'values':       values,
        'data_labels':  {'category': True, 'percentage': True,
                         'position': 'outside_end', 'separator': ' '}
        })
    if (compiler == 'rvgcc'):
        chart.set_title({'name': 'RISC-V Instructions'})
    # elif (compiler == 'IAR'):
    #     chart.set_title({'name': 'IAR Instructions'})
    chart.set_style(10)
    chart.set_size({'width': 435, 'height': 320})
    wksheet.insert_chart(chart_loc_cell, chart, {'x_offset': 0,
                                                 'y_offset': 0})


def add_instr_formats_table(wksheet, compiler, formats):
    """ Add the 'Instruction Labels' table to the current worksheet. """
    if (compiler == 'rvgcc'):
        row = excel.get_table_loc(RVGCC_TOTALS_TABLE)[0]
        col = excel.get_table_loc(RVGCC_TABLE)[3] + 2
        headers = ['Instruction', '# (RISC-V)']
        row_labels = []
        for lbl in formats.keys():
            for instr in formats[lbl]:
                row_labels.append(instr)
        for lbl in formats.keys():
            table_nm = lbl
            end_row = row + len(row_labels) + 2
            end_col = col + len(headers) - 1
            excel.create_table(wksheet, row, col, end_row, end_col,
                               table_nm, headers, False)
            excel.add_row_labels(wksheet, table_nm, row_labels)
            col = col + 3

    for lbl in formats.keys():
        table_nm = lbl
        for instr in formats[lbl]:
            val = formats[lbl][instr]
            if (compiler == 'rvgcc'):
                cell = excel.get_table_cell(table_nm, '# (RISC-V)', instr)
            # elif (compiler == 'IAR'):
            #     cell = excel.get_table_cell(table_nm, '# (IAR)', instr)
            wksheet.write_number(cell, val, excel.light_bg_format)


def add_instr_formats_radar(wksheet, compiler):
    """ Add radar to visualize most frequent instruction formats. """
    # Location of chart: next to totals table
    if (compiler == 'rvgcc'):
        coord = excel.get_table_loc(RVGCC_TOTALS_TABLE)
    # elif (compiler == 'IAR'):
    #     coord = excel.get_table_loc(IAR_TOTALS_TABLE)
    ch_row = coord[0] - 1
    ch_col = coord[3] + 2
    chart_loc_cell = CELL_NAME[(ch_row, ch_col)]

    # Make the pie chart underneath to mark the instruction format
    chart1 = excel.wkbook.add_chart({'type': 'pie'})
    chart1.add_series({
        'categories':   ['tmp', 0, 0, len(RV32_FORMATS) - 1, 0],
        'values':       ['tmp', 0, 1, len(RV32_FORMATS) - 1, 1],
        })
    if (compiler == 'rvgcc'):
        chart1.set_title({'name': 'RISC-V Instruction Formats',
                          'layout': {'x': 0.01, 'y': 0.01}})
    # elif (compiler == 'IAR'):
    #     chart1.set_title({'name': 'IAR Instruction Formats',
    #                       'layout': {'x': 0.01, 'y': 0.01}})
    chart1.set_legend({'position': 'overlay_right'})
    chart1.set_size({'width': 640, 'height': 490})
    chart1.set_chartarea({'border': {'none': True}})
    chart1.set_plotarea({'border': {'none': True}})
    chart1.set_rotation(357)
    wksheet.insert_chart(chart_loc_cell, chart1)

    # Make the radar chart
    chart = excel.wkbook.add_chart({'type': 'radar'})
    for i in range(len(RV32_FORMATS)):
        tbl_nm = RV32_FORMATS[i]
        (row, col, end_row, end_col) = excel.get_table_loc(tbl_nm)
        name = [wksheet.get_name(), row, col]
        categories = [wksheet.get_name(), row + 3, col, end_row, col]
        if (compiler == 'rvgcc'):
            val_col = excel.get_table_col(tbl_nm, '# (RISC-V)')
        # elif (compiler == 'IAR'):
        #     val_col = excel.get_table_col(tbl_nm, '# (IAR)')
        values = [wksheet.get_name(), row + 3, val_col, end_row, val_col]
        chart.add_series({
                'name':         name,
                'categories':   categories,
                'values':       values,
                'line':         {'color': 'black'},
                'marker':       {'type': 'diamond', 'fill': {'color': 'black'},
                                 'border': {'color': 'black'}, 'size': 8}
            })
    chart.set_size({'width': 640, 'height': 490})
    chart.set_chartarea({'fill': {'none': True}, 'border': {'none': True}})
    chart.set_plotarea({'fill': {'none': True}})
    chart.set_legend({'none': True})
    ch_row = ch_row + 1
    chart_loc_cell = CELL_NAME[(ch_row, ch_col)]
    wksheet.insert_chart(chart_loc_cell, chart, {'x_offset': 0, 'y_offset': 0})


def add_riscv_bits_table(wksheet, compiler):
    """ Add Offset Bits table to the worksheet for the given compiler. """
    if (compiler == 'rvgcc'):
        loc_table = RVGCC_INSTR_TABLE
        data_table = RVGCC_TABLE
        tot_table = RVGCC_TOTALS_TABLE
        table = RVGCC_BITS_TABLE
    # elif (compiler == 'IAR'):
    #     loc_table = IAR_INSTR_TABLE
    #     data_table = IAR_TABLE
    #     tot_table = IAR_TOTALS_TABLE
    #     table = IAR_BITS_TABLE

    # Location: Directly below the compiler Instructions table
    row = excel.get_table_loc(loc_table)[2] + 2
    col = excel.get_table_loc(loc_table)[1]
    headers = ['', 'Results', 'Comments']
    row_labels = ['Max Offset', 'Min Offset', 'Data Size', '',
                  'Total Size', '# of Bits']
    end_row = row + len(row_labels) + 1
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)
    excel.add_row_labels(wksheet, table, row_labels)

    # Offset data location in RISC-V table
    data_coord = excel.get_table_loc(data_table)
    offset_col = excel.get_table_col(data_table, 'Offset size')
    start = CELL_NAME[(data_coord[0] + 3, offset_col)]
    end = CELL_NAME[(data_coord[2], offset_col)]

    # Maximum offset for 32-bit lw instruction
    max_cell = excel.get_table_cell(table, 'Results', 'Max Offset')
    formula = '=MIN(' + start + ':' + end + ')'  # Actual offset is negative
    wksheet.write_formula(max_cell, formula, excel.light_bg_format)

    # Minimum offset
    min_cell = excel.get_table_cell(table, 'Results', 'Min Offset')
    formula = '=MAX(' + start + ':' + end + ')'  # Actual offset is negative
    wksheet.write_formula(min_cell, formula, excel.light_bg_format)

    # Total range of offsets
    diff_cell = excel.get_table_cell(table, 'Results', 'Data Size')
    formula = '=(' + min_cell + ' - ' + max_cell + ')'
    wksheet.write_formula(diff_cell, formula, excel.bold_light_format)
    comment_cell = excel.get_table_cell(table, 'Comments', 'Data Size')
    wksheet.write_string(comment_cell, '(Max - Min)', excel.light_bg_format)

    # Total size of function and data
    size_cell = excel.get_table_cell(table, 'Results', 'Total Size')
    est_cell = excel.get_table_cell(tot_table, 'Bytes',
                                    'Final Estimate')
    formula = '=(' + est_cell + ' + ' + diff_cell + ')'
    wksheet.write_formula(size_cell, formula, excel.bold_light_format)
    comment_cell = excel.get_table_cell(table, 'Comments', 'Total Size')
    wksheet.write_string(comment_cell, 'Function size + data size',
                         excel.light_bg_format)

    # Number of bits needed to span full range of function + data
    bits_cell = excel.get_table_cell(table, 'Results', '# of Bits')
    formula = '=ROUNDUP(LOG(' + size_cell + ',2),0)'
    wksheet.write_formula(bits_cell, formula)
    # Only 8 bits available in 16-bit instruction, so need offset <= 8 bits
    format_dict = {'type': 'cell', 'criteria': '>', 'value': 10,
                   'format': excel.red_light_format}
    wksheet.conditional_format(bits_cell + ':' + bits_cell, format_dict)
    format_dict = {'type': 'cell', 'criteria': '<=', 'value': 10,
                   'format': excel.green_light_format}
    wksheet.conditional_format(bits_cell + ':' + bits_cell, format_dict)
    comment_cell = excel.get_table_cell(table, 'Comments', '# of Bits')
    wksheet.write_string(comment_cell, 'To span all addresses',
                         excel.light_bg_format)


def mark_compact_rows(wksheet, compiler, compact_loc, lwpc_fail):
    """
    Formats cx instruction rows w/light background.
    If cx.lwpc cannot be used, re-format those cells to be red.
    """
    if (compiler == 'rvgcc'):
        start = excel.get_table_loc(RVGCC_TABLE)[1]
        end = excel.get_table_loc(RVGCC_TABLE)[3]
    # elif (compiler == 'IAR'):
    #     start = excel.get_table_loc(IAR_TABLE)[1]
    #     end = excel.get_table_loc(IAR_TABLE)[3]
    for instr in compact_loc.keys():
        row_lst = compact_loc[instr]
        for row in row_lst:
            cell_range = CELL_NAME[(row, start)] + ':' + CELL_NAME[(row, end)]
            if (instr == 'cx.lwpc') and lwpc_fail:
                format_dict = {'type': 'no_errors', 'format': excel.red_format}
                wksheet.conditional_format(cell_range, format_dict)
            else:
                format_dict = {'type': 'no_errors',
                               'format': excel.light_bg_format}
                wksheet.conditional_format(cell_range, format_dict)


def mark_failed_rows(wksheet, compiler, loc):
    """
    Formats failed cx instruction rows w/orange background.
    """
    if (compiler == 'rvgcc'):
        start = excel.get_table_loc(RVGCC_TABLE)[1]
        end = excel.get_table_loc(RVGCC_TABLE)[3]
    # elif (compiler == 'IAR'):
    #     start = excel.get_table_loc(IAR_TABLE)[1]
    #     end = excel.get_table_loc(IAR_TABLE)[3]
    for instr in loc.keys():
        row_lst = loc[instr]
        for row in row_lst:
            cell_range = CELL_NAME[(row, start)] + ':' + CELL_NAME[(row, end)]
            format_dict = {'type': 'no_errors',
                           'format': excel.orange_bg_format}
            wksheet.conditional_format(cell_range, format_dict)


def mark_pair_rows(wksheet, compiler, pair_loc):
    """
    Formats instruction pairs of interest w/gold background.
    """
    if (compiler == 'rvgcc'):
        coord = excel.get_table_loc(RVGCC_TABLE)
    # elif (compiler == 'IAR'):
    #     coord = excel.get_table_loc(IAR_TABLE)
    start = coord[1]
    end = coord[3]
    format_dict = {'type': 'no_errors', 'format': excel.gold_bg_format}
    for pair in pair_loc.keys():
        row_lst = pair_loc[pair]
        for row in row_lst:
            cells = CELL_NAME[(row, start)] + ':' + CELL_NAME[(row + 1, end)]
            wksheet.conditional_format(cells, format_dict)


def add_tables_charts_marks(wksheet, compiler, instr, formats, compact,
                            not_repl_loc, lwpc, pairs):
    # Instruction Occurrence
    add_instr_freq_table(wksheet, compiler, instr)
    add_instr_freq_chart(wksheet, compiler)
    # Instruction Formats
    add_instr_formats_table(wksheet, compiler, formats)
    add_instr_formats_radar(wksheet, compiler)
    # Offset Bits for cx.lwpc
    add_riscv_bits_table(wksheet, compiler)
    # Mark new replaced instructions and pairs
    mark_compact_rows(wksheet, compiler, compact, lwpc)
    mark_failed_rows(wksheet, compiler, not_repl_loc)
    mark_pair_rows(wksheet, compiler, pairs)


""" Functions to record data to the worksheet """


def record_func_name(wksheet, name):
    """ Write out the function name to the worksheet. """
    table = ARM_TABLE
    row = excel.get_table_loc(table)[0] + 1
    col = excel.get_table_loc(table)[1]
    wksheet.write_string(row, col, name)
    # table = IAR_TABLE
    # row = excel.get_table_loc(table)[0] + 1
    # col = excel.get_table_loc(table)[1]
    # wksheet.write_string(row, col, name)
    table = RVGCC_TABLE
    row = excel.get_table_loc(table)[0] + 1
    col = excel.get_table_loc(table)[1]
    wksheet.write_string(row, col, name)


def record_instruction(wksheet, compiler, curr_row, addr, instr, opcode,
                       args, comments):
    """ Write out info for a single instruction. """
    if (compiler == 'rvgcc'):
        table = RVGCC_TABLE
    # elif (compiler == 'IAR'):
    #     table = IAR_TABLE
    elif (compiler.find('arm') != -1):
        table = ARM_TABLE

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


def record_riscv_totals(wksheet, compiler, original, reductions):
    """ Write out the RISC-V function totals to the Totals table. """
    if (compiler == 'rvgcc'):
        table = RVGCC_TOTALS_TABLE
    # elif (compiler == 'IAR'):
    #     table = IAR_TOTALS_TABLE
    # Calculate the total reduction for the function
    func_reduction = 0
    for instr in reductions.keys():
        func_reduction += reductions[instr]
    # Write out the function size and potential reduction
    cell = excel.get_table_cell(table, 'Bytes', 'Total')
    wksheet.write_number(cell, original, excel.bold_light_format)
    cell = excel.get_table_cell(table, 'Bytes', 'Reduction')
    wksheet.write_number(cell, func_reduction, excel.bold_light_format)

    # Write out indiv. compact instruction names and reductions
    for instr_name in reductions.keys():
        cell = excel.get_table_cell(table,
                                    'Instruction', instr_name)
        wksheet.write_string(cell, instr_name, excel.light_bg_format)
        cell = excel.get_table_cell(table, 'Bytes', instr_name)
        wksheet.write_number(cell, reductions[instr_name],
                             excel.light_bg_format)

    # Calculate and write out potential final size of the function
    est = original - func_reduction
    cell = excel.get_table_cell(table, 'Bytes', 'Final Estimate')
    wksheet.write_number(cell, est, excel.bold_light_format)


def record_arm_totals(wksheet, bytes):
    """ Write out the function totals to the 'ARM Totals' table. """
    cell = excel.get_table_cell(ARM_TOTALS_TABLE, 'Bytes', 'Total')
    wksheet.write_number(cell, bytes, excel.bold_light_format)


def record_comments(wksheet, compiler, curr_row, instr, args):
    """
    Write out comments for a single compact instruction to the following cols:
            - 'Compact version', 'Implementation', 'Offset size', 'Rules'
    """
    if (compiler == 'rvgcc'):
        table = RVGCC_TABLE
    # elif (compiler == 'IAR'):
    #     table = IAR_TABLE

    ver_col = excel.get_table_col(table, 'Compact version')
    impl_col = excel.get_table_col(table, 'Implementation')
    off_col = excel.get_table_col(table, 'Offset size')

    ver_text = ''
    impl_text = ''
    rule_text = ''
    (r2, r1, offset) = args

    # Compact version
    if (instr == 'cx.lwpc'):
        ver_text = 'Load PC Relative'
    elif (instr == 'cx.lbu'):
        ver_text = 'Load Unsigned Byte'
    elif (instr == 'cx.lhu'):
        ver_text = 'Load Unsigned Halfword'
    elif (instr == 'cx.lb'):
        ver_text = 'Load Byte'
    elif (instr == 'cx.lh'):
        ver_text = 'Load Halfword'
    elif (instr == 'cx.sb'):
        ver_text = 'Store Byte'
    elif (instr == 'cx.sh'):
        ver_text = 'Store Halfword'
    elif (instr == 'cx.addi8'):
        ver_text = 'Add Large Immediate'
    elif (instr == 'cx.addi5'):
        ver_text = 'Non-destructive Add'
    elif (instr == 'cx.subi8'):
        ver_text = 'Subtract Large Immediate'
    elif (instr == 'cx.subi5'):
        ver_text = 'Non-destructive Subtraction'
    elif (instr == 'cx.slli'):
        ver_text = 'Non-destructive Shift Left Logical'
    elif (instr == 'cx.bne'):
        ver_text = 'Branch if Not Equal'
    elif (instr == 'cx.blt'):
        ver_text = 'Branch if Less Than'
    elif (instr == 'cx.bge'):
        ver_text = 'Branch if Greater Than or Equal'
    elif (instr == 'cx.sbzero'):
        ver_text = 'Store Zero Byte'
    elif (instr == 'cx.shzero'):
        ver_text = 'Store Zero Halfword'
    elif (instr == 'cx.swzero'):
        ver_text = 'Store Zero Word'
    elif (instr == 'c.j (restore)'):
        ver_text = 'Jump (Restore)'
    elif (instr == 'c.jal (save)'):
        ver_text = 'Jump-And-Link (Save)'
    elif (instr == 'pop (restore)'):
        ver_text = 'Pop From Stack'
        if (offset == '__riscv_restore_0'):
            r2 = 'ra'
        elif (offset == '__riscv_restore_1'):
            r2 = 's0, ra'
        elif (offset == '__riscv_restore_2'):
            r2 = 's0, s1, ra'
        elif (offset == '__riscv_restore_3'):
            r2 = 's0, s1, s2, ra'
        elif (offset == '__riscv_restore_4'):
            r2 = 's0, s1, s2, s3, ra'
        elif (offset == '__riscv_restore_5'):
            r2 = 's0, s1, s2, s3, s4, ra'
        elif (offset == '__riscv_restore_6'):
            r2 = 's0, s1, s2, s3, s4, s5, ra'
        elif (offset == '__riscv_restore_7'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, ra'
        elif (offset == '__riscv_restore_8'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, ra'
        elif (offset == '__riscv_restore_9'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, ra'
        elif (offset == '__riscv_restore_10'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, ra'
        elif (offset == '__riscv_restore_11'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, ra'
        elif (offset == '__riscv_restore_12'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, ra'
    elif (instr == 'push (save)'):
        ver_text = 'Push onto Stack'
        if (offset == '__riscv_save_0'):
            r2 = 'ra'
        elif (offset == '__riscv_save_1'):
            r2 = 's0, ra'
        elif (offset == '__riscv_save_2'):
            r2 = 's0, s1, ra'
        elif (offset == '__riscv_save_3'):
            r2 = 's0, s1, s2, ra'
        elif (offset == '__riscv_save_4'):
            r2 = 's0, s1, s2, s3, ra'
        elif (offset == '__riscv_save_5'):
            r2 = 's0, s1, s2, s3, s4, ra'
        elif (offset == '__riscv_save_6'):
            r2 = 's0, s1, s2, s3, s4, s5, ra'
        elif (offset == '__riscv_save_7'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, ra'
        elif (offset == '__riscv_save_8'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, ra'
        elif (offset == '__riscv_save_9'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, ra'
        elif (offset == '__riscv_save_10'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, ra'
        elif (offset == '__riscv_save_11'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, ra'
        elif (offset == '__riscv_save_12'):
            r2 = 's0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, ra'

    # Implementation
    if (instr == 'cx.lwpc'):
        impl_text = 'cx.lwpc ' + r2 + ', offset(pc)'
    elif (instr == 'c.j (restore)'):
        impl_text = instr + ' ' + offset
    elif (instr == 'c.jal (save)'):
        impl_text = instr + ' ' + r2 + ', ' + offset
    elif (instr[:4] == 'cx.b') or (instr[:10] == 'cx.addi5') or \
            (instr[:10] == 'cx.subi5') or (instr == 'cx.slli'):
        impl_text = instr + ' ' + r2 + ', ' + r1 + ', ' + str(offset)
    elif (instr[:10] == 'cx.addi8') or (instr[:10] == 'cx.subi8'):
        impl_text = instr + ' ' + r2 + ', ' + str(offset)
    elif (instr == 'pop (restore)'):
        impl_text = 'pop ' + r2
    elif (instr == 'push (save)'):
        impl_text = 'push ' + r2
    else:
        impl_text = instr + ' ' + r2 + ', ' + str(offset) + '(' + r1 + ')'

    wksheet.write_string(curr_row, ver_col, ver_text)
    wksheet.write_string(curr_row, impl_col, impl_text)

    # Offset (for PC relative load word)
    if (instr == 'cx.lwpc'):
        wksheet.write_number(curr_row, off_col, -int(offset))
