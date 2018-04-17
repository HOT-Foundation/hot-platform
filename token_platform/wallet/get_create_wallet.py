from functools import reduce
from typing import Any, Dict, List, Mapping, NewType, Optional, Union

from aiohttp import web

import requests
from conf import settings
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError
from wallet.wallet import (build_create_wallet_transaction,
                           wallet_address_is_duplicate)


async def get_create_wallet_from_request(request: web.Request):
    """Aiohttp Request wallet address to get create wallet transaction."""
    try:
        source_address = request.match_info['wallet_address']
    except KeyError:
        raise web.HTTPBadRequest

    queries = request.query
    destination_address: str = queries.get('target', None)
    amount: int = int(queries.get('starting_amount', 0))

    if destination_address is None or source_address is None or amount == 0:
        return web.json_response({'error': 'Please check your parameter type.'}, status=404)

    duplicate = wallet_address_is_duplicate(destination_address)
    if duplicate:
        raise ValueError('Wallet ID of new wallet is duplicate.')

    unsigned_xdr, tx_hash = build_create_wallet_transaction(source_address, destination_address, amount)

    signers: List[str] = [source_address, destination_address]
    host: str = settings['HOST']
    result = {
        'id': source_address,
        'signers': signers,
        'unsigned_xdr': unsigned_xdr,
        'transaction_url': f'{host}/transaction/{tx_hash}'
    }

    return web.json_response(result)
