from _pytest.capture import CaptureFixture
import pytest
from typer.testing import CliRunner

from sqlean.main import app, Stats

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
    result = runner.invoke(app, ["tests/fixtures/pass/dir_1/clean.sql"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_target_invalid() -> None:
    result = runner.invoke(app, ["tests/fixtures/does_not_exist"])
    assert result.exit_code == 1
    assert "No files found" in result.stdout


def test_noreplace_pass() -> None:
    result = runner.invoke(app, ["tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_noreplace_fail() -> None:
    result = runner.invoke(app, ["tests/fixtures/fail"])
    assert result.exit_code == 1
    assert "+++ with sqlean" in result.stdout
    assert "--- tests/fixtures/fail/dir_1/dirty.sql" in result.stdout
    assert "--- tests/fixtures/fail/dir_2/dirty.sql" in result.stdout
    assert "│ -from" in result.stdout
    assert "│ +FROM" in result.stdout
    assert "Summary" in result.stdout
    assert "Some files failed" in result.stdout


def test_stats__is_passed() -> None:
    stats = Stats()
    assert stats.is_passed() is None
    stats.num_files = 2
    assert not stats.is_passed()
    stats.num_clean = 2
    assert stats.is_passed()
    stats.num_clean = 1
    stats.num_ignored = 1
    assert stats.is_passed()


def test_stats__print_summary__no_files(capsys: CaptureFixture[str]) -> None:
    stats = Stats()
    stats.print_summary()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_stats__print_summary__generic(capsys: CaptureFixture[str]) -> None:
    stats = Stats()
    stats.num_files = 10
    stats.num_clean = 4
    stats.num_ignored = 1
    stats.num_dirty = 2
    stats.num_unparsable = 3
    stats.print_summary()
    captured = capsys.readouterr()
    assert "Number of SQL files │ 10" in captured.out
    assert "Clean files │ 40.0%" in captured.out
    assert "Ignored files │ 10.0%" in captured.out
    assert "Dirty files │ 20.0%" in captured.out
    assert "Unparseable files │ 30.0%" in captured.out
    assert "Time elapsed" in captured.out
