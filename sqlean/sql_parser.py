"""Parse sql strings"""
import os.path as path
from lark import Lark
from lark.tree import Tree
from lark.visitors import Visitor_Recursive


IMPORT_PATH = path.join(path.dirname(__file__), "grammar")


class Parser:
    """SQL parser class"""

    def __init__(self):
        self.__parser = Lark.open(
            "grammar/sql.lark", rel_to=__file__, import_paths=[IMPORT_PATH]
        )

    def get_tree(self, raw_query: str):
        """Generate a tree for a given query provided as a string"""
        tree = self.__parser.parse(raw_query)
        RemoveModulePrefix().visit(tree)
        return tree


class RemoveModulePrefix(Visitor_Recursive):
    """Remove the module prefix on .data and .type fields in sub-modules"""

    def __default__(self, tree):
        """Executed on each node of the tree"""
        tree.data = self.__remove_prefix(tree.data)
        for child in tree.children:
            if isinstance(child, Tree):
                continue
            child.type = self.__remove_prefix(child.type)

    @staticmethod
    def __remove_prefix(input_string):
        return input_string.split("__")[-1]
