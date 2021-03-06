from aiohttp import web

from conf import settings
from transaction.transaction import get_current_sequence_number


async def get_current_tx_sequence_from_request(request: web.Request) -> web.Response:
    """Get current sequence number of the wallet"""
    wallet_address: str = request.match_info.get('wallet_address')
    sequence = await get_current_sequence_number(wallet_address)

    if sequence is None:
        msg = (
            f'Not found current sequence of wallet address \'{wallet_address}\', Please ensure wallet address is valid.'
        )
        raise web.HTTPNotFound(reason=msg)
    return web.json_response({'current_sequence': sequence})
