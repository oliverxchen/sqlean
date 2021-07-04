def test_select_star(parser):
    raw_query = "select *, foo from table"
    output = parser.print(raw_query)
    assert (
        output
        == """SELECT
    *,
    foo
FROM
    table"""
    )
