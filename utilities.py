def index_to_letter(index: int) -> str:
    """Convert a zero-based column index to an Excel-like column letter."""
    letter = ''
    while index >= 0:
        letter = chr(index % 26 + ord('A')) + letter
        index = index // 26 - 1
    return letter


def letter_to_index(letter: str) -> int:
    """Convert an Excel column letter to a zero-based column index."""
    index = 0
    for char in letter.upper():
        index = index * 26 + (ord(char) - ord('A'))
    return index


def is_convertible_to_float(value: str) -> bool:
    """Check if the given string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False
