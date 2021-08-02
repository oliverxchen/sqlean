from tests.conftest import assert_parse_result


def test_single_table(parser):
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


def test_single_table_outerbackticks(parser):
    raw_query = "select field from `project.dataset.table`"
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
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "table_name",
                                [
                                    Token("PROJECT_ID", "project"),
                                    Token("DATASET_ID", "dataset"),
                                    Token("TABLE_ID", "table")
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


def test_single_table_multiplebackticks(parser):
    raw_query = "select field from `project`.`dataset`.`table`"
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
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "table_name",
                                [
                                    Token("PROJECT_ID", "project"),
                                    Token("DATASET_ID", "dataset"),
                                    Token("TABLE_ID", "table")
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


def test_sub_query(parser):
    raw_query = "select field from (select field, field2 from table)"
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
                    Tree(
                        "from_item",
                        [
                            Tree(
                                "query_expr",
                                [
                                    Token("SELECT", "select"),
                                    Tree(
                                        "select_list",
                                        [
                                            Tree(
                                                "select_item_unaliased",
                                                [Token("CNAME", "field")]
                                            ),
                                            Tree(
                                                "select_item_unaliased",
                                                [Token("CNAME", "field2")]
                                            )
                                        ]
                                    ),
                                    Token("FROM", "from"),
                                    Tree(
                                        "from_clause",
                                        [
                                            Tree(
                                                "from_item",
                                                [
                                                    Tree(
                                                        "table_name",
                                                        [Token("CNAME", "table")]
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
