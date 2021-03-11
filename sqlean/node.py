import abc
from typing import List, Union

# TODO: abstractify
class Node(abc.ABC):
    indent = 4 * " "

    def __init__(self, line: int, pos: int):
        self.line = line
        self.pos = pos

    @staticmethod
    def add_indent(input_lines: str, indent_level: int):
        output_lines = [
            f"{indent_level * Node.indent}{x}" for x in input_lines.split("\n")
        ]
        return "\n".join(output_lines)

    @abc.abstractmethod
    def print(self, indent_level: int = 0):
        pass


#  class FunctionExpression(Node):
    #  def __init__(
        #  self, function_name: str, argument_list: List[Union[FunctionExpression, str]]
    #  ):  # frowny face -> define an ArgumentItem abstract base class that FunctionExpression derives from
        #  pass


class SelectItem(Node):
    def __init__(self, value: str, alias: str, line: int, pos: int):
        super().__init__(line, pos)
        self.value = value
        self.alias = alias

    # TODO: don't use alias if value = alias
    def print(self, indent_level: int):
        if self.value == self.alias:
            return self.add_indent(f"{self.value}", indent_level)
        else:
            return self.add_indent(f"{self.value} AS {self.alias}", indent_level)


class SelectList(Node):
    def __init__(self, select_items: List[SelectItem], line: int, pos: int):
        super().__init__(line, pos)
        self.select_items = select_items

    def print(self, indent_level: int):
        select_items_output = [x.print(indent_level) for x in self.select_items]
        return ",\n".join(select_items_output) + "\n"

    def append(self, select_item: SelectItem):
        self.select_items += [select_item]


class Query(Node):
    def __init__(self, select_list: SelectList, line: int, pos: int):
        super().__init__(line, pos)
        self.select_list = select_list

    def print(self, indent_level: int = 0):
        return (
            self.add_indent("SELECT", indent_level)
            + "\n"
            + self.select_list.print(indent_level + 1)
            + self.add_indent("FROM", indent_level)
            + "\n"
        )
