"""Parse sql strings"""
from os import linesep
import os.path as path
from typing import Union
from lark import Lark, Transformer, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive


IMPORT_PATH = path.join(path.dirname(__file__), "grammar")


class Parser:
    """SQL parser class"""

    def __init__(self):
        self.__parser = Lark.open(
            "grammar/sql.lark", rel_to=__file__, import_paths=[IMPORT_PATH]
        )

    def get_tree(self, raw_query: str) -> Tree:
        """Generate a tree for a given query provided as a string"""
        tree = self.__parser.parse(raw_query)
        TreeGroomer().visit(tree)
        return tree

    def print(self, raw_query: str):
        """Pretty print the query"""
        tree = self.get_tree(raw_query)
        AtomicFormatter().visit_topdown(tree)
        return Printer().transform(tree)


class TreeGroomer(Visitor_Recursive):
    """Clean and add necessary attributes to trees"""

    def __default__(self, tree):
        """Executed on each node of the tree"""
        tree = self.__remove_prefix_from_node(tree)
        tree.has_parent = False
        for child in tree.children:
            child = self.__update_has_parent(child)
            child = self.__remove_prefix_from_node(child)

    @staticmethod
    def __update_has_parent(child: Union[Tree, Token]) -> Union[Tree, Token]:
        if isinstance(child, Tree):
            child.has_parent = True  # type: ignore
        return child

    def __remove_prefix_from_node(
        self, child: Union[Tree, Token]
    ) -> Union[Tree, Token]:
        if isinstance(child, Token):
            child.type = self.__remove_prefix_from_string(child.type)
        elif isinstance(child, Tree):
            child.data = self.__remove_prefix_from_string(child.data)
        return child

    @staticmethod
    def __remove_prefix_from_string(input_str: str) -> str:
        return input_str.split("__")[-1]


class AtomicFormatter(Visitor_Recursive):
    """Format the atoms (eg select_item, table_name, etc) by adding indentation
    and appropriate capitalisation"""

    indent_type = 4 * " "
    groups = {"select_list", "from_clause"}
    indent_exemptions = {"table_name"}

    def __default__(self, tree):
        """Executed on each node of the tree"""
        if not tree.has_parent:
            tree.num_indent = 0
        for child in tree.children:
            if isinstance(child, Tree):
                child.num_indent = tree.num_indent + self._incremental_indent(
                    tree.data, child.data
                )

    def select_item(self, tree):
        """format select_item"""
        new_value = f"{tree.num_indent * self.indent_type}{tree.children[0].value}"
        tree.children[0] = tree.children[0].update(value=new_value)

    def table_name(self, tree):
        """format table_name"""
        new_value = f"{tree.num_indent * self.indent_type}{tree.children[0].value}"
        tree.children[0] = tree.children[0].update(value=new_value)

    def _incremental_indent(self, tree_data, child_data):
        if (tree_data in self.groups) or (child_data in self.indent_exemptions):
            return 0
        return 1


# class Debugger(Visitor_Recursive):
#     """Print out attribues for debugging"""

#     def __default__(self, tree):
#         print(f"tree.data: {tree.data}")
#         if hasattr(tree, "has_parent"):
#             print(f"tree.has_parent: {tree.has_parent}")
#         print(f"tree.num_indent: {tree.indent}\n")


class Printer(Transformer):
    """Pretty printer: formats the lists of atoms and the overall query"""

    # def __default__(self, *args):
    #     """Executed on each node of the tree.
    #     * tree.data is in zeroth element
    #     * tree.children is in first element
    #     * tree.meta is in second element"""
    #     output = list()
    #     print("\n")
    #     print(args)
    #     for child in args[1]:
    #         print(child)
    #         if not isinstance(child, Tree):
    #             if isinstance(child, Token):
    #                 output.append(child.value)
    #             else:
    #                 output.append(child)
    #     return linesep.join(output)

    @staticmethod
    def select_list(children):
        """print select_list"""
        output = list()
        print(children)
        for child in children:
            output.append(child.children[0])
        output_string = f",{linesep}".join(output)
        return output_string

    @staticmethod
    def from_clause(children):
        """print from_clause"""
        return children[0].children[0].children[0].value

    @staticmethod
    def query_expr(children):
        """print query_expr"""
        output = list()
        for child in children:
            if hasattr(child, "type"):
                output.append(child.type)
            elif isinstance(child, str):
                output.append(child)
        return linesep.join(output)
