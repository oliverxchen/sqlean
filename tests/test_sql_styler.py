"""NOTE: most of the parts of sql_styler.py are tested in integration
testing in tests/test_snapshots.py
"""
from lark.exceptions import VisitError
import pytest

from sqlean.custom_classes import CData, CTree, CToken
from sqlean.sql_styler import Styler, BaseMixin, CommentedListClass, TerminalMixin


def test_commented_list_class__get_last_item_idx() -> None:
    item = CTree(data=CData(name="item"), children=[])
    not_item = CTree(data=CData(name="not_item"), children=[])

    list_second_last = CommentedListClass(
        item_types={"item"}, children=[not_item, item, item, not_item]
    )
    assert list_second_last.last_item_idx == 2

    list_last = CommentedListClass(
        item_types={"item"}, children=[not_item, item, item, item]
    )
    assert list_last.last_item_idx == 3

    list_first = CommentedListClass(
        item_types={"item"}, children=[item, not_item, not_item, not_item]
    )
    assert list_first.last_item_idx == 0


def test_commented_list_class__lines_from_previous() -> None:
    comment = CToken(
        type_=CData(name="COMMENT", lines_from_previous=1, lines_to_next=2),
        value="-- comment",
    )
    other = CTree(data=CData(name="other"), children=[])
    assert CommentedListClass()._lines_from_previous(comment, other) == 1
    assert CommentedListClass()._lines_from_previous(other, comment) == 2
    assert CommentedListClass()._lines_from_previous(other, other) is None

    # Here the child is checked first (and not the previous child)
    assert CommentedListClass()._lines_from_previous(comment, comment) == 1


def test_commented_list_class__is_item() -> None:
    item_types = {"tree_item", "TOKEN_ITEM"}
    list_ = CommentedListClass(item_types=item_types)

    token_item = CToken(type_=CData(name="TOKEN_ITEM"), value="token")
    assert list_._is_item(token_item)

    tree_item = CTree(data=CData(name="tree_item"), children=[])
    assert list_._is_item(tree_item)

    token_not_item = CToken(type_=CData(name="TOKEN_NOT_ITEM"), value="token")
    assert list_._is_item(token_not_item) is False

    tree_not_item = CTree(data=CData(name="tree_not_item"), children=[])
    assert list_._is_item(tree_not_item) is False


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


def test__format_block_comment() -> None:
    block_comment = "/*This\nis\na\nblock\ncomment*/"
    assert (
        TerminalMixin._format_block_comment(block_comment)
        == "/* This\n   is\n   a\n   block\n   comment*/"
    )
    another_block_comment = "/*   Another\nblock\ncomment\n*/"
    assert (
        TerminalMixin._format_block_comment(another_block_comment)
        == "/* Another\n   block\n   comment\n*/"
    )
