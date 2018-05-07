from typing import Dict, List

from aiohttp import web
from stellar_base.builder import Builder

from conf import settings


async def create_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    body = await request.json()
    stellar_escrow_address = body.get('stellar_escrow_address', None)
    stellar_merchant_address = body.get('stellar_merchant_address', None)
    stellar_hotnow_address = body.get('stellar_hotnow_address', None)
    starting_banace = body.get('starting_balance', None)
    exp_date = body.get('expriring_date', None)
    cost_per_tx = body.get('cost_per_tx', None)
    result = get_unsigned_generate_wallet_xdr(stellar_escrow_address,
        stellar_merchant_address,
        stellar_hotnow_address,
        starting_banace,
        exp_date,
        cost_per_tx
    )
    return web.json_response(result)

async def get_unsigned_generate_wallet_xdr(stellar_escrow_address:str,
            stellar_merchant_address:str,
            stellar_hotnow_address:str,
            starting_banace:int,
            exp_date:str,
            cost_per_tx:int
        ) -> Dict:
    '''Building transaction for generating escrow account with minimum balance of lumens

        Args:

        * stellar_escrow_address: an address of escrow account
        * stellar_merchant_address: an address of merchant account
        * stellar_hotnow_address: an address of hotnow account
        * starting_banace: starting amount of HTKN balance
        * exp_date: a date when the escrow account is no longer available in formate (dd/mm/yyyy)
        * cost_per_tx: amount of HTKN when submitting transaction
    '''

    return {}
