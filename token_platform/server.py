import asyncio
import logging
from logging import config

from aiohttp import ClientSession, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from controller import handle
from log_conf import log_setting
from log_middleware import handle_log
from exception_middleware import handle_error
from router import generate_routes


async def init_app():
    """Initialize the application server."""
    app = web.Application(middlewares=[handle_log, handle_error])
    app.add_routes(generate_routes())
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    config.dictConfig(log_setting)
    web.run_app(app, port=80)
