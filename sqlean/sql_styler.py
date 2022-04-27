"""Styling of SQL queries"""

from os import linesep
from typing import List, Union

import black
from lark.tree import Tree
from lark.lexer import Token
from lark.visitors import v_args, Transformer

from sqlean.custom_classes import CToken, CTree


class BaseMixin(Transformer):  # type: ignore
    """Mixin that crafts tokens and trees into styled strings"""

    def __init__(self, indent: str) -> None:
        self.__indent = indent
        self.__indent_size = len(indent)
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

    def _token_indent_adjust_case(self, token: CToken) -> str:
        return self._apply_indent(token.upper(), token.type.indent_level)

    def _token_indent(self, token: CToken) -> str:
        return self._apply_indent(token, token.type.indent_level)

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

    def _rollup_comma_inline(self, node: CTree) -> str:
        """Join list with comma space"""
        return ", ".join(self._stringify_children(node))

    def _apply_black(self, input_str: str) -> str:
        """Apply black to token"""
        return self._change_indent_size(
            black.format_str(input_str, mode=black.Mode()).strip(),  # type: ignore
            self.__indent_size,
        )

    @staticmethod
    def _change_indent_size(input_str: str, indent_size: int) -> str:
        """Change the default indent size of 4 used by black to the specified
        indent size"""
        lines = input_str.split(linesep)
        for i, line in enumerate(lines):
            if line.startswith(" " * 4):
                lines[i] = line.replace(" " * 4, " " * indent_size)
        return linesep.join(lines)


