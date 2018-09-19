from decimal import Decimal
from typing import Tuple

from aiohttp import web
from stellar_base.builder import Builder
from stellar_base.exceptions import AccountNotExistError, HorizonError
from stellar_base.utils import DecodeError

from conf import settings
from stellar.wallet import Wallet, get_stellar_wallet


async def get_wallet(wallet_address: str) -> Wallet:
    """Get wallet from stellar address"""
    try:
        wallet = await get_stellar_wallet(wallet_address)
    except (web.HTTPNotFound) as ex:
        msg = "{}: {}".format(str(ex), wallet_address)
        raise web.HTTPNotFound(reason=msg)
    return wallet


async def wallet_address_is_duplicate(destination_address: str) -> bool:
    """Check address ID is not duplicate"""
    try:
        wallet = await get_wallet(destination_address)
        return True
    except (web.HTTPNotFound) as ex:
        return False
    return True


def build_generate_trust_wallet_transaction(
    transaction_source_address: str,
    source_address: str,
    destination_address: str,
    xlm_amount: Decimal,
    htkn_amount: Decimal = Decimal(0),
    sequence=None,
) -> Tuple[bytes, bytes]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            transaction_source_address: Owner of a transaction.
            source_address: Owner of creator address and payment operations.
            destination_address: wallet id of new wallet.
            xlm_amount: starting xlm_balance of new wallet.
            htkn_amount: starting htkn_balance of new wallet.
    """
    builder = Builder(
        address=transaction_source_address,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
        sequence=sequence,
    )
    builder.append_create_account_op(
        source=source_address, destination=destination_address, starting_balance=xlm_amount
    )
    try:
        builder.append_trust_op(
            source=destination_address,
            destination=settings['ISSUER'],
            code=settings['ASSET_CODE'],
            limit=settings['LIMIT_ASSET'],
        )
    except DecodeError:
        raise web.HTTPBadRequest(reason='Parameter values are not valid.')
    except Exception as e:
        msg = str(e)
        raise web.HTTPInternalServerError(reason=msg)

    if htkn_amount > 0:
        builder.append_payment_op(
            source=source_address,
            destination=destination_address,
            asset_code=settings['ASSET_CODE'],
            asset_issuer=settings['ISSUER'],
            amount=htkn_amount,
        )

    try:
        unsigned_xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()

    return unsigned_xdr, tx_hash


def build_generate_wallet_transaction(
    transaction_source_address: str, source_address: str, destination_address: str, amount: Decimal, sequence=None
) -> Tuple[bytes, bytes]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            transaction_source_address: Owner of the transactoin
            source_address: Owner of creator wallet
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
    """

    builder = Builder(
        address=transaction_source_address,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
        sequence=sequence,
    )

    try:
        builder.append_create_account_op(
            source=source_address, destination=destination_address, starting_balance=amount
        )
    except DecodeError:
        raise web.HTTPBadRequest(reason='Parameter values are not valid.')
    except Exception as e:
        msg = str(e)
        raise web.HTTPInternalServerError(reason=msg)

    try:
        unsigned_xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()

    return unsigned_xdr, tx_hash
