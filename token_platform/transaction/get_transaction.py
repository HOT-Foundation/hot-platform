from aiohttp import web, web_request, web_response
from conf import settings
from transaction.transaction import get_transaction, get_transaction_hash


async def get_transaction_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request transaction hash to get transaction detail"""
    tx_hash = request.match_info.get('transaction_hash', "")
    result = await get_transaction(tx_hash)
    return web.json_response(result)


async def get_transaction_hash_from_request(request: web.Request) -> web.Response:
    """Get transaction hash by wallet address and idempotency key in memo."""
    address = request.match_info.get('wallet_address')
    meta = request.rel_url.query['meta']
    status = 200

    result = await get_transaction_hash(address, meta)
    if not result:
        status = 400

    return web.json_response({'transaction_hash' : result}, status=status)
