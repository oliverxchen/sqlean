"""Breaks up input into a collection of tokens"""

from enum import Enum
from typing import List, Dict
import re

import ply.lex as lex

import sqlean.dialects as dialects


class Dialect(str, Enum):
    """Enum for the different dialects SqlLexer can lex"""

    BIGQUERY = "bigquery"


class SqlLexer:
    """Class to break up input into tokens"""

    tokens: List[str]

    def __init__(self, dialect: Dialect):
        self.reserved_words = self.get_reserved_words(dialect)
        SqlLexer.set_tokens(self.reserved_words)

        # re.S: dot matches all (including newline)
        self.lexer = lex.lex(module=self, reflags=re.S)

    @classmethod
    def set_tokens(cls, reserved_words: Dict[str, str]) -> None:
        cls.tokens = list(set(reserved_words.values())) + [
            "ID",
            "COMMA",
            "STAR",
            "LPAREN",
            "RPAREN",
            "JINJA_VAR",
            "JINJA_BLOCK_START",
            "JINJA_BLOCK_END",
            "SQL_COMMENT",
        ]

    @staticmethod
    def get_reserved_words(dialect: Dialect):
        """Returns the list of reserved words for the selected dialect"""
        reserved_words = dict()
        reserved_words.update(dialects.COMMON_SQL)
        if dialect == Dialect.BIGQUERY:
            reserved_words.update(dialects.BIGQUERY)
        return reserved_words

    # Regular expression rules for simple tokens
    t_COMMA = r","
    t_STAR = r"\*"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_JINJA_BLOCK_START = r"\{%"
    t_JINJA_BLOCK_END = r"%\}"

    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        t.type = self.reserved_words.get(
            t.value.lower(), "ID"
        )  # Check for reserved words
        return t

    @staticmethod
    def t_SQL_COMMENT(t):
        r"--.*"
        return t

    @staticmethod
    def t_JINJA_VAR(t):
        r"\{\{.*?\}\}"
        return t

    # Define a rule so we can track line numbers
    @staticmethod
    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = " \t"

    # Error handling rule
    @staticmethod
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def get_tokens(self, data):
        self.lexer.input(data)
        return list(self.lexer)
