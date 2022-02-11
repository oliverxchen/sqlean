"""Styling of SQL queries"""

from os import linesep
from typing import List

import black
from lark import Transformer
from lark.tree import Tree
from lark.lexer import Token
from lark.visitors import v_args

from sqlean.custom_classes import CToken, CTree


class BaseMixin(Transformer):  # type: ignore
    """Mixin that crafts tokens and trees into styled strings"""

    def __init__(self, indent: str) -> None:
        self.__indent = indent
        super().__init__()

    @property
    def indent(self) -> str:
        """String for a single indent"""
        return self.__indent

    def _simple_indent(self, node: CTree) -> str:
        """Apply indentation to a node, left strips previous indentation"""
        return self._apply_indent(
            self._rollup_space(node).lstrip(), node.data.indent_level
        )

    def _apply_indent(self, text: str, indent_level: int) -> str:
        """Apply indentation to text"""
        lines = [f"{self.indent * indent_level}{line}" for line in text.split(linesep)]
        return linesep.join(lines)

    def _token_indent(self, token: CToken) -> str:
        return self._apply_indent(token.upper(), token.type.indent_level)

    @staticmethod
    def _stringify_children(node: CTree) -> List[str]:
        """Stringify children"""
        return [str(child) for child in node.children]

    def _rollup(self, node: CTree) -> str:
        """Join list"""
        return "".join(self._stringify_children(node))

    def _rollup_linesep(self, node: CTree) -> str:
        """Join list with linesep"""
        return linesep.join(self._stringify_children(node))

    def _rollup_double_linesep(self, node: CTree) -> str:
        """Join list with a double linesep"""
        return (2 * linesep).join(self._stringify_children(node))

    def _rollup_space(self, node: CTree) -> str:
        """Join list with space"""
        output = [child.lstrip() for child in self._stringify_children(node)]
        return " ".join(output)

    def _rollup_dot(self, node: CTree) -> str:
        """Join list with space"""
        return ".".join(self._stringify_children(node))

    def _rollup_comma_inline(self, node: CTree) -> str:
        """Join list with comma space"""
        return ", ".join(self._stringify_children(node))

    @staticmethod
    def _apply_black(input_str: str) -> str:
        """Apply black to token"""
        return black.format_str(input_str, mode=black.Mode()).strip()  # type: ignore


