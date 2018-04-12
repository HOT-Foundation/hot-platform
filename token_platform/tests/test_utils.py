from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
from router import routes


class BaseTestClass(AioHTTPTestCase):
    """Set up server for testing"""
    async def get_application(self):
        app = web.Application()
        app.add_routes(routes)
        return app


class Factory():


    async def create_test(self):
        return 2

