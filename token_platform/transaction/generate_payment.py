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


async def generate_payment_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""

    body = await request.json()
    source_account = request.match_info.get("wallet_address", "")
    target_address = body['target_address']
    amount = body['amount']
    meta = body.get('meta', None)
    sequence_number = body.get('sequence_number', None)

    await get_wallet(source_account)
    await get_wallet(target_address)

    result = await generate_payment(source_account, target_address, amount, sequence_number)
    return web.json_response(result)


async def generate_payment(source_address: str, destination: str, amount: int, sequence:int = None, meta:str = None) -> JSONType:
    """Get unsigned transfer transaction and signers

        Args:
            source_address: Owner of operation
            destination_address: address of receiveing wallet
            amount: amount of money that would be transferred
            sequence: sequence number for generate transaction [optional]
            meta: memo text [optional]
    """
    unsigned_xdr, tx_hash = build_unsigned_transfer(source_address, destination, amount, sequence, meta)
    host: str = settings['HOST']
    result = {
        '@id': source_address,
        '@url': '{}/wallet/{}/generate-payment'.format(host, source_address),
        '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
        'min_signer': await get_threshold_weight(source_address, 'payment'),
        'signers': await get_signers(source_address),
        'unsigned_xdr': unsigned_xdr
    }
    return result


def build_unsigned_transfer(source_address: str, destination_address: str, amount: Union[int, Decimal], sequence=None, memo_text=None) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of operation
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
    """
    builder = Builder(address=source_address, network=settings['STELLAR_NETWORK'], sequence=sequence)

    if(memo_text):
        builder.add_text_memo(memo_text)

    builder.append_payment_op(destination_address, amount, asset_type=settings['ASSET_CODE'],
                          asset_issuer=settings['ISSUER'], source=source_address)
    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
