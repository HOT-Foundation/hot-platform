from typing import Dict

from aiohttp import web
from stellar_base.horizon import horizon_livenet, horizon_testnet
from stellar_base.transaction import Transaction
from stellar_base.transaction_envelope import TransactionEnvelope as Te

from conf import settings

async def is_duplicate_transaction(transaction_hash: str) -> bool:
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    transaction = horizon.transaction(transaction_hash)
    id = transaction.get('id')
    return True if id else False

async def submit_transaction(xdr: bytes) -> Dict[str, str]:
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    try:
        response = horizon.submit(xdr)
    except Exception as e:
        raise web.HTTPInternalServerError
    if response['status'] == 400:
        raise web.HTTPBadRequest
    if response['status'] != 200:
        raise web.HTTPInternalServerError
    return response


async def put_transaction_from_request(request: web.Request) -> web.Response:

    signed_xdr = await request.text()
    tx_hash = request.match_info['transaction_hash']
    result = {'message': 'transaction success.'}

    if await is_duplicate_transaction(tx_hash):
        raise web.HTTPBadRequest(reason='Duplicate transaction.')

    if not signed_xdr or not tx_hash:
        raise web.HTTPBadRequest(reason='transaction fail, please check your parameter.')

    response = await submit_transaction(signed_xdr)
    return web.json_response(result)
