"""Styling of SQL queries"""

from os import linesep
from typing import List, Optional, Set, Union

import black
from lark.tree import Tree
from lark.lexer import Token
from lark.visitors import v_args, Transformer

from sqlean.custom_classes import CData, CToken, CTree


class CommentedListClass:  # pylint: disable=too-many-instance-attributes
    """Generic object to hold a list of children that may contain comments, to style
    them properly"""

    def __init__(  # pylint: disable=too-many-arguments, dangerous-default-value
        self,
        children: List[Union[CToken, CTree]] = [],
        separator: str = ",",
        line_separator: str = linesep,
        has_ending_separator: bool = True,
        item_types: Set[str] = set(),
        indent: str = "  ",
    ) -> None:
        self.children = children
        self.separator = separator
        self.line_separator = line_separator
        self.has_ending_separator = has_ending_separator
        self.item_types = item_types
        self.num_children = len(children)
        self.last_item_idx = self.__get_last_item_idx()
        self.output: List[str] = []
        self.indent = indent

    def __get_last_item_idx(self) -> int:
        counter = len(self.children) - 1
        while counter >= 0:
            child = self.children[counter]
            if self._is_item(child):
                return counter
            counter -= 1
        return -1

    @staticmethod
    def _lines_from_previous(
        child: Union[CToken, CTree], prev_child: Union[CToken, CTree]
    ) -> Optional[int]:
        """Returns None if both child and prev_child are not comments.
        If one or both of them are, returns the number of lines between them.
        """
        if isinstance(child, Token) and child.type == "COMMENT":
            return child.type.lines_from_previous
        if isinstance(prev_child, Token) and prev_child.type == "COMMENT":
            return prev_child.type.lines_to_next
        return None

    def _is_item(self, child: Union[CToken, CTree]) -> bool:
        is_item = False
        if isinstance(child, Tree) and str(child.data) in self.item_types:
            is_item = True
        elif isinstance(child, Token) and str(child.type) in self.item_types:
            is_item = True
        return is_item

    def rollup_list(self) -> str:
        """Rolls up the list of children (which may have comments) into a string"""
        self._fill_output()
        return "".join(self.output)

    def _fill_output(self) -> None:
        self.output.append(self._indent_if_comment(self.children[0]))
        for idx in range(1, self.num_children):
            self._append_child_by_idx(idx)
        self.output[-1] += self._get_separator_by_idx(self.num_children - 1, True)

    def _append_child_by_idx(self, idx: int) -> None:
        child = self.children[idx]
        prev_child = self.children[idx - 1]  # the 0th child was added separately
        lines_from_neighbor = self._lines_from_previous(child, prev_child)
        if lines_from_neighbor is not None:
            self._append_comment(child, lines_from_neighbor, idx)
        else:
            self.output[-1] += self._get_separator_by_idx(idx - 1, False)
            self.output.append(str(child))

    def _append_comment(
        self, child: Union[CToken, CTree], lines_between: int, idx: int
    ) -> None:
        this_separator = self._get_separator_by_idx(idx - 1, is_inline=True)
        self.output[-1] += this_separator
        if lines_between == 0:
            self.output.append(lines_between * linesep + "  " + str(child))
        else:
            self.output.append(lines_between * linesep + self._indent_if_comment(child))

    def _indent_if_comment(self, child: Union[CToken, CTree]) -> str:
        if isinstance(child, Token) and child.type == "COMMENT":
            lines = [
                f"{self.indent * child.type.indent_level}{line}"
                for line in child.split(linesep)
            ]
            return linesep.join(lines)
        return str(child)

    def _get_separator_by_idx(self, idx: int, is_inline: bool) -> str:
        """This assumes that the child at idx has already been added to the output
        at the last index"""
        child = self.children[idx]
        if self._is_item(child):
            if idx < self.last_item_idx:
                this_separator = self.separator
            else:
                if self.has_ending_separator:
                    this_separator = self.separator
                else:
                    this_separator = ""
        elif idx < self.num_children:
            this_separator = ""
        if is_inline:
            return this_separator
        return this_separator + self.line_separator


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

    def _rollup_list(  # pylint: disable=too-many-arguments
        self,
        children: List[Union[CToken, CTree]],
        separator: str,
        line_separator: str,
        has_ending_separator: bool,
        item_types: Set[str],
    ) -> str:
        list_ = CommentedListClass(
            children=children,
            separator=separator,
            line_separator=line_separator,
            has_ending_separator=has_ending_separator,
            item_types=item_types,
            indent=self.indent,
        )
        return list_.rollup_list()


