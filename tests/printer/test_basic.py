def test_select_star(sql_parser):
    raw_query = "select *, foo from table"
    actual = sql_parser.print(raw_query)
    expected = """
SELECT
    *,
    foo
FROM
    table
"""
    assert actual == expected[1:-1]
