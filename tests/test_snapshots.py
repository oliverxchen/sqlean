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
        fails = "\n".join(self.fail_files)
        print(Panel(fails, title=f"{self.title} failures"))

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


def test_all_parsing(sql_parser: Parser) -> None:
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


def normalise_string(input_string: str) -> str:
    """Remove whitespace and commas, change to single quotes"""
    return re.sub(r"\s|,", "", input_string).replace('"', "'")


def get_short_file_path(file_path: Path) -> str:
    return str(file_path.relative_to(SNAPSHOT_PATH)).replace("/", " / ")


class SnapshotResults:
    def __init__(self, title: str) -> None:
        self.title = title
        self.changed_files: List[str] = []
        self.n_same: int = 0

    def n_total(self) -> int:
        return len(self.changed_files) + self.n_same

    def print_changed(self) -> None:
        if len(self.changed_files) == 0:
            return
        changed = "\n".join(self.changed_files)
        print(Panel(changed, title=f"{self.title} changed"))

    def get_summary(self) -> str:
        return (
            f"{self.title.ljust(5)}: {self.n_same} / {self.n_total()} stayed the same"
        )

    def needs_rewrite(self, actual: str, expected: str, file_path: Path) -> bool:
        if actual == expected:
            self.n_same += 1
            needs_rewrite = False
        else:
            self.changed_files.append(get_short_file_path(file_path))
            needs_rewrite = True
        return needs_rewrite


class AllSnapshotResults:
    parse: SnapshotResults = SnapshotResults("Parse")
    style: SnapshotResults = SnapshotResults("Style")

    def print_all_changes(self) -> None:
        self.style.print_changed()
        self.parse.print_changed()

    def print_summary(self) -> None:
        summary = f"{self.style.get_summary()}\n{self.parse.get_summary()}"
        print(Panel(summary, title="Summary"))


@pytest.mark.generate_snapshots()
def test_generate_tree_snapshots(sql_parser: Parser, match: str, location: str) -> None:
    all_snapshot_results = AllSnapshotResults()
    walk_path = get_walk_path(location)

    if os.path.isfile(walk_path):
        all_snapshot_results = write_snapshot(
            sql_parser, walk_path, all_snapshot_results
        )

    else:
        for file_address in os.walk(walk_path):
            for file_name in file_address[2]:
                if match not in file_name:
                    continue
                file_path = Path(file_address[0]) / file_name
                all_snapshot_results = write_snapshot(
                    sql_parser, file_path, all_snapshot_results
                )
    all_snapshot_results.print_all_changes()
    all_snapshot_results.print_summary()


def get_walk_path(location: str) -> Path:
    snapshot_dir = SNAPSHOT_PATH.name
    index = location.find(snapshot_dir)
    output = SNAPSHOT_PATH / location[index + len(snapshot_dir) + 1 :]
    return output


def write_snapshot(
    sql_parser: Parser,
    file_path: Path,
    all_snapshot_results: AllSnapshotResults,
) -> AllSnapshotResults:
    raw, snapshot_styled, snapshot_tree = parse_snapshot(file_path)
    styled = sql_parser.print(
        raw, is_debug=True, file_path=get_short_file_path(file_path)
    )
    tree_repr = black.format_str(
        str(sql_parser.get_tree(raw)), mode=black.Mode(line_length=120)  # type: ignore
    )
    # The type: ignore is because mypy fails this line in python 3.6 for some reason.

    style_needs_rewrite = all_snapshot_results.style.needs_rewrite(
        styled, snapshot_styled, file_path
    )
    parse_needs_rewrite = all_snapshot_results.parse.needs_rewrite(
        normalise_string(tree_repr), normalise_string(snapshot_tree), file_path
    )

    if style_needs_rewrite or parse_needs_rewrite:
        with open(file_path, "wt", encoding="utf-8") as writer:
            writer.write(raw)
            writer.write(f"\n\n{FILE_SEPARATOR}\n")
            writer.write(styled)
            writer.write(f"\n\n{FILE_SEPARATOR}\n")
            writer.write(tree_repr)

    return all_snapshot_results
