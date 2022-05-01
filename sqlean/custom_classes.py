"""Parse sql strings"""
from typing import List, Sequence, Union

from lark.lexer import Token
from lark.tree import Tree


class CData(str):
    """Custom data structure for trees and tokens"""

    indent_level: int
    lines_from_previous: int
    lines_to_next: int

    def __new__(
        cls,
        name: str,
        indent_level: int = 0,
        lines_from_previous: int = 0,
        lines_to_next: int = 0,
    ) -> "CData":
        """Class method to create a new instance of CData.
        CData inherits from `str` to be a valid object for
        Tree.data and Token.type.

        Lark transformers will have access to the attributes
        of CData that are specified here."""
        obj = str.__new__(cls, name)
        obj.indent_level = indent_level
        obj.lines_from_previous = lines_from_previous
        obj.lines_to_next = lines_to_next
        return obj


class CToken(Token):
    """Custom structure for tokens"""

    def __init__(  # pylint: disable=super-init-not-called
        self, type_: CData, value: str
    ) -> None:
        """Initialize the CToken object"""
        self.type: CData = type_
        self.value = value


class CTree(Tree[Token]):
    """Custom structure for trees"""

    def __init__(  # pylint: disable=super-init-not-called
        self, data: CData, children: List[Union["CTree", CToken]]
    ) -> None:
        """Initialize the CTree object"""
        self.data: CData = data
        self.children: Sequence[Union["CTree", CToken]] = children  # type: ignore
        self._meta = None
