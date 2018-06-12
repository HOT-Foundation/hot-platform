from datetime import datetime, timezone

from aiohttp import web
from dateutil import parser
from stellar_base import address
from stellar_base.horizon import horizon_livenet, horizon_testnet

from conf import settings
from router import reverse


async def get_wallet_history_from_request(request: web.Request) -> web.Response:
    """Get wallet history"""
    wallet_address = request.match_info.get('wallet_address', "")
    limit = request.query.get('limit', 10)
    type = request.query['type']
    sort = request.query.get('sort', 'DESC')
    offset = request.query.get('offset')
    start_date = request.query.get('start-date')
    end_date = request.query.get('end-date')

    if not(sort == 'ASC' or sort == 'DESC'):
        raise web.HTTPBadRequest(reason=f'Invalid. Parameter sort.')

    def _datetime_is_valid(value: str) -> datetime:

        date_time = None
        try:
            date_time = parser.isoparse(value) # type: ignore
        except ValueError as ex:
            raise web.HTTPBadRequest(reason=f'Invalid. Parameter date time is in wrong format.')

        timezone_offset = date_time.utcoffset()
        if timezone_offset is None:
            raise web.HTTPBadRequest(reason=f'Invalid. Parameter date time doesn\'t timezone.')

        return date_time

    if start_date:
        start_date = _datetime_is_valid(start_date)
        start_date = start_date.astimezone(tz=timezone.utc)

    if end_date:
        end_date = _datetime_is_valid(end_date)
        end_date = end_date.astimezone(tz=timezone.utc)

    #get_wallet_history()

    return web.json_response(status=200)

async def get_wallet_history(self):

    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    pass
