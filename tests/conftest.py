import pytest
from sqlean.sql_parser import Parser


@pytest.fixture(scope="session")
def parser():
    return Parser()


def assert_parse_result(actual: str, expected: str):
    def normalise_strings(input_string: str):
        return input_string.replace(" ", "").replace("\n", "").replace('"', "'")

    assert normalise_strings(actual) == normalise_strings(expected)
