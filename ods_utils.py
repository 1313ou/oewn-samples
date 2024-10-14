

def ensure_row(sheet, row_index):
    current_rows = sheet.nrows()
    if current_rows <= row_index:
        sheet.append_rows(row_index - current_rows + 1)


def ensure_col(sheet, col_index):
    current_cols = sheet.ncols()
    if current_cols <= col_index:
        sheet.append_columns(col_index - current_cols + 1)
