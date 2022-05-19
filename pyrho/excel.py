"""
Excel Helper

This file contains helper functions for creating and modifying an Excel
workbook. In particular, it tracks the location and makeup of any tables added
to Excel worksheets.

Author: Jennifer Hellar

"""

import xlsxwriter
from constants import XLS_FORMATS   # cell formats
from constants import CELL_NAME     # row, col map to cell e.g. (0, 1) --> 'A2'
from constants import CELL_COORD    # cell map to row, col e.g. 'B6' --> (1, 5)
from constants import SUMMARY_MAIN_TABLE

# Key: table title,
#   Val: (first row, first column, last row, last column)
# Used by excel.get_table_loc()
table_loc = {}

# Key: table title,
#   Val: {Key: Column Header,
#           Val: {Key: Row Label,
#                   Val: corresponding cell name}}
# Used by excel.get_table_cell()
table_map = {}

# Key: table title,
#   Val: {Key: Column Header,
#           Val: Column #}
# Used by excel.get_table_col()
table_cols = {}

# Key: full function name,
#   Val: short worksheet name
wksheet_names = {}


def create_workbook(name):
    """ Creates workbook, saves as a global variable, adds format options. """
    global wkbook
    wkbook = xlsxwriter.Workbook(name)
    add_cell_formats()


def close_workbook():
    """ Closes the open workbook. """
    global wkbook
    wkbook.close()


def add_cell_formats():
    """ Adds global cell format options for the scripts to utilize. """
    global header_format, red_header_format, gold_header_format
    global orange_header_format, title_format
    header_format = wkbook.add_format(XLS_FORMATS['header'])
    red_header_format = wkbook.add_format(XLS_FORMATS['red_header'])
    gold_header_format = wkbook.add_format(XLS_FORMATS['gold_header'])
    orange_header_format = wkbook.add_format(XLS_FORMATS['orange_header'])
    title_format = wkbook.add_format(XLS_FORMATS['title'])

    global light_bg_format, dark_bg_format, bold_light_format, bold_dark_format
    light_bg_format = wkbook.add_format(XLS_FORMATS['light_bg'])
    dark_bg_format = wkbook.add_format(XLS_FORMATS['dark_bg'])
    bold_light_format = wkbook.add_format(XLS_FORMATS['bold_light'])
    bold_dark_format = wkbook.add_format(XLS_FORMATS['bold_dark'])

    global gold_bg_format
    gold_bg_format = wkbook.add_format(XLS_FORMATS['gold_bg'])

    global red_format, red_light_format, red_dark_format
    red_format = wkbook.add_format(XLS_FORMATS['red'])
    red_light_format = wkbook.add_format(XLS_FORMATS['red_light'])
    red_dark_format = wkbook.add_format(XLS_FORMATS['red_dark'])

    global green_format, green_light_format, green_dark_format
    green_format = wkbook.add_format(XLS_FORMATS['green'])
    green_light_format = wkbook.add_format(XLS_FORMATS['green_light'])
    green_dark_format = wkbook.add_format(XLS_FORMATS['green_dark'])

    global gold_light_format
    gold_light_format = wkbook.add_format(XLS_FORMATS['gold_light'])

    global orange_bg_format, orange_light_format
    orange_bg_format = wkbook.add_format(XLS_FORMATS['orange_bg'])
    orange_light_format = wkbook.add_format(XLS_FORMATS['orange_light'])

    global percent_format, red_light_percent_format, green_light_percent_format
    percent_format = wkbook.add_format(XLS_FORMATS['percent'])
    format_opt = XLS_FORMATS['red_light_percent']
    red_light_percent_format = wkbook.add_format(format_opt)
    format_opt = XLS_FORMATS['green_light_percent']
    green_light_percent_format = wkbook.add_format(format_opt)


def create_table(wksheet, row, col, end_row, end_col,
                 table, headers, format_bool):
    """

    Creates a table in the worksheet and space defined by input coordinates.
    Headers are written out to the worksheet and used as keys in
    table_map/table_cols. If format_bool is TRUE, then the inner cells of the
    table are pre-formatted w/light background.

    """
    # Note: even though most function tables are static, some do change in size
    global table_cols, table_map, table_loc
    # Saves the location of the table
    table_loc[table] = (row, col, end_row, end_col)
    table_cols[table] = {}
    table_map[table] = {}
    # Adds the table to the table mappings
    for i in range(len(headers)):
        column = col + i
        table_cols[table][headers[i]] = column
        table_map[table][headers[i]] = {}

    # Writes out the title to the upper left coordinate of the table
    wksheet.write_string(row, col, table, title_format)
    # (Optionally) pre-formats the inner cells to have the light background
    if format_bool:
        for r in range(row + 2, end_row + 1):
            for c in range(col + 1, end_col + 1):
                wksheet.write_blank(r, c, None, light_bg_format)
    # Write out the column headers provided and update the mappings
    for i in range(len(headers)):
        column = col + i
        wksheet.write_string(row + 2, column, headers[i], header_format)


