from typing import Tuple

from aiohttp import web
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError, DecodeError

from conf import settings
from aiohttp import web
from stellar_base.utils import AccountNotExistError

async def get_wallet(wallet_address: str) -> StellarAddress:
    """Get wallet from stellar address"""
    wallet = StellarAddress(address=wallet_address, network=settings['STELLAR_NETWORK'])

    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

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


def build_create_wallet_transaction(source_address: str, destination_address: str, amount: int) -> Tuple[bytes, bytes]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
            builder(optional): Builder object
    """

    builder = Builder(address='GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5',
                      network=settings['STELLAR_NETWORK'],
                      secret='SD7X3ZXMGTLH7SGDVG4ELXJXJ52L5MF57BYHFEJ2AZENF3DICUU5RBSC')
    builder.append_create_account_op(
        source=source_address, destination=destination_address, starting_balance=amount)
    try:
        builder.append_trust_op(source=destination_address,
                                destination=destination_address, code=settings['ASSET_CODE'])
    except DecodeError:
        raise web.HTTPBadRequest(reason='Parameter values are not valid.')

    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()

    return unsigned_xdr, tx_hash
