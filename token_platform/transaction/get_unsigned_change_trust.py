import binascii
from typing import Any, Dict, List, Mapping, NewType, Optional, Tuple, Union

from stellar_base.address import Address as StellarAddress
from stellar_base.builder import Builder

from aiohttp import web
from conf import settings
from wallet.wallet import (build_generate_trust_wallet_transaction,
                           wallet_address_is_duplicate)

from transaction.transaction import get_threshold_weight, get_signers
from router import reverse


async def get_unsigned_change_trust_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    source_account = request.match_info.get("wallet_address", "")
    transaction_source_address = request.query['transaction-source-address']

    result = await get_unsigned_change_trust(source_account, transaction_source_address)
    return web.json_response(result)


async def get_unsigned_change_trust(source_address: str, transaction_source_address: str) -> Dict:
    """Get unsigned transfer transaction and signers"""
    unsigned_xdr, tx_hash = build_unsigned_change_trust(source_address, transaction_source_address)
    host: str = settings['HOST']
    result = {
        '@id': source_address,
        '@url': f"{host}{reverse('change-trust', wallet_address=source_address)}",
        '@transaction_url': f"{host}{reverse('transaction', transaction_hash=tx_hash)}",
        'min_signer': await get_threshold_weight(source_address, 'change-trust'),
        'signers': await get_signers(source_address),
        'xdr': unsigned_xdr,
        'transaction_hash': tx_hash
    }
    return result


def build_unsigned_change_trust(source_address: str, transaction_source_address: str) -> Tuple[str, str]:
    """"Build unsigned transfer transaction return unsigned XDR and transaction hash.

        Args:
            source_address: address need to be trust HTKN
    """
    builder = Builder(address=transaction_source_address, network=settings['STELLAR_NETWORK'])
    builder.append_trust_op(settings['ISSUER'], settings['ASSET_CODE'], source=source_address, limit=settings['LIMIT_ASSET'])

    try:
        unsigned_xdr = builder.gen_xdr()
        tx_hash = builder.te.hash_meta()
    except Exception as ex:
        raise web.HTTPNotFound(text=str(ex))

    return unsigned_xdr.decode('utf8'), binascii.hexlify(tx_hash).decode()
