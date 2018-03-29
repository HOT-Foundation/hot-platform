from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web, ClientSession
from controller import handle
import asyncio

from account.get_account import get_account 

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/account/{account_address}', get_account)

web.run_app(app, port=8081)
