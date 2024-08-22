import unittest
from resources.parser import Tokenizer, Token, TokenType, ValueType


class TestTokenizer(unittest.TestCase):
    def assertTokenListEqual(self, actual, expected):
        self.assertEqual(
            [(token.value, token.token_type, token.subtype) for token in actual],
            [(token.value, token.token_type, token.subtype) for token in expected]
        )

    def test_simple_expression(self):
        formula = "A1+B2"
        expected = [
            Token('A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('+', TokenType.OPERATOR, None),
            Token('B2', TokenType.VALUE, ValueType.IDENTIFIER)
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_function_call(self):
        formula = "SUM(sheet1!A1:A10)"
        expected = [
            Token('SUM', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1:A10', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_function_with_parameters(self):
        formula = "IF(sheet1!A1=1, sheet1!B2, sheet1!C3)"
        expected = [
            Token('IF', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('=', TokenType.OPERATOR, None),
            Token('1', TokenType.VALUE, ValueType.NUMBER),
            Token(',', TokenType.COMMA, None),
            Token('sheet1!B2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(',', TokenType.COMMA, None),
            Token('sheet1!C3', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_cell_reference_with_sheet(self):
        formula = "Pozycje!A1 + Właściwości!B2"
        expected = [
            Token('Pozycje!A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('+', TokenType.OPERATOR, None),
            Token('Właściwości!B2', TokenType.VALUE, ValueType.IDENTIFIER)
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_nested_function_1(self):
        formula = "AVERAGE(SUM(sheet1!A1:A10), MAX(sheet1!B1:B10))"
        expected = [
            Token('AVERAGE', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('SUM', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1:A10', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token(',', TokenType.COMMA),
            Token('MAX', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!B1:B10', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_string_literal(self):
        formula = '"Hello World"'
        expected = [
            Token('Hello World', TokenType.VALUE, ValueType.STRING)
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_expression_with_strings(self):
        formula = 'IF(sheet1!A1="Yes", "Confirmed", "Pending")'
        expected = [
            Token('IF', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('=', TokenType.OPERATOR, None),
            Token('Yes', TokenType.VALUE, ValueType.STRING),
            Token(',', TokenType.COMMA),
            Token('Confirmed', TokenType.VALUE, ValueType.STRING),
            Token(',', TokenType.COMMA),
            Token('Pending', TokenType.VALUE, ValueType.STRING),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_complex_expression(self):
        formula = 'IF(AND(sheet1!A1>1, sheet1!B2<5), "In Range", "Out of Range")'
        expected = [
            Token('IF', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('AND', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('>', TokenType.OPERATOR, None),
            Token('1', TokenType.VALUE, ValueType.NUMBER),
            Token(',', TokenType.COMMA),
            Token('sheet1!B2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('<', TokenType.OPERATOR, None),
            Token('5', TokenType.VALUE, ValueType.NUMBER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token(',', TokenType.COMMA),
            Token('In Range', TokenType.VALUE, ValueType.STRING),
            Token(',', TokenType.COMMA),
            Token('Out of Range', TokenType.VALUE, ValueType.STRING),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_nested_function_2(self):
        formula = "IF(SUM(sheet1!A1:B2)==1; SUM(sheet1!A1:A2);9999)"
        expected = [
            Token('IF', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('SUM', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1:B2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token('=', TokenType.OPERATOR, None),
            Token('=', TokenType.OPERATOR, None),
            Token('1', TokenType.VALUE, ValueType.NUMBER),
            Token(';', TokenType.SEMICOLON, None),
            Token('SUM', TokenType.FUNCTION, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('sheet1!A1:A2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token(';', TokenType.SEMICOLON, None),
            Token('9999', TokenType.VALUE, ValueType.NUMBER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_multiple_operators(self):
        formula = 'A1+B2-C3*D4/E5'
        expected = [
            Token('A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('+', TokenType.OPERATOR, None),
            Token('B2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('-', TokenType.OPERATOR, None),
            Token('C3', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('*', TokenType.OPERATOR, None),
            Token('D4', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('/', TokenType.OPERATOR, None),
            Token('E5', TokenType.VALUE, ValueType.IDENTIFIER)
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_empty_formula(self):
        formula = ""
        expected = []
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_spaces_around_operators(self):
        formula = ' A1  +   B2 '
        expected = [
            Token('A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('+', TokenType.OPERATOR, None),
            Token('B2', TokenType.VALUE, ValueType.IDENTIFIER)
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)

    def test_parentheses_edge_cases(self):
        formula = "(A1 + (B2 - C3))"
        expected = [
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('A1', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('+', TokenType.OPERATOR, None),
            Token('(', TokenType.PARENTHESIS, 'OPEN'),
            Token('B2', TokenType.VALUE, ValueType.IDENTIFIER),
            Token('-', TokenType.OPERATOR, None),
            Token('C3', TokenType.VALUE, ValueType.IDENTIFIER),
            Token(')', TokenType.PARENTHESIS, 'CLOSE'),
            Token(')', TokenType.PARENTHESIS, 'CLOSE')
        ]
        self.assertTokenListEqual(Tokenizer.tokenize(formula), expected)


if __name__ == '__main__':
    unittest.main()
