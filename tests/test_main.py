import pytest
from typer.testing import CliRunner

from sqlean.main import app

runner = CliRunner()


def test_default() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert "Some files failed" in result.stdout


@pytest.mark.parametrize("flag", ["--replace", "-r"])
def test_replace(flag: str) -> None:
    result = runner.invoke(app, flag)
    assert result.exit_code == 1
    assert "--replace not implemented yet." in result.stdout


@pytest.mark.parametrize("flag", ["--whisper", "-w"])
def test_whisper(flag: str) -> None:
    result = runner.invoke(app, flag)
    assert result.exit_code == 1
    assert "--whisper not implemented yet." in result.stdout


@pytest.mark.parametrize("flag", ["--ignore-write", "-i"])
def test_ignore_write(flag: str) -> None:
    result = runner.invoke(app, flag)
    assert result.exit_code == 1
    assert "--ignore-write not implemented yet." in result.stdout


@pytest.mark.parametrize("flag", ["--force", "-f"])
def test_force(flag: str) -> None:
    result = runner.invoke(app, flag)
    assert result.exit_code == 1
    assert "--force not implemented yet." in result.stdout


def test_target_file() -> None:
    result = runner.invoke(app, ["tests/fixtures/pass/dir_1/ok_1.sql"])
    assert result.exit_code == 0
    assert "1 / 1 files passed" in result.stdout
    assert "All files passed" in result.stdout


def test_target_invalid() -> None:
    result = runner.invoke(app, ["tests/fixtures/does_not_exist"])
    assert result.exit_code == 1
    assert "No files found" in result.stdout


def test_noreplace_pass() -> None:
    result = runner.invoke(app, ["tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "2 / 3 files passed" in result.stdout
    assert "1 / 3 files ignored" in result.stdout
    assert "s elapsed" in result.stdout
    assert "All files passed" in result.stdout


def test_noreplace_fail() -> None:
    result = runner.invoke(app, ["tests/fixtures/fail"])
    assert result.exit_code == 1
    assert "+++ with sqlean" in result.stdout
    assert "--- tests/fixtures/fail/dir_1/fail_1.sql" in result.stdout
    assert "--- tests/fixtures/fail/dir_2/fail_2.sql" in result.stdout
    assert "│ -from" in result.stdout
    assert "│ +FROM" in result.stdout
    assert "1 / 6 files ignored" in result.stdout
    assert "2 / 6 files dirty" in result.stdout
    assert "1 / 6 files unparsable" in result.stdout
    assert "s elapsed" in result.stdout
    assert "Some files failed" in result.stdout
