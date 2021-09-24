import os
from pathlib import Path
import re
from typing import List, Tuple

import black
from lark.exceptions import LarkError
import pytest
from rich import print
from rich.panel import Panel

from sqlean.definitions import SNAPSHOT_PATH
from sqlean.sql_parser import Parser


FILE_SEPARATOR = "---\n"


class Results:
    def __init__(self, title: str) -> None:
        self.title = title
        self.n_pass = 0
        self.fail_files: List[str] = []

    def n_total(self) -> int:
        return self.n_pass + len(self.fail_files)

    def print_fails(self) -> None:
        if len(self.fail_files) == 0:
            return
        parse_failures = "\n".join(self.fail_files)
        print(Panel(parse_failures, title=f"{self.title} failures"))

    def get_summary(self) -> str:
        return f"{self.title.ljust(11)}: {self.n_pass} / {self.n_total()} passed"

    def update_test_results(self, actual: str, expected: str, file_path: Path) -> None:
        if actual == expected:
            self.n_pass += 1
        else:
            self.fail_files.append(get_short_file_path(file_path))


class AllResults:
    parse: Results = Results("Parse")
    style: Results = Results("Style")
    idempotence: Results = Results("Idempotence")

    def print_all_fails(self) -> None:
        self.parse.print_fails()
        self.style.print_fails()
        self.idempotence.print_fails()

    def print_summary(self) -> None:
        summary = (
            f"{self.parse.get_summary()}\n"
            f"{self.style.get_summary()}\n"
            f"{self.idempotence.get_summary()}"
        )
        print(Panel(summary, title="Summary"))

    def assert_all_passed(self) -> None:
        assert self.parse.n_total() == self.parse.n_pass
        assert self.style.n_total() == self.style.n_pass
        assert self.idempotence.n_total() == self.idempotence.n_pass


def test_all_parsing(sql_parser):
    all_test_results = AllResults()

    for file_address in os.walk(SNAPSHOT_PATH):
        for file_name in file_address[2]:
            file_path = Path(file_address[0]) / file_name
            all_test_results = assert_snapshot_correct(
                sql_parser, file_path, all_test_results
            )

    all_test_results.print_all_fails()
    all_test_results.print_summary()
    all_test_results.assert_all_passed()


def assert_snapshot_correct(
    sql_parser: Parser, file_path: Path, all_test_results: AllResults
) -> AllResults:
    raw, styled, tree_repr = parse_snapshot(file_path)
    actual_styled = sql_parser.print(raw)
    actual_tree = str(sql_parser.get_tree(raw))
    try:
        styled_styled = str(sql_parser.print(actual_styled))
    except LarkError as error:
        title = "Idempotence Error: " + get_short_file_path(file_path)
        print(Panel(str(error), title=title))
        styled_styled = ""

    all_test_results.parse.update_test_results(
        actual=normalise_string(actual_tree),
        expected=normalise_string(tree_repr),
        file_path=file_path,
    )
    all_test_results.style.update_test_results(
        actual=actual_styled,
        expected=styled,
        file_path=file_path,
    )
    all_test_results.idempotence.update_test_results(
        actual=styled_styled,
        expected=styled,
        file_path=file_path,
    )

    return all_test_results


def parse_snapshot(file_path: Path) -> Tuple[str, str, str]:
    with open(file_path, "r", encoding="utf-8") as reader:
        rows = reader.readlines()

    sep = [idx for idx, row in enumerate(rows) if row == FILE_SEPARATOR]

    styled_query = ""
    tree_repr = ""

    if len(sep) == 0:
        raw_query = "".join(rows).strip()
    elif len(sep) == 1:
        raw_query = "".join(rows[: sep[0]]).strip()
    elif len(sep) == 2:
        raw_query = "".join(rows[: sep[0]]).strip()
        styled_query = "".join(rows[sep[0] + 1 : sep[1]]).strip()
        tree_repr = "".join(rows[sep[1] + 1 :]).strip()
    else:
        raise ValueError(f"Unexpected number of separators: {len(sep)}")
    return raw_query, styled_query, tree_repr


def normalise_string(input_string: str):
    """Remove whitespace and commas, change to single quotes"""
    return re.sub(r"\s|,", "", input_string).replace('"', "'")


def get_short_file_path(file_path: Path) -> str:
    return str(file_path.relative_to(SNAPSHOT_PATH)).replace("/", " / ")


@pytest.mark.generate_snapshots()
def test_generate_tree_snapshots(sql_parser, match, loc):
    walk_path = get_walk_path(loc)
    if os.path.isfile(walk_path):
        write_snapshot(sql_parser, walk_path)
        return

    for file_address in os.walk(walk_path):
        for file_name in file_address[2]:
            if match not in file_name:
                continue
            file_path = Path(file_address[0]) / file_name
            write_snapshot(sql_parser, file_path)


def get_walk_path(loc):
    tree_snapshot_dir = SNAPSHOT_PATH.name
    index = loc.find(tree_snapshot_dir)
    return SNAPSHOT_PATH / loc[index + 15 :]


def write_snapshot(sql_parser: Parser, file_path: Path) -> None:
    raw, _, _ = parse_snapshot(file_path)
    with open(file_path, "wt", encoding="utf-8") as writer:
        writer.write(raw)
        writer.write(f"\n\n{FILE_SEPARATOR}\n")
        writer.write(sql_parser.print(raw, is_debug=True))
        writer.write(f"\n\n{FILE_SEPARATOR}\n")
        writer.write(
            black.format_str(
                str(sql_parser.get_tree(raw)), mode=black.Mode(line_length=120)  # type: ignore # noqa: E501
            )
        )
        # The type: ignore is because mypy fails this line in python 3.6 for some
        # reason.
