from typing import List

import ply.yacc as yacc

from sqlean.lexicon import SqleanLexer, Dialect
from sqlean.node import Query, SelectList, SelectItem


class SqleanParser:
    tokens: List[str]

    def __init__(self, dialect: Dialect):
        self.lexer = SqleanLexer(dialect)
        SqleanParser.set_tokens(self.lexer.tokens)
        self.parser = yacc.yacc(module=self)

    @classmethod
    def set_tokens(cls, tokens: List[str]) -> None:
        cls.tokens = tokens

    def p_query(self, p):
        "query : SELECT select_list FROM"
        p[0] = Query(select_list=p[2], line=p.lineno, pos=p.lexpos)

    def p_select_list(self, p):
        """select_list : select_item
        | select_list COMMA select_item"""
        if len(p) == 2:
            p[0] = SelectList([p[1]], line=p.lineno, pos=p.lexpos)
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            raise NotImplemented("Unhandled length for p in p_select_list")

    def p_select_item(self, p):
        """select_item : field_expression AS ID
        | field_expression ID
        | field_expression"""
        alias = p[len(p) - 1]
        p[0] = SelectItem(value=p[1], alias=alias, line=p.lineno, pos=p.lexpos)

    def p_field_expression(self, p):
        """field_expression : ID
        | function LPAREN argument_list RPAREN
        | case_expression"""
        p[0] = p[1]

    def p_argument_list(self, p):
        """argument_list : argument_item
        | argument_list COMMA argument_list"""
        if len(p) == 2:
            p[0] = SelectList([p[1]], line=p.lineno, pos=p.lexpos)
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            raise NotImplemented("Unhandled length for p in p_select_list")

    # TODO: add arguments like `INTERVAL 1 DAY`
    def p_argument_item(self, p):
        """argument_item : ID
        | field_expression"""
        pass

    def p_function(self, p):
        """function : FUNCTION
        | AGG_FUNCTION"""
        p[0] = p[1]

    def p_case_expression(self, p):
        """case_expression : CASE when_list END"""
        pass

    def p_when_list(self, p):
        """when_list : when_list when_item
        | when_item"""
        pass

    def p_when_item(self, p):
        """when_item : WHEN"""
        p[0] = "a"

    @staticmethod
    def p_error(p):
        print("Syntax error in input!")
