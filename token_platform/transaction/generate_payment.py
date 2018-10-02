import binascii
from decimal import Decimal
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from stellar_base.builder import Builder
from stellar_base.utils import DecodeError, decode_check

from aiohttp import web
from conf import settings
from router import reverse
from transaction.transaction import get_signers, get_threshold_weight, get_transaction_by_memo
from wallet.get_wallet import get_wallet_detail
from wallet.wallet import get_wallet


async def generate_payment_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""

    body = await request.json()
    source_account = request.match_info.get("wallet_address", "")
    transaction_source_address = body['transaction_source_address']
    target_address = body['target_address']
    amount_htkn = body.get('amount_htkn')
    amount_xlm = body.get('amount_xlm')
    tax_amount_htkn = body.get('tax_amount_htkn', None)
    sequence_number = body.get('sequence_number', None)
    memo = body.get('memo', None)
    memo_on = body.get('memo_on', 'source')
    await get_wallet(source_account)

    if memo_on not in ['destination', 'source']:
        raise web.HTTPBadRequest(
            reason='memo_on should be only "source" or "destination"')

    try:
        decode_check('account', target_address)
    except DecodeError as e:
        raise web.HTTPBadRequest(
            reason='Invalid value : {}'.format(target_address))

    if memo:
        focus_address = target_address if memo_on == 'destination' else source_account
        url_get_transaction = await get_transaction_by_memo(focus_address, memo)
        if url_get_transaction:
            raise web.HTTPBadRequest(reason="Transaction is already submitted")
    result = await generate_payment(
        transaction_source_address, source_account, target_address, amount_htkn, amount_xlm, tax_amount_htkn, sequence_number, memo
    )
    return web.json_response(result)


async def generate_payment(
    transaction_source_address: str,
    source_address: str,
    destination: str,
    amount_htkn: Decimal,
    amount_xlm: Decimal,
    tax_amount_htkn: Decimal = None,
    sequence: int = None,
    memo: str = None
) -> Dict:
    """Get unsigned transfer transaction and signers

        Args:
            source_address: Owner of operation
            destination_address: address of receiveing wallet
            amount_htkn: amount of HoToken that would be transferred
            amount_xlm: amount of XLM that would be transferred
            sequence: sequence number for generate transaction [optional]
            memo: memo text [optional]
    """
    unsigned_xdr, tx_hash = await build_unsigned_transfer(
        transaction_source_address, source_address, destination, amount_htkn, amount_xlm, tax_amount_htkn, sequence, memo
    )
    host: str = settings['HOST']
    result = {
        '@id': reverse('generate-payment', wallet_address=source_address),
        '@transaction_url': reverse('transaction', transaction_hash=tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'payment'),
        'signers': await get_signers(source_address),
        'xdr': unsigned_xdr,
        'transaction_hash': tx_hash,
    }
    return result


async def build_unsigned_transfer(
    transaction_source_address: str,
    source_address: str,
    destination_address: str,
    amount_htkn: Decimal,
    amount_xlm: Decimal,
    tax_amount_htkn: Decimal = None,
    sequence: int = None,
    memo_text: str = None
) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of operation
            destination_address: wallet id of new wallet
            amount_htkn: amount of htkn that would be transfer
            amount_xlm: amount of xlm that would be transfer
            sequence: sequence number for generate transaction [optional]
            memo: memo text [optional]
    """
    builder = Builder(
        address=transaction_source_address,
        sequence=sequence,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
    )

    wallet = await get_wallet_detail(destination_address)
    if amount_xlm:
        builder.append_payment_op(
            destination_address, amount_xlm, source=source_address)
    if amount_htkn and wallet['asset'].get(settings['ASSET_CODE'], False):
        builder.append_payment_op(
            destination_address,
            amount_htkn,
            asset_code=settings['ASSET_CODE'],
            asset_issuer=settings['ISSUER'],
            source=source_address,
        )
    if tax_amount_htkn and tax_amount_htkn > 0:
        builder.append_payment_op(
            settings['TAX_COLLECTOR_ADDRESS'], tax_amount_htkn, source=source_address)

    if amount_htkn and not wallet['asset'].get(settings['ASSET_CODE'], False):
        raise web.HTTPBadRequest(reason="{} is not trusted {}".format(
            destination_address, settings['ASSET_CODE']))

    if memo_text:
        builder.add_text_memo(memo_text)

    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
