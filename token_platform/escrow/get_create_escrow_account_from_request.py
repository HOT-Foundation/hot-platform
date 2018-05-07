from typing import Dict, List

from aiohttp import web
from escrow.generate_account_xdr import get_unsigned_generate_wallet_xdr


async def get_create_account_and_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    body = await request.json()
    stellar_escrow_address = body.get('stellar_escrow_address', None)
    stellar_merchant_address = body.get('stellar_merchant_address', None)
    stellar_hotnow_address = body.get('stellar_hotnow_address', None)
    starting_banace = body.get('starting_balance', None)
    exp_date = body.get('expriring_date', None)
    cost_per_tx = body.get('cost_per_tx', None)

    result = {
        "create_account": await get_unsigned_generate_wallet_xdr(
            stellar_escrow_address,
            stellar_merchant_address,
            stellar_hotnow_address,
            starting_banace,
            exp_date,
            cost_per_tx
        ),
        "pre_signed_tx": await get_presigned_tx_xdr(
            stellar_escrow_address,
            stellar_merchant_address,
            stellar_hotnow_address,
            starting_banace,
            exp_date,
            cost_per_tx
        )
    }

    return web.json_response(result)


async def get_presigned_tx_xdr(stellar_escrow_address:str,
            stellar_merchant_address:str,
            stellar_hotnow_address:str,
            starting_banace:int,
            exp_date:str,
            cost_per_tx:int
        ) -> List:

    return []
