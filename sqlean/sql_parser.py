"""Parse sql strings"""
from typing import Union

from lark.lark import Lark
from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive
from rich import print as rprint
from rich.panel import Panel

from sqlean.custom_classes import CData, CToken, CTree
from sqlean.definitions import IMPORT_PATH
from sqlean.sql_styler import Styler
from sqlean.settings import Settings


class Parser:
    """SQL parser class"""

    def __init__(self, options: Settings = Settings()):
        self.__parser = Lark.open(
            "grammar/sql.lark",
            rel_to=__file__,
            import_paths=[IMPORT_PATH],
            parser="lalr",
            maybe_placeholders=False,
        )
        self.indent = options.indent_size * " "
        self.whisper = options.whisper
        self.max_line_length = options.max_line_length
        self.dialect = options.dialect

    def get_tree(self, raw_query: str) -> Tree[Token]:
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
            rprint(Panel(debug.get_logs(), title=file_path))
        output = Styler(self.indent).transform(tree)
        return str(output)


class TreeGroomer(Visitor_Recursive[Token]):
    """Grooms the trees of ugly branches and leaves, sets indentation,
    determines line spacing for comments."""

    root = "query_file"

    # These nodes will be incremented by the value with respect to the
    # node's parent's indent level. Otherwise, the node's indent level will
    # be the same as its parent's.
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
        "field_list": 1,
        "orderby_modifier": -1,
        "orderby_list": 1,
        "on_clause": -1,
    }

    # These tokens will be incremented by the value with respect to the
    # token's parent's indent level. Otherwise, the token's indent level will
    # not be set.
    token_indent_map = {
        "COMMENT": 0,
        "FROM": 0,
        "STANDARD_TABLE_NAME": 0,
        "WHERE": -1,
        "WITH": 0,
    }

    # If a node has one of these as a parent, it will be indented by one more
    # than its parent.
    parents_to_indent = {
        "sub_query_expr",
        "on_clause",
        "with_clause",
        "having_clause",
    }

    # If a node has one of these as a parent, it's indent will be set to 0
    parents_to_zero = {"in_list"}

    def __default__(self, tree: CTree) -> None:
        """Executed on each node of the tree"""

        if tree.data == TreeGroomer.root:
            tree.data = CData(name=TreeGroomer.root, indent_level=0)

        for idx, child in enumerate(tree.children):
            child = self.__remove_prefix_from_node(child)
            child = self.__set_indent_level(child, tree.data)
            if isinstance(child, Token) and child.type == "COMMENT":
                if idx > 0:
                    child = self.__set_lines_from_previous(
                        child, tree.children[idx - 1]
                    )
                if idx < len(tree.children) - 1:
                    child = self.__set_lines_to_next(child, tree.children[idx + 1])

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
        elif parent_data in self.parents_to_zero:
            increment_level = -parent_data.indent_level
        return parent_data.indent_level + increment_level

    def __set_lines_from_previous(
        self, child: CToken, prev_child: Union[CTree, CToken]
    ) -> CToken:
        name = child.type
        indent_level = child.type.indent_level
        lines_from_previous = child.line - self.__get_tree_end_line(prev_child)
        child.type = CData(
            name=name,
            indent_level=indent_level,
            lines_from_previous=lines_from_previous,
        )
        return child

    def __get_tree_end_line(self, child: Union[CTree, CToken]) -> int:
        end_line: int
        if isinstance(child, Tree):
            end_line = self.__get_tree_end_line(child.children[-1])
        else:
            end_line = child.end_line
        return end_line

    def __set_lines_to_next(
        self, child: CToken, next_child: Union[CTree, CToken]
    ) -> CToken:
        name = child.type
        indent_level = child.type.indent_level
        lines_from_previous = child.type.lines_from_previous
        lines_to_next = self.__get_tree_start_line(next_child) - child.end_line
        child.type = CData(
            name=name,
            indent_level=indent_level,
            lines_from_previous=lines_from_previous,
            lines_to_next=lines_to_next,
        )
        return child

    def __get_tree_start_line(self, child: Union[CTree, CToken]) -> int:
        start_line: int
        if isinstance(child, Tree):
            start_line = self.__get_tree_start_line(child.children[0])
        else:
            start_line = child.line
        return start_line


class Debugger(Visitor_Recursive[Token]):
    """Print out attributes for debugging"""

    def __init__(self) -> None:
        self.log = ""
        super().__init__()

    def __default__(self, tree: CTree) -> None:
        self.log += f"{tree.data.ljust(30)}indent_level: {tree.data.indent_level}\n"

    def get_logs(self) -> str:
        """retrieve the debug logs, ready for printing"""
        return self.log.rstrip()
