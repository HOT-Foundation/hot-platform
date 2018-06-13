from datetime import datetime, timezone

from aiohttp import web
from dateutil import parser
from stellar_base.address import Address
from stellar_base.horizon import HORIZON_LIVE, HORIZON_TEST

from conf import settings
from router import reverse


async def get_wallet_history_from_request(request: web.Request) -> web.Response:
    """Get wallet history"""
    wallet_address = request.match_info.get('wallet_address', "")
    limit = request.query.get('limit', 10)
    type = request.query.get('type')
    sort = request.query.get('sort', 'asc')
    offset = request.query.get('offset')
    start_date = request.query.get('start-date')
    end_date = request.query.get('end-date')

    if not(sort == 'asc' or sort == 'desc'):
        raise web.HTTPBadRequest(reason=f'Invalid. Parameter sort.')

    if start_date:
        start_date = datetime_is_valid(start_date)
        start_date = start_date.astimezone(tz=timezone.utc)

    if end_date:
        end_date = datetime_is_valid(end_date)
        end_date = end_date.astimezone(tz=timezone.utc)

    history = await get_wallet_history(wallet_address, sort, limit, offset)
    result = await format_history(history)

    return web.json_response(result)

def datetime_is_valid(value: str) -> datetime:

    date_time = None
    try:
        date_time = parser.isoparse(value) # type: ignore
    except ValueError as ex:
        raise web.HTTPBadRequest(reason=f'Invalid. Parameter date time is in wrong format.')

    timezone_offset = date_time.utcoffset()
    if timezone_offset is None:
        raise web.HTTPBadRequest(reason=f'Invalid. Parameter date time doesn\'t timezone.')

    return date_time

async def get_wallet_history(wallet_address: str, sort: str='asc', limit: int=10, offset: str=None) -> dict:
    """
        Get wallet history from Stellar network.
    """

    horizon = HORIZON_TEST
    if settings['STELLAR_NETWORK'] == 'PUBLIC':
        horizon = HORIZON_LIVE

    params = { 'order': sort, 'limit': limit}
    if offset:
        params['cursor'] = offset
    address = Address(address=wallet_address, horizon=horizon)
    effects = address.effects(**params)
    return effects

async def format_history(history: dict)-> list:


    def _format_record(record):
        result = record
        result.pop('_links', None)
        result.pop('type_i', None)
        result['offset'] = result.pop('paging_token', None)
        result['address'] = result.pop('account', None)
        return result


    records = [_format_record(record) for record in history['_embedded']['records']]
    return records
