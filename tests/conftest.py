from typing import List
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser as PytestParser
from _pytest.nodes import Item
from _pytest.python import Metafunc

from sqlean.sql_parser import Parser


@pytest.fixture(scope="session")
def sql_parser() -> Parser:
    return Parser()


def pytest_addoption(parser: PytestParser) -> None:
    parser.addoption(
        "-G",
        "--generate-snapshots",
        action="store_true",
        default=False,
        help="Generate parsing snapshots",
    )
    parser.addoption("-M", "--match", action="store", default="")
    parser.addoption("-L", "--location", action="store", default="")


def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    if config.getoption("--generate-snapshots"):
        skip_others = pytest.mark.skip(
            reason="--generate-snapshots option used, other tests skipped"
        )
        for item in items:
            if "generate_snapshots" not in item.keywords:
                item.add_marker(skip_others)
    else:
        skip_call = pytest.mark.skip(reason="need --generate-snapshots option to run")
        for item in items:
            if "generate_snapshots" in item.keywords:
                item.add_marker(skip_call)


def pytest_generate_tests(metafunc: Metafunc) -> None:
    match_option_value = metafunc.config.option.match
    if "match" in metafunc.fixturenames and match_option_value is not None:
        metafunc.parametrize("match", [match_option_value])
    location_option_value = metafunc.config.option.location
    if "location" in metafunc.fixturenames and location_option_value is not None:
        metafunc.parametrize("location", [location_option_value])
