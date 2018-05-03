import binascii
from functools import reduce
from typing import Any, Dict, List, Mapping, NewType, Optional, Union

import requests
from aiohttp import web
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError

from conf import settings
from wallet.wallet import (build_create_wallet_transaction,
                           wallet_address_is_duplicate)


async def post_create_wallet_from_request(request: web.Request):
    """Aiohttp Request wallet address to get create wallet transaction."""
    json_response = await request.json()
    destination_address: str = json_response.get('target_address', None)
    source_address: str = json_response.get('wallet_address', None)
    balance: int = int(json_response.get('starting_balance', 0))

    if destination_address is None or balance == 0:
        raise web.HTTPBadRequest(reason = 'Bad request, parameter missing.')

    duplicate = wallet_address_is_duplicate(destination_address)
    if duplicate:
        raise web.HTTPBadRequest(reason = 'Target address is already used.')

    unsigned_xdr_byte, tx_hash_byte = build_create_wallet_transaction(source_address, destination_address, balance)

    unsigned_xdr: str = unsigned_xdr_byte.decode()
    tx_hash: str = binascii.hexlify(tx_hash_byte).decode()

    signers: List[str] = [source_address, destination_address]
    host: str = settings['HOST']

    result = {
        'source_address': source_address,
        'signers': signers,
        'unsigned_xdr': unsigned_xdr,
        'transaction_url': f'{host}/transaction/{tx_hash}',
        '@url': f'{host}{request.path_qs}'
    }

    return web.json_response(result)
