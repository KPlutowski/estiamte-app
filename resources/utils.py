import re


def index_to_letter(index: int) -> str:
    """Convert a zero-based column index to an Excel-like column letter."""
    if index < 0:
        return None  # Index cannot be negative
    letter = ''
    while index >= 0:
        letter = chr(index % 26 + ord('A')) + letter
        index = index // 26 - 1
    return letter


def letter_to_index(letter: str) -> int:
    """Convert an Excel column letter to a zero-based column index."""
    if not letter.isalpha():
        return None  # Invalid column letter
    index = 0
    for char in letter.upper():
        if 'A' <= char <= 'Z':
            index = index * 26 + (ord(char) - ord('A'))
        else:
            return None  # Invalid character in column letter
    return index


def is_convertible_to_float(value: str) -> bool:
    """Check if the given string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse_column_row(part: str) -> tuple[int, int]:
    """Parse a column and row from a reference part."""
    if not isinstance(part, str):
        return None, None  # Invalid input type
    col_letter = ''.join(filter(str.isalpha, part))
    row_number_str = ''.join(filter(str.isdigit, part))

    if len(col_letter) >= 2:
        return None, None

    if not row_number_str:
        return None, None  # No row number found

    try:
        row_number = int(row_number_str)
    except ValueError:
        return None, None  # Invalid row number

    col_index = letter_to_index(col_letter)
    if col_index is None:
        return None, None  # Invalid column letter

    return row_number - 1, col_index


def parse_cell_address(cell_address) -> tuple[str, int, int]:
    # address like Sheet1!A2
    if not isinstance(cell_address, str) or '!' not in cell_address:
        return None, None, None  # Invalid input

    parts = cell_address.split('!', 1)
    if len(parts) != 2:
        return None, None, None  # Invalid cell address format

    sheet_name, cell_part = parts
    row_number, col_number = parse_column_row(cell_part)
    if row_number is None or col_number is None:
        return None, None, None  # Parsing failed

    return sheet_name, row_number, col_number


def parse_cell_address_range(cell_range) -> tuple[str, int, int, int, int]:
    # address like Sheet1!A2:B3
    if not isinstance(cell_range, str) or '!' not in cell_range or ':' not in cell_range:
        return None, None, None, None, None  # Invalid input

    parts = cell_range.split('!', 1)
    if len(parts) != 2:
        return None, None, None, None, None  # Invalid cell range format

    sheet_name, range_part = parts
    start_part, end_part = range_part.split(':', 1)

    start_row_number, start_col_number = parse_column_row(start_part)
    end_row_number, end_col_number = parse_column_row(end_part)

    if (start_row_number is None or start_col_number is None or
            end_row_number is None or end_col_number is None):
        return None, None, None, None, None  # Parsing failed

    return sheet_name, start_row_number, start_col_number, end_row_number, end_col_number


def is_cell_reference(cell_reference: str) -> bool:
    """Check if the given string is a valid cell reference."""
    if not isinstance(cell_reference, str):
        return False

    # Regex pattern for a valid cell reference with Unicode characters
    pattern = r'^[^\!]+![A-Z][0-9]+$'
    return bool(re.match(pattern, cell_reference, re.UNICODE))


def is_cell_range(cell_range: str) -> bool:
    """Check if the given string is a valid cell range."""
    if not isinstance(cell_range, str):
        return False

    # Regex pattern for a valid cell range with Unicode characters
    pattern = r'^[^\!]+![A-Z][0-9]+:[A-Z][0-9]+$'
    return bool(re.match(pattern, cell_range, re.UNICODE))
