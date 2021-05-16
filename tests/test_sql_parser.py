from sqlean.sql_parser import parser


def test_simple_query():
    raw_query = "select field from table"
    actual = parser.parse(raw_query)
    assert actual.data == "query"

    query = actual.children
    assert query[0].type == "SELECT"
    assert query[1].data == "select_list"
    assert query[2].type == "FROM"
    assert query[3].data == "from_item"


def test_select_item_no_alias():
    raw_query = "select field from table"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"


def test_select_item_implicit_alias():
    raw_query = "select field new_field_name from table"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"
    assert select_item.children[1].data == "alias"
    assert select_item.children[1].children[0].value == "new_field_name"


def test_select_item_explicit_alias():
    raw_query = "select field as new_field_name from table"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"
    assert select_item.children[1].data == "alias"
    assert select_item.children[1].children[0].type == "AS"
    assert select_item.children[1].children[1].value == "new_field_name"


def test_arg_item_generic():
    raw_query = "select SUM(x) from c"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "SUM"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list_one = select_item.children[0].children[2]
    assert arg_list_one.data == "arg_list"
    assert arg_list_one.children[0].value == "x"


def test_arg_item_with_date_interval():
    raw_query = "select date_trunc(a, month) from c"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "date_trunc"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list_two = select_item.children[0].children[2]
    assert arg_list_two.data == "arg_list"
    assert arg_list_two.children[0].value == "a"
    assert arg_list_two.children[1].type == "DATE_INTERVAL"
    assert arg_list_two.children[1].value == "month"


def test_arg_item_with_time_interval():
    raw_query = "select time_trunc(b, SECOND) from c"
    select_item = parser.parse(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "time_trunc"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list_three = select_item.children[0].children[2]
    assert arg_list_three.data == "arg_list"
    assert arg_list_three.children[0].value == "b"
    assert arg_list_three.children[1].type == "TIME_INTERVAL"
    assert arg_list_three.children[1].value == "SECOND"
