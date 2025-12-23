import pytest

@pytest.fixture
def sample_fixture():
    return "Hello, World!"

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config.addinivalue_line("markers", "sample: mark test as sample")