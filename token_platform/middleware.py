from aiohttp import web
from stellar_base.utils import AccountNotExistError, DecodeError


@web.middleware
async def error_middleware(request, handler):
    try:
        result = await handler(request)
        return result
    except AccountNotExistError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except web.HTTPBadRequest as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except ValueError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except TypeError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except web.HTTPNotFound as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=404)
    except web.HTTPInternalServerError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=500)
    except DecodeError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
