"""Stats for sqlean runs"""
from dataclasses import dataclass
import time
from typing import Optional

from rich import print as rprint
from rich.table import Table

from sqlean.settings import Settings


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

    def get_time_elapsed(self) -> str:
        """Return the time elapsed since the start"""
        return f"{round(time.time() - self.start_time, 3)}s"

    def is_passed(self) -> Optional[bool]:
        """Return True if all files passed"""
        if self.num_files == 0:
            return None
        return self.num_clean + self.num_ignored == self.num_files

    def print_summary(self, options: Settings) -> None:
        """Prints a summary of the stats."""
        if self.num_files == 0:
            return
        table = Table(title="Summary")
        table.add_column("Metric", justify="right", style="cyan")
        table.add_column("Value", justify="left", style="white")
        table.add_row("Number of SQL files", f"{self.num_files:,}")
        table.add_row("Clean files", f"{100 * self.num_clean / self.num_files:.1f}%")
        if options.diff_only is False:
            table.add_row(
                "Changed/sqleaned files",
                f"{100 * self.num_changed / self.num_files:.1f}%",
            )
        table.add_row(
            "Ignored files", f"{100 * self.num_ignored / self.num_files:.1f}%"
        )

        dirty_style = unparseable_style = ""
        if self.num_dirty > 0:
            dirty_style = "[bold white on red]"
        if self.num_unparsable > 0:
            unparseable_style = "[bold white on red]"
        if options.diff_only is True:
            table.add_row(
                "Dirty files",
                f"{dirty_style}{100 * self.num_dirty / self.num_files:.1f}%",
            )
        table.add_row(
            "Unparseable files",
            f"{unparseable_style}{100 * self.num_unparsable / self.num_files:.1f}%",
        )
        table.add_row("Time elapsed", self.get_time_elapsed())
        rprint("\n")
        rprint(table)