@v_args(tree=True)
class TerminalMixin(BaseMixin):
    """Mixin for terminals that need to be separately printed"""

    def FROM(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print FROM"""
        return self._token_indent_adjust_case(token)

    def WHERE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WHERE"""
        return self._token_indent_adjust_case(token)

    def WITH(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WITH"""
        return self._token_indent_adjust_case(token)

    def COMMENT(self, token: Token) -> Token:  # pylint: disable=invalid-name
        """print COMMENT"""
        if token.startswith("/*"):
            token = token.update(value=self._format_block_comment(str(token)))
        elif not token.startswith("---"):
            content = "-- " + token[2:].strip()
            token = token.update(value=content)
        return token

    @staticmethod
    def _format_block_comment(block_comment: str) -> str:
        lines = [line.lstrip() for line in block_comment.split(linesep)]
        output: List[str] = []
        for line in lines:
            if line.startswith("/*"):
                output.append(f"/* {line[2:].lstrip()}")
            elif line.startswith("*/"):
                output.append(line)
            else:
                output.append(f"   {line}")
        return linesep.join(output)

    def STANDARD_TABLE_NAME(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print STANDARD_TABLE_NAME"""
        return self._token_indent(token)

    @staticmethod
    def rstring(node: CTree) -> str:
        """print rstring. Not technically a terminal as defined in the grammar,
        but close enough."""
        return f"r{node.children[0]}"

    def SINGLE_QUOTED_STRING(  # pylint: disable=invalid-name
        self, token: CToken
    ) -> str:
        """print SINGLE_QUOTED_STRING"""
        return self._apply_black(str(token))

    def DOUBLE_QUOTED_STRING(  # pylint: disable=invalid-name
        self, token: CToken
    ) -> str:
        """print SINGLE_QUOTED_STRING"""
        return self._apply_black(str(token))


@v_args(tree=True)
class QueryMixin(BaseMixin):
    """Mixin for query level nodes"""

    def query_file(self, node: CTree) -> str:
        """print query_file"""
        output = self._rollup_list(
            children=list(node.children),
            separator="",
            line_separator=2 * linesep,
            has_ending_separator=True,
            item_types={"dbt_config"},
        )

        # remove double linesep between set statements
        return output.replace("%}\n\n{%", "%}\n{%")

    def query_expr(self, node: CTree) -> str:
        """rollup items in query_expr"""
        return self._rollup_list(
            children=self._treat_commas_in_query_expr(node),
            separator="",
            line_separator=2 * linesep,
            has_ending_separator=False,
            item_types=set(),
        )

    @staticmethod
    def _treat_commas_in_query_expr(node: CTree) -> List[Union[CTree, CToken]]:
        """treat commas in query_expr"""
        children = list(node.children)
        counter = len(children) - 1
        while counter >= 0:
            if children[counter] == ",":
                counter += -1
                # when we find a comma, go back and append the comma to the
                # most recent with_clause
                while counter >= 0:
                    child = children[counter]
                    if isinstance(child, CToken) and child.type == "with_clause":
                        children[counter] = CToken(
                            type_=CData("with_clause"),
                            value=child.value + ",",
                        )
                        break
                    counter += -1
            counter += -1
        # remove the commas from the list
        return [child for child in children if child != ","]

    def sub_query_expr(self, node: CTree) -> CToken:
        """Returns sub_query_expr as a CToken for identification by parent"""
        output = (
            self._apply_indent(str(node.children[0]), node.data.indent_level)
            + linesep
            + str(node.children[1])
            + linesep
            + self._apply_indent(str(node.children[2]), node.data.indent_level)
        )
        return CToken(
            type_=CData("sub_query_expr"),
            value=output,
        )

    def with_clause(self, node: CTree) -> CToken:
        """Returns a token of type `with_clause` for identification by the parent"""
        if len(node.children) == 1:
            return CToken(type_=CData("with_clause"), value=self._simple_indent(node))

        value = (
            self._apply_indent(f"{node.children[0]} AS (", node.data.indent_level)
            + linesep
            + str(node.children[3])
            + linesep
            + self._apply_indent(str(node.children[4]), node.data.indent_level)
        )
        return CToken(
            type_=CData("with_clause"),
            value=value,
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

    def select_list(self, node: CTree) -> str:
        """rollup items in select_list"""
        return self._rollup_list(
            children=list(node.children),
            separator=",",
            line_separator=linesep,
            has_ending_separator=True,
            item_types={"select_item"},
        )

    def select_item_unaliased(self, node: CTree) -> CToken:
        """Returns a token of type select_item
        for identification by the parent"""
        return CToken(type_=CData("select_item"), value=self._simple_indent(node))

    def select_item_aliased(self, node: CTree) -> CToken:
        """Returns a token of type select_item
        for identification by the parent"""
        output = f"{node.children[0]} AS {node.children[1]}"
        return CToken(
            type_=CData("select_item"),
            value=self._apply_indent(output, node.data.indent_level),
        )

    @staticmethod
    def struct_item_unaliased(node: CTree) -> str:
        """prints struct_item_unaliased"""
        return str(node.children[0])

    @staticmethod
    def struct_item_aliased(node: CTree) -> str:
        """prints struct_item_aliased"""
        return f"{node.children[0]} AS {node.children[1]}"

    def struct_list(self, node: CTree) -> str:
        """prints struct_list"""
        return self._rollup_comma_inline(node)

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
class SetMixin(BaseMixin):
    """Mixin for set related nodes"""

    def set_operator(self, node: CTree) -> str:
        """rollup items in set_operator"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def set_operation(self, node: CTree) -> str:
        """rollup items in set_operation"""
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

    def from_item(self, node: CTree) -> str:
        """print from_item"""
        return self._rollup_list(
            children=list(node.children),
            separator="",
            line_separator=linesep,
            has_ending_separator=False,
            item_types=set(),
        )

    def table_name(self, node: CTree) -> str:
        """print table_name"""
        return self._apply_indent(
            self._rollup(node), indent_level=node.data.indent_level
        )


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

    def standard_function_expression(self, node: CTree) -> str:
        """print standard_function_expression"""
        return self._rollup(node)

    @staticmethod
    def FUNCTION_NAME(token: CToken) -> str:  # pylint: disable=invalid-name
        """print FUNCTION_NAME"""
        # Ensure that the function name is capitalized (and project.datasets are not)
        children = token.value.split(".")
        children[-1] = children[-1].upper()
        for i, child in enumerate(children):
            if child.upper() == "SAFE":
                children[i] = "SAFE"
        output = ".".join(children)
        # Ensure that there is no space between the function name and
        # the opening parenthesis
        return output[:-1].rstrip() + "("

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

    def frame_between(self, node: CTree) -> str:
        """print frame_between"""
        return self._rollup_space(node)

    def frame_start(self, node: CTree) -> str:
        """print frame_start"""
        return self._rollup_space(node)

    def frame_end(self, node: CTree) -> str:
        """print frame_end"""
        return self._rollup_space(node)

    def window_frame_clause(self, node: CTree) -> str:
        """print window_frame_clause"""
        return self._rollup_space(node)

    def struct_expression(self, node: CTree) -> str:
        """print struct_expression"""
        return self._rollup(node)


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
        list_ = CommentedListClass(
            children=list(node.children),
            separator="",
            line_separator=linesep,
            has_ending_separator=False,
            indent="",
        )
        output = list_.rollup_list()
        return output.replace("AND" + linesep, "AND ").replace("OR" + linesep, "OR ")

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

    def array_subscript_specifier(self, node: CTree) -> str:
        """rollup array_subscript_specifier"""
        return self._rollup(node)

    def base_expression(self, node: CTree) -> str:
        """rollup base_expression"""
        return self._rollup(node)

    def negated_expression(self, node: CTree) -> str:
        """print negated_expression"""
        return self._rollup(node)

    def arithmetic_expression(self, node: CTree) -> str:
        """print arithmetic_expression"""
        return self._rollup_space(node)

    def parenthetic_expression(self, node: CTree) -> str:
        """print parenthetic_expression"""
        return self._rollup(node)


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
        if (
            isinstance(node.children[0], CToken)
            and node.children[0].type == "sub_query_expr"
        ):
            return str(node.children[0])

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
        return self.__format_macro_expr(node).replace("CONFIG", "config")

    def __format_macro_expr(self, node: CTree) -> str:
        """format macro expression as single or multi line using black"""
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

    def source_id(self, node: CTree) -> str:
        """print source_id"""
        return self._apply_black(str(node.children[0]))

    def table_id(self, node: CTree) -> str:
        """print table_id"""
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

    def jinja_set_block(self, node: CTree) -> str:
        """print jinja_set_block"""
        joined_children = "".join(str(child) for child in node.children[1:-1])
        blacked = self._apply_black(joined_children)
        # single line print when black returns one line
        if len(blacked.splitlines()) == 1:
            output = "{% " + blacked + " %}"
        else:
            # multi line print
            output = "{%\n" + self._apply_indent(blacked, 1) + "\n%}"
        return output.replace("SET", "set ")

    def jinja_variable(self, node: CTree) -> str:
        """print jinja_variable"""
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
    SetMixin,
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
