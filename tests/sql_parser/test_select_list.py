from tests.conftest import assert_parse_result


def test_select_star(parser):
    raw_query = "select * from table"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree("select_list", [Tree("select_item_unaliased", [Token("STAR", "*")])]),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_select_item_no_alias(parser):
    raw_query = "select field from table"
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
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_select_item_implicit_alias(parser):
    raw_query = "select field new_field_name from table"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_aliased",
                        [
                            Token("CNAME", "field"),
                            Token("ALIAS_NAME", "new_field_name")
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_select_item_explicit_alias(parser):
    raw_query = "select field as new_field_name from table"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_aliased",
                        [
                            Token("CNAME", "field"),
                            Token("ALIAS_NAME", "new_field_name")
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "table")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_arg_item_generic(parser):
    raw_query = "select SUM(x) from c"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_unaliased",
                        [
                            Tree(
                                "base_expression",
                                [
                                    Token("FUNCTION", "SUM"),
                                    Token("LPAR", "("),
                                    Tree("arg_list", [Token("CNAME", "x")]),
                                    Token("RPAR", ")")
                                ]
                            )
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "c")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_arg_item_with_date_interval(parser):
    raw_query = "select date_trunc(a, month) from c"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_unaliased",
                        [
                            Tree(
                                "base_expression",
                                [
                                    Token("FUNCTION", "date_trunc"),
                                    Token("LPAR", "("),
                                    Tree(
                                        "arg_list",
                                        [
                                            Token("CNAME", "a"),
                                            Token("DATE_INTERVAL", "month")
                                        ]
                                    ),
                                    Token("RPAR", ")")
                                ]
                            )
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "c")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_arg_item_with_time_interval(parser):
    raw_query = "select time_trunc(b, SECOND) from c"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_unaliased",
                        [
                            Tree(
                                "base_expression",
                                [
                                    Token("FUNCTION", "time_trunc"),
                                    Token("LPAR", "("),
                                    Tree(
                                        "arg_list",
                                        [
                                            Token("CNAME", "b"),
                                            Token("TIME_INTERVAL", "SECOND")
                                        ]
                                    ),
                                    Token("RPAR", ")")
                                ]
                            )
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "c")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_arg_item_with_func(parser):
    raw_query = "select date_trunc(date(timestamp_millis(t)), month) from a"
    actual = str(parser.get_tree(raw_query))
    expected = """
    Tree(
        "query_expr",
        [
            Token("SELECT", "select"),
            Tree(
                "select_list",
                [
                    Tree(
                        "select_item_unaliased",
                        [
                            Tree(
                                "base_expression",
                                [
                                    Token("FUNCTION", "date_trunc"),
                                    Token("LPAR", "("),
                                    Tree(
                                        "arg_list",
                                        [
                                            Tree(
                                                "arg_item",
                                                [
                                                    Token("FUNCTION", "date"),
                                                    Token("LPAR", "("),
                                                    Tree(
                                                        "arg_list",
                                                        [
                                                            Tree(
                                                                "arg_item",
                                                                [
                                                                    Token(
                                                                        "FUNCTION",
                                                                        "timestamp_millis"
                                                                    ),
                                                                    Token("LPAR", "("),
                                                                    Tree(
                                                                        "arg_list",
                                                                        [
                                                                            Token(
                                                                                "CNAME",
                                                                                "t"
                                                                            )
                                                                        ]
                                                                    ),
                                                                    Token("RPAR", ")")
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                    Token("RPAR", ")")
                                                ]
                                            ),
                                            Token("DATE_INTERVAL", "month")
                                        ]
                                    ),
                                    Token("RPAR", ")")
                                ]
                            )
                        ]
                    )
                ]
            ),
            Token("FROM", "from"),
            Tree(
                "from_clause",
                [Tree("from_item", [Tree("table_name", [Token("CNAME", "a")])])]
            )
        ]
    )
    """
    assert_parse_result(actual, expected)
