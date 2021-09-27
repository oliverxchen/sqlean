"""Mixins for style transfomer."""

from os import linesep
from typing import List

from lark import Transformer
from lark.visitors import v_args

from sqlean.custom_classes import CToken, CTree


class CraftMixin(Transformer):  # type: ignore
    """Mixin that crafts tokens and trees into styled strings"""

    def __init__(self, indent: str) -> None:
        self.__indent = indent
        super().__init__()

    @property
    def indent(self) -> str:
        """String for a single indent"""
        return self.__indent

    def _simple_indent(self, node: CTree) -> str:
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def _apply_indent(self, text: str, indent_level: int) -> str:
        """Apply indentation to text"""
        return f"{self.indent * indent_level}{text}"

    def _token_indent(self, token: CToken) -> str:
        return self._apply_indent(token.upper(), token.type.indent_level)

    @staticmethod
    def _stringify_children(node: CTree) -> List[str]:
        """Stringify children"""
        return [str(child) for child in node.children]

    def _rollup_linesep(self, node: CTree) -> str:
        """Join list with linesep"""
        return linesep.join(self._stringify_children(node))

    def _rollup_space(self, node: CTree) -> str:
        """Join list with space"""
        return " ".join(self._stringify_children(node))

    def _rollup_comma_inline(self, node: CTree) -> str:
        """Join list with comma space"""
        return ", ".join(self._stringify_children(node))

    def _rollup_comma_newline(self, node: CTree) -> str:
        """Join list with comma newline"""
        return f",{linesep}".join(self._stringify_children(node))


@v_args(tree=True)
class TerminalMixin(CraftMixin):
    """Mixin for terminals that need to be separate printed"""

    def FROM(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print FROM"""
        return self._token_indent(token)

    def WHERE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WHERE"""
        return self._token_indent(token)


@v_args(tree=True)
class SelectMixin(CraftMixin):
    """Mixin for SELECT related nodes"""

    def select_statement(self, node: CTree) -> str:
        """print select_statement"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def select_list(self, node: CTree) -> str:
        """rollup items in select_list"""
        return self._rollup_comma_newline(node) + ","

    def select_item_unaliased(self, node: CTree) -> str:
        """print select_item_unaliased"""
        return self._simple_indent(node)

    def select_item_aliased(self, node: CTree) -> str:
        """print select_item_aliased"""
        output = f"{node.children[0]} AS {node.children[1]}"
        return self._apply_indent(output, node.data.indent_level)


@v_args(tree=True)
class FromMixin(CraftMixin):
    """Mixin for FROM/table related nodes"""

    def from_clause(self, node: CTree) -> str:
        """rollup items in from_clause"""
        return self._rollup_linesep(node)

    def simple_table_name(self, node: CTree) -> str:
        """print simple_table_name"""
        return self._simple_indent(node)

    def single_table_name(self, node: CTree) -> str:
        """print single_table_name"""
        return self._simple_indent(node)

    def explicit_table_name(self, node: CTree) -> str:
        """print explicit_table_name"""
        output = f"`{node.children[0]}.{node.children[1]}.{node.children[2]}`"
        return self._apply_indent(output, node.data.indent_level)


@v_args(tree=True)
class JoinMixin(CraftMixin):
    """Mixin for JOIN related nodes"""

    def join_operation_with_condition(self, node: CTree) -> str:
        """rollup join_operation_with_condition"""
        return self._rollup_linesep(node)

    def inner_join(self, node: CTree) -> str:
        """print inner_join"""
        return self._apply_indent("INNER JOIN", node.data.indent_level)

    def left_join(self, node: CTree) -> str:
        """print left_join"""
        return self._apply_indent("LEFT OUTER JOIN", node.data.indent_level)

    def right_join(self, node: CTree) -> str:
        """print right_join"""
        return self._apply_indent("RIGHT OUTER JOIN", node.data.indent_level)

    def full_join(self, node: CTree) -> str:
        """print full_join"""
        return self._apply_indent("FULL OUTER JOIN", node.data.indent_level)

    def cross_join_operation(self, node: CTree) -> str:
        """rollup cross_join_operation"""
        return self._rollup_linesep(node)

    def cross_join(self, node: CTree) -> str:
        """print cross_join"""
        return self._apply_indent("CROSS JOIN", node.data.indent_level)

    def using_clause(self, node: CTree) -> str:
        """rollup using_clause"""
        return self._apply_indent(f"USING ({node.children[2]})", node.data.indent_level)

    def using_list(self, node: CTree) -> str:
        """rollup using_list"""
        return self._rollup_comma_inline(node)

    def on_clause(self, node: CTree) -> str:
        """rollup on_clause"""
        output = self._apply_indent("ON\n", node.data.indent_level)
        return output + str(node.children[1])


@v_args(tree=True)
class FromModifierMixin(CraftMixin):
    """Mixin for FROM modifier related nodes.
    Eg GROUP BY/ORDER BY/LIMIT"""

    def where_clause(self, node: CTree) -> str:
        """rollup where_clause"""
        return self._rollup_linesep(node)

    def groupby_modifier(self, node: CTree) -> str:
        """rollup groupby_modifier"""
        output = self._apply_indent("GROUP BY\n", node.data.indent_level)
        return output + str(node.children[2])

    def groupby_list(self, node: CTree) -> str:
        """rollup groupby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def groupby_item(self, node: CTree) -> str:
        """print groupby_item"""
        return self._rollup_space(node)

    def orderby_modifier(self, node: CTree) -> str:
        """rollup orderby_modifier"""
        output = self._apply_indent("ORDER BY\n", node.data.indent_level)
        return output + str(node.children[2])

    def orderby_list(self, node: CTree) -> str:
        """rollup orderby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def orderby_item(self, node: CTree) -> str:
        """print orderby_item"""
        return self._rollup_space(node)

    def limit_clause(self, node: CTree) -> str:
        """rollup limit_clause"""
        return self._simple_indent(node)


@v_args(tree=True)
class FunctionMixin(CraftMixin):
    """Mixin for function related nodes"""

    @staticmethod
    def function_expression(node: CTree) -> str:
        """print function_expression"""
        return f"{node.children[0]}({node.children[1]})"

    def arg_list(self, node: CTree) -> str:
        """rollup arg_list"""
        return self._rollup_comma_inline(node)

    def arg_item(self, node: CTree) -> str:
        """print arg_item"""
        return self._rollup_space(node)


@v_args(tree=True)
class BoolMixin(CraftMixin):
    """Mixin for bool related nodes"""

    def leading_unary_bool_operation(self, node: CTree) -> str:
        """rollup leading_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operation(self, node: CTree) -> str:
        """print trailing_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operator(self, node: CTree) -> str:
        """print trailing_unary_bool_operator"""
        return self._rollup_space(node)

    def bool_list(self, node: CTree) -> str:
        """rollup where_list"""
        return self._rollup_linesep(node)

    def first_bool_item(self, node: CTree) -> str:
        """print first_where_item"""
        return self._simple_indent(node)

    def after_bool_item(self, node: CTree) -> str:
        """print subsequent_where_item"""
        return self._simple_indent(node)


@v_args(tree=True)
class ComparisonMixin(CraftMixin):
    """Mixin for comparison related nodes"""

    def binary_comparison_operation(self, node: CTree) -> str:
        """rollup binary_comparison_operation"""
        return self._rollup_space(node)
