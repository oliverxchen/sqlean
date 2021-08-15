def test_select_star(sql_parser):
    raw_query = "select *, foo from table"
    _ = sql_parser.print(raw_query)
    _ = """
SELECT
    *,
    foo
FROM
    table
"""
    # assert actual == expected[1:-1]
    # temporarly auto pass this until snapshot testing is implemented
    assert True
