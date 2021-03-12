import pytest
from typing import Generator

from sqlean.configuration import Config
from sqlean.lexicon import SqlLexer


@pytest.fixture()
def lexer() -> Generator:
    yield SqlLexer(Config.get_instance())
    Config._Config__instance = None  # type: ignore


def assert_types(actual, expected):
    for actual_tok, expected_type in zip(actual, expected):
        assert str(actual_tok.type) == expected_type


def test_simple_tokens(lexer):
    data = ",*(){%%}"
    actual = lexer.get_tokens(data)
    expected = [
        "COMMA",
        "STAR",
        "LPAREN",
        "RPAREN",
        "JINJA_BLOCK_START",
        "JINJA_BLOCK_END",
    ]
    assert_types(actual, expected)


def test_case_insensitive_reserved_words(lexer):
    data = "sElEcT SELECT select"
    actual = lexer.get_tokens(data)
    expected = ["SELECT", "SELECT", "SELECT"]
    assert_types(actual, expected)


def test_whole_word_match(lexer):
    data = "selected_fields from_date is_purchased"
    actual = lexer.get_tokens(data)
    expected = ["ID", "ID", "ID"]
    assert_types(actual, expected)


def test_some_common_sql_reserved_words(lexer):
    data = "select from where group by order"
    actual = lexer.get_tokens(data)
    expected = ["SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER"]
    assert_types(actual, expected)


def test_bigquery_functions(lexer):
    data = "AVG ROW_NUMBER sin AVERAGE"
    actual = lexer.get_tokens(data)
    expected = ["AGG_FUNCTION", "NUM_FUNCTION", "FUNCTION", "ID"]
    assert_types(actual, expected)


def test_combined_words(lexer):
    data = "SELECT * FROM {{ source(a, b) }}"
    actual = lexer.get_tokens(data)
    expected = [
        "SELECT",
        "STAR",
        "FROM",
        "JINJA_VAR",
    ]
    assert_types(actual, expected)


def test_sql_comment(lexer):
    data = "SELECT * FROM foo -- this is a comment"
    actual = lexer.get_tokens(data)
    expected = [
        "SELECT",
        "STAR",
        "FROM",
        "ID",
        "SQL_COMMENT",
    ]
    assert_types(actual, expected)


def test_jinja_var(lexer):
    data = """{{
  config(
    foo=bar
  )
}}"""
    actual = lexer.get_tokens(data)
    expected = ["JINJA_VAR"]
    assert_types(actual, expected)
