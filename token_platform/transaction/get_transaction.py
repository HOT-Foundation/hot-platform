from typing import Dict

from aiohttp import web, web_request, web_response
from conf import settings
from transaction.transaction import (get_transaction,
                                     get_transaction_hash,
                                     get_transaction_by_memo)


async def get_transaction_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request transaction hash to get transaction detail"""
    tx_hash = request.match_info.get('transaction_hash', "")
    result = await get_transaction(tx_hash)
    return web.json_response(result)


async def get_transaction_hash_from_request(request: web.Request) -> web.Response:
    """Get transaction hash by wallet address and idempotency key in memo."""
    address = request.match_info.get('wallet_address')
    memo = request.rel_url.query['memo']
    status = 200

    result = await get_transaction_hash(address, memo)
    if not result:
        status = 404
        result= 'Not Found'

    return web.json_response({'transaction_hash' : result}, status=status)


async def get_transaction_hash_from_memo_from_reqeust(request: web.Request) -> web.Response:
    """AIOHttp Request transaction hash from memo"""
    address = request.match_info.get('wallet_address')
    memo = request.match_info.get('memo')
    transaction = await get_transaction_by_memo(address, memo)

    return web.json_response(transaction)
