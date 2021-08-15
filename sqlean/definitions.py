"""Project level definitions."""
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
TREE_SNAPSHOT_PATH = ROOT_PATH / "tests" / "tree_snapshots"
IMPORT_PATH = ROOT_PATH / "sqlean" / "grammar"
