import binascii
import hashlib
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError

from aiohttp import web
from conf import settings
from wallet.wallet import (build_create_wallet_transaction, get_wallet,
                           wallet_address_is_duplicate)

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


async def get_unsigned_transfer_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    try:
        source_account = request.match_info.get("wallet_address", "")
        destination = request.rel_url.query['destination']
        amount = request.rel_url.query['amount']
    except KeyError as context:
        raise ValueError("Invalid, please check your parameter.")

    source_wallet = StellarAddress(address=source_account, network=settings['STELLAR_NETWORK'])
    destination_wallet = StellarAddress(address=source_account, network=settings['STELLAR_NETWORK'])

    try:
        source_wallet.get()
        destination_wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    result = await get_unsigned_transfer(source_account, destination, amount)
    return web.json_response(result)


async def get_unsigned_transfer(source_address: str, destination: str, amount: int) -> JSONType:
    """Get unsigned transfer transaction and signers"""
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


def build_unsigned_transfer(source_address: str, destination_address: str, amount: int) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: Owner of
            destination_address: wallet id of new wallet
            amount: starting balance of new wallet
            builder(optional): Builder object
    """
    builder = Builder(address=source_address, network=settings['STELLAR_NETWORK'])
    builder.append_payment_op(destination_address, amount, asset_type=settings['ASSET_CODE'],
                          asset_issuer=settings['ISSUER'], source=source_address)
    unsigned_xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()
    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()


async def get_signers(wallet_address: str) -> List[Dict[str, str]]:
    """Get signers list of wallet address"""
    wallet = await get_wallet(wallet_address)
    signers = list(filter(lambda signer: signer['weight'] > 0, wallet.signers))
    formated = list(map(lambda signer: {'public_key': signer['public_key'], 'weight': signer['weight']}, signers))
    return formated


async def get_threshold_weight(wallet_address:str, operation_type:str) -> int:
    """Get threshold weight for operation type of wallet address"""

    def _get_threshould_level(operation_type):
        """Get threshould level from operation type"""
        low = ['allow_trust']
        high = ['set_signer', 'set_thershould']

        if operation_type in low:
            return 'low_threshold'
        elif operation_type in high:
            return 'high_threshold'
        else:
            return 'med_threshold'

    wallet = await get_wallet(wallet_address)

    level = _get_threshould_level(operation_type)
    return wallet.thresholds[level]
