"""CLI commands"""
import difflib
from os import linesep
from pathlib import Path
import re
from typing import Iterator, List, Optional

from lark import ParseError
from rich import print as rprint
from rich.markdown import Markdown
import typer

from sqlean.settings import set_options, Settings
from sqlean.sql_parser import Parser
from sqlean.stats import Stats


app = typer.Typer(add_completion=False)


@app.command()
def main(
    target: Optional[Path] = typer.Argument(None),
    diff_only: bool = typer.Option(
        False,
        "--diff-only/",
        "-d/",
        help="Include this flag to only show diffs and not replace files in-place.",
    ),
    write_ignore: bool = typer.Option(
        False,
        "--write-ignore/",
        "-i/",
        help="Include this flag to write `# sqlean ignore` as the first line of"
        " a file if the file cannot be parsed by sqlean.",
    ),
    force: bool = typer.Option(
        False,
        "--force/",
        "-f/",
        help="Force parsing of all files, even if they have a first line of "
        "`# sqlean ignore`. This should be run when sqlean has been updated"
        " and more the set of parseable queries has grown.",
    ),
) -> None:
    """🧹Clean your SQL queries!🧹"""
    code = 0
    if write_ignore:
        typer.echo("--write-ignore not implemented yet.")
        code = 1
    if force:
        typer.echo("--force not implemented yet.")
        code = 1

    options = set_options(
        target=target, diff_only=diff_only, write_ignore=write_ignore, force=force
    )
    stats = Stats()
    sql_parser = Parser(options)
    for path in options.target:
        if path.is_dir():
            stats = sqlean_recursive(path, stats, sql_parser, options)
        elif path.is_file():
            stats = sqlean_file(path, stats, sql_parser, options)
    stats.print_summary(options)
    is_passed = stats.is_passed()
    if is_passed:
        rprint("🧘 [bold white on green]All files passed[/bold white on green] 🧘")
    elif is_passed is False:
        rprint("🙀 [bold white on red]Some files failed[/bold white on red] 🙀")
        code = 1
    elif is_passed is None:
        typer.echo("🤷 No files found 🤷")
        code = 1
    if code == 1:
        raise typer.Exit(code=code)


def sqlean_recursive(
    target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> Stats:
    """Recursively walks a directory and applies sqlean."""
    for path in target.iterdir():
        if path.is_dir():
            stats = sqlean_recursive(path, stats, sql_parser, options)
        elif path.is_file():
            stats = sqlean_file(path, stats, sql_parser, options)
    return stats


def sqlean_file(
    target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> Stats:
    """sqleans an individual file."""
    if target.suffix == ".sql":
        stats.num_files += 1
        raw_list = read_file(target)
        raw = "".join(raw_list)[:-1]  # remove newline (might not be correct)
        if should_ignore(raw_list):
            stats.num_ignored += 1
        else:
            sqlean_unignored_file(
                raw=raw,
                target=target,
                stats=stats,
                sql_parser=sql_parser,
                options=options,
            )
    return stats


def sqlean_unignored_file(
    raw: str, target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> Stats:
    """sqleans unignored file (or with option --force)."""
    try:
        styled = sql_parser.print(raw)
        if styled == raw:
            stats.num_clean += 1
        else:
            if options.diff_only:
                print_diff(raw, styled, target)
                stats.num_dirty += 1
            else:
                write_file(styled, target)
                stats.num_changed += 1
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
    if len(lines) > 0 and lines[0].startswith("# sqlean ignore"):
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


def write_file(styled: str, target: Path) -> None:
    """Writes the sqleaned file."""
    with open(target, "wt", encoding="utf-8") as writer:
        writer.write(styled)
