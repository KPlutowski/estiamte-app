import re
from typing import List, Optional
# from Spreadsheet import SpreadsheetCell
from utilities import *


class Parser:
    def __init__(self, spreadsheet_manager):
        self.spreadsheet_manager = spreadsheet_manager

    def parse_formula_for_dependencies(self, formula: str) -> List['SpreadsheetCell']:
        """Parse formula and return a list of dependent cells."""
        dependencies = []

        # Regular expression to match cell references (e.g., =Sheet1!C3)
        cell_ref_pattern = re.compile(r'([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+)')
        # Regular expression to match range references (e.g., Sheet2!A1:A6)
        range_ref_pattern = re.compile(
            r'([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+):([A-Z]+)(\d+)')
        # Regular expression to match function calls (e.g., SUM(Sheet2!A1:A6))
        func_call_pattern = re.compile(r'\bSUM?\b\s*\(([^)]+)\)')

        # Extract cell references
        for match in cell_ref_pattern.finditer(formula):
            sheet_name = match.group(1)
            col_letter = match.group(2)
            row_number = match.group(3)
            cell_name = f"{col_letter}{row_number}"
            cell = self._get_cell_from_reference(sheet_name, col_letter, int(row_number))
            if cell:
                dependencies.append(cell)

        # Extract range references
        for match in range_ref_pattern.finditer(formula):
            sheet_name = match.group(1)
            start_col_letter = match.group(2)
            start_row_number = match.group(3)
            end_col_letter = match.group(4)
            end_row_number = match.group(5)

            start_col = letter_to_index(start_col_letter)
            end_col = letter_to_index(end_col_letter)
            start_row = int(start_row_number) - 1
            end_row = int(end_row_number) - 1

            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell = self._get_cell_from_reference(sheet_name, index_to_letter(col), row + 1)
                    if cell:
                        dependencies.append(cell)

        # Extract function calls (if the function contains cell or range references)
        for match in func_call_pattern.finditer(formula):
            inner_formula = match.group(1)
            # Recursive call to handle nested formulas
            dependencies.extend(self.parse_formula_for_dependencies(inner_formula))

        return dependencies

    def _get_cell_from_reference(self, sheet_name: str, col_letter: str, row_number: int) -> Optional['SpreadsheetCell']:
        """Get a cell from a reference."""
        cell_index = letter_to_index(col_letter)
        return self.spreadsheet_manager.get_cell(row_number - 1, cell_index, sheet_name)

    def make_python_formula(self, cell: 'SpreadsheetCell'):
        """Create a Python formula based on the cell's formula"""
        formula = cell.formula

        # Remove the '=' at the start of the formula
        formula = formula[1:]

        # Regular expressions for different types of references
        cell_ref_pattern = re.compile(r'([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+)')
        range_ref_pattern = re.compile(
            r'([A-Za-z_\u00C0-\u017F][A-Za-z0-9_\u00C0-\u017F]*)!([A-Z]+)(\d+):([A-Z]+)(\d+)')
        func_call_pattern = re.compile(r'\bSUM?\b\s*\(([^)]+)\)')

        def replace_cell_ref(match):
            sheet_name = match.group(1)
            col_letter = match.group(2)
            row_number = match.group(3)
            cell_index = letter_to_index(col_letter)
            return f"float(self.get_cell({int(row_number) - 1}, {cell_index}, '{sheet_name}').value)"

        def replace_range_ref(match):
            sheet_name = match.group(1)
            start_col_letter = match.group(2)
            start_row_number = match.group(3)
            end_col_letter = match.group(4)
            end_row_number = match.group(5)

            start_col = letter_to_index(start_col_letter)
            end_col = letter_to_index(end_col_letter)
            start_row = int(start_row_number) - 1
            end_row = int(end_row_number) - 1

            return f"self._get_range({start_row}, {start_col}, {end_row}, {end_col}, '{sheet_name}')"

        def replace_func_call(match):
            inner_formula = match.group(1)
            return f"self.sum({inner_formula})"  # Note: Assumes function calls need further parsing

        # Convert range references
        formula = range_ref_pattern.sub(replace_range_ref, formula)

        # Convert cell references
        formula = cell_ref_pattern.sub(replace_cell_ref, formula)

        # Convert function calls
        formula = func_call_pattern.sub(replace_func_call, formula)

        cell.python_formula = formula

