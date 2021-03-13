import pytest

from sqlean.configuration import Config, DEFAULT_CONFIG, SqlDialect
from sqlean.exceptions import ConfigError


def test_config_default():
    config = Config()
    assert config.indent == DEFAULT_CONFIG.indent_size * " "
    assert config.dialect == DEFAULT_CONFIG.dialect
    Config._Config__instance = None  # reset for other tests


def test_config_singleton():
    _ = Config()
    with pytest.raises(ConfigError) as excinfo:
        _ = Config()
    assert str(excinfo.value) == "The Config class can only be initialised once"
    Config._Config__instance = None  # reset for other tests


def test_config_nondefault():
    config_one = Config(indent_size=2, dialect=SqlDialect.BIGQUERY)
    two_spaces = 2 * " "
    assert config_one.indent == two_spaces
    assert config_one.dialect == SqlDialect.BIGQUERY
    config_two = Config.get_instance()
    assert config_two.indent == two_spaces
    assert config_two.dialect == SqlDialect.BIGQUERY
    Config._Config__instance = None  # reset for other tests
