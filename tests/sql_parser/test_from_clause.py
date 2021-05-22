def test_single_table(parser):
    raw_query = "select field from table"
    from_clause = parser.get_tree(raw_query).children[3]

    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "table_id"
    assert from_clause.children[0].children[0].type == "CNAME"
    assert from_clause.children[0].children[0].value == "table"


def test_single_table_outerbackticks(parser):
    raw_query = "select field from `project.dataset.table`"
    from_clause = parser.get_tree(raw_query).children[3]

    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "table_id"
    assert from_clause.children[0].children[0].type == "PROJECT_NAME"
    assert from_clause.children[0].children[0].value == "project"
    assert from_clause.children[0].children[1].type == "DATASET_NAME"
    assert from_clause.children[0].children[1].value == "dataset"
    assert from_clause.children[0].children[2].type == "TABLE_NAME"
    assert from_clause.children[0].children[2].value == "table"


def test_single_table_multiplebackticks(parser):
    raw_query = "select field from `project`.`dataset`.`table`"
    from_clause = parser.get_tree(raw_query).children[3]

    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "table_id"
    assert from_clause.children[0].children[0].type == "PROJECT_NAME"
    assert from_clause.children[0].children[0].value == "project"
    assert from_clause.children[0].children[1].type == "DATASET_NAME"
    assert from_clause.children[0].children[1].value == "dataset"
    assert from_clause.children[0].children[2].type == "TABLE_NAME"
    assert from_clause.children[0].children[2].value == "table"
