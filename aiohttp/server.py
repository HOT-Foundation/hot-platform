from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web, ClientSession
from controller import handle
import asyncio

app = web.Application()
app.router.add_get('/{name}', handle)

web.run_app(app, port=8081)
