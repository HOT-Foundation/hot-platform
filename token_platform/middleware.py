from aiohttp import web
from stellar_base.utils import AccountNotExistError

@web.middleware
async def error_middleware(request, handler):
    try:
        result = await handler(request)
        return result
    except web.HTTPNotFound as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=404)

