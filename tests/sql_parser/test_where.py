from tests.conftest import assert_parse_result


def test_where_single_expression(parser):
    raw_query = "select field from table where a"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [Tree("select_item_unaliased", [Token("CNAME", "field")])]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [
                    Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])]),
                    Tree(
                        "from_modifier", [Tree("where_clause", [Token("CNAME", "a")])]
                    )
                ]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_where_binary_bool_expression(parser):
    raw_query = "select field from table where a AND b"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [Tree("select_item_unaliased", [Token("CNAME", "field")])]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [
                    Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])]),
                    Tree(
                        "from_modifier",
                        [
                            Tree(
                                "where_clause",
                                [
                                    Tree(
                                        "binary_bool_operation",
                                        [
                                            Token("CNAME", "a"),
                                            Token("BINARY_BOOL_OPERATOR", "AND"),
                                            Token("CNAME", "b")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_where_multiple_binary_bool_expression(parser):
    # TODO: order of operations is violated here, AND should have precedence over OR
    raw_query = "select field from table where a OR b AND c"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [Tree("select_item_unaliased", [Token("CNAME", "field")])]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [
                    Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])]),
                    Tree(
                        "from_modifier",
                        [
                            Tree(
                                "where_clause",
                                [
                                    Tree(
                                        "binary_bool_operation",
                                        [
                                            Token("CNAME", "a"),
                                            Token("BINARY_BOOL_OPERATOR", "OR"),
                                            Token("CNAME", "b"),
                                            Token("BINARY_BOOL_OPERATOR", "AND"),
                                            Token("CNAME", "c")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_where_leading_unary_bool_operator(parser):
    raw_query = "select field from table where NOT a"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [Tree("select_item_unaliased", [Token("CNAME", "field")])]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [
                    Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])]),
                    Tree(
                        "from_modifier",
                        [
                            Tree(
                                "where_clause",
                                [
                                    Tree(
                                        "leading_unary_bool_operation",
                                        [
                                            Token("LEADING_UNARY_BOOL_OPERATOR", "NOT"),
                                            Token("CNAME", "a")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_where_trailing_unary_bool_operator(parser):
    raw_query = "select field from table where a is not null"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [Tree("select_item_unaliased", [Token("CNAME", "field")])]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [
                    Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])]),
                    Tree(
                        "from_modifier",
                        [
                            Tree(
                                "where_clause",
                                [
                                    Tree(
                                        "trailing_unary_bool_operation",
                                        [
                                            Token("CNAME", "a"),
                                            Tree(
                                                "trailing_unary_bool_operator",
                                                [
                                                    Token("IS", "is"),
                                                    Token("NOT", "not"),
                                                    Token("NULL", "null")
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)
