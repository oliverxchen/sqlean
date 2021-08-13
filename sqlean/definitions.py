"""Project level definitions."""
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
SNAPSHOT_PATH = ROOT_PATH / "tests" / "snapshots"
IMPORT_PATH = ROOT_PATH / "sqlean" / "grammar"
