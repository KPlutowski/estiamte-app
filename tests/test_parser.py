import unittest
from unittest.mock import MagicMock
from resources.parser import Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.mock_spreadsheet_manager = MagicMock()
        self.parser = Parser(self.mock_spreadsheet_manager)

    def test_parse_cell_reference(self):
        formula = "=Sheet1!A1"
        cell = MagicMock()
        self.mock_spreadsheet_manager.get_cell.return_value = cell
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), {cell})
        self.mock_spreadsheet_manager.get_cell.assert_called_with('Sheet1!A1')

    def test_parse_range_reference(self):
        formula = "=Sheet1!A1:B2"
        cells = [MagicMock() for _ in range(4)]
        self.mock_spreadsheet_manager.get_range.return_value = cells
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), set(cells))
        self.mock_spreadsheet_manager.get_range.assert_called_with('Sheet1!A1:B2')

    def test_parse_function_call(self):
        formula = "=SUM(Sheet1!A1:B2)"
        cells = [MagicMock() for _ in range(4)]
        self.mock_spreadsheet_manager.get_cell.side_effect = cells
        self.mock_spreadsheet_manager.get_range.side_effect = lambda ref: cells if ref == 'Sheet1!A1:B2' else []
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), set(cells))

    def test_parse_nested_function(self):
        formula = "=IF(SUM(Sheet1!A1:B2)==1; SUM(Sheet1!A1:A2); 9999)"
        cells = [MagicMock() for _ in range(4)]
        cellsA1B2 = [cells[0], cells[1], cells[2], cells[3]]
        cellsA1A2 = [cells[0], cells[1]]

        self.mock_spreadsheet_manager.get_range.side_effect = lambda \
            ref: cellsA1A2 if ref == 'Sheet1!A1:A2' else cellsA1B2
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), set(cells))

    def test_parse_formula_with_invalid_reference(self):
        formula = "=Sheet1!invalid"
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), set())

    def test_parse_formula_with_invalid_function(self):
        formula = "=INVALID_FUNCTION(Sheet1!A1)"
        cell = MagicMock()
        self.mock_spreadsheet_manager.get_cell.return_value = cell
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), {cell})
        self.mock_spreadsheet_manager.get_cell.assert_called_with('Sheet1!A1')

    def test_parse_formula_with_no_reference(self):
        formula = "=2 + 2"
        dependencies = self.parser.parse_formula_for_dependencies(formula)
        self.assertEqual(set(dependencies), set([]))

    def test_parse_formula_with_multiple_functions(self):
        formula = "=SUM(Sheet1!A1:A2) + IF(Sheet1!B1 > 10; Sheet1!C1; Sheet1!D1)"
        cellB = MagicMock()  # Sheet1!B1
        cellC = MagicMock()  # Sheet1!C1
        cellD = MagicMock()  # Sheet1!D1
        cellsA1A2 = [MagicMock() for _ in range(2)]  # Mock cells for Sheet1!A1:A2
        self.mock_spreadsheet_manager.get_cell.side_effect = lambda ref: {
            'Sheet1!B1': cellB,
            'Sheet1!C1': cellC,
            'Sheet1!D1': cellD
        }.get(ref, None)

        self.mock_spreadsheet_manager.get_range.side_effect = lambda ref: {
            'Sheet1!A1:A2': cellsA1A2
        }.get(ref, [])

        dependencies = self.parser.parse_formula_for_dependencies(formula)

        expected_dependencies = cellsA1A2 + [cellB, cellC, cellD]
        self.assertEqual(set(dependencies), set(expected_dependencies))


if __name__ == '__main__':
    unittest.main()
