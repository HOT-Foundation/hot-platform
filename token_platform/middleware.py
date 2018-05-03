from aiohttp import web
from stellar_base.utils import AccountNotExistError, DecodeError
from json import JSONDecodeError

@web.middleware
async def error_middleware(request, handler):
    try:
        result = await handler(request)
        return result
    except JSONDecodeError:
        return web.json_response({'error': 'Request payload must be json format.'}, status=400)
    except AccountNotExistError as ex:
        message = str(ex)
        return web.json_response({'error': message}, status=400)
    except (TypeError, ValueError, web.HTTPBadRequest)  as ex:
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
