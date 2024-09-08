from enum import Enum

from resources.utils import is_convertible_to_float


class ErrorType(Enum):
    REF = ("#REF!", 'Invalid cell reference.')
    DIV = ('#DIV/0!', 'Division by zero.')
    NAME = ('#NAME?', 'Invalid function or range name.')
    VALUE = ('#VALUE!', 'Wrong type of argument or operand.')
    NA = ('#N/A', 'A value is not available.')
    NUM = ('#NUM!', 'Invalid numeric value.')
    NULL = ('#NULL!', 'Incorrect use of range in formula.')
    CIRCULAR = ('#CIRCULAR!', 'Circular reference detected.')


class FormulaType(Enum):
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    EXPRESSION = 'EXPRESSION'
    NO_TYPE = 'NO_TYPE'

    @staticmethod
    def determine_formula_type(formula: str) -> 'FormulaType':
        """Determine the type of the formula based on its content."""
        if formula.startswith('='):
            return FormulaType.EXPRESSION
        elif is_convertible_to_float(formula):
            return FormulaType.NUMBER
        else:
            return FormulaType.STRING