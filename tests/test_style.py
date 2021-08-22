import os
from pathlib import Path
import pytest
from sqlean.definitions import STYLE_SNAPSHOT_PATH
from sqlean.sql_parser import Parser

FILE_SEPARATOR = "---\n"
ESCAPED_FILE_SEPARATOR = "---\\n"


def parse_style_snapshot(file_path: Path):
    with open(file_path, "r") as reader:
        rows = reader.readlines()
        try:
            separator = rows.index(FILE_SEPARATOR)
        except ValueError:
            raise ValueError(
                f"No separator '{ESCAPED_FILE_SEPARATOR}' found in {file_path}"
            )
        raw_query = "".join(rows[: separator - 1]).strip()
        styled_query = "".join(rows[separator + 2 :]).strip()
    return raw_query, styled_query


def assert_snapshot_correct(
    sql_parser: Parser, raw: str, expected: str, file_path: Path
):
    actual = sql_parser.print(raw)
    try:
        assert actual == expected
        return 1
    except AssertionError:
        print(f"{file_path} failed!")
        return 0


def test_all_styling(sql_parser):
    print("")
    counter = 0
    success_counter = 0
    for file_address in os.walk(STYLE_SNAPSHOT_PATH):
        for file_name in file_address[2]:
            file_path = os.path.join(file_address[0], file_name)
            raw, expected = parse_style_snapshot(file_path)
            success_counter += assert_snapshot_correct(
                sql_parser, raw, expected, file_path
            )
            counter += 1
    print(f"{success_counter} out of {counter} tests passed.")
    if success_counter < counter:
        raise AssertionError("Not all tests passed!")


@pytest.mark.generate_snapshots()
def test_generate_style_snapshots(sql_parser, match):
    for file_address in os.walk(STYLE_SNAPSHOT_PATH):
        for file_name in file_address[2]:
            if match not in file_name:
                continue
            file_path = Path(file_address[0]) / file_name
            raw, _ = parse_style_snapshot(file_path)
            write_snapshot(sql_parser, raw, file_path)


def write_snapshot(sql_parser: Parser, raw: str, file_path: Path):
    with open(file_path, "wt") as writer:
        writer.write(raw)
        writer.write(f"\n\n{FILE_SEPARATOR}\n")
        writer.write(sql_parser.print(raw, is_debug=True))
