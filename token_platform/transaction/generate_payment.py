import binascii
from decimal import Decimal
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.horizon import horizon_livenet, horizon_testnet
from stellar_base.utils import AccountNotExistError

from aiohttp import web
from conf import settings
from transaction.transaction import get_signers, get_threshold_weight, get_transaction_by_memo
from wallet.wallet import get_wallet


async def generate_payment_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""

    body = await request.json()
    source_account = request.match_info.get("wallet_address", "")
    target_address = body['target_address']
    amount_htkn = body.get('amount_htkn')
    amount_xlm = body.get('amount_xlm')
    sequence_number = body.get('sequence_number', None)
    meta = body.get('meta', None)
    await get_wallet(source_account)

    if meta:
        url_get_transaction = await get_transaction_by_memo(source_account, meta)
        if url_get_transaction:
            return web.json_response(url_get_transaction, status=400)

    result = await generate_payment(source_account, target_address, amount_htkn, amount_xlm, sequence_number, meta)
    return web.json_response(result)

async def generate_payment(source_address: str, destination: str, amount_htkn: Decimal, amount_xlm:Decimal, sequence:int = None, meta:str = None) -> Dict:
    """Get unsigned transfer transaction and signers

        Args:
            source_address: Owner of operation
            destination_address: address of receiveing wallet
            amount_htkn: amount of HoToken that would be transferred
            amount_xlm: amount of XLM that would be transferred
            sequence: sequence number for generate transaction [optional]
            meta: memo text [optional]
    """
    unsigned_xdr, tx_hash = await build_unsigned_transfer(source_address, destination, amount_htkn, amount_xlm, sequence, meta)
    host: str = settings['HOST']
    result = {
        '@id': source_address,
        '@url': '{}/wallet/{}/generate-payment'.format(host, source_address),
        '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'payment'),
        'signers': await get_signers(source_address),
        'unsigned_xdr': unsigned_xdr,
        'transaction_hash': tx_hash
    }
    return result


async def build_unsigned_transfer(source_address: str, destination_address: str, amount_htkn: Decimal, amount_xlm: Decimal, sequence:int=None, memo_text:str=None) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of operation
            destination_address: wallet id of new wallet
            amount_htkn: amount of htkn that would be transfer
            amount_xlm: amount of xlm that would be transfer
            sequence: sequence number for generate transaction [optional]
            meta: memo text [optional]
    """

    builder = Builder(address=source_address, network=settings['STELLAR_NETWORK'], sequence=sequence)

    wallet = StellarAddress(address=destination_address, network=settings['STELLAR_NETWORK'])
    try:
        wallet.get()
        if amount_xlm:
            builder.append_payment_op(destination_address, amount_xlm, source=source_address)
    except AccountNotExistError as e:
        builder.append_create_account_op(source=source_address, destination=destination_address, starting_balance=amount_xlm)

    if amount_htkn:
        builder.append_payment_op(
            destination_address, amount_htkn, asset_type=settings['ASSET_CODE'], asset_issuer=settings['ISSUER'], source=source_address
        )

    if memo_text:
        builder.add_text_memo(memo_text)

    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
