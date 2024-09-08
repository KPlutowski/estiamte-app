from typing import List
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
        pass

    @staticmethod
    def tokenize(formula: str) -> List[Token]:
        operators = {'+', '-', '*', '/', '=', '<', '>', '(', ')'}
        delimiters = {',', ';'}
        functions = {'IF', 'SUM', 'AVERAGE', 'MAX', 'MIN', 'AND', 'OR'}

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
                        if token.strip() in functions:
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
                elif char in operators:
                    if token:
                        if token.replace('.', '', 1).isdigit():
                            add_token(token, TokenType.VALUE, ValueType.NUMBER)
                        else:
                            add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)
                        token = ''
                    tokens.append(Token(char, TokenType.OPERATOR))
                elif char in delimiters:
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
            if token in functions:
                add_token(token, TokenType.FUNCTION)
            elif token.replace('.', '', 1).isdigit():
                add_token(token, TokenType.VALUE, ValueType.NUMBER)
            else:
                add_token(token, TokenType.VALUE, ValueType.IDENTIFIER)

        return tokens


class Parser:
    def __init__(self):
        pass

    @staticmethod
    def parse_formula_for_dependencies(formula: str) -> List['ItemWithFormula']:
        """Parse formula and return a list of dependent cells."""
        from model.Model import Model
        if formula.startswith('='):
            formula = formula[1:]
        else:
            return list()
        dependencies = set()
        tokens = Tokenizer.tokenize(formula)

        for token in tokens:
            if token.token_type == TokenType.VALUE:
                if token.subtype == ValueType.IDENTIFIER:
                    if is_valid_cell_reference(token.value):
                        cell = Model.get_cell(token.value)
                        if cell:
                            dependencies.add(cell)
                    elif is_valid_cell_range(token.value):
                        cells = Model.get_range(token.value)
                        dependencies.update(cells)
                    elif is_valid_properties_field(token.value):
                        _property = Model.get_property(token.value)
                        if _property:
                            dependencies.add(_property)
                    else:
                        pass
            elif token.token_type == TokenType.FUNCTION:
                pass

        return list(dependencies)

    ####################################################################

    @staticmethod
    def make_python_formula(formula: str) -> str:
        """Convert a spreadsheet formula to a Python expression."""
        if formula.startswith('='):
            formula = formula[1:]
        else:
            return ''
        tokens = Tokenizer.tokenize(formula)

        def convert_token(token: Token) -> str:
            if token.token_type == TokenType.VALUE:
                if token.subtype == ValueType.IDENTIFIER:
                    if is_valid_cell_reference(token.value):
                        return f"Model.get_cell('{token.value}').value"
                    elif is_valid_cell_range(token.value):
                        return f"Model.get_range('{token.value}')"
                    elif is_valid_properties_field(token.value):
                        return f"Model.get_property('{token.value}').value"
                    else:
                        return token.value
                elif token.subtype == ValueType.NUMBER:
                    return token.value
                elif token.subtype == ValueType.STRING:
                    return f'"{token.value}"'
            elif token.token_type == TokenType.FUNCTION:
                func = token.value
                if func == 'SUM':
                    return 'Model.sum_function'
                elif func == 'IF':
                    return 'Model.if_function'
                elif func == 'AVERAGE':
                    return 'Model.average_function'
                elif func == 'MAX':
                    return 'Model.max_function'
                elif func == 'MIN':
                    return 'Model.min_function'
                elif func == 'AND':
                    return 'Model.and_function'
                elif func == 'OR':
                    return 'Model.or_function'
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


