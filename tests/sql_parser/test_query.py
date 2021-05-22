def test_simple_query(parser):
    raw_query = "select field from table"
    actual = parser.get_tree(raw_query)
    assert actual.data == "query"

    query = actual.children
    assert query[0].type == "SELECT"
    assert query[1].data == "select_list"
    assert query[2].type == "FROM"
    assert query[3].data == "from_clause"
