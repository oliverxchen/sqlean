"""Parse sql strings"""
import os.path as path
from lark import Lark


IMPORT_PATH = path.join(path.dirname(__file__), "grammar")
parser = Lark.open("grammar/sql.lark", rel_to=__file__, import_paths=[IMPORT_PATH])
