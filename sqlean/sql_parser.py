"""Parse sql strings"""
from typing import Union

from lark import Lark, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive
from rich import print as rich_print
from rich.panel import Panel
from rich.traceback import install

from sqlean.custom_classes import CData, CToken, CTree
from sqlean.definitions import IMPORT_PATH
from sqlean.sql_styler import Styler


install()


class Parser:
    """SQL parser class"""

    def __init__(self, num_spaces_per_indent: int = 4):
        self.__parser = Lark.open(
            "grammar/sql.lark",
            rel_to=__file__,
            import_paths=[IMPORT_PATH],
            parser="lalr",
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
        output = Styler(self.indent).transform(tree)
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
