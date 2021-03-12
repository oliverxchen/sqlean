"""Class definitions for nodes of queries"""

import abc
from typing import List


class Node:
    """Base class for any entity within a query"""

    def __init__(self, line: int, pos: int, indent_size: int = 4):
        self.line = line
        self.pos = pos
        self.indent = indent_size * " "

    def add_indent(self, input_lines: str, indent_level: int):
        """Indent all lines by `indent_level` * `indent_size`"""
        output_lines = [
            f"{indent_level * self.indent}{x}" for x in input_lines.split("\n")
        ]
        return "\n".join(output_lines)

    @abc.abstractmethod
    def print(self, indent_level: int) -> str:
        """Implement this to output the properly indentded string
        representation of the node"""


#  class FunctionExpression(Node):
#  def __init__(
#  self, function_name: str, argument_list: List[Union[FunctionExpression, str]]
#  ):  # frowny face -> define an ArgumentItem abstract base class that
# $                     FunctionExpression derives from
#  pass


class SelectItem(Node):
    """Item within a select list"""

    def __init__(self, value: str, alias: str, line: int, pos: int):
        super().__init__(line, pos)
        self.value = value
        self.alias = alias

    # Note: don't use alias if value = alias
    def print(self, indent_level: int) -> str:
        if self.value == self.alias:
            return self.add_indent(f"{self.value}", indent_level)
        return self.add_indent(f"{self.value} AS {self.alias}", indent_level)


class SelectList(Node):
    """List of items that are selected"""

    def __init__(self, select_items: List[SelectItem], line: int, pos: int):
        super().__init__(line, pos)
        self.select_items = select_items

    def print(self, indent_level: int) -> str:
        select_items_output = [x.print(indent_level) for x in self.select_items]
        return ",\n".join(select_items_output) + "\n"

    def append(self, select_item: SelectItem):
        """add select item to a select list"""
        self.select_items += [select_item]


class Query(Node):
    """Overal query"""

    def __init__(self, select_list: SelectList, line: int, pos: int):
        super().__init__(line, pos)
        self.select_list = select_list

    def print(self, indent_level: int = 0) -> str:
        return (
            self.add_indent("SELECT", indent_level)
            + "\n"
            + self.select_list.print(indent_level + 1)
            + self.add_indent("FROM", indent_level)
            + "\n"
        )
