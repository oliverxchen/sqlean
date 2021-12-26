"""CLI commands"""
from dataclasses import dataclass
import difflib
from os import linesep
from pathlib import Path
import re
import time
from typing import Iterator, List, Optional

from lark import ParseError
from rich import print as rprint
from rich.markdown import Markdown
from rich.panel import Panel
import typer

from sqlean.sql_parser import Parser


app = typer.Typer(add_completion=False)


# pylint: disable=too-many-arguments
@app.command()
def main(
    target: Path = typer.Argument("."),
    replace: bool = typer.Option(
        False, "--replace/", "-r/", help="Include this flag to replace files in-place."
    ),
    whisper: bool = typer.Option(
        False,
        "--whisper/",
        "-w/",
        help="Include this flag to whisper SQL keywords instead of SHOUTING.",
    ),
    ignore_write: bool = typer.Option(
        False,
        "--ignore-write/",
        "-i/",
        help="Include this flag to write `# sqlean ignore` as the first line of"
        " a file if the file cannot be parsed by sqlean.",
    ),
    force: bool = typer.Option(
        False,
        "--force/",
        "-f/",
        help="Force parsing of all files, even if they have a first line of "
        "`# sqlean ignore`.",
    ),
    size_indent: int = typer.Option(
        4,
        "--size-indent/",
        "-s/",
        help="Number of spaces in a single indent.",
    ),
) -> None:
    """🧹Clean your SQL queries!🧹"""
    code = 0
    if replace:
        typer.echo("--replace not implemented yet.")
        code = 1
    if whisper:
        typer.echo("--whisper not implemented yet.")
        code = 1
    if ignore_write:
        typer.echo("--ignore-write not implemented yet.")
        code = 1
    if force:
        typer.echo("--force not implemented yet.")
        code = 1
    if size_indent != 4:
        typer.echo("non-default --size-indent not implemented yet.")
        code = 1
    stats = Stats()
    sql_parser = Parser()
    if target.is_dir():
        stats = sqlean_recursive(target, stats, sql_parser)
    elif target.is_file():
        stats = sqlean_file(target, stats, sql_parser)
    stats.print_summary()
    is_passed = stats.is_passed()
    if is_passed:
        typer.secho("🧘 All files passed 🧘", fg=typer.colors.GREEN, bold=True)
    elif is_passed is False:
        typer.secho(
            "🙀 Some files failed 🙀",
            fg=typer.colors.WHITE,
            bg=typer.colors.RED,
            bold=True,
        )
        code = 1
    elif is_passed is None:
        typer.echo("🤷 No files found 🤷")
        code = 1
    if code == 1:
        raise typer.Exit(code=code)


@dataclass
class Stats:
    """Stats for applying sqlean to a directory recursively"""

    num_files: int = 0
    num_ignored: int = 0
    num_passed: int = 0
    num_dirty: int = 0
    num_unparsable: int = 0
    start_time: float = time.time()

    def get_time_elapsed(self) -> str:
        """Return the time elapsed since the start"""
        return f"{round(time.time() - self.start_time, 3)}s"

    def is_passed(self) -> Optional[bool]:
        """Return True if all files passed"""
        if self.num_files == 0:
            return None
        return self.num_passed + self.num_ignored == self.num_files

    def print_summary(self) -> None:
        """Prints a summary of the stats."""
        if self.num_files == 0:
            return
        rprint(
            Panel.fit(
                f"{self.num_passed} / {self.num_files} files passed\n"
                f"{self.num_ignored} / {self.num_files} files ignored\n"
                f"{self.num_dirty} / {self.num_files} files dirty\n"
                f"{self.num_unparsable} / {self.num_files} files unparsable",
                title="Summary",
            )
        )
        typer.echo(f"{self.get_time_elapsed()} elapsed")


def sqlean_recursive(target: Path, stats: Stats, sql_parser: Parser) -> Stats:
    """Recursively walks a directory and applies sqlean."""
    for path in target.iterdir():
        if path.is_dir():
            stats = sqlean_recursive(path, stats, sql_parser)
        elif path.is_file():
            stats = sqlean_file(path, stats, sql_parser)
    return stats


def sqlean_file(target: Path, stats: Stats, sql_parser: Parser) -> Stats:
    """sqleans an individual file."""
    stats.num_files += 1
    if target.suffix == ".sql":
        raw_list = read_file(target)
        raw = "".join(raw_list)[:-1]  # remove newline (might not be correct)
        if should_ignore(raw_list):
            stats.num_ignored += 1
        else:
            try:
                styled = sql_parser.print(raw)
                if styled == raw:
                    stats.num_passed += 1
                else:
                    print_diff(raw, styled, target)
                    stats.num_dirty += 1
            except ParseError:
                stats.num_unparsable += 1
    return stats


def read_file(target: Path) -> List[str]:
    """Reads a file and returns a list of lines."""
    with open(target.resolve(), "r", encoding="utf-8") as reader:
        lines = reader.readlines()
    return lines


def should_ignore(lines: List[str]) -> bool:
    """Returns True if the file should be ignored."""
    if lines[0].startswith("# sqlean ignore"):
        return True
    return False


def print_diff(raw: str, styled: str, target: Path) -> None:
    """Prints a diff between two strings."""
    diff = difflib.unified_diff(
        raw.splitlines(),
        styled.splitlines(),
        fromfile=str(target),
        tofile="with sqlean",
    )
    diff_str = process_diffs(diff)
    diff_md = Markdown(f"""```diff{linesep}{diff_str}{linesep}```""")
    rprint(diff_md)


pattern = re.compile("^@@")


def process_diffs(diff: Iterator[str]) -> str:
    """Vertically space the diff out better"""
    diff_list = [pattern.sub("\n@@", item).rstrip("\n") for item in list(diff)]
    return "\n".join(diff_list)
