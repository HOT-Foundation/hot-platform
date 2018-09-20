import binascii
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from aiohttp import web
from stellar_base.builder import Builder

from conf import settings
from router import reverse
from transaction.transaction import get_signers, get_threshold_weight
from wallet.wallet import get_wallet
from stellar.wallet import get_stellar_wallet


async def get_unsigned_add_trust_and_htkn_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    source_account = request.match_info.get("wallet_address", "")
    transaction_source_address = request.query['transaction-source-address']
    htkn_amount = request.query['htkn_amount']
    try:
        htkn_amount = Decimal(htkn_amount)
    except InvalidOperation:
        raise web.HTTPBadRequest(reason='htkn_amount cannot convert to decimal.')

    trust = await does_wallet_have_trust(source_account)
    if trust:
        raise web.HTTPBadRequest(reason='Wallet already has trust.')

    result = await get_unsigned_add_trust_and_htkn(source_account, transaction_source_address, htkn_amount)
    return web.json_response(result)


async def does_wallet_have_trust(wallet_address: str) -> bool:
    """Check address ID is not duplicate"""
    try:
        wallet = await get_wallet(wallet_address)
        if (
            len(
                list(
                    filter(
                        lambda b: b.get('asset_code', None) == settings['ASSET_CODE']
                        and b.get('asset_issuer', None) == settings['ISSUER'],
                        wallet.balances,
                    )
                )
            )
            == 0
        ):
            return False
        return True
    except (web.HTTPNotFound):
        return False


async def get_unsigned_add_trust_and_htkn(
    source_address: str, transaction_source_address: str, htkn_amount: Decimal
) -> Dict:
    """Get unsigned transfer transaction and signers"""
    wallet = await get_stellar_wallet(transaction_source_address)
    unsigned_xdr, tx_hash = await build_unsigned_add_trust_and_htkn(
        source_address, transaction_source_address, htkn_amount, wallet.sequence
    )
    host: str = settings['HOST']
    result = {
        '@id': reverse('change-trust', wallet_address=source_address),
        '@transaction_url': reverse('transaction', transaction_hash=tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'change-trust'),
        'signers': await get_signers(source_address),
        'xdr': unsigned_xdr,
        'transaction_hash': tx_hash,
    }
    return result


async def build_unsigned_add_trust_and_htkn(
    source_address: str, transaction_source_address: str, htkn_amount: Decimal, sequence: str = None
) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: address need to be trust HOT and address for getting HOT
    """
    builder = Builder(
        address=transaction_source_address,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
        sequence=sequence,
    )
    builder.append_trust_op(
        settings['ISSUER'], settings['ASSET_CODE'], source=source_address, limit=settings['LIMIT_ASSET']
    )

    if htkn_amount > 0:
        builder.append_payment_op(
            source=transaction_source_address,
            destination=source_address,
            asset_code=settings['ASSET_CODE'],
            asset_issuer=settings['ISSUER'],
            amount=htkn_amount,
        )

    try:
        unsigned_xdr = builder.gen_xdr()
        tx_hash = builder.te.hash_meta()
    except Exception as ex:
        raise web.HTTPNotFound(text=str(ex))
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()


async def get_unsigned_change_trust_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    source_account = request.match_info.get("wallet_address", "")
    transaction_source_address = request.query['transaction-source-address']

    result = await get_unsigned_change_trust(source_account, transaction_source_address)
    return web.json_response(result)


async def get_unsigned_change_trust(source_address: str, transaction_source_address: str) -> Dict:
    """Get unsigned transfer transaction and signers"""
    wallet = await get_stellar_wallet(transaction_source_address)
    unsigned_xdr, tx_hash = build_unsigned_change_trust(source_address, transaction_source_address, wallet.sequence)
    host: str = settings['HOST']
    result = {
        '@id': reverse('change-trust', wallet_address=source_address),
        '@transaction_url': reverse('transaction', transaction_hash=tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'change-trust'),
        'signers': await get_signers(source_address),
        'xdr': unsigned_xdr,
        'transaction_hash': tx_hash,
    }
    return result


def build_unsigned_change_trust(
    source_address: str, transaction_source_address: str, sequence: str = None
) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: address need to be trust HOT
    """
    builder = Builder(
        address=transaction_source_address,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
        sequence=sequence,
    )
    builder.append_trust_op(
        settings['ISSUER'], settings['ASSET_CODE'], source=source_address, limit=settings['LIMIT_ASSET']
    )

    try:
        unsigned_xdr = builder.gen_xdr()
        tx_hash = builder.te.hash_meta()
    except Exception as ex:
        raise web.HTTPNotFound(text=str(ex))

    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
