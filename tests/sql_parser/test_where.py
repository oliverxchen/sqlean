def test_where_single_expression(parser):
    raw_query = "select field from table where a"

    where_clause = parser.get_tree(raw_query).children[5]
    assert where_clause.type == "CNAME"
    assert where_clause.value == "a"


def test_where_binary_bool_expression(parser):
    raw_query = "select field from table where a AND b"

    where_clause = parser.get_tree(raw_query).children[5]
    print(where_clause)
    assert where_clause.data == "binary_bool_operation"
    assert where_clause.children[1].type == "BINARY_BOOL_OPERATOR"
    assert where_clause.children[1].value == "AND"


def test_where_multiple_binary_bool_expression(parser):
    # TODO: order of operations is violated here, AND should have precedence over OR
    raw_query = "select field from table where a OR b AND c"

    where_clause = parser.get_tree(raw_query).children[5]
    assert where_clause.data == "binary_bool_operation"

    assert where_clause.children[1].type == "BINARY_BOOL_OPERATOR"
    assert where_clause.children[1].value == "OR"
    assert where_clause.children[3].type == "BINARY_BOOL_OPERATOR"
    assert where_clause.children[3].value == "AND"


def test_where_leading_unary_bool_operator(parser):
    raw_query = "select field from table where NOT a"

    where_clause = parser.get_tree(raw_query).children[5]
    assert where_clause.data == "leading_unary_bool_operation"
    assert where_clause.children[0].type == "LEADING_UNARY_BOOL_OPERATOR"
    assert where_clause.children[0].value == "NOT"


def test_where_trailing_unary_bool_operator(parser):
    raw_query = "select field from table where a is not null"

    where_clause = parser.get_tree(raw_query).children[5]
    assert where_clause.data == "trailing_unary_bool_operation"
    assert where_clause.children[1].data == "trailing_unary_bool_operator"
    assert where_clause.children[1].children[0].type == "IS"
    assert where_clause.children[1].children[1].type == "NOT"
    assert where_clause.children[1].children[2].type == "NULL"
