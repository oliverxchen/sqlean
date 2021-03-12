import pytest

from sqlean.lexicon import Dialect
from sqlean.ast import SqlParser


@pytest.fixture()
def parser() -> SqlParser:
    return SqlParser(Dialect.BIGQUERY)


def test_select_list(parser):
    query = "select foo, bar baz, qux as quuz from"
    actual = parser.parser.parse(query).print()
    expected = """SELECT
    foo,
    bar AS baz,
    qux AS quuz
FROM
"""
    assert actual == expected


#  def test_select_item_function(parser):
#  query = "select sum(foo), count(bar) as c from"
#  actual = parser.parser.parse(query).print()
#  print(actual)
#  expected = """SELECT
#  SUM(foo) AS sum(foo),
#  COUNT(bar) as c
#  FROM"""
#  assert actual == expected
