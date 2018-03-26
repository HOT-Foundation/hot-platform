import pytest
from aiohttp import web
import asyncio
from router import routes


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.add_routes(routes)
    return loop.run_until_complete(aiohttp_client(app))

async def test_case_001(cli):
    resp = await cli.get('/123124')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello--------------, 123124' in text
    print('test complete')
