import pytest
from sqlean.sql_parser import parser


@pytest.fixture()
def text():
    return "select bar, baz as b, qux q from foo"


def test_sql_parser(text):
    actual = parser.parse(text)
    print(actual)
    assert actual.data == "query"

    actual_query = actual.children
    assert actual_query[0].type == "SELECT"
    assert actual_query[1].data == "select_clause"
    assert actual_query[2].type == "FROM"
    assert actual_query[3].data == "from_item"

    actual_select_items = actual_query[1].children
    assert actual_select_items[0].type == "CNAME"
    assert actual_select_items[0].value == "bar"
    assert actual_select_items[1].children[0].type == "CNAME"
    assert actual_select_items[1].children[0].value == "baz"
    assert actual_select_items[1].children[1].type == "AS"
    assert actual_select_items[1].children[2].type == "CNAME"
    assert actual_select_items[1].children[2].value == "b"
    assert actual_select_items[1].children[0].type == "CNAME"
    assert actual_select_items[2].children[0].value == "qux"
    assert actual_select_items[2].children[1].type == "CNAME"
    assert actual_select_items[2].children[1].value == "q"
