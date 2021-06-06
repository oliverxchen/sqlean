def test_join(parser):
    raw_query = "select * from table1 join table2"

    from_clause = parser.get_tree(raw_query).children[3]
    assert from_clause.data == "from_clause"
    assert from_clause.children[0].data == "from_item"
    assert from_clause.children[0].children[0].data == "join_operation"

    join_op_w_cond = from_clause.children[0].children[0].children[0]
    assert join_op_w_cond.data == "join_operation_with_condition"
    assert join_op_w_cond.children[1].data == "join_type"
    assert join_op_w_cond.children[1].children[0].data == "inner_join"


def test_inner_join(parser):
    raw_query = "select * from table1 inner  join table2"

    from_clause = parser.get_tree(raw_query).children[3]
    join_op_w_cond = from_clause.children[0].children[0].children[0]
    assert join_op_w_cond.children[1].children[0].data == "inner_join"


def test_full_join(parser):
    raw_query = "select * from table1 full outer join table2"

    from_clause = parser.get_tree(raw_query).children[3]
    join_op_w_cond = from_clause.children[0].children[0].children[0]
    assert join_op_w_cond.children[1].children[0].data == "full_join"


def test_left_join(parser):
    raw_query = "select * from table1 left join table2"

    from_clause = parser.get_tree(raw_query).children[3]
    join_op_w_cond = from_clause.children[0].children[0].children[0]
    assert join_op_w_cond.children[1].children[0].data == "left_join"


def test_right_join(parser):
    raw_query = "select * from table1 right\t join table2"

    from_clause = parser.get_tree(raw_query).children[3]
    join_op_w_cond = from_clause.children[0].children[0].children[0]
    assert join_op_w_cond.children[1].children[0].data == "right_join"
