"""Determine settings for a sqlean run."""
from enum import Enum
from pathlib import Path
import sys
from typing import List, Optional, Union

from pydantic import BaseModel, validator, Extra
from pydantic.error_wrappers import ValidationError
import tomli
from rich import print as rprint
from rich.console import Console


console = Console()


class DialectEnum(str, Enum):
    """Enum for dialects."""

    BIGQUERY = "BIGQUERY"


class Settings(BaseModel, allow_mutation=False):
    """Data class for storing settings."""

    target: List[Path] = [Path.cwd()]
    diff_only: bool = False
    write_ignore: bool = False
    force: bool = False
    whisper: bool = False
    indent_size: int = 4
    max_line_length: int = -1
    dialect: DialectEnum = DialectEnum.BIGQUERY

    # Validators: these are needed because the attributes are input with value None
    # if they are not in the command line options or config file.
    @staticmethod
    def _default_as_false(value: Optional[bool]) -> bool:
        """Returns False if value is None."""
        if value is None:
            return False
        return value

    @validator("diff_only", always=True)
    @classmethod
    def diff_only_default(cls, value: Optional[bool]) -> bool:
        """Fills in default value for diff_only if not provided."""
        return cls._default_as_false(value)

    @validator("write_ignore", always=True)
    @classmethod
    def write_ignore_default(cls, value: Optional[bool]) -> bool:
        """Fills in default value for write_ignore if not provided."""
        return cls._default_as_false(value)

    @validator("force", always=True)
    @classmethod
    def force_default(cls, value: Optional[bool]) -> bool:
        """Fills in default value for force if not provided."""
        return cls._default_as_false(value)


def set_options(
    target: Optional[Path],
    diff_only: Optional[bool],
    write_ignore: Optional[bool],
    force: Optional[bool],
) -> Settings:
    """Returns a Settings object taking into account CLI options
    and configuration file options."""
    config_file = get_config_file(target)
    config = get_settings_from_config_file(config_file)
    if target is None:
        if config.includes is not None:
            actual_target = config.includes
        else:
            actual_target = [Path.cwd()]
    else:
        actual_target = [target]
    return Settings(
        target=actual_target,
        diff_only=diff_only,
        write_ignore=write_ignore,
        force=force,
        **config.dict(),
    )


def get_config_file(target: Optional[Path]) -> Optional[Path]:
    """Returns the path to the configuration file, if it exists."""
    # If no target has been supplied as a CLI argument, use the current directory.
    if target is None:
        target = Path.cwd()
    # Otherwise, change target to an absolute path.
    else:
        target = target.resolve()
    config_file_name = "pyproject.toml"
    # Keep looking up to parent directories for pyproject.toml
    while not (target / config_file_name).is_file():
        target = target.parent
        if target == Path("/"):
            return None
    return target / config_file_name


class ConfigFileOptions(BaseModel, extra=Extra.forbid):
    """Data class for storing configuration file options."""

    includes: Optional[Union[List[Path], Path]] = None
    whisper: Optional[bool] = False
    indent_size: Optional[int] = 4
    max_line_length: Optional[int] = -1
    dialect: Optional[DialectEnum] = DialectEnum.BIGQUERY
    # future options —
    # excludes: Optional[Union[List[str], str]] = None
    # extensions: Optional[Union[List[str], str]] = "sql"

    @validator("includes", always=True)
    @classmethod
    def coerce_includes_to_list(
        cls, value: Optional[Union[List[Path], Path]]
    ) -> Optional[List[Path]]:
        """Changes Path to List[Path] in includes"""
        if isinstance(value, Path):
            value = [value]
        return value


def get_settings_from_config_file(config_file: Optional[Path]) -> ConfigFileOptions:
    """Returns a ConfigFileOptions object from a configuration file."""

    # Return all defaults if no pyproject.toml file was found
    if config_file is None:
        return ConfigFileOptions()

    toml_text = config_file.read_text(encoding="utf-8")
    try:
        config = tomli.loads(toml_text)
    except tomli.TOMLDecodeError as exc:
        rprint(f"[white on red]Invalid toml file:[red on black]\n  {config_file}")
        sys.tracebacklimit = 0
        raise exc

    try:
        options = ConfigFileOptions(**config.get("tool", {}).get("sqlean", {}))
    except ValidationError as exc:
        rprint(r"[white on red]Invalid \[tool.sqlean] section in:")
        rprint(f"[red on black]  {config_file}")
        sys.tracebacklimit = 0
        raise exc

    return options