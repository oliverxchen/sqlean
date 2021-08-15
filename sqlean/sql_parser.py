"""Parse sql strings"""
from os import linesep
from typing import Union
from lark import Lark, Transformer, Token
from lark.tree import Tree
from lark.visitors import Visitor_Recursive

from sqlean.definitions import IMPORT_PATH


class TreeData(str):
    """Data structure for tree"""

    indent_level: int

    def __new__(cls, value: str, indent_level: int):
        """Class method to create a new instance of TreeData"""
        obj = str.__new__(cls, value)
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

    def print(self, raw_query: str):
        """Pretty print the query"""
        tree = self.get_tree(raw_query)
        output = Printer(self.indent).transform(tree)
        print(output)
        return output


class TreeGroomer(Visitor_Recursive):
    """Grooms the trees of ugly branches and leaves, sets indentation."""

    root = "query_expr"
    groups = {"select_list", "from_clause"}
    indent_exemptions = {"table_name"}

    def __default__(self, tree):
        """Executed on each node of the tree"""

        if tree.data == TreeGroomer.root:
            tree.data = TreeData(TreeGroomer.root, 0)
        else:
            tree = self.__remove_prefix_from_node(tree)

        for child in tree.children:
            child = self.__remove_prefix_from_node(child)
            child = self.__set_indent_level(child, tree.data)

    def __remove_prefix_from_node(self, node: Union[Tree, Token]) -> Union[Tree, Token]:
        if isinstance(node, Token):
            node.type = self.__remove_prefix_from_string(node.type)
        elif isinstance(node, Tree):
            cleaned_data = self.__remove_prefix_from_string(node.data)
            if hasattr(node.data, "indent_level"):
                node.data = TreeData(
                    cleaned_data, node.data.indent_level  # type: ignore
                )
            else:
                node.data = cleaned_data
        return node

    @staticmethod
    def __remove_prefix_from_string(input_str: str) -> str:
        return input_str.split("__")[-1]

    def __set_indent_level(self, child, tree_data):
        if isinstance(child, Tree):
            child_data = child.data
            child.data = TreeData(
                child_data,
                self.__calculate_indent_level(tree_data, child_data),
            )
        return child

    def __calculate_indent_level(self, tree_data, child_data):
        incremental_level = 1
        if (tree_data in self.groups) or (child_data in self.indent_exemptions):
            incremental_level = 0
        return tree_data.indent_level + incremental_level


# class Debugger(Visitor_Recursive):
#     """Print out attribues for debugging"""
#
#     def __default__(self, tree):
#         print(f"tree.data: {tree.data}, {tree.data.indent_level}")


class Printer(Transformer):
    """Pretty printer: formats the lists of atoms and the overall query"""

    def __init__(self, indent: str):
        super().__init__()
        self.indent = indent

    def __default__(self, *args):
        """Executed on each node of the tree.
        * tree.data is in zeroth element
        * tree.children is in first element
        * tree.meta is in second element"""
        print("\nIN __default__")
        print(args[1])
        return Tree(args[0], args[1], args[2])

    # @staticmethod
    def select_list(self, children):
        """print select_list"""
        print("in select_list")
        print(children)
        output = list()
        for child in children:
            output.append(
                self.__apply_indent(child.children[0], child.data.indent_level)
            )
        output_string = f",{linesep}".join(output)
        return output_string

    def from_clause(self, children):
        """print from_clause"""
        return self.__apply_indent(
            children[0].children[0].value,
            children[0].data.indent_level,
        )

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

    def __apply_indent(self, text: str, indent_level: int) -> str:
        """Apply indentation to the text"""
        return f"{self.indent * indent_level}{text}"
