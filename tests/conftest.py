import pytest
from sqlean.sql_parser import Parser


@pytest.fixture(scope="session")
def parser():
    return Parser()
