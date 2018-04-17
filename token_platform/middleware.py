import traceback

from aiohttp import web
from stellar_base.utils import AccountNotExistError


@web.middleware
async def error_middleware(request, handler):
    try:
        result = await handler(request)
        return result
    except web.HTTPBadRequest as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except web.HTTPNotFound as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=404)
    except web.HTTPInternalServerError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=500)
    # except Exception:
    #     traceback.print_exc()
    #     return web.json_response({'error': 'Internal server error.'}, status=500)
