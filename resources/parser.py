from typing import List, Optional
from resources.utils import *


class TokenType:
    VALUE = 'VALUE'
    OPERATOR = 'OPERATOR'
    PARENTHESIS = 'PARENTHESIS'
    COMMA = 'COMMA'
    SEMICOLON = 'SEMICOLON'
    FUNCTION = 'FUNCTION'


class ValueType:
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'


class Token:
    def __init__(self, value: str, token_type: str, subtype: str = None):
        self.value = value
        self.token_type = token_type
        self.subtype = subtype

    def __repr__(self):
        return f"Token(value={self.value}, type={self.token_type}, subtype={self.subtype})"


class Tokenizer:
    def __init__(self):
        self.operators = {'+', '-', '*', '/', '=', '<', '>', '(', ')'}
        self.delimiters = {',', ';'}
        self.functions = {'IF', 'SUM', 'AVERAGE', 'MAX', 'MIN', 'AND', 'OR'}

    def tokenize(self, formula: str) -> List[Token]:
        tokens = []
        token = ''
        inside_parentheses = 0
        in_string = False

        def add_token(value, token_type, subtype=None):
            if value.strip():
                tokens.append(Token(value.strip(), token_type, subtype))

        for char in formula:
            if char == '"':
                in_string = not in_string
                if not in_string:
                    add_token(token, TokenType.VALUE, ValueType.STRING)
                    token = ''
            elif in_string:
                token += char
            else:
                if char == '(':
                    if token:
                        # Handle function names and identifiers
                        if token.strip() in self.functions:
                            add_token(token, TokenType.FUNCTION)
                        else:
                            add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)
                        token = ''
                    tokens.append(Token(char, TokenType.PARENTHESIS, 'OPEN'))
                    inside_parentheses += 1
                elif char == ')':
                    if token.replace('.', '', 1).isdigit():
                        add_token(token, TokenType.VALUE, ValueType.NUMBER)
                    else:
                        add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)
                    token = ''
                    tokens.append(Token(char, TokenType.PARENTHESIS, 'CLOSE'))
                    inside_parentheses -= 1
                elif char in self.operators:
                    if token:
                        if token.replace('.', '', 1).isdigit():
                            add_token(token, TokenType.VALUE, ValueType.NUMBER)
                        else:
                            add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)
                        token = ''
                    tokens.append(Token(char, TokenType.OPERATOR))
                elif char in self.delimiters:
                    if token:
                        if is_convertible_to_float(token):
                            add_token(token, TokenType.VALUE, ValueType.NUMBER)
                            token = ''
                        else:
                            add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)
                            token = ''

                    tokens.append(Token(char, TokenType.COMMA if char == ',' else TokenType.SEMICOLON))
                else:
                    token += char

        if token:
            if token in self.functions:
                add_token(token, TokenType.FUNCTION)
            elif token.replace('.', '', 1).isdigit():
                add_token(token, TokenType.VALUE, ValueType.NUMBER)
            else:
                add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)

        return tokens


class Parser:
    def __init__(self, spreadsheet_manager):
        self._model: 'Model' = spreadsheet_manager
        self.tokenizer = Tokenizer()

    def parse_formula_for_dependencies(self, formula: str) -> List['SpreadsheetCell']:
        """Parse formula and return a list of dependent cells."""
        if formula.startswith('='):
            formula = formula[1:]
        else:
            return list()
        dependencies = set()
        tokens = self.tokenizer.tokenize(formula)

        for token in tokens:
            if token.token_type == TokenType.VALUE:
                if token.subtype == ValueType.IDENTIFIER:
                    if is_valid_cell_reference(token.value):
                        cell = self._get_cell_reference(token)
                        if cell:
                            dependencies.add(cell)
                    elif is_valid_cell_range(token.value):
                        cells = self._get_range_reference(token)
                        dependencies.update(cells)
                    else:
                        pass
            elif token.token_type == TokenType.FUNCTION:
                pass

        return list(dependencies)

    ####################################################################

    def _get_cell_reference(self, token: Token) -> Optional['SpreadsheetCell']:
        """Parse a cell reference token."""
        return self._model.get_cell(token.value)

    def _get_range_reference(self, token: Token) -> List['SpreadsheetCell']:
        """Parse a range reference token."""
        return self._model.get_range(token.value)

    def make_python_formula(self, cell: 'SpreadsheetCell') -> str:
        """Convert a spreadsheet formula to a Python expression."""

        formula = cell.formula
        if formula.startswith('='):
            formula = formula[1:]
        else:
            return ''
        tokens = self.tokenizer.tokenize(formula)

        def convert_token(token: Token) -> str:
            if token.token_type == TokenType.VALUE:
                if token.subtype == ValueType.IDENTIFIER:
                    if is_valid_cell_reference(token.value):
                        return f"self.get_cell('{token.value}').value"
                    elif is_valid_cell_range(token.value):
                        return f"self.get_range('{token.value}')"
                    else:
                        return token.value
                elif token.subtype == ValueType.NUMBER:
                    return token.value
                elif token.subtype == ValueType.STRING:
                    return f'"{token.value}"'
            elif token.token_type == TokenType.FUNCTION:
                func = token.value
                if func == 'SUM':
                    return 'self.sum_function'
                elif func == 'IF':
                    return 'self.if_function'
                elif func == 'AVERAGE':
                    return 'self.average_function'
                elif func == 'MAX':
                    return 'self.max_function'
                elif func == 'MIN':
                    return 'self.min_function'
                elif func == 'AND':
                    return 'self.and_function'
                elif func == 'OR':
                    return 'self.or_function'
            elif token.token_type == TokenType.OPERATOR:
                return token.value
            elif token.token_type in {TokenType.COMMA, TokenType.SEMICOLON}:
                return ','
            elif token.token_type == TokenType.PARENTHESIS:
                return '(' if token.subtype == 'OPEN' else ')'
            return ''

        # Convert the tokens to Python expression
        python_expression = ''.join(convert_token(token) for token in tokens)

        return python_expression
