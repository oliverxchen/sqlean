"""Class definitions for nodes of queries"""

import abc
from os import linesep as NL
from typing import List

from sqlean.configuration import Config


INDENT = Config.get_instance().indent


class Node(abc.ABC):
    """Base class for any entity within a query"""

    def __init__(self, line: int, pos: int):
        self.line = line
        self.pos = pos

    @staticmethod
    def add_indent(input_lines: str, indent_level: int):
        """Indent all lines by `indent_level` * `indent_size`"""
        output_lines = [f"{indent_level * INDENT}{x}" for x in input_lines.split(NL)]
        return NL.join(output_lines)

    @abc.abstractmethod
    def print(self, indent_level: int) -> str:
        """Implement this to output the properly indentded string
        representation of the node"""
        raise NotImplementedError


class NodeList(abc.ABC):
    """Base class for any list of the same entity within a query"""

    def __init__(self, items: List[Node]):
        self.items = items

    def append(self, item: Node):
        self.items.append(item)


#  class ArgumentItem(Node):
#  """Item within a arugment list"""

#  def __init__(self, value: str, line: int, pos: int):
#  super().__init__(line, pos)
#  self.value = value

#  def print(self, indent_level: int) -> str:
#  return self.add_indent(f"{self.value}", indent_level)


#  class ArgumentList(Node):
#  """List of arguments in a function call"""

#  def __init__(self, argument_items: List[ArgumentItem], line: int, pos: int):
#  super().__init__(line, pos)
#  self.argument_items = argument_items

#  def print(self, indent_level: int) -> str:
#  argument_items_output = [x.print(indent_level) for x in self.argument_items]
#  return ",\n".join(argument_items_output) + "\n"

#  def append(self, select_item: ArgumentItem):
#  """add select item to a select list"""
#  self.select_items += [select_item]


#  class FunctionExpression(Node):
#  def __init__(self, function_name: str, argument_list: ArgumentList):
#  pass


class SelectItem(Node):
    """Item within a select list"""

    def __init__(self, value: str, alias: str, line: int, pos: int):
        super().__init__(line, pos)
        self.value = value
        self.alias = alias

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
        return f",{NL}".join(select_items_output) + NL

    def append(self, select_item: SelectItem):
        """add select item to a select list"""
        self.select_items += [select_item]


class Query(Node):
    """Representation of an sql query"""

    def __init__(self, select_list: SelectList, line: int, pos: int):
        super().__init__(line, pos)
        self.select_list = select_list

    def print(self, indent_level: int = 0) -> str:
        return (
            self.add_indent("SELECT", indent_level)
            + NL
            + self.select_list.print(indent_level + 1)
            + self.add_indent("FROM", indent_level)
            + NL
        )
