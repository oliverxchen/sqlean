"""NOTE: most of the parts of sql_styler.py are tested in integration
testing in tests/test_snapshots.py
"""
from lark.exceptions import VisitError
import pytest

from sqlean.custom_classes import CData, CTree
from sqlean.sql_styler import Styler, BaseMixin


def test_unknown_node() -> None:
    tree = CTree(data=CData(name="unknown_node"), children=[])
    with pytest.raises(NotImplementedError) as exc:
        Styler("").transform(tree)
    exc.match("Unsupported node: unknown_node")


def test_window_function_expression_branch_not_implemented() -> None:
    tree = CTree(data=CData(name="window_function_expression"), children=[])
    with pytest.raises(VisitError) as exc:
        Styler("").transform(tree)
    exc.match("window_function_expression: not implemented for 0 children")


def test_change_indent_size() -> None:
    four_space_indent = 4 * " "
    input_str = f"a\n{four_space_indent}b\n{four_space_indent}c\n"
    two_space_indent = 2 * " "
    expected = f"a\n{two_space_indent}b\n{two_space_indent}c\n"
    actual = BaseMixin._change_indent_size(input_str, 2)
    assert actual == expected
