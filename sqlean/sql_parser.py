"""Parse sql strings"""
# pylint: disable=too-many-public-methods
from os import linesep
from typing import Union
from lark import Lark, Transformer, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive, v_args

from sqlean.definitions import IMPORT_PATH


class CustomData(str):
    """Data structure for trees and tokens"""

    indent_level: int

    def __new__(cls, name: str, indent_level: int):
        """Class method to create a new instance of CustomData.
        CustomData inherits from `str` to be a valid object for
        Tree.data and Token.type.

        Lark transformers will have access to the attributes
        of CustomData that are specified here."""
        obj = str.__new__(cls, name)
        obj.indent_level = indent_level
        return obj


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

    def print(self, raw_query: str, is_debug: bool = False) -> str:
        """Pretty print the query"""
        tree = self.get_tree(raw_query)
        if is_debug:
            print("\nIn Tree debugger after grooming")
            Debugger().visit_topdown(tree)
            print("")
        output = Printer(self.indent).transform(tree)
        return output


class TreeGroomer(Visitor_Recursive):
    """Grooms the trees of ugly branches and leaves, sets indentation."""

    root = "query_file"
    nodes_to_indent = {"from_clause", "select_list", "where_list", "groupby_list"}
    parents_to_indent = {"sub_query_expr"}
    nodes_to_dedent = {
        "from_modifier",
        "inner_join",
        "left_join",
        "right_join",
        "full_join",
        "cross_join",
        "groupby_modifier",
    }
    tokens_to_indent = {"FROM"}

    def __default__(self, tree):
        """Executed on each node of the tree"""

        if tree.data == TreeGroomer.root:
            tree.data = CustomData(name=TreeGroomer.root, indent_level=0)

        for child in tree.children:
            child = self.__remove_prefix_from_node(child)
            child = self.__set_indent_level(child, tree.data)

    def __remove_prefix_from_node(self, node: Union[Tree, Token]) -> Union[Tree, Token]:
        if isinstance(node, Token):
            node.type = self.__remove_prefix_from_string(node.type)
        elif isinstance(node, Tree) and not hasattr(node.data, "indent_level"):
            node.data = self.__remove_prefix_from_string(node.data)
        return node

    @staticmethod
    def __remove_prefix_from_string(input_str: str) -> str:
        return input_str.split("__")[-1]

    def __set_indent_level(
        self, child: Union[Tree, Token], parent_data: CustomData
    ) -> Union[Tree, Token]:
        if isinstance(child, Tree):
            name = child.data
            child.data = CustomData(
                name=name,
                indent_level=self.__get_indent_level(name, parent_data),
            )
        elif child.type in self.tokens_to_indent:
            child.type = CustomData(
                name=child.type, indent_level=parent_data.indent_level
            )
        return child

    def __get_indent_level(self, name: str, parent_data: CustomData) -> int:
        increment_level = 0
        if name in self.nodes_to_indent:
            increment_level = 1
        elif parent_data in self.parents_to_indent:
            increment_level = 1
        elif name in self.nodes_to_dedent:
            increment_level = -1
        return parent_data.indent_level + increment_level


class Debugger(Visitor_Recursive):
    """Print out attributes for debugging"""

    def __default__(self, tree):
        print(f"name: {tree.data}, " f"indent_level: {tree.data.indent_level}, ")


