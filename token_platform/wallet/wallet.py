from typing import Tuple

from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError, DecodeError

from aiohttp import web
from conf import settings
from decimal import Decimal


async def get_wallet(wallet_address: str) -> StellarAddress:
    """Get wallet from stellar address"""
    wallet = StellarAddress(address=wallet_address, network=settings['STELLAR_NETWORK'])

    try:
        wallet.get()
    except AccountNotExistError as ex:
        msg = "{}: {}".format(str(ex), wallet_address)
        raise web.HTTPNotFound(reason=msg)
    return wallet


def wallet_address_is_duplicate(destination_address: str) -> bool:
    """Check address ID is not duplicate"""
    wallet = StellarAddress(address=destination_address,
                            network=settings['STELLAR_NETWORK'])

    try:
        wallet.get()
        return True
    except (AccountNotExistError):
        return False
    except (ValueError):
        return True


def build_generate_trust_wallet_transaction(transaction_source_address: str, source_address: str, destination_address: str, amount: Decimal) -> Tuple[bytes, bytes]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of creator address
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
    """
    builder = Builder(address=transaction_source_address, horizon=settings['LOCAL_HORIZON'], network=settings['LOCAL_PASSPHRASE'])
    builder.append_create_account_op(
        source=source_address, destination=destination_address, starting_balance=amount)
    try:
        builder.append_trust_op(
            source=destination_address, destination=settings['ISSUER'], code=settings['ASSET_CODE'], limit=settings['LIMIT_ASSET'])
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

def build_generate_wallet_transaction(transaction_source_address: str, source_address: str, destination_address: str, amount: Decimal) -> Tuple[bytes, bytes]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            transaction_source_address: Owner of the transactoin
            source_address: Owner of creator wallet
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
    """
    builder = Builder(address=transaction_source_address, horizon=settings['LOCAL_HORIZON'], network=settings['LOCAL_PASSPHRASE'])

    try:
        builder.append_create_account_op(
        source=source_address, destination=destination_address, starting_balance=amount)
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
