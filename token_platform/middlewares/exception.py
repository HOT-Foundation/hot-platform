import traceback
from json import JSONDecodeError

from aiohttp import web
from stellar_base.utils import AccountNotExistError, DecodeError
from typing import Dict

@web.middleware
async def handle_error(request, handler):
    try:
        response = await handler(request)
    except JSONDecodeError:
        message = 'Request payload must be json format.'
        return web.json_response(format_error(ex), status=400)
    except KeyError as e:
        message = "Parameter {} not found. Please ensure parameters is valid.".format(str(e))
        return web.json_response(format_error(ex), status=400)
    except TypeError as ex:
        message = "Invalid type of {}, please check your parameter.".format(str(ex))
        return web.json_response(format_error(ex), status=400)
    except (ValueError, AccountNotExistError, web.HTTPBadRequest, DecodeError) as ex:
        return web.json_response(format_error(ex), status=400)
    except web.HTTPNotFound as ex:
        return web.json_response(format_error(ex), status=404)
    except web.HTTPInternalServerError as ex:
        return web.json_response(format_error(ex), status=500)
    except web.HTTPConflict as ex:
        return web.json_response(format_error(ex), status=409)
    except Exception as ex:
        return web.json_response(format_error(ex), status=400)
    return response


def format_error(e):
    try:
        body = e.reason
        if isinstance(body, Dict):
            e = body['message']
    except:
        pass

    return {
        'message': str(e),
        'traceback': traceback.format_exc(chain=False).split('\n')
    }
