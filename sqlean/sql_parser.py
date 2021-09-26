"""Parse sql strings"""
# pylint: disable=too-many-public-methods
from os import linesep
from typing import Any, List, Sequence, Union

from lark import Lark, Transformer, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive, v_args
from rich import print as rich_print
from rich.panel import Panel
from rich.traceback import install

from sqlean.definitions import IMPORT_PATH


install()


class CData(str):
    """Custom data structure for trees and tokens"""

    indent_level: int

    def __new__(cls, name: str, indent_level: int = 0) -> "CData":
        """Class method to create a new instance of CData.
        CData inherits from `str` to be a valid object for
        Tree.data and Token.type.

        Lark transformers will have access to the attributes
        of CData that are specified here."""
        obj = str.__new__(cls, name)
        obj.indent_level = indent_level
        return obj


class CToken(Token):
    """Custom structure for tokens"""

    def __init__(self, type_: CData, value: Any) -> None:
        """Initialize the CToken object"""
        super().__init__(type_, value)
        self.type: CData = type_


class CTree(Tree):
    """Custom structure for trees"""

    def __init__(  # pylint: disable=super-init-not-called
        self, data: CData, children: List[Union["CTree", CToken]]
    ) -> None:
        """Initialize the CTree object"""
        self.data: CData = data
        self.children: Sequence[Union["CTree", CToken]] = children  # type: ignore


class Parser:
    """SQL parser class"""

    def __init__(self, num_spaces_per_indent: int = 4):
        self.__parser = Lark.open(
            "grammar/sql.lark", rel_to=__file__, import_paths=[IMPORT_PATH]
        )
        self.indent = num_spaces_per_indent * " "

    def get_tree(self, raw_query: str) -> Tree:
        """Generate a tree for a given query provided as a string"""
        tree = self.__parser.parse(raw_query)
        TreeGroomer().visit_topdown(tree)
        return tree

    def print(self, raw_query: str, is_debug: bool = False, file_path: str = "") -> str:
        """Pretty print the query"""
        tree = self.get_tree(raw_query)
        if is_debug:
            debug = Debugger()
            debug.visit_topdown(tree)
            rich_print(Panel(debug.get_logs(), title=file_path))
        output = Printer(self.indent).transform(tree)
        return str(output)


class TreeGroomer(Visitor_Recursive):
    """Grooms the trees of ugly branches and leaves, sets indentation."""

    root = "query_file"
    node_indent_map = {
        "from_clause": 1,
        "select_list": 1,
        "from_modifier": -1,
        "inner_join": -1,
        "left_join": -1,
        "right_join": -1,
        "full_join": -1,
        "cross_join": -1,
        "using_clause": -1,
        "groupby_modifier": -1,
        "groupby_list": 1,
        "orderby_modifier": -1,
        "orderby_list": 1,
        "on_clause": -1,
    }
    token_indent_map = {"FROM": 0, "WHERE": -1}
    parents_to_indent = {"sub_query_expr", "on_clause"}

    def __default__(self, tree: CTree) -> None:
        """Executed on each node of the tree"""

        if tree.data == TreeGroomer.root:
            tree.data = CData(name=TreeGroomer.root, indent_level=0)

        for child in tree.children:
            child = self.__remove_prefix_from_node(child)
            child = self.__set_indent_level(child, tree.data)

    def __remove_prefix_from_node(
        self, node: Union[CTree, CToken]
    ) -> Union[CTree, CToken]:
        if isinstance(node, Token):
            node.type = CData(self.__remove_prefix_from_string(node.type))
        elif isinstance(node, Tree) and not hasattr(node.data, "indent_level"):
            node.data = CData(self.__remove_prefix_from_string(node.data))
        return node

    @staticmethod
    def __remove_prefix_from_string(input_str: str) -> str:
        return input_str.split("__")[-1]

    def __set_indent_level(
        self, child: Union[CTree, CToken], parent_data: CData
    ) -> Union[CTree, CToken]:
        if isinstance(child, Tree):
            name = child.data
            child.data = CData(
                name=name,
                indent_level=self.__get_indent_level(name, parent_data),
            )
        elif child.type in self.token_indent_map:
            indent_level = parent_data.indent_level + self.token_indent_map[child.type]
            child.type = CData(name=child.type, indent_level=indent_level)
        return child

    def __get_indent_level(self, name: str, parent_data: CData) -> int:
        increment_level = 0
        if name in self.node_indent_map:
            increment_level = self.node_indent_map[name]
        elif parent_data in self.parents_to_indent:
            increment_level = 1
        return parent_data.indent_level + increment_level


class Debugger(Visitor_Recursive):
    """Print out attributes for debugging"""

    def __init__(self) -> None:
        self.log = ""
        super().__init__()

    def __default__(self, tree: CTree) -> None:
        self.log += f"{tree.data.ljust(30)}indent_level: {tree.data.indent_level}\n"

    def get_logs(self) -> str:
        """retrieve the debug logs, ready for printing"""
        return self.log.rstrip()


