import asyncio
import logging
from logging import config

from aiohttp import ClientSession, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from controller import handle
from middlewares import exception
from request_tracking import metrics
from log import log, log_conf
from router import generate_routes


async def init_app():
    """Initialize the application server."""
    app = web.Application(middlewares=[log.handle_log, exception.handle_error, metrics.metrics_mapping])
    app.add_routes(generate_routes())
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    config.dictConfig(log_conf.log_setting)
    web.run_app(app, port=80)
