def test_select_item_no_alias(parser):
    raw_query = "select field from table"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"


def test_select_item_implicit_alias(parser):
    raw_query = "select field new_field_name from table"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"
    assert select_item.children[1].data == "alias"
    assert select_item.children[1].children[0].value == "new_field_name"


def test_select_item_explicit_alias(parser):
    raw_query = "select field as new_field_name from table"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].type == "CNAME"
    assert select_item.children[0].value == "field"
    assert select_item.children[1].data == "alias"
    assert select_item.children[1].children[0].type == "AS"
    assert select_item.children[1].children[1].value == "new_field_name"


def test_arg_item_generic(parser):
    raw_query = "select SUM(x) from c"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "SUM"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list = select_item.children[0].children[2]
    assert arg_list.data == "arg_list"
    assert arg_list.children[0].value == "x"


def test_arg_item_with_date_interval(parser):
    raw_query = "select date_trunc(a, month) from c"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "date_trunc"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list = select_item.children[0].children[2]
    assert arg_list.data == "arg_list"
    assert arg_list.children[0].value == "a"
    assert arg_list.children[1].type == "DATE_INTERVAL"
    assert arg_list.children[1].value == "month"


def test_arg_item_with_time_interval(parser):
    raw_query = "select time_trunc(b, SECOND) from c"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "time_trunc"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list = select_item.children[0].children[2]
    assert arg_list.data == "arg_list"
    assert arg_list.children[0].value == "b"
    assert arg_list.children[1].type == "TIME_INTERVAL"
    assert arg_list.children[1].value == "SECOND"


def test_arg_item_with_func(parser):
    raw_query = "select date_trunc(date(timestamp_millis(t)), month) from a"
    select_item = parser.get_tree(raw_query).children[1].children[0]

    assert select_item.data == "select_item"
    assert select_item.children[0].data == "select_value"
    assert select_item.children[0].children[0].type == "FUNCTION"
    assert select_item.children[0].children[0].value == "date_trunc"
    assert select_item.children[0].children[1].type == "LPAR"
    assert select_item.children[0].children[3].type == "RPAR"

    arg_list = select_item.children[0].children[2]
    assert arg_list.data == "arg_list"
    assert arg_list.children[0].data == "arg_item"
    assert arg_list.children[0].children[0].type == "FUNCTION"
    assert arg_list.children[0].children[0].value == "date"

    inner_arg_list = arg_list.children[0].children[2]
    assert inner_arg_list.data == "arg_list"
    assert inner_arg_list.children[0].data == "arg_item"
    assert inner_arg_list.children[0].children[0].type == "FUNCTION"
    assert inner_arg_list.children[0].children[0].value == "timestamp_millis"

    inner_inner_arg_list = inner_arg_list.children[0].children[2]
    assert inner_inner_arg_list.data == "arg_list"
    assert inner_inner_arg_list.children[0].value == "t"
