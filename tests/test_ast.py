import pytest
from typing import Generator

from sqlean.configuration import Config
from sqlean.ast import SqlParser


@pytest.fixture()
def parser() -> Generator:
    yield SqlParser(Config.get_instance())
    Config._Config__instance = None  # type: ignore


def test_select_list(parser):
    query = "select foo, bar baz, qux as quuz from"
    ast = parser.parse(query)
    actual = ast.print()
    expected = """SELECT
    foo,
    bar AS baz,
    qux AS quuz
FROM
"""
    assert actual == expected


#  def test_select_item_function(parser):
#  query = "select sum(foo), count(bar) as c from"
#  ast = parser.parse(query)
#  actual = ast.print()
#  print('*************************')
#  print(actual)
#  expected = """SELECT
#  SUM(foo),
#  COUNT(bar) as c
#  FROM"""
#  assert actual == expected
