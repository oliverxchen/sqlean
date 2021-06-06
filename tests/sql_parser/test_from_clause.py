def test_single_table(parser):
    raw_query = "select field from table"

    from_clause = parser.get_tree(raw_query).children[3]
    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "from_item"
    assert from_clause.children[0].children[0].data == "table_name"
    assert from_clause.children[0].children[0].children[0].type == "CNAME"
    assert from_clause.children[0].children[0].children[0].value == "table"


def test_single_table_outerbackticks(parser):
    raw_query = "select field from `project.dataset.table`"

    from_clause = parser.get_tree(raw_query).children[3]
    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "from_item"
    assert from_clause.children[0].children[0].data == "table_name"
    assert from_clause.children[0].children[0].children[0].type == "PROJECT_ID"
    assert from_clause.children[0].children[0].children[0].value == "project"
    assert from_clause.children[0].children[0].children[1].type == "DATASET_ID"
    assert from_clause.children[0].children[0].children[1].value == "dataset"
    assert from_clause.children[0].children[0].children[2].type == "TABLE_ID"
    assert from_clause.children[0].children[0].children[2].value == "table"


def test_single_table_multiplebackticks(parser):
    raw_query = "select field from `project`.`dataset`.`table`"

    from_clause = parser.get_tree(raw_query).children[3]
    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "from_item"
    assert from_clause.children[0].children[0].data == "table_name"
    assert from_clause.children[0].children[0].children[0].type == "PROJECT_ID"
    assert from_clause.children[0].children[0].children[0].value == "project"
    assert from_clause.children[0].children[0].children[1].type == "DATASET_ID"
    assert from_clause.children[0].children[0].children[1].value == "dataset"
    assert from_clause.children[0].children[0].children[2].type == "TABLE_ID"
    assert from_clause.children[0].children[0].children[2].value == "table"


def test_sub_query(parser):
    raw_query = "select field from (select field, field2 from table)"

    from_clause = parser.get_tree(raw_query).children[3]
    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "from_item"

    sub_query = from_clause.children[0].children[0]
    assert sub_query.data == "query_expr"
    assert sub_query.children[0].type == "SELECT"
    assert sub_query.children[1].data == "select_list"
    assert sub_query.children[2].type == "FROM"
    assert sub_query.children[3].data == "from_clause"
