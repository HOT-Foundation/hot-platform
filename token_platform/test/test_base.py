from aiohttp.test_utils import TestClient, loop_context
from aiohttp import web, ClientSession
import asyncio

HOST='http://localhost:8081'


loop = asyncio.get_event_loop()
async def test_case_001():
    async with ClientSession() as session:
        resp = await session.get('{}/hotnow'.format(HOST))
        assert resp.status == 200
        text = await resp.text()
        assert 'Hello hotnow' in text
        print('test complete')
loop.run_until_complete(test_case_001())


async def test_case_002():
    async with ClientSession() as session:
        resp = await session.get('{}/hotnow'.format(HOST))
        assert resp.status == 200
        text = await resp.text()
        assert 'Hello hotnow' in text
        print('test complete')
loop.run_until_complete(test_case_002())

loop.close()
