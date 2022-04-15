from _pytest.capture import CaptureFixture
from pathlib import Path
from pydantic.error_wrappers import ValidationError
import pytest
from pytest_mock import MockerFixture

import click
import sqlean.settings as settings


def test_Settings__defaults() -> None:
    options = settings.Settings()
    assert options.target == [Path.cwd()]
    assert options.dry_run is False
    assert options.write_ignore is False
    assert options.force is False


def test_Settings__immutability() -> None:
    options = settings.Settings()
    with pytest.raises(TypeError):
        options.dry_run = True
    with pytest.raises(TypeError):
        options.write_ignore = True
    with pytest.raises(TypeError):
        options.force = True


def test_get_configuration_file_path() -> None:
    default_file = settings.get_config_file(None)
    assert default_file is not None
    assert default_file.name == "pyproject.toml"
    assert default_file.parent.name == "sqlean"

    non_existent_file = settings.get_config_file(Path("/non/existent/path"))
    assert non_existent_file is None

    ancestor_file = settings.get_config_file(Path("tests/fixtures"))
    assert ancestor_file is not None
    assert ancestor_file.name == "pyproject.toml"
    assert ancestor_file.parent.name == "sqlean"

    fixture_file_1 = settings.get_config_file(
        Path("tests/fixtures/config_file/query.sql")
    )
    assert fixture_file_1 is not None
    assert fixture_file_1.name == "pyproject.toml"
    assert fixture_file_1.parent.name == "config_file"

    fixture_file_2 = settings.get_config_file(Path("tests/fixtures/config_file/"))
    assert fixture_file_2 is not None
    assert fixture_file_2.name == "pyproject.toml"
    assert fixture_file_2.parent.name == "config_file"

    fixture_file_3 = settings.get_config_file(
        Path("tests/fixtures/config_file/dir/query.sql")
    )
    assert fixture_file_3 is not None
    assert fixture_file_3.name == "pyproject.toml"
    assert fixture_file_3.parent.name == "config_file"


def test_ConfigFileOptions__single_includes() -> None:
    single_includes = settings.ConfigFileOptions(includes="foo")
    assert single_includes.includes == [Path("foo")]


def test_ConfigFileOptions__multiple_includes() -> None:
    multiple_includes = settings.ConfigFileOptions(includes=["foo", "bar"])
    assert multiple_includes.includes == [Path("foo"), Path("bar")]


def test_ConfigFileOptions__invalid_inputs() -> None:
    with pytest.raises(ValidationError) as exc:
        settings.ConfigFileOptions(**{"includes": 1, "whisper": "wa"})
    exc.match("3 validation errors")
    exc.match("includes\n  value is not a valid list")
    exc.match("includes\n  value is not a valid path")
    exc.match("whisper\n  value could not be parsed to a boolean")


@pytest.fixture()
def samples_dir() -> Path:
    return Path("tests/fixtures/config_file/sample_files")


def test_get_settings_from_config_file__no_sqlean_section(samples_dir: Path) -> None:
    defaults = settings.ConfigFileOptions()
    no_section = settings.get_settings_from_config_file(samples_dir / "no_section.toml")
    assert no_section == defaults


def test_get_settings_from_config_file__partial_options(samples_dir: Path) -> None:
    partial_options = settings.get_settings_from_config_file(
        samples_dir / "partial_options.toml"
    )
    assert partial_options.whisper is True
    assert partial_options.indent_size == 3
    assert partial_options.dialect == settings.DialectEnum.BIGQUERY


def test_get_settings_from_config_file__extra_fields(samples_dir: Path) -> None:
    with pytest.raises(ValidationError) as exc:
        settings.get_settings_from_config_file(samples_dir / "additional_option.toml")
    exc.match("foo\n  extra fields not permitted")


def test_get_settings_from_config_file__invalid_toml(
    samples_dir: Path, capsys: CaptureFixture[str]
) -> None:
    with pytest.raises(Exception) as exc:
        settings.get_settings_from_config_file(samples_dir / "invalid_toml.toml")
    msg = str(exc.value)
    assert msg == "Invalid value (at line 5, column 15)"
    captured = capsys.readouterr()
    assert "Invalid toml file:" in captured.out
    assert "tests/fixtures/config_file/sample_files/invalid_toml.toml" in captured.out


def test_get_settings_from_config_file__invalid_sqlean_section(
    samples_dir: Path, capsys: CaptureFixture[str]
) -> None:
    with pytest.raises(Exception) as exc:
        settings.get_settings_from_config_file(samples_dir / "additional_option.toml")
    msg = str(exc.value)
    assert "foo\n  extra fields not permitted" in msg
    captured = capsys.readouterr()
    assert "Invalid [tool.sqlean] section in:" in captured.out
    assert (
        "tests/fixtures/config_file/sample_files/additional_option.toml" in captured.out
    )


@pytest.fixture()
def includes_set_path() -> Path:
    return Path("tests/fixtures/config_file/sample_files/includes_set")


@pytest.fixture()
def includes_not_set_path() -> Path:
    return Path("tests/fixtures/config_file/sample_files/includes_not_set")


def test_set_options__with_cli_target_config_set(includes_set_path: Path) -> None:
    options = settings.set_options(
        target=includes_set_path,
        dry_run=True,
        verbose=False,
        write_ignore=True,
        force=True,
    )
    assert options.target == [includes_set_path]


def test_set_options__with_cli_target_config_not_set(
    includes_not_set_path: Path,
) -> None:
    options = settings.set_options(
        target=includes_not_set_path,
        dry_run=True,
        verbose=False,
        write_ignore=True,
        force=True,
    )
    assert options.target == [includes_not_set_path]


def test_set_options__with_config_file_target(
    mocker: MockerFixture, includes_set_path: Path
) -> None:
    mocker.patch("pathlib.Path.cwd", return_value=includes_set_path)
    options = settings.set_options(
        target=None, dry_run=True, verbose=False, write_ignore=True, force=True
    )
    assert options.target == [Path("path_from_config_file")]


def test_set_options__with_no_target() -> None:
    with pytest.raises(click.exceptions.Exit):
        settings.set_options(
            target=None, dry_run=True, verbose=False, write_ignore=True, force=True
        )
