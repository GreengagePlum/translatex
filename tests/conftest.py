import pytest
from fixtures.fixt_markers import *
from fixtures.fixt_tokenizers import *
from fixtures.fixt_preprocessors import *
from fixtures.fixt_translators import *


def pytest_addoption(parser):
    parser.addoption("--runapi", action="store_true",
                     help="Run the tests that include API calls.")


def pytest_configure(config):
    config.addinivalue_line("markers", "api: mark test as testing the response of an API call")


def pytest_runtest_setup(item):
    if "api" in item.keywords and not item.config.getoption("--runapi"):
        pytest.skip("Need --runapi option to run this test")
