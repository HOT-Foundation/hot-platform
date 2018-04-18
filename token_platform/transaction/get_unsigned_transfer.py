from aiohttp import web
from conf import settings
from stellar_base.builder import Builder
from typing import Tuple
import hashlib


async def get_unsigned_transfer_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request unsigned transfer transaction"""
    source_account = request.match_info.get("account_address", "")
    destination = request.rel_url.query['destination']
    amount = request.rel_url.query['amount']
    return await get_unsigned_transfer(source_account, destination, amount)


async def get_unsigned_transfer(source_address, destination, amount) -> web.Response:
    unsigned_xdr, tx_hash = build_unsigned_transfer(source_address, destination, amount)
    # signers = get_signers()
    host: str = settings['HOST']
    result = {
        '@id': source_address,
        'signers': ["signers"],
        'unsigned_xdr': unsigned_xdr.decode('utf8'),
        'transaction_url': '{}/transaction/{}'.format(host, tx_hash)
    }
    return web.json_response(result)


def build_unsigned_transfer(source_address: str, destination_address: str, amount: int) -> Tuple[bytes, str]:
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
        
    print("=====>>>> {}".format(hashlib.sha256(tx_hash)))
    print("----->>>> {}".format(builder.te.hash_meta()))
    return unsigned_xdr, tx_hash