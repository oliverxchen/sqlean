import os
from pathlib import Path
import re
import black
import pytest
from sqlean.definitions import TREE_SNAPSHOT_PATH
from sqlean.sql_parser import Parser

FILE_SEPARATOR = "---\n"
ESCAPED_FILE_SEPARATOR = "---\\n"


def parse_tree_snapshot(file_path: Path):
    with open(file_path, "r") as reader:
        rows = reader.readlines()
        try:
            separator = rows.index(FILE_SEPARATOR)
        except ValueError:
            raise ValueError(
                f"No separator '{ESCAPED_FILE_SEPARATOR}' found in {file_path}"
            )
        raw_query = "".join(rows[:separator]).strip()
        expected_tree = "".join(rows[separator + 1 :]).strip()
    return raw_query, expected_tree


def assert_snapshot_correct(
    sql_parser: Parser, raw: str, expected: str, file_path: Path
):
    actual = str(sql_parser.get_tree(raw))
    try:
        assert normalise_strings(actual) == normalise_strings(expected)
        return 1
    except AssertionError:
        print(f"{file_path} failed!")
        return 0


def normalise_strings(input_string: str):
    """Remove whitespace and commas, change to single quotes"""
    return re.sub(r"\s|,", "", input_string).replace('"', "'")


def test_all_parsing(sql_parser):
    print("")
    counter = 0
    success_counter = 0
    for file_address in os.walk(TREE_SNAPSHOT_PATH):
        for file_name in file_address[2]:
            file_path = os.path.join(file_address[0], file_name)
            raw, expected = parse_tree_snapshot(file_path)
            success_counter += assert_snapshot_correct(
                sql_parser, raw, expected, file_path
            )
            counter += 1
    print(f"{success_counter} out of {counter} tests passed.")
    if success_counter < counter:
        raise AssertionError("Not all tests passed!")


@pytest.mark.generate_snapshots()
def test_generate_tree_snapshots(sql_parser, match):
    for file_address in os.walk(TREE_SNAPSHOT_PATH):
        for file_name in file_address[2]:
            if match not in file_name:
                continue
            file_path = Path(file_address[0]) / file_name
            raw, _ = parse_tree_snapshot(file_path)
            write_snapshot(sql_parser, raw, file_path)


def write_snapshot(sql_parser: Parser, raw: str, file_path: Path):
    with open(file_path, "wt") as writer:
        writer.write(raw)
        writer.write(f"\n\n{FILE_SEPARATOR}\n")
        writer.write(
            black.format_str(
                str(sql_parser.get_tree(raw)), mode=black.Mode(line_length=120)  # type: ignore # noqa: E501
            )
        )
        # The type: ignore is because mypy fails this line in python 3.6 for some
        # reason.
