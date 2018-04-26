from aiohttp import web


async def get_create_account_and_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    body = await request.json()
    stellar_escrow_address = body.get('stellar_escrow_address', None)
    stellar_merchant_address = body.get('stellar_merchant_address', None)
    stellar_hotnow_address = body.get('stellar_hotnow_address', None)
    starting_banace = body.get('starting_balance', None)
    exp_date = body.get('expriring_date', None)
    cost_per_tx = body.get('cost_per_tx', None)

    return web.json_response(body)