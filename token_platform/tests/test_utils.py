from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
from server import init_app

class BaseTestClass(AioHTTPTestCase):
    """Set up server for testing"""
    async def get_application(self):
        return await init_app()
