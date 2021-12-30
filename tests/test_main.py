from pathlib import Path
import shutil
import tempfile

import pytest
from typer.testing import CliRunner

from sqlean.main import app


runner = CliRunner()


def test_diff_only() -> None:
    result = runner.invoke(app, ["-d"])
    assert result.exit_code == 1
    assert "Some files failed" in result.stdout


@pytest.mark.parametrize("flag", ["--write-ignore", "-i"])
def test_ignore_write(flag: str) -> None:
    result = runner.invoke(app, ["-d", flag])
    assert result.exit_code == 1
    assert "--write-ignore not implemented yet." in result.stdout


@pytest.mark.parametrize("flag", ["--force", "-f"])
def test_force(flag: str) -> None:
    result = runner.invoke(app, ["-d", flag])
    assert result.exit_code == 1
    assert "--force not implemented yet." in result.stdout


def test_target_file() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/pass/dir_1/clean.sql"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_target_invalid() -> None:
    result = runner.invoke(app, ["tests/fixtures/does_not_exist"])
    assert result.exit_code == 1
    assert "No files found" in result.stdout


def test_diffonly_pass() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_diffonly_fail() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/fail"])
    assert result.exit_code == 1
    assert "+++ with sqlean" in result.stdout
    assert "--- tests/fixtures/fail/dir_1/dirty.sql" in result.stdout
    assert "--- tests/fixtures/fail/dir_2/dirty.sql" in result.stdout
    assert "│ -from" in result.stdout
    assert "│ +FROM" in result.stdout
    assert "Summary" in result.stdout
    assert "Some files failed" in result.stdout


def test_replace_pass() -> None:
    result = runner.invoke(app, ["tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_replace_fail() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy the files to a temporary directory so that they're not changed in git
        dest = Path(tmpdir) / "fail"
        shutil.copytree("tests/fixtures/fail", dest)
        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 1
        assert "Clean files │ 33.3%" in result.stdout
        assert "Changed/sqleaned files │ 33.3%" in result.stdout

        # run sqlean again to check that files were changed
        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 1
        assert "Clean files │ 66.7%" in result.stdout
        assert "Changed/sqleaned files │ 0.0%" in result.stdout
