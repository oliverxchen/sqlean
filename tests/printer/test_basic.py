def test_select_star(parser):
    raw_query = "select *, foo from table"
    actual = parser.print(raw_query)
    expected = """
SELECT
    *,
    foo
FROM
    table
"""
    assert actual == expected[1:-1]
