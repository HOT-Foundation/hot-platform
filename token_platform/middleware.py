import traceback
from json import JSONDecodeError

from aiohttp import web
from stellar_base.utils import AccountNotExistError, DecodeError


@web.middleware
async def error_middleware(request, handler):
    try:
        result = await handler(request)
        return result
    except JSONDecodeError:
        return web.json_response({'error': 'Request payload must be json format.'}, status=400)
    except AccountNotExistError as ex:
        message = str(ex)
        print(message)
        print(traceback.format_exc(chain=False))
        return web.json_response({'error': message}, status=400)
    except KeyError as e:
        msg = "Parameter {} not found. Please ensure parameters is valid.".format(str(e))
        return web.json_response({'error': msg}, status=400)
    except TypeError as ex:
        message = "Invalid type of {}, please check your parameter.".format(str(ex))
        return web.json_response({'error': message}, status=400)
    except ValueError as ex:
        return web.json_response({'error': str(ex)}, status=400)
    except web.HTTPBadRequest as ex:
        message = str(ex)
        print(message)
        print(traceback.format_exc(chain=False))
        return web.json_response({'error': message}, status=400)
    except web.HTTPNotFound as ex:
        message = str(ex)
        print(message)
        print(traceback.format_exc(chain=False))
        return web.json_response({'error': message}, status=404)
    except web.HTTPInternalServerError as ex:
        message = str(ex)
        print(message)
        return web.json_response({'error': message}, status=500)
    except DecodeError as ex:
        message = str(ex)
        print(message)
        print(traceback.format_exc(chain=False))
        return web.json_response({'error': message}, status=400)

