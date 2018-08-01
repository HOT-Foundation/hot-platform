import json
import logging
import traceback
from datetime import datetime

from aiohttp import web


@web.middleware
async def handle_log(request, handler):
    start_time = datetime.utcnow()
    response = await handler(request)
    write_access_log(request, response, start_time)

    if response.status != 200 and response.text:
        body = json.loads(response.text)
        error_message = body.get('message') or body.get('error')
        traceback = '\n'.join(body.get('traceback')) if body.get(
            'traceback') else None
        if error_message and traceback:
            write_error_log(error_message, traceback)
    return response


def write_access_log(request, response, time):
    request_name = request.path_qs
    if request_name == '/metrics':
        return None

    now = datetime.utcnow()
    diff_time = now - time
    diff_time_seconds = diff_time.total_seconds()

    user_agent = request.headers.get('User-Agent', '-')
    referer = request.headers.get('Referer', '-')
    logger = logging.getLogger('aiohttp.access.custom')
    logger.info(f'{request.remote} "{request.method} {request.path_qs} HTTP/{request.version.major}.{request.version.minor}" "{referer}" "{user_agent}" "{response.status}" {diff_time_seconds} seconds')


def write_error_log(error_message, traceback_stack):
    logger = logging.getLogger('aiohttp.server')
    logger.error(error_message)
    logger.error(traceback_stack)


def format_error(e):
    return {
        'message': str(e),
        'traceback': traceback.format_exc(chain=False).split('\n')
    }


def write_audit_log(request, response, operation, message):
    user_agent = request.headers.get('User-Agent', '-')
    referer = request.headers.get('Referer', '-')

    logger = logging.getLogger('audit')
    log_message = f'{operation} {request.remote} {request.method} {request.path_qs} {referer} {user_agent} : {message}'
    logger.info(log_message)