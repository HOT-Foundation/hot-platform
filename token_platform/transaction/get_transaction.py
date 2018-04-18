from aiohttp import web, web_request, web_response
from conf import settings
from transaction.transaction import get_transaction


async def get_transaction_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request transaction hash to get transaction detail"""
    tx_hash = request.match_info.get('transaction_hash', "")
    return await get_transaction(tx_hash)
