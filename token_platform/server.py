import asyncio
import logging

from aiohttp import ClientSession, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from controller import handle
from middleware import error_middleware
from router import generate_routes


async def init_app():
    """Initialize the application server."""
    app = web.Application(middlewares=[error_middleware])
    app.add_routes(generate_routes())

    ### Example for logging ###
    # create logger with 'aiohttp.access'
    logger = logging.getLogger('aiohttp.access')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('access.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, port=80)
