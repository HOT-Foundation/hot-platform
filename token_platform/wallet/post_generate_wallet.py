import binascii
from functools import reduce
from typing import Any, Dict, List, Mapping, NewType, Optional, Union

import requests
from json import JSONDecodeError
from aiohttp import web
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder

from conf import settings
from router import reverse
from wallet.wallet import (build_generate_wallet_transaction,
                           wallet_address_is_duplicate)


async def post_generate_wallet_from_request(request: web.Request):
    """Aiohttp Request wallet address to get create wallet transaction."""
    try:
        json_response = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='Bad request, JSON data missing.')

    source_address: str = request.match_info.get('wallet_address')

    destination_address: str = json_response['target_address']
    balance: int = int(json_response.get('starting_balance', 0))

    if balance == 0:
        raise web.HTTPBadRequest(reason = 'Balance must have more than 0.')

    duplicate = wallet_address_is_duplicate(destination_address)
    if duplicate:
        raise web.HTTPBadRequest(reason = 'Target address is already used.')

    unsigned_xdr_byte, tx_hash_byte = build_generate_wallet_transaction(source_address, destination_address, balance)

    unsigned_xdr: str = unsigned_xdr_byte.decode()
    tx_hash: str = binascii.hexlify(tx_hash_byte).decode()

    signers: List[str] = [source_address, destination_address]
    host: str = settings['HOST']

    result = {
        'source_address': source_address,
        'signers': signers,
        'xdr': unsigned_xdr,
        'transaction_url': f"{host}{reverse('transaction', transaction_hash=tx_hash)}",
        'transaction_hash': tx_hash,
        '@url': f'{host}{request.path}'
    }

    return web.json_response(result)
