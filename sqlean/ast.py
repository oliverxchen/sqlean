"""Given a colelction of tokens, recognizes SQL grammar and produces
an abstract syntax tree (AST)"""

from typing import List

import ply.yacc as yacc

from sqlean.lexicon import SqlLexer, Dialect
from sqlean.node import Query, SelectList, SelectItem


class SqlParser:
    """Class to parse the input and ouput an AST"""

    tokens: List[str]

    def __init__(self, dialect: Dialect):
        self.lexer = SqlLexer(dialect)
        SqlParser.set_tokens(self.lexer.tokens)
        self.parser = yacc.yacc(module=self)

    @classmethod
    def set_tokens(cls, tokens: List[str]) -> None:
        cls.tokens = tokens

    @staticmethod
    def p_query(p):
        "query : SELECT select_list FROM"
        p[0] = Query(select_list=p[2], line=p.lineno, pos=p.lexpos)

    @staticmethod
    def p_select_list(p):
        """select_list : select_item
        | select_list COMMA select_item"""
        if len(p) == 2:
            p[0] = SelectList([p[1]], line=p.lineno, pos=p.lexpos)
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            raise NotImplementedError("Unhandled length for p in p_select_list")

    @staticmethod
    def p_select_item(p):
        """select_item : field_expression AS ID
        | field_expression ID
        | field_expression"""
        alias = p[len(p) - 1]
        p[0] = SelectItem(value=p[1], alias=alias, line=p.lineno, pos=p.lexpos)

    @staticmethod
    def p_field_expression(p):
        """field_expression : ID
        | function LPAREN argument_list RPAREN
        | case_expression"""
        p[0] = p[1]

    @staticmethod
    def p_argument_list(p):
        """argument_list : argument_item
        | argument_list COMMA argument_list"""
        if len(p) == 2:
            p[0] = SelectList([p[1]], line=p.lineno, pos=p.lexpos)
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            raise NotImplementedError("Unhandled length for p in p_select_list")

    # Note: add arguments like `INTERVAL 1 DAY`
    def p_argument_item(self, p):
        """argument_item : ID
        | field_expression"""

    @staticmethod
    def p_function(p):
        """function : FUNCTION
        | AGG_FUNCTION"""
        p[0] = p[1]

    def p_case_expression(self, p):
        """case_expression : CASE when_list END"""

    def p_when_list(self, p):
        """when_list : when_list when_item
        | when_item"""

    @staticmethod
    def p_when_item(p):
        """when_item : WHEN"""
        p[0] = "a"

    @staticmethod
    def p_error(p):
        print(f"Syntax error in input! {p}")
