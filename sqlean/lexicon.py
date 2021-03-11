from enum import Enum
from typing import List, Dict
import re

import ply.lex as lex

import sqlean.dialects as dialects


class Dialect(str, Enum):
    BIGQUERY = "bigquery"


class SqleanLexer:
    tokens: List[str]

    def __init__(self, dialect: Dialect):
        self.reserved_words = self.get_reserved_words(dialect)
        SqleanLexer.set_tokens(self.reserved_words)

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
            "JINJA_COMMENT",
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

    def t_SQL_COMMENT(self, t):
        r"--.*"
        return t

    def t_JINJA_COMMENT(self, t):
        r"\{\#.*?\#\}"
        return t

    def t_JINJA_VAR(self, t):
        r"\{\{.*?\}\}"
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = " \t"

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def get_tokens(self, data):
        self.lexer.input(data)
        return [tok for tok in self.lexer]