@v_args(tree=True)
class TerminalMixin(BaseMixin):
    """Mixin for terminals that need to be separately printed"""

    def FROM(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print FROM"""
        return self._token_indent_adjust_case(token)

    def WHERE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WHERE"""
        return self._token_indent_adjust_case(token)

    @staticmethod
    def COMMENT(token: Token) -> Token:  # pylint: disable=invalid-name
        """print COMMENT"""
        if not token.startswith("---") and not token.startswith("/*"):
            content = "-- " + token[2:].strip()
            token = token.update(value=content)
        return token

    def STANDARD_TABLE_NAME(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print STANDARD_TABLE_NAME"""
        return self._token_indent(token)


@v_args(tree=True)
class QueryMixin(BaseMixin):
    """Mixin for query level nodes"""

    def query_file(self, node: CTree) -> str:
        """print query_file"""
        return self._rollup_double_linesep(node)

    def query_expr(self, node: CTree) -> str:
        """rollup items in query_expr"""
        query_parts = self._remove_commas_from_query_expr(node)
        query_parts = self._insert_commas_linesep_to_query_expr(query_parts)
        return linesep.join([str(p) for p in query_parts])

    def _remove_commas_from_query_expr(
        self, node: CTree
    ) -> List[Union[CTree, CToken, str]]:
        """Remove commas from query_expr and indent WITH"""
        query_parts: List[Union[CTree, CToken, str]] = []
        is_first: bool = True
        for child in node.children:
            if str(child) == ",":
                continue
            if is_first:
                query_parts.append(
                    self._apply_indent(str(child), node.data.indent_level)
                )
                is_first = False
            else:
                query_parts.append(child)
        return query_parts

    @staticmethod
    def _insert_commas_linesep_to_query_expr(
        query_parts: List[Union[CTree, CToken, str]]
    ) -> List[Union[CTree, CToken, str]]:
        """Insert commas and linesep after CTEs, linesep after WITH.
        No additional linesep after comments."""
        last_with: int = 0
        for idx, part in enumerate(query_parts):
            clean_part = str(part).strip().lower()
            if not (
                clean_part == "with"
                or isinstance(part, Token)
                or clean_part.startswith("select")
            ):
                query_parts[idx] = str(part) + "," + linesep
                last_with = idx
            if idx == 0 and clean_part == "with":
                query_parts[idx] = str(part) + linesep
        query_parts[last_with] = (
            str(query_parts[last_with]).rstrip("," + linesep) + linesep
        )
        return query_parts

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

    def star_expression(self, node: CTree) -> str:
        """print star_expression"""
        return self._apply_indent(self._rollup(node), node.data.indent_level)

    def except_expression(self, node: CTree) -> str:
        """print except_expression"""
        return " " + self._rollup(node)

    def except_list(self, node: CTree) -> str:
        """print except_list"""
        return self._rollup_comma_inline(node)

    def except_item(self, node: CTree) -> str:
        """print except_item"""
        return self._rollup(node)

    @staticmethod
    def select_list(node: CTree) -> str:
        """rollup items in select_list"""
        counter = 0
        output: List[str] = []
        while counter < len(node.children):
            child = node.children[counter]
            if counter + 1 < len(node.children):
                next_child = node.children[counter + 1]
                if isinstance(next_child, Token) and next_child.type == "COMMENT":
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

    def when_item(self, node: CTree) -> str:
        """print when_item"""
        # turn multi-line expression into single line
        bool_list = str(node.children[1]).split("\n")
        bool_list = [item.lstrip() for item in bool_list]
        item = f'WHEN {" ".join(bool_list)} THEN {node.children[3]}'
        # indent 1 relative to case header and end footer
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
        return f"{node.children[0]}{node.children[1]})"

    @staticmethod
    def FUNCTION_NAME(token: CToken) -> str:  # pylint: disable=invalid-name
        """print FUNCTION_NAME"""
        children = token.value.split(".")
        children[-1] = children[-1].upper()
        for i, child in enumerate(children):
            if child.upper() == "SAFE":
                children[i] = "SAFE"
        return ".".join(children)

    def arg_list(self, node: CTree) -> str:
        """rollup arg_list"""
        return self._rollup_comma_inline(node)

    def arg_item(self, node: CTree) -> str:
        """print arg_item"""
        return self._rollup_space(node).replace(linesep, " ")

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
            output = f"{node.children[0]}{node.children[1]}) {node.children[2]}"
        elif len(node.children) == 2:
            output = f"{node.children[0]}) {node.children[1]}"
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
class ExpressionMixin(BaseMixin):
    """Mixin for expression related nodes"""

    def leading_unary_bool_operation(self, node: CTree) -> str:
        """rollup leading_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operation(self, node: CTree) -> str:
        """print trailing_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operator(self, node: CTree) -> str:
        """print trailing_unary_bool_operator"""
        return self._rollup_space(node)

    @staticmethod
    def binary_bool_operation(node: CTree) -> str:
        """print binary_bool_operation"""
        return f"{node.children[0]}\n{node.children[1]} {node.children[2]}"

    @staticmethod
    def parenthetical_bool_expression(node: CTree) -> str:
        """print parenthetical_bool_expression, removes line separators when
        parenthesized"""
        # TODO: Deal with long lines
        output = str(node.children[1]).replace(linesep, " ")
        return f"({output})"

    def indented_bool_expression(self, node: CTree) -> str:
        """rollup indented_bool_expression"""
        return self._simple_indent(node)


@v_args(tree=True)
class ComparisonMixin(BaseMixin):
    """Mixin for comparison related nodes"""

    def binary_comparison_operation(self, node: CTree) -> str:
        """rollup binary_comparison_operation"""
        return self._rollup_space(node)

    def like_comparison_operation(self, node: CTree) -> str:
        """rollup like_comparison_operation"""
        return self._rollup_space(node)

    def in_comparison_operation(self, node: CTree) -> str:
        """rollup in_comparison_operation"""
        return self._rollup_space(node)

    def in_list(self, node: CTree) -> str:
        """rollup in_list"""
        return f"({self._rollup_comma_inline(node)})"

    def between_comparison_operation(self, node: CTree) -> str:
        """rollup between_comparison_operation"""
        return self._rollup_space(node)


@v_args(tree=True)
class JinjaMixin(BaseMixin):
    """Mixin for Jinja related nodes"""

    def dbt_table_name(self, node: CTree) -> str:
        """print dbt_table_name"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def python_arg_value(self, node: CTree) -> str:
        """print python_arg_value"""
        return self._rollup(node)

    def arg_name(self, node: CTree) -> str:
        """print arg_name"""
        return self._rollup(node)

    def python_arg_item(self, node: CTree) -> str:
        """print python_arg_item"""
        return self._rollup(node)

    def python_arg_list(self, node: CTree) -> str:
        """print python_arg_list"""
        return self._rollup(node)

    def python_dict_item(self, node: CTree) -> str:
        """print python_dict_item"""
        return self._rollup(node)

    def python_dict_list(self, node: CTree) -> str:
        """print python_dict_list"""
        return self._rollup(node)

    def dbt_config(self, node: CTree) -> str:
        """print dbt_config"""
        blacked = self._apply_black(f"config({node.children[3]})")
        return "{{\n" + self._apply_indent(blacked, 1) + "\n}}"

    def __format_macro_expr(self, node: CTree) -> str:
        """form single line macro expressions"""
        joined_children = "".join(str(child) for child in node.children[1:-1])
        blacked = self._apply_black(joined_children)
        # single line print when black returns one line
        if len(blacked.splitlines()) == 1:
            return "{{ " + blacked + " }}"

        # multi line print
        return "{{\n" + self._apply_indent(blacked, 1) + "\n}}"

    def macro(self, node: CTree) -> str:
        """print macro"""
        return self.__format_macro_expr(node)

    def source_name(self, node: CTree) -> str:
        """print source_name"""
        return self._apply_black(str(node.children[0]))

    def table_name(self, node: CTree) -> str:
        """print table_name"""
        return self._apply_black(str(node.children[0]))

    def dbt_reference(self, node: CTree) -> str:
        """print dbt_reference"""
        return self._apply_black(str(node.children[0]))

    def dbt_ref(self, node: CTree) -> str:
        """print dbt_ref"""
        return self.__format_macro_expr(node)

    def dbt_src(self, node: CTree) -> str:
        """print dbt_src"""
        return self.__format_macro_expr(node)


@v_args(tree=True)
class Styler(  # pylint: disable=too-many-ancestors
    ExpressionMixin,
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

    def __default__(self, data: str, children: List[Tree[Token]], meta: str) -> str:
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
            or token.type.endswith("COMMENT")
            or token.type == "SOURCE"
            or token.type == "REF"
        )
