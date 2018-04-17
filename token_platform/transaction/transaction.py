from typing import Dict

from aiohttp import web, web_exceptions, web_request, web_response
from stellar_base.horizon import horizon_livenet, horizon_testnet
from stellar_base.transaction import Transaction
from stellar_base.transaction_envelope import TransactionEnvelope as Te

from conf import settings


async def submit_transaction(xdr: bytes) -> Dict[str, str]:
    horizon = horizon_livenet(
    ) if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    try:
        response = horizon.submit(xdr)
    except Exception as e:
        raise web_exceptions.HTTPServerError(reason=str(e))
    if response['status'] == 400:
        raise web_exceptions.HTTPBadRequest()
    if response['status'] != 200:
        raise web_exceptions.HTTPServerError()
    return response


async def submit_transaction_from_request(request: web_request.Request) -> web_response.Response:
    signed_xdr = await request.text()
    tx_hash = request.match_info['transaction_hash']
    result = {'message': 'transaction success.'}
    if not signed_xdr or not tx_hash:
        return web.json_response({'message': 'transaction fail, please check your parameter.'}, status=400)
    response = await submit_transaction(signed_xdr)
    return web.json_response(result) if (response['status'] == 200) else web.json_response(web_exceptions.HTTPServerError)