@v_args(tree=True)
class Printer(Transformer):
    """Pretty printer: formats the lists of atoms and the overall query"""

    def __init__(self, indent: str):
        super().__init__()
        self.indent = indent

    def __default__(self, *args):
        """default for all Trees without a callback"""
        raise NotImplementedError(f"Unsupported node: {args[0]}")

    def __default_token__(self, token):
        if self._is_non_keyword(token):
            return token
        return token.upper()

    @staticmethod
    def _is_non_keyword(token: Token) -> bool:
        return token.type.endswith("NAME") or token.type.endswith("_ID")

    def _simple_indent(self, node):
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def _apply_indent(self, text: str, indent_level: int) -> str:
        """Apply indentation to text"""
        return f"{self.indent * indent_level}{text}"

    @staticmethod
    def _rollup_linesep(node):
        """Join list with linesep"""
        return linesep.join(node.children)

    @staticmethod
    def _rollup_space(node):
        """Join list with space"""
        return " ".join(node.children)

    @staticmethod
    def _rollup_comma_inline(node):
        """Join list with comma space"""
        return ", ".join(node.children)

    @staticmethod
    def _rollup_comma_newline(node):
        """Join list with comma newline"""
        return f",{linesep}".join(node.children)

    def select_item_unaliased(self, node):
        """print select_item_unaliased"""
        return self._simple_indent(node)

    def select_item_aliased(self, node):
        """print select_item_aliased"""
        output = f"{node.children[0]} AS {node.children[1]}"
        return self._apply_indent(output, node.data.indent_level)

    def select_list(self, node):
        """rollup items in select_list"""
        return self._rollup_comma_newline(node) + ","

    def single_table_name(self, node):
        """print single_table_name"""
        return self._simple_indent(node)

    def from_clause(self, node):
        """rollup items in from_clause"""
        return self._rollup_linesep(node)

    def query_expr(self, node):
        """rollup itms in query_expr"""
        return self._rollup_linesep(node)

    def leading_unary_bool_operation(self, node):
        """rollup leading_unary_bool_operation"""
        return self._rollup_space(node)

    def trailing_unary_bool_operator(self, node):
        """print trailing_unary_bool_operator"""
        return self._rollup_space(node)

    def trailing_unary_bool_operation(self, node):
        """print trailing_unary_bool_operation"""
        return self._rollup_space(node)

    def where_clause(self, node):
        """rollup where_clause"""
        return self._rollup_linesep(node)

    def from_modifier(self, node):
        """rollup from_modifier"""
        return self._rollup_linesep(node)

    def where_list(self, node):
        """rollup where_list"""
        return self._rollup_linesep(node)

    def first_where_item(self, node):
        """print first_where_item"""
        return self._simple_indent(node)

    def after_where_item(self, node):
        """print subsequent_where_item"""
        return self._simple_indent(node)

    def simple_table_name(self, node):
        """print simple_table_name"""
        return self._simple_indent(node)

    def explicit_table_name(self, node):
        """print explicit_table_name"""
        output = f"`{node.children[0]}.{node.children[1]}.{node.children[2]}`"
        return self._apply_indent(output, node.data.indent_level)

    @staticmethod
    def query_file(node):
        """print query_file"""
        return node.children[0]

    def sub_query_expr(self, node):
        """print sub_query_expr"""
        return (
            self._apply_indent("(\n", node.data.indent_level)
            + node.children[0]
            + "\n"
            + self._apply_indent(")", node.data.indent_level)
        )

    def select_statement(self, node):
        """print select_statement"""
        return self._apply_indent(self._rollup_space(node), node.data.indent_level)

    def FROM(self, token):  # pylint: disable=invalid-name
        """print FROM"""
        return self._apply_indent(token.upper(), token.type.indent_level)

    def inner_join(self, node):
        """print inner_join"""
        return self._apply_indent("INNER JOIN", node.data.indent_level)

    def left_join(self, node):
        """print left_join"""
        return self._apply_indent("LEFT OUTER JOIN", node.data.indent_level)

    def right_join(self, node):
        """print right_join"""
        return self._apply_indent("RIGHT OUTER JOIN", node.data.indent_level)

    def full_join(self, node):
        """print full_join"""
        return self._apply_indent("FULL OUTER JOIN", node.data.indent_level)

    def join_operation_with_condition(self, node):
        """rollup join_operation_with_condition"""
        return self._rollup_linesep(node)

    def cross_join(self, node):
        """print cross_join"""
        return self._apply_indent("CROSS JOIN", node.data.indent_level)

    def cross_join_operation(self, node):
        """rollup cross_join_operation"""
        return self._rollup_linesep(node)

    def arg_item(self, node):
        """print arg_item"""
        return self._rollup_space(node)

    def arg_list(self, node):
        """rollup arg_list"""
        return self._rollup_comma_inline(node)

    @staticmethod
    def function_expression(node):
        """print function_expression"""
        return f"{node.children[0]}({node.children[1]})"

    def groupby_item(self, node):
        """print groupby_item"""
        return self._rollup_space(node)

    def groupby_list(self, node):
        """rollup groupby_list"""
        return self._apply_indent(
            self._rollup_comma_inline(node), node.data.indent_level
        )

    def groupby_modifier(self, node):
        """rollup groupby_modifier"""
        output = self._apply_indent("GROUP BY\n", node.data.indent_level)
        return output + node.children[2]
