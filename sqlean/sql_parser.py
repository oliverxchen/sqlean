"""Parse sql strings"""
from os import linesep
from typing import Union
from lark import Lark, Transformer, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive, v_args

from sqlean.definitions import IMPORT_PATH


class TreeData(str):
    """Data structure for tree"""

    indent_level: int
    is_inline: bool

    def __new__(cls, name: str, indent_level: int, is_inline: bool):
        """Class method to create a new instance of TreeData.
        TreeData inherits from `str` to be a valid object for
        tree.data. Lark transformers will have access to the attributes
        of TreeData that are specified here."""
        obj = str.__new__(cls, name)
        obj.indent_level = indent_level
        obj.is_inline = is_inline
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

    root = "query_expr"
    nodes_to_indent = {"from_clause", "select_list", "where_list"}
    nodes_to_dedent = {"from_modifier"}
    nodes_to_inline = {"arg_item"}

    def __default__(self, tree):
        """Executed on each node of the tree"""

        if tree.data == TreeGroomer.root:
            tree.data = TreeData(name=TreeGroomer.root, indent_level=0, is_inline=True)

        for child in tree.children:
            child = self.__remove_prefix_from_node(child)
            child = self.__set_indent_level(child, tree.data.indent_level)

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
        self, child: Union[Tree, Token], parent_indent_level: int
    ) -> Union[Tree, Token]:
        if isinstance(child, Tree):
            name = child.data
            child.data = TreeData(
                name=name,
                indent_level=self.__get_indent_level(name, parent_indent_level),
                is_inline=self.__get_is_inline(name),
            )
        return child

    def __get_indent_level(self, name: str, parent_indent_level: int) -> int:
        increment_level = 0
        if name in self.nodes_to_indent:
            increment_level = 1
        elif name in self.nodes_to_dedent:
            increment_level = -1
        return parent_indent_level + increment_level

    def __get_is_inline(self, name: str) -> bool:
        if name in self.nodes_to_inline:
            return True
        return False


class Debugger(Visitor_Recursive):
    """Print out attributes for debugging"""

    def __default__(self, tree):
        print(
            f"name: {tree.data}, "
            f"indent_level: {tree.data.indent_level}, "
            f"is_inline: {tree.data.is_inline}"
        )


@v_args(tree=True)
class Printer(Transformer):
    """Pretty printer: formats the lists of atoms and the overall query"""

    nonkeywords = {"FIELD_NAME", "TABLE_NAME"}

    def __init__(self, indent: str):
        super().__init__()
        self.indent = indent

    def __default_token__(self, token):
        if token.type in self.nonkeywords:
            return token
        return token.upper()

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

    def subsequent_where_item(self, node):
        """print subsequent_where_item"""
        return self._simple_indent(node)