@v_args(tree=True)
class TerminalMixin(BaseMixin):
    """Mixin for terminals that need to be separately printed"""

    def FROM(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print FROM"""
        return self._token_indent(token)

    def WHERE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WHERE"""
        return self._token_indent(token)

    def CONFIG(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print CONFIG"""
        blacked = self._apply_black(token[2:-2])
        return "{{\n" + self._apply_indent(blacked, 1) + "\n}}"

    def __format_macro_expr(self, token: CToken) -> str:
        """form single line macro expressions"""
        blacked = self._apply_black(token[2:-2])
        # single line print when black returns one line
        if len(blacked.splitlines()) == 1:
            return self._apply_indent("{{ " + blacked + " }}", token.type.indent_level)

        # multi line print
        return self._apply_indent(
            "{{\n" + self._apply_indent(blacked, 1) + "\n}}",
            token.type.indent_level,
        )

    def DBT_SOURCE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print DBT_SOURCE"""
        return self.__format_macro_expr(token)

    def DBT_REF(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print DBT_REF"""
        return self.__format_macro_expr(token)

    def MACRO(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print MACRO"""
        return self.__format_macro_expr(token)

    @staticmethod
    def INLINE_COMMENT(token: Token) -> Token:  # pylint: disable=invalid-name
        """print INLINE_COMMENT"""
        content = "-- " + token[2:].strip()
        token = token.update(value=content)
        return token


@v_args(tree=True)
class QueryMixin(BaseMixin):
    """Mixin for query level nodes"""

    def query_file(self, node: CTree) -> str:
        """print query_file"""
        return self._rollup_double_linesep(node)

    def query_expr(self, node: CTree) -> str:
        """rollup itms in query_expr"""
        output: List[str] = []
        counter = 0
        for child in node.children:
            if str(child) == ",":
                output[counter - 1] += ","
            elif counter == 0:
                output.append(self._apply_indent(str(child), node.data.indent_level))
                counter += 1
            else:
                output.append(str(child))
                counter += 1
        return (2 * linesep).join(output)

    def sub_query_expr(self, node: CTree) -> str:
        """print sub_query_expr"""
        return (
            self._apply_indent(str(node.children[0]), node.data.indent_level)
            + linesep
            + str(node.children[1])
            + linesep
            + self._apply_indent(str(node.children[2]), node.data.indent_level)
        )

    def with_clause(self, node: CTree) -> str:
        """print with_clause"""
        if len(node.children) == 1:
            return self._simple_indent(node)

        return (
            self._apply_indent(f"{node.children[0]} AS (", node.data.indent_level)
            + linesep
            + str(node.children[3])
            + linesep
            + self._apply_indent(str(node.children[4]), node.data.indent_level)
        )


@v_args(tree=True)
class SelectMixin(BaseMixin):
    """Mixin for SELECT related nodes"""

    def select_expr(self, node: CTree) -> str:
        """rollup itms in select_expr"""
        return self._rollup_linesep(node)

    def select_type(self, node: CTree) -> str:
        """print select_type"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    @staticmethod
    def select_list(node: CTree) -> str:
        """rollup items in select_list"""
        counter = 0
        output: List[str] = []
        while counter < len(node.children):
            child = node.children[counter]
            if counter + 1 < len(node.children):
                next_child = node.children[counter + 1]
                if (
                    isinstance(next_child, Token)
                    and next_child.type == "INLINE_COMMENT"
                ):
                    output.append(f"{str(child)},  {str(next_child)}")
                    counter += 1
                else:
                    output.append(str(child) + ",")
            else:
                output.append(str(child) + ",")
            counter += 1
        return linesep.join(output)

    def select_item_unaliased(self, node: CTree) -> str:
        """print select_item_unaliased"""
        return self._simple_indent(node)

    def select_item_aliased(self, node: CTree) -> str:
        """print select_item_aliased"""
        output = f"{node.children[0]} AS {node.children[1]}"
        return self._apply_indent(output, node.data.indent_level)

    def table_referenced_field(self, node: CTree) -> str:
        """print table_referenced_field"""
        return self._rollup_dot(node)

    def when_item(self, node: CTree) -> str:
        """print when_item"""
        # turn multi-line bool_list into single line
        bool_list = str(node.children[1]).split("\n")
        bool_list = [item.lstrip() for item in bool_list]
        item = f'WHEN {" ".join(bool_list)} THEN {node.children[3]}'
        # indent 1 relatvie to case header and end footer
        return self._apply_indent(item, 1)

    def when_list(self, node: CTree) -> str:
        """print when_list"""
        return self._rollup_linesep(node)

    @staticmethod
    def common_case_expression(node: CTree) -> str:
        """print common_case_expression"""
        case_line = f"CASE {node.children[1]}\n"
        other_lines = linesep.join([str(item) for item in node.children[2:]])
        return case_line + other_lines

    def else_clause(self, node: CTree) -> str:
        """print else_clause"""
        # indent 1 relative to case header and end footer
        return self._apply_indent(self._rollup_space(node), 1)

    def separate_case_expression(self, node: CTree) -> str:
        """print separate_case_expression"""
        return self._rollup_linesep(node)


@v_args(tree=True)
class FromMixin(BaseMixin):
    """Mixin for FROM/table related nodes"""

    def from_clause(self, node: CTree) -> str:
        """rollup items in from_clause"""
        return self._rollup_linesep(node)

    def simple_table_name(self, node: CTree) -> str:
        """print simple_table_name"""
        return self._simple_indent(node)

    def explicit_table_name(self, node: CTree) -> str:
        """print explicit_table_name"""
        output = f"`{self._rollup_dot(node)}`"
        return self._apply_indent(output, node.data.indent_level)

    def table_item_aliased(self, node: CTree) -> str:
        """print explicit_table_name"""
        output = f"{str(node.children[0]).lstrip()} AS {node.children[1]}"
        return self._apply_indent(output, node.data.indent_level)


@v_args(tree=True)
class JoinMixin(BaseMixin):
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
        output = self._apply_indent("ON", node.data.indent_level)
        return output + linesep + str(node.children[1])


@v_args(tree=True)
class FromModifierMixin(BaseMixin):
    """Mixin for FROM modifier related nodes.
    Eg GROUP BY/ORDER BY/LIMIT"""

    def groupby_modifier(self, node: CTree) -> str:
        """rollup groupby_modifier"""
        output = self._apply_indent("GROUP BY", node.data.indent_level)
        output += linesep + str(node.children[1])
        if len(node.children) == 3:
            output += linesep + str(node.children[2])
        return output

    def field_list(self, node: CTree) -> str:
        """rollup field_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def orderby_modifier(self, node: CTree) -> str:
        """rollup orderby_modifier"""
        output = self._apply_indent("ORDER BY", node.data.indent_level)
        return output + linesep + str(node.children[1])

    def orderby_list(self, node: CTree) -> str:
        """rollup orderby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def orderby_item(self, node: CTree) -> str:
        """print orderby_item"""
        return self._rollup_space(node)

    def having_clause(self, node: CTree) -> str:
        """print having_clause"""
        output = self._apply_indent("HAVING", node.data.indent_level)
        return output + linesep + str(node.children[1])

    def limit_clause(self, node: CTree) -> str:
        """rollup limit_clause"""
        return self._simple_indent(node)


@v_args(tree=True)
class FunctionMixin(BaseMixin):
    """Mixin for function related nodes"""

    @staticmethod
    def standard_function_expression(node: CTree) -> str:
        """print standard_function_expression"""
        return f"{str(node.children[0])}({node.children[1]})"

    @staticmethod
    def function_name(node: CTree) -> str:
        """print function_name"""
        if len(node.children) == 6:
            upper_set = {5}
        elif len(node.children) == 3 and str(node.children[0]).upper() != "SAFE":
            upper_set = {2}
        else:
            upper_set = set(range(len(node.children)))
        children: List[str] = []
        for i, child in enumerate(node.children):
            if i in upper_set:
                children.append(str(child).upper())
            else:
                children.append(str(child))
        return "".join(children)

    def arg_list(self, node: CTree) -> str:
        """rollup arg_list"""
        return self._rollup_comma_inline(node)

    def arg_item(self, node: CTree) -> str:
        """print arg_item"""
        return self._rollup_space(node)

    def data_type(self, node: CTree) -> str:
        """print data_type"""
        return self._rollup(node)

    def window_specification(self, node: CTree) -> str:
        """print window_specification"""
        return self._rollup_space(node)

    def over_clause(self, node: CTree) -> str:
        """print over_clause"""
        return f"OVER ({self._rollup(node)})"

    @staticmethod
    def window_function_expression(node: CTree) -> str:
        """print window_function_expression"""
        if len(node.children) == 3:
            output = f"{node.children[0]}({node.children[1]}) {node.children[2]}"
        elif len(node.children) == 2:
            output = f"{str(node.children[0])}() {node.children[1]}"
        else:
            raise NotImplementedError(
                "window_function_expression: "
                f"not implemented for {len(node.children)} children"
            )
        return output

    @staticmethod
    def window_orderby_modifier(node: CTree) -> str:
        """print window_orderby_modifier"""
        return f"ORDER BY {str(node.children[1]).lstrip()}"

    @staticmethod
    def partition_modifier(node: CTree) -> str:
        """print partition_modifier"""
        return f"PARTITION BY {str(node.children[1]).lstrip()}"


@v_args(tree=True)
class BoolMixin(BaseMixin):
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
class ComparisonMixin(BaseMixin):
    """Mixin for comparison related nodes"""

    def binary_comparison_operation(self, node: CTree) -> str:
        """rollup binary_comparison_operation"""
        return self._rollup_space(node)


@v_args(tree=True)
class JinjaMixin(BaseMixin):
    """Mixin for Jinja related nodes"""

    def dbt_table_name(self, node: CTree) -> str:
        """print dbt_table_name"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)


@v_args(tree=True)
class Styler(  # pylint: disable=too-many-ancestors
    BoolMixin,
    ComparisonMixin,
    FromMixin,
    FromModifierMixin,
    FunctionMixin,
    JinjaMixin,
    JoinMixin,
    QueryMixin,
    SelectMixin,
    TerminalMixin,
):
    """Pretty printer: formats the lists of atoms and the overall query"""

    def __default__(self, data: str, children: List[Tree], meta: str) -> str:
        """default for all Trees without a callback"""
        raise NotImplementedError(f"Unsupported node: {data}")

    def __default_token__(self, token: CToken) -> str:
        if self._is_non_keyword(token):
            return token
        return token.upper()

    @staticmethod
    def _is_non_keyword(token: CToken) -> bool:
        return (
            token.type.endswith("NAME")
            or token.type.endswith("_EXPR")
            or token.type.endswith("_ID")
            or token.type.endswith("_STRING")
        )
