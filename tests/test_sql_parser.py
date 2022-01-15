"""NOTE: most of the parts of sql_parser.py are tested in integration
testing in tests/test_snapshots.py
"""
from _pytest.capture import CaptureFixture

from sqlean.sql_parser import Parser


def test_debug(sql_parser: Parser, capsys: CaptureFixture[str]) -> None:
    raw = "select * from table"
    sql_parser.print(raw, is_debug=False, file_path="test.sql")
    captured = capsys.readouterr()
    assert captured.out == ""
    sql_parser.print(raw, is_debug=True, file_path="test.sql")
    captured = capsys.readouterr()
    assert "── test.sql ──" in captured.out
    assert captured.out.count("indent_level: ") > 5
