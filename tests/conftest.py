import pytest

from sqlean.sql_parser import Parser


@pytest.fixture(scope="session")
def sql_parser():
    return Parser()


def pytest_addoption(parser):
    parser.addoption(
        "--generate-snapshots",
        action="store_true",
        default=False,
        help="Generate parsing snapshots",
    )
    parser.addoption("--match", action="store", default="")


def pytest_collection_modifyitems(config, items):
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


def pytest_generate_tests(metafunc):
    option_value = metafunc.config.option.match
    if "match" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("match", [option_value])
