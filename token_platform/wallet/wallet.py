from typing import Tuple

from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from conf import settings

def wallet_address_is_duplicate(destination_address: str) -> bool:
    """Check address ID is not duplicate"""
    wallet = StellarAddress(address=destination_address)
    try:
        wallet.get()
        return False
    except ValueError:
        return True


def build_create_wallet_transaction(source_address: str, destination_address: str, amount: int) -> Tuple[bytes, str]:
    """"Build transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
            builder(optional): Builder object
    """
    builder = Builder(address=source_address)
    builder.append_create_account_op(
        source=source_address, destination=destination_address, starting_balance=amount)
    builder.append_trust_op(source=destination_address,
                            destination=destination_address, code=settings['ASSET_CODE'])
    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr, tx_hash
