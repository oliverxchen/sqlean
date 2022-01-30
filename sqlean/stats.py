"""Stats for sqlean runs"""
from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import List, Optional

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from sqlean.settings import Settings


# This is needed to make the number in the "elapsed time" line to
# appear without bold on the integer part.
console = Console(theme=Theme({"repr.number": "cyan italic"}))


# pylint: disable=too-many-instance-attributes
@dataclass
class Stats:
    """Stats for applying sqlean to a directory recursively"""

    num_files: int = 0
    num_ignored: int = 0
    num_clean: int = 0
    num_changed: int = 0
    num_dirty: int = 0
    num_unparsable: int = 0
    start_time: float = time.time()
    changed_files: List[Path] = field(default_factory=list)
    newly_ignored_files: List[Path] = field(default_factory=list)
    unparsable_files: List[Path] = field(default_factory=list)

    def get_time_elapsed(self) -> str:
        """Return the time elapsed since the start"""
        return f"{round(time.time() - self.start_time, 3)}s"

    def is_passed(self) -> Optional[bool]:
        """Return True if all files are now ok"""
        if self.num_files == 0:
            return None
        return self.num_clean + self.num_changed + self.num_ignored == self.num_files

    def print_summary(self, options: Settings) -> None:
        """Prints a summary of the stats."""
        if self.num_files == 0:
            return
        self.print_changed_files()
        self.print_unparsable_files()
        self.print_newly_ignored_files()
        table = Table(
            title="Summary\n",
            show_header=False,
            box=None,
            title_style="bold italic #f6cc61",  # this is the neutral emoji skin tone
            title_justify="left",
            row_styles=["on navy_blue", ""],
        )
        table.add_column("Metric", justify="right", style="spring_green2")
        table.add_column("Value", justify="right", style="white")
        table.add_row("Number of SQL files", f"{self.num_files:,}")
        table.add_row("Clean files", f"{100 * self.num_clean / self.num_files:.1f}%")
        if options.dry_run is False:
            table.add_row(
                "Changed/sqleaned files",
                f"{100 * self.num_changed / self.num_files:.1f}%",
            )
        table.add_row(
            "Ignored files", f"{100 * self.num_ignored / self.num_files:.1f}%"
        )

        dirty_style = unparsable_style = ""
        if self.num_dirty > 0:
            dirty_style = "[bold white on red]"
        if self.num_unparsable > 0:
            unparsable_style = "[bold white on red]"
        if options.dry_run is True:
            table.add_row(
                "Dirty files",
                f"{dirty_style}{100 * self.num_dirty / self.num_files:.1f}%",
            )
        table.add_row(
            "Unparsable files",
            f"{unparsable_style}{100 * self.num_unparsable / self.num_files:.1f}%",
        )

        rprint("\n")
        rprint(table)
        console.print(f"\nTime elapsed: [cyan italic]{self.get_time_elapsed()}\n")

    def print_changed_files(self) -> None:
        """Prints a list of changed files"""
        if len(self.changed_files) == 0:
            return
        changed = "\n".join([str(f) for f in self.changed_files])
        rprint(Panel.fit(changed, title="Changed files"))

    def print_unparsable_files(self) -> None:
        """Prints a list of unparsable files"""
        if len(self.unparsable_files) == 0:
            return
        unparsable = "\n".join([str(f) for f in self.unparsable_files])
        rprint(Panel.fit(unparsable, title="Unparsable files"))

    def print_newly_ignored_files(self) -> None:
        """Prints a list of newly ignored files"""
        if len(self.newly_ignored_files) == 0:
            return
        newly_ignored = "\n".join([str(f) for f in self.newly_ignored_files])
        rprint(Panel.fit(newly_ignored, title="Newly ignored files"))
