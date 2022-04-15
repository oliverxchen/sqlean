"""CLI commands"""
import difflib
from os import linesep
from pathlib import Path
import re
from typing import Iterator, List, Optional

from lark.exceptions import ParseError, LexError
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
    dry_run: bool = typer.Option(
        False,
        "--dry-run/",
        "-d/",
        help="Include this flag to only show diffs and not replace files in-place.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose/",
        "-v/",
        help="Include this flag to show show exception messages.",
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
        help="Force parsing of all files, even if they have a first line that starts "
        "with `# sqlean ignore`. If that header is there, the whole first line will "
        "be removed and the file will be parsed. This should be run when sqlean has "
        "been updated and the set of parsable queries has grown.",
    ),
) -> None:
    """🧹 Clean your SQL queries! 🧹\n
    WARNING: running with no options will change your files in-place."""

    options = set_options(
        target=target,
        dry_run=dry_run,
        verbose=verbose,
        write_ignore=write_ignore,
        force=force,
    )
    stats = Stats()
    sql_parser = Parser(options)
    for path in options.target:
        if path.is_dir():
            sqlean_recursive(path, stats, sql_parser, options)
        elif path.is_file():
            sqlean_file(path, stats, sql_parser, options)
    stats.print_summary(options)
    is_passed = stats.is_passed()
    if is_passed:
        rprint("🧘 [bold white on green]All files passed[/bold white on green] 🧘")
    elif is_passed is False:
        rprint("🙀 [bold white on red]Some files failed[/bold white on red] 🙀")
        raise typer.Exit(code=1)
    elif is_passed is None:
        typer.echo("🤷 No files found 🤷")
        raise typer.Exit(code=1)


def sqlean_recursive(
    target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> None:
    """Recursively walks a directory and applies sqlean."""
    for path in target.iterdir():
        if path.is_dir():
            sqlean_recursive(path, stats, sql_parser, options)
        elif path.is_file():
            sqlean_file(path, stats, sql_parser, options)


def sqlean_file(
    target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> Stats:
    """sqleans an individual file."""
    if target.suffix == ".sql":
        stats.num_files += 1
        raw_list = read_file(target)
        raw = "".join(raw_list).strip()
        if not options.force and should_ignore(raw_list):
            stats.num_ignored += 1
        else:
            if options.force and should_ignore(raw_list):
                raw = remove_ignore_header(target, raw_list)
            sqlean_unignored_file(
                raw=raw,
                target=target,
                stats=stats,
                sql_parser=sql_parser,
                options=options,
            )
    return stats  # return needed for testing


def sqlean_unignored_file(
    raw: str, target: Path, stats: Stats, sql_parser: Parser, options: Settings
) -> None:
    """sqleans unignored file (or with option --force)."""
    try:
        styled = sql_parser.print(raw)
        if styled == raw:
            stats.num_clean += 1
        else:
            if options.dry_run:
                print_diff(raw, styled, target)
                stats.num_dirty += 1
            else:
                write_file(styled, target)
                stats.num_changed += 1
                stats.changed_files.append(target)
    except (ParseError, LexError) as exception:
        if options.write_ignore:
            write_ignore_header(target)
            stats.num_ignored += 1
            stats.newly_ignored_files.append(target)
        else:
            stats.num_unparsable += 1
            stats.unparsable_files.append(target)
        if options.verbose:
            rprint(f"\n[red underline]{target}:")
            rprint(exception)


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
    # Ensure the file ends with a new line
    if styled[-1] != linesep:
        styled += linesep
    with open(target, "wt", encoding="utf-8") as writer:
        writer.write(styled)


def write_ignore_header(target: Path) -> None:
    """Writes the `# sqlean ignore` header."""
    with open(target, "rt", encoding="utf-8") as reader:
        content = reader.read()
    write_file(f"# sqlean ignore{linesep}{content}", target)


def remove_ignore_header(target: Path, raw_list: List[str]) -> str:
    """Removes the `# sqlean ignore` header."""
    raw_list.pop(0)
    raw = "".join(raw_list)
    write_file(raw, target)
    return raw
