from pathlib import Path
import shutil
import tempfile

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from sqlean.main import app
import sqlean.main as main


runner = CliRunner()


def test_target__invalid() -> None:
    result = runner.invoke(app, ["tests/fixtures/does_not_exist"])
    assert result.exit_code == 1
    assert "No files found" in result.stdout


def test_dryrun__runs_on_directory() -> None:
    result = runner.invoke(app, ["-d", "."])
    assert result.exit_code == 1
    assert "Some files were unparsable" in result.stdout
    assert "Some files were dirty" in result.stdout


def test_dryrun__missing_target() -> None:
    result = runner.invoke(app, ["-d"])
    assert result.exit_code == 1
    assert "No target specified" in result.stdout


def test_dryrun__recursive(mocker: MockerFixture) -> None:
    # validate that recursive run works and calls the sub function the
    # correct number of times
    spy = mocker.spy(main, "sqlean_file")
    runner.invoke(app, ["-d", "tests/fixtures/fail"])
    assert spy.call_count == 7  # still needs to be called for non-sql files
    assert spy.spy_return.num_files == 6
    assert spy.spy_return.num_ignored == 1
    assert spy.spy_return.num_clean == 2
    assert spy.spy_return.num_changed == 0
    assert spy.spy_return.num_dirty == 2
    assert spy.spy_return.num_unparsable == 1


def test_dryrun__runs_on_target_file() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/pass/dir_1/clean.sql"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_dryrun__pass() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_dryrun__fail() -> None:
    result = runner.invoke(app, ["-d", "tests/fixtures/fail"])
    assert result.exit_code == 1
    assert "+++ with sqlean" in result.stdout
    assert "--- tests/fixtures/fail/dir_1/dirty.sql" in result.stdout
    assert "--- tests/fixtures/fail/dir_2/dirty.sql" in result.stdout
    assert "│ -from" in result.stdout
    assert "│ +FROM" in result.stdout
    assert "── Unparsable files ──" in result.stdout
    assert "│ tests/fixtures/fail/dir_1/unparsable.sql" in result.stdout
    assert "Summary" in result.stdout
    assert "Some files were unparsable" in result.stdout
    assert "Some files were dirty" in result.stdout


def test_dryrun_verbose__fail() -> None:
    result = runner.invoke(app, ["-d", "-v", "tests/fixtures/fail"])
    assert result.exit_code == 1
    assert "tests/fixtures/fail/dir_1/unparsable.sql:" in result.stdout
    assert (
        "Unexpected token Token('STANDARD_TABLE_NAME', 'foo') at line 1, column 1."
        in result.stdout
    )
    assert "Expected one of:" in result.stdout
    assert "Previous tokens: [None]" in result.stdout


def test_replace__pass() -> None:
    result = runner.invoke(app, ["tests/fixtures/pass"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "All files passed" in result.stdout


def test_replace__fail() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy the files to a temporary directory so that they're not changed in git
        dest = Path(tmpdir) / "fail"
        shutil.copytree("tests/fixtures/fail", dest)
        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 1
        # the actual files can't be checked because with the tempdir, the paths
        # are too long and breaking in the panel is inconsistent
        assert "── Changed files ──" in result.stdout
        assert "── Unparsable files ──" in result.stdout
        assert "Clean files  33.3%" in result.stdout
        assert "Changed/sqleaned files  33.3%" in result.stdout

        # run sqlean again to check that files were changed
        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 1
        assert "── Unparsable files ──" in result.stdout
        assert "Clean files  66.7%" in result.stdout
        assert "Changed/sqleaned files   0.0%" in result.stdout


def test_write_ignore() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy the files to a temporary directory so that they're not changed in git
        dest = Path(tmpdir) / "ignore"
        shutil.copytree("tests/fixtures/fail", dest)
        unparsable_file = dest / "dir_1/unparsable.sql"

        # start with dry-run as a baseline
        result = runner.invoke(app, ["-d", tmpdir])
        assert result.exit_code == 1
        assert "Ignored files  16.7%" in result.stdout
        assert "Unparsable files  16.7%" in result.stdout
        with open(unparsable_file, "rt", encoding="utf-8") as reader:
            assert reader.read() == "foo\n"

        # run write-ignore once
        result = runner.invoke(app, ["--write-ignore", tmpdir])
        assert result.exit_code == 1
        assert "── Newly ignored files ──" in result.stdout
        assert "Changed/sqleaned files  50.0" in result.stdout
        assert "Ignored files  33.3%" in result.stdout
        assert "Unparsable files   0.0%" in result.stdout
        with open(unparsable_file, "rt", encoding="utf-8") as reader:
            assert reader.read() == "# sqlean ignore\nfoo\n"

        # run write-ignore a second time to make sure everything is the same
        result = runner.invoke(app, ["--write-ignore", tmpdir])
        assert result.exit_code == 0
        assert "Ignored files  33.3%" in result.stdout
        assert "Unparsable files   0.0%" in result.stdout
        with open(unparsable_file, "rt", encoding="utf-8") as reader:
            assert reader.read() == "# sqlean ignore\nfoo\n"


def test_force() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy the files to a temporary directory so that they're not changed in git
        dest = Path(tmpdir) / "force"
        shutil.copytree("tests/fixtures/fail", dest)
        ignored_file = dest / "dir_1/ignored.sql"

        # start with dry-run as a baseline
        result = runner.invoke(app, ["-d", tmpdir])
        assert result.exit_code == 1
        assert "Ignored files  16.7%" in result.stdout
        assert "Unparsable files  16.7%" in result.stdout
        with open(ignored_file, "rt", encoding="utf-8") as reader:
            assert reader.read() == "# sqlean ignore\ninvalid_sql_to_ignore\n"

        # run force
        result = runner.invoke(app, ["--force", tmpdir])
        assert result.exit_code == 1
        assert "Ignored files   0.0%" in result.stdout
        assert "Unparsable files  33.3%" in result.stdout
        with open(ignored_file, "rt", encoding="utf-8") as reader:
            content = reader.read()
            assert content == "invalid_sql_to_ignore\n"
