from tests.conftest import assert_parse_result


def test_join(parser):
    raw_query = "select * from table1 join table2"
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
                [
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "join_operation",
                                [
                                    Tree(
                                        "join_operation_with_condition",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table1")]
                                                    )
                                                ]
                                            ),
                                            Tree("join_type", [Tree("inner_join", [])]),
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table2")]
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
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_inner_join(parser):
    raw_query = "select * from table1 inner  join table2"
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
                [
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "join_operation",
                                [
                                    Tree(
                                        "join_operation_with_condition",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table1")]
                                                    )
                                                ]
                                            ),
                                            Tree("join_type", [Tree("inner_join", [])]),
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table2")]
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
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_full_join(parser):
    raw_query = "select * from table1 full outer join table2"
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
                [
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "join_operation",
                                [
                                    Tree(
                                        "join_operation_with_condition",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table1")]
                                                    )
                                                ]
                                            ),
                                            Tree("join_type", [Tree("full_join", [])]),
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table2")]
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
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_left_join(parser):
    raw_query = "select * from table1 left join table2"
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
                [
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "join_operation",
                                [
                                    Tree(
                                        "join_operation_with_condition",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table1")]
                                                    )
                                                ]
                                            ),
                                            Tree("join_type", [Tree("left_join", [])]),
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table2")]
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
        ]
    )
    """
    assert_parse_result(actual, expected)


def test_right_join(parser):
    raw_query = "select * from table1 right\t join table2"
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
                [
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "join_operation",
                                [
                                    Tree(
                                        "join_operation_with_condition",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table1")]
                                                    )
                                                ]
                                            ),
                                            Tree("join_type", [Tree("right_join", [])]),
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table2")]
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
        ]
    )
    """
    assert_parse_result(actual, expected)
