from aiohttp import web
from stellar_base.horizon import horizon_livenet, horizon_testnet

from conf import settings
from transaction.transaction import get_next_sequence_number


async def get_next_tx_sequence_from_request(request: web.Request) -> web.Response:
    """Get next available sequence number of the wallet"""
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()

    wallet_address: str = request.match_info.get('wallet_address')

    if wallet_address is None:
        raise ValueError('Bad request, url is not value.')
    sequence = await get_next_sequence_number(wallet_address)
    return web.json_response({'next_sequence': sequence})
