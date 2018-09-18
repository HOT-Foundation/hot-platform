import binascii
from functools import reduce
from typing import Any, Dict, List, Mapping, NewType, Optional, Union

import requests
from json import JSONDecodeError
from aiohttp import web
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from decimal import Decimal, InvalidOperation
from conf import settings
from router import reverse
from wallet.wallet import (build_generate_trust_wallet_transaction,  get_wallet,
                           wallet_address_is_duplicate)


async def post_generate_trust_wallet_from_request(request: web.Request):
    """Aiohttp Request wallet address to get create wallet transaction."""
    try:
        json_response = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='Bad request, JSON data missing.')

    source_address: str = request.match_info.get('wallet_address')

    destination_address: str = json_response['target_address']

    transaction_source_address: str = json_response['transaction_source_address']

    try:
        xlm_amount: Decimal = Decimal(json_response.get('xlm_amount', 0))
    except InvalidOperation:
        raise web.HTTPBadRequest(reason = f"{json_response.get('xlm_amount')} is not decimal type")

    if xlm_amount == 0:
        raise web.HTTPBadRequest(reason = 'XLM balance must have more than 0.')

    try:
        htkn_amount: Decimal = Decimal(json_response.get('htkn_amount', 0))
    except InvalidOperation:
        raise web.HTTPBadRequest(reason = f"{json_response.get('htkn_amount')} is not decimal type")

    duplicate = await wallet_address_is_duplicate(destination_address)
    if duplicate:
        raise web.HTTPBadRequest(reason = 'Target address is already used.')

    wallet = await get_wallet(transaction_source_address)
    unsigned_xdr_byte, tx_hash_byte = build_generate_trust_wallet_transaction(transaction_source_address, source_address, destination_address, xlm_amount, htkn_amount, sequence=wallet.sequence)

    unsigned_xdr: str = unsigned_xdr_byte.decode()
    tx_hash: str = binascii.hexlify(tx_hash_byte).decode()

    signers: List[str] = []
    if (source_address == transaction_source_address):
        signers = [source_address, destination_address]
    else:
        signers = [source_address, destination_address, transaction_source_address]

    host: str = settings['HOST']

    result = {
        'source_address': source_address,
        'transaction_source_address': transaction_source_address,
        'signers': signers,
        'xdr': unsigned_xdr,
        'transaction_url': reverse('transaction', transaction_hash=tx_hash),
        'transaction_hash': tx_hash,
        '@id': reverse('generate-trust-wallet', wallet_address=source_address)
    }

    return web.json_response(result)