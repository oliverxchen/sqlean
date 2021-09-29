"""Parse sql strings"""
from typing import Any, List, Sequence, Union

from lark import Token
from lark.tree import Tree


class CData(str):
    """Custom data structure for trees and tokens"""

    indent_level: int

    def __new__(cls, name: str, indent_level: int = 0) -> "CData":
        """Class method to create a new instance of CData.
        CData inherits from `str` to be a valid object for
        Tree.data and Token.type.

        Lark transformers will have access to the attributes
        of CData that are specified here."""
        obj = str.__new__(cls, name)
        obj.indent_level = indent_level
        return obj


class CToken(Token):
    """Custom structure for tokens"""

    def __init__(self, type_: CData, value: Any) -> None:
        """Initialize the CToken object"""
        super().__init__(type_, value)
        self.type: CData = type_


class CTree(Tree):
    """Custom structure for trees"""

    def __init__(  # pylint: disable=super-init-not-called
        self, data: CData, children: List[Union["CTree", CToken]]
    ) -> None:
        """Initialize the CTree object"""
        self.data: CData = data
        self.children: Sequence[Union["CTree", CToken]] = children  # type: ignore
