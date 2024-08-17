import unittest
from unittest.mock import MagicMock
from resources.parser import Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.mock_spreadsheet_manager = MagicMock()
        self.parser = Parser(self.mock_spreadsheet_manager)

    def test_make_python_formula_cell_reference(self):
        cell = MagicMock()
        cell.formula = "=Sheet1!A1"
        expected = "self.get_cell('Sheet1!A1').value"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_range_reference(self):
        cell = MagicMock()
        cell.formula = "=Sheet1!A1:B2"
        expected = "self.get_range('Sheet1!A1:B2')"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_sum_function(self):
        cell = MagicMock()
        cell.formula = "=SUM(Sheet1!A1:B2)"
        expected = "self.sum_function(self.get_range('Sheet1!A1:B2'))"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_if_function(self):
        cell = MagicMock()
        cell.formula = "=IF(Sheet1!A1 > 10; Sheet1!B1; 5)"
        expected = "self.if_function(self.get_cell('Sheet1!A1').value>10,self.get_cell('Sheet1!B1').value,5)"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_complex_formula(self):
        cell = MagicMock()
        cell.formula = "=SUM(Sheet1!A1:A2) + IF(Sheet1!B1 > 10; Sheet1!C1; Sheet1!D1)"
        expected = "self.sum_function(self.get_range('Sheet1!A1:A2'))+self.if_function(self.get_cell('Sheet1!B1').value>10,self.get_cell('Sheet1!C1').value,self.get_cell('Sheet1!D1').value)"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_empty_formula(self):
        cell = MagicMock()
        cell.formula = "="
        expected = ""
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_no_formula(self):
        cell = MagicMock()
        cell.formula = "string"
        expected = ""
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)

    def test_make_python_formula_only_operators(self):
        cell = MagicMock()
        cell.formula = "=+ - * /"
        expected = "+-*/"
        result = self.parser.make_python_formula(cell)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