def add_row_labels(wksheet, table, labels):
    """ Adds row labels to a table and updates the table mappings. """
    global table_loc, table_map, table_cols

    # Get the table location and horizontal/column headers
    (table_row, table_col, table_end_row, table_end_col) = get_table_loc(table)
    col_headers = table_cols[table]
    for i in range(len(labels)):
        row = table_row + 3 + i
        # Write out the row labels
        wksheet.write_string(row, table_col, labels[i], header_format)
        for col_header in col_headers.keys():
            col_num = col_headers[col_header]
            row_label = labels[i]
            table_map[table][col_header][row_label] = CELL_NAME[(row, col_num)]


def get_table_loc(table):
    return table_loc[table]


def get_table_col(table, header):
    return table_cols[table][header]


def get_table_cell(table, col_header, row_label):
    return table_map[table][col_header][row_label]


def update_table_loc(table, row, col, end_row, end_col):
    global table_loc
    table_loc[table] = (row, col, end_row, end_col)


def update_table_map(table, col_header, row_label, row):
    global table_map
    col_num = get_table_col(table, col_header)
    table_map[table][col_header][row_label] = CELL_NAME[(row, col_num)]


""" Helper functions to manipulate data within tables """


def subtract_col(wksheet, table, col1_name, col2_name, dest_col_name):
    """ Subtract col2 from col1 and place the result in dest_col. """
    (row, col, end_row, end_col) = get_table_loc(table)
    row = row + 3

    col1 = get_table_col(table, col1_name)
    c1_range = CELL_NAME[(row, col1)] + ':' + CELL_NAME[(end_row, col1)]

    col2 = get_table_col(table, col2_name)
    c2_range = CELL_NAME[(row, col2)] + ':' + CELL_NAME[(end_row, col2)]

    col_d = get_table_col(table, dest_col_name)
    dest_range = CELL_NAME[(row, col_d)] + ':' + CELL_NAME[(end_row, col_d)]

    formula = '{=(' + c1_range + ' - ' + c2_range + ')}'
    wksheet.write_array_formula(dest_range, formula)

    # Apply a conditional format: red text if the result is > 0
    # (keep alternating background)
    if (table == SUMMARY_MAIN_TABLE):
        for r in range(row, end_row + 1):
            cell = CELL_NAME[(r, col_d)]
            if (r % 2) == (row % 2):
                wksheet.conditional_format(cell, {'type': 'cell',
                                                  'criteria': '>', 'value': 0,
                                                  'format': red_light_format})
                wksheet.conditional_format(cell, {'type': 'cell',
                                                  'criteria': '<=', 'value': 0,
                                                  'format': light_bg_format})
            else:
                wksheet.conditional_format(cell, {'type': 'cell',
                                                  'criteria': '>', 'value': 0,
                                                  'format': red_dark_format})
                wksheet.conditional_format(cell, {'type': 'cell',
                                                  'criteria': '<=', 'value': 0,
                                                  'format': dark_bg_format})


def sum_col(wksheet, table, col_name, dest_cell):
    """ Sums a column of a table and place the result in dest_cell. """
    (row, col, end_row, end_col) = get_table_loc(table)
    row = row + 3

    col = get_table_col(table, col_name)
    start = CELL_NAME[(row, col)]
    end = CELL_NAME[(end_row, col)]

    formula = '=SUM(' + start + ':' + end + ')'
    wksheet.write_formula(dest_cell, formula, light_bg_format)


def record_percentage(wksheet, num, denom, dest, threshold, direction):
    """
    dest = num/denom (displayed as percentage)

    Colors the text red/green if the percentage is above/below a threshold.

    num, denom, and dest should be cell names
    """
    formula = '=(' + num + '/' + denom + ')'
    wksheet.write_formula(dest, formula, percent_format)
    if (direction is True):  # value > threshold is good (green)
        greater_format = green_light_percent_format
        lesser_format = red_light_percent_format
    else:                    # value > threshold is bad (red)
        greater_format = red_light_percent_format
        lesser_format = green_light_percent_format
    wksheet.conditional_format(dest, {'type': 'cell', 'criteria': '>',
                                      'value': threshold,
                                      'format': greater_format})
    wksheet.conditional_format(dest, {'type': 'cell', 'criteria': '<',
                                      'value': threshold,
                                      'format': lesser_format})
