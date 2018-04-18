from transaction.transaction import is_duplicate_transaction, submit_transaction
from aiohttp import web

async def put_transaction_from_request(request: web.Request) -> web.Response:
    signed_xdr = await request.text()
    tx_hash = request.match_info.get('transaction_hash')

    if not signed_xdr or not tx_hash:
        raise web.HTTPBadRequest(reason='transaction fail, please check your parameter.')

    result = {'message': 'transaction success.'}

    if await is_duplicate_transaction(tx_hash):
        raise web.HTTPBadRequest(reason='Duplicate transaction.')

    response = await submit_transaction(signed_xdr)
    return web.json_response(result)