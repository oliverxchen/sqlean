"""Parse sql strings"""

from lark import Lark


IMPORT_PATH = "/Users/oliver.chen/src/sqlean/sqlean"
parser = Lark.open("sql.lark", rel_to=__file__, import_paths=[IMPORT_PATH])
