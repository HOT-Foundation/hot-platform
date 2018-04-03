from server import init_app
import pytest

@pytest.fixture
def cli(loop, aiohttp_client):
    app = loop.run_until_complete(init_app())
    return loop.run_until_complete(aiohttp_client(app))