@v_args(tree=True)
class Printer(Transformer):  # type: ignore
    """Pretty printer: formats the lists of atoms and the overall query"""

    def __init__(self, indent: str):
        super().__init__()
        self.indent = indent

    def __default__(self, data: str, children: List[Tree], meta: str) -> str:
        """default for all Trees without a callback"""
        raise NotImplementedError(f"Unsupported node: {data}")

    def __default_token__(self, token: CToken) -> str:
        if self._is_non_keyword(token):
            return token
        return token.upper()

    @staticmethod
    def _is_non_keyword(token: CToken) -> bool:
        return token.type.endswith("NAME") or token.type.endswith("_ID")

    def _simple_indent(self, node: CTree) -> str:
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def _apply_indent(self, text: str, indent_level: int) -> str:
        """Apply indentation to text"""
        return f"{self.indent * indent_level}{text}"

    def _token_indent(self, token: CToken) -> str:
        return self._apply_indent(token.upper(), token.type.indent_level)

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

    @staticmethod
    def _stringify_children(node: CTree) -> List[str]:
        """Stringify children"""
        return [str(child) for child in node.children]

    def FROM(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print FROM"""
        return self._token_indent(token)

    def WHERE(self, token: CToken) -> str:  # pylint: disable=invalid-name
        """print WHERE"""
        return self._token_indent(token)

    def select_item_unaliased(self, node: CTree) -> str:
        """print select_item_unaliased"""
        return self._simple_indent(node)

    def select_item_aliased(self, node: CTree) -> str:
        """print select_item_aliased"""
        output = f"{node.children[0]} AS {node.children[1]}"
        return self._apply_indent(output, node.data.indent_level)

    def select_list(self, node: CTree) -> str:
        """rollup items in select_list"""
        return self._rollup_comma_newline(node) + ","

    def single_table_name(self, node: CTree) -> str:
        """print single_table_name"""
        return self._simple_indent(node)

    def from_clause(self, node: CTree) -> str:
        """rollup items in from_clause"""
        return self._rollup_linesep(node)

    def query_expr(self, node: CTree) -> str:
        """rollup itms in query_expr"""
        return self._rollup_linesep(node)

    def leading_unary_bool_operation(self, node: CTree) -> str:
        """rollup leading_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operator(self, node: CTree) -> str:
        """print trailing_unary_bool_operator"""
        return self._rollup_space(node)

    def trailing_unary_bool_operation(self, node: CTree) -> str:
        """print trailing_unary_bool_operation"""
        return self._rollup_space(node)

    def where_clause(self, node: CTree) -> str:
        """rollup where_clause"""
        return self._rollup_linesep(node)

    def bool_list(self, node: CTree) -> str:
        """rollup where_list"""
        return self._rollup_linesep(node)

    def first_bool_item(self, node: CTree) -> str:
        """print first_where_item"""
        return self._simple_indent(node)

    def after_bool_item(self, node: CTree) -> str:
        """print subsequent_where_item"""
        return self._simple_indent(node)

    def simple_table_name(self, node: CTree) -> str:
        """print simple_table_name"""
        return self._simple_indent(node)

    def explicit_table_name(self, node: CTree) -> str:
        """print explicit_table_name"""
        output = f"`{node.children[0]}.{node.children[1]}.{node.children[2]}`"
        return self._apply_indent(output, node.data.indent_level)

    @staticmethod
    def query_file(node: CTree) -> str:
        """print query_file"""
        return str(node.children[0])

    def sub_query_expr(self, node: CTree) -> str:
        """print sub_query_expr"""
        return (
            self._apply_indent("(\n", node.data.indent_level)
            + str(node.children[0])
            + "\n"
            + self._apply_indent(")", node.data.indent_level)
        )

    def select_statement(self, node: CTree) -> str:
        """print select_statement"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

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

    def join_operation_with_condition(self, node: CTree) -> str:
        """rollup join_operation_with_condition"""
        return self._rollup_linesep(node)

    def cross_join(self, node: CTree) -> str:
        """print cross_join"""
        return self._apply_indent("CROSS JOIN", node.data.indent_level)

    def cross_join_operation(self, node: CTree) -> str:
        """rollup cross_join_operation"""
        return self._rollup_linesep(node)

    def arg_item(self, node: CTree) -> str:
        """print arg_item"""
        return self._rollup_space(node)

    def arg_list(self, node: CTree) -> str:
        """rollup arg_list"""
        return self._rollup_comma_inline(node)

    @staticmethod
    def function_expression(node: CTree) -> str:
        """print function_expression"""
        return f"{node.children[0]}({node.children[1]})"

    def groupby_item(self, node: CTree) -> str:
        """print groupby_item"""
        return self._rollup_space(node)

    def groupby_list(self, node: CTree) -> str:
        """rollup groupby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def groupby_modifier(self, node: CTree) -> str:
        """rollup groupby_modifier"""
        output = self._apply_indent("GROUP BY\n", node.data.indent_level)
        return output + str(node.children[2])

    def orderby_item(self, node: CTree) -> str:
        """print orderby_item"""
        return self._rollup_space(node)

    def orderby_list(self, node: CTree) -> str:
        """rollup orderby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def orderby_modifier(self, node: CTree) -> str:
        """rollup orderby_modifier"""
        output = self._apply_indent("ORDER BY\n", node.data.indent_level)
        return output + str(node.children[2])

    def limit_clause(self, node: CTree) -> str:
        """rollup limit_clause"""
        return self._simple_indent(node)

    def using_list(self, node: CTree) -> str:
        """rollup using_list"""
        return self._rollup_comma_inline(node)

    def using_clause(self, node: CTree) -> str:
        """rollup using_clause"""
        return self._apply_indent(f"USING ({node.children[2]})", node.data.indent_level)

    def binary_comparison_operation(self, node: CTree) -> str:
        """rollup binary_comparison_operation"""
        return self._rollup_space(node)

    def on_clause(self, node: CTree) -> str:
        """rollup on_clause"""
        output = self._apply_indent("ON\n", node.data.indent_level)
        return output + str(node.children[1])
