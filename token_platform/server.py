from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web, ClientSession
from controller import handle
import asyncio
from middleware import error_middleware
from account.get_account import get_account 


async def init_app():
    """Initialize the application server."""
    app = web.Application(middlewares=[error_middleware])
    app.router.add_get('/', handle)
    app.router.add_get('/account/{account_address}', get_account)
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, port=8081)

