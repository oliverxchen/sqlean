"""Class definitions for nodes of queries"""

import abc
from os import linesep as NL
from typing import Sequence

from sqlean.configuration import Config
from sqlean.exceptions import NodeListError


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

    @property
    def class_name(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def print(self, indent_level: int) -> str:
        """Implement this to output the properly indentded string
        representation of the node"""
        raise NotImplementedError


class NodeList(Node):
    """Base class for any list of the same entity within a query"""

    def __init__(self, items: Sequence[Node], line: int, pos: int):
        super().__init__(line, pos)
        self.items = list(items)
        self.type = self._get_list_type()

    def _get_list_type(self):
        class_names_in_list = {i.class_name for i in self.items}
        if len(class_names_in_list) > 1:
            raise NodeListError(
                f"There was more than one type in NodeList: {str(class_names_in_list)}"
            )
        return class_names_in_list.pop()

    def append(self, item: Node):
        if item.class_name != self.type:
            raise NodeListError(
                f"Cannot append item with type {item.class_name} "
                f"to NodeList with type {self.type}"
            )
        self.items.append(item)

    def print(self, indent_level: int) -> str:
        output = [x.print(indent_level) for x in self.items]
        return f",{NL}".join(output) + NL


class SelectItem(Node):
    """Item within a select list"""

    def __init__(self, value: str, alias: str, line: int, pos: int):
        super().__init__(line, pos)
        self.value = value
        self.alias = alias

    def print(self, indent_level: int) -> str:
        if self.value == self.alias:
            return self.add_indent(self.value, indent_level)
        return self.add_indent(f"{self.value} AS {self.alias}", indent_level)


class SelectList(NodeList):
    """List of items that are selected"""

    def __init__(self, select_items: Sequence[SelectItem], line: int, pos: int):
        super().__init__(select_items, line, pos)


class ArgumentItem(Node):
    """Item within an argument list"""

    def __init__(self, value: str, line: int, pos: int):
        super().__init__(line, pos)
        self.value = value

    def print(self, indent_level: int) -> str:
        return self.add_indent(self.value, indent_level)


class ArgumentList(NodeList):
    """List of arguments in a function call"""

    def __init__(self, argument_items: Sequence[ArgumentItem], line: int, pos: int):
        super().__init__(argument_items, line, pos)


#  class FunctionExpression(Node):
#  def __init__(self, function_name: str, argument_list: ArgumentList):
#  pass


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
