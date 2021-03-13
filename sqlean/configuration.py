"""Set and get configuration values"""

from enum import Enum
from typing import Optional, NamedTuple

from sqlean.exceptions import ConfigError


class SqlDialect(str, Enum):
    """Enum for the different dialects SqlLexer can lex"""

    BIGQUERY = "bigquery"


class _DefaultConfig(NamedTuple):
    indent_size: int = 4
    dialect: SqlDialect = SqlDialect.BIGQUERY


DEFAULT_CONFIG = _DefaultConfig()


class Config:
    """Singleton that stores all configuration values"""

    __instance = None

    # TODO: allow reading configuration from a file. If there is no command line
    #       argument, First check pyproject.toml and then .sqlean.toml
    def __init__(
        self, indent_size: Optional[int] = None, dialect: Optional[SqlDialect] = None
    ):
        if Config.__instance is not None:
            raise ConfigError("The Config class can only be initialised once")

        self.indent: str
        self.dialect: SqlDialect
        self._set_indent(indent_size)
        self._set_dialect(dialect)
        Config.__instance = self

    @staticmethod
    def get_instance():
        """Static access method for the object"""
        if Config.__instance is None:
            Config()
        return Config.__instance

    def _set_indent(self, indent_size: Optional[int]):
        if indent_size is None:
            indent_size = DEFAULT_CONFIG.indent_size
        self.indent = indent_size * " "

    def _set_dialect(self, dialect: Optional[SqlDialect]):
        if dialect is None:
            dialect = DEFAULT_CONFIG.dialect
        self.dialect = dialect
