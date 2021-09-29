"""Styling of SQL queries"""

from typing import List

from lark.tree import Tree
from lark.visitors import v_args

from sqlean.custom_classes import CToken, CTree
from sqlean.style_mixins import (
    BoolMixin,
    ComparisonMixin,
    FromMixin,
    FromModifierMixin,
    FunctionMixin,
    JoinMixin,
    SelectMixin,
    TerminalMixin,
)


@v_args(tree=True)
class Styler(  # pylint: disable=too-many-ancestors
    BoolMixin,
    ComparisonMixin,
    FromMixin,
    FromModifierMixin,
    FunctionMixin,
    JoinMixin,
    SelectMixin,
    TerminalMixin,
):
    """Pretty printer: formats the lists of atoms and the overall query"""

    def __default__(self, data: str, children: List[Tree], meta: str) -> str:
        """default for all Trees without a callback"""
        raise NotImplementedError(f"Unsupported node: {data}")

    def __default_token__(self, token: CToken) -> str:
        if self._is_non_keyword(token):
            return token
        return token.upper()

    @staticmethod
    def _is_non_keyword(token: CToken) -> bool:
        return token.type.endswith("NAME") or token.type.endswith("_ID")

    def query_expr(self, node: CTree) -> str:
        """rollup itms in query_expr"""
        return self._rollup_linesep(node)

    @staticmethod
    def query_file(node: CTree) -> str:
        """print query_file"""
        return str(node.children[0])

    def sub_query_expr(self, node: CTree) -> str:
        """print sub_query_expr"""
        return (
            self._apply_indent("(\n", node.data.indent_level)
            + str(node.children[0])
            + "\n"
            + self._apply_indent(")", node.data.indent_level)
        )
