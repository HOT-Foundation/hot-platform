from stellar_base.builder import Builder
from stellar_base.address import Address as StellarAddress

def wallet_address_is_not_duplicate(destination_address: str) -> bool:
    """Check address ID is not duplicate"""
    wallet = StellarAddress(address=destination_address)
    try:
        wallet.get()
        return False
    except Exception:
        return True

def build_create_wallet_transaction(source_address: str, destination_address: str, amount: int, builder: Builder = None) -> bytes:
    """"Build transaction

        Args:
            source_address: Owner of
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
            builder(optional): Builder object
    """
    if builder is None:
        builder = Builder(address=source_address)
    builder.append_create_account_op(source=source_address, destination=destination_address, starting_balance=amount)
    builder.append_trust_op(source=destination_address, destination=destination_address, code="HTKN")
    unsigned_xdr = builder.gen_xdr()

    import pdb; pdb.set_trace()
    return unsigned_xdr
