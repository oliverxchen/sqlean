from _pytest.capture import CaptureFixture

from sqlean.settings import Settings
from sqlean.stats import Stats


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
    stats.print_summary(options=Settings())
    captured = capsys.readouterr()
    assert captured.out == ""


def test_stats__print_summary__replace(capsys: CaptureFixture[str]) -> None:
    stats = Stats()
    stats.num_files = 10
    stats.num_clean = 4
    stats.num_ignored = 1
    stats.num_changed = 2
    stats.num_unparsable = 3
    stats.print_summary(options=Settings())
    captured = capsys.readouterr()
    assert "Number of SQL files │ 10" in captured.out
    assert "Clean files │ 40.0%" in captured.out
    assert "Changed/sqleaned files │ 20.0%" in captured.out
    assert "Ignored files │ 10.0%" in captured.out
    assert "Unparseable files │ 30.0%" in captured.out
    assert "Time elapsed" in captured.out
    assert "Dirty files" not in captured.out


def test_stats__print_summary__diffonly(capsys: CaptureFixture[str]) -> None:
    options = Settings(diff_only=True)
    stats = Stats()
    stats.num_files = 10
    stats.num_clean = 4
    stats.num_ignored = 1
    stats.num_dirty = 2
    stats.num_unparsable = 3
    stats.print_summary(options=options)
    captured = capsys.readouterr()
    assert "Number of SQL files │ 10" in captured.out
    assert "Clean files │ 40.0%" in captured.out
    assert "Ignored files │ 10.0%" in captured.out
    assert "Dirty files │ 20.0%" in captured.out
    assert "Unparseable files │ 30.0%" in captured.out
    assert "Time elapsed" in captured.out
    assert "Changed/sqleaned files" not in captured.out
