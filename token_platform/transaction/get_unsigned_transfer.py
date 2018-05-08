import binascii
from decimal import Decimal
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from aiohttp import web
from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder

from conf import settings
from transaction.transaction import get_signers, get_threshold_weight
from wallet.wallet import get_wallet

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


async def get_unsigned_transfer_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    try:
        source_account = request.match_info.get("wallet_address", "")
        destination = request.rel_url.query['destination']
        amount = request.rel_url.query['amount']
    except KeyError as context:
        raise ValueError("Invalid, please check your parameter.")

    await get_wallet(source_account)
    await get_wallet(destination)

    result = await get_unsigned_transfer(source_account, destination, amount)
    return web.json_response(result)


async def get_unsigned_transfer(source_address: str, destination: str, amount: int, sequence:int = None) -> JSONType:
    """Get unsigned transfer transaction and signers

        Args:
            source_address: Owner of operation
            destination_address: address of receiveing wallet
            amount: amount of money that would be transferred
    """
    unsigned_xdr, tx_hash = build_unsigned_transfer(source_address, destination, amount)
    host: str = settings['HOST']
    result = {
        '@id': source_address,
        '@url': '{}/wallet/{}/transaction/transfer'.format(host, source_address),
        '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'payment'),
        'signers': await get_signers(source_address),
        'unsigned_xdr': unsigned_xdr
    }
    return result


def build_unsigned_transfer(source_address: str, destination_address: str, amount: Union[int, Decimal], sequence=None) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of operation
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
    """
    builder = Builder(address=source_address, network=settings['STELLAR_NETWORK'], sequence=sequence)
    builder.append_payment_op(destination_address, amount, asset_type=settings['ASSET_CODE'],
                          asset_issuer=settings['ISSUER'], source=source_address)
    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
