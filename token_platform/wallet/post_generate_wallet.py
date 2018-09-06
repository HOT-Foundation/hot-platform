import binascii
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError

from aiohttp import web
from conf import settings
from router import reverse
from transaction.transaction import get_signers
from wallet.wallet import (build_generate_wallet_transaction, get_wallet_async,
                           wallet_address_is_duplicate)

async def post_generate_wallet_from_request(request: web.Request):
    """Aiohttp Request wallet address to get create wallet transaction."""
    try:
        json_response = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='Bad request, JSON data missing.')

    source_address: str = request.match_info.get('wallet_address')

    destination_address: str = json_response['target_address']

    transaction_source_address: str = json_response['transaction_source_address']
    try:
        balance: Decimal = Decimal(json_response.get('amount_xlm', 0))
    except InvalidOperation:
        raise web.HTTPBadRequest(reason = f"{json_response.get('amount_xlm')} is not decimal type")

    if balance == 0:
        raise web.HTTPBadRequest(reason = 'Balance must have more than 0.')

    duplicate = await wallet_address_is_duplicate(destination_address)
    if duplicate:
        raise web.HTTPBadRequest(reason = 'Target address is already used.')

    #Don't move this line below build_generate_wallet_transaction otherwise it will be very slow.
    signers = await get_signers(source_address)

    wallet = await get_wallet_async(transaction_source_address)
    unsigned_xdr_byte, tx_hash_byte = build_generate_wallet_transaction(transaction_source_address, source_address, destination_address, balance, sequence=wallet.sequence)

    unsigned_xdr: str = unsigned_xdr_byte.decode()
    tx_hash: str = binascii.hexlify(tx_hash_byte).decode()

    host: str = settings['HOST']

    result = {
        'source_address': source_address,
        'signers': signers,
        'xdr': unsigned_xdr,
        'transaction_url': f"{host}{reverse('transaction', transaction_hash=tx_hash)}",
        'transaction_hash': tx_hash,
        '@id': f'{host}{request.path}'
    }

    return web.json_response(result)
