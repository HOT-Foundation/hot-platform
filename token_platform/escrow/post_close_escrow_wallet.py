from aiohttp import web
from escrow.get_escrow_wallet import get_escrow_wallet_detail
from stellar_base.builder import Builder
from conf import settings
from typing import Tuple, Any, Dict
from decimal import Decimal
from router import reverse

import binascii

async def post_close_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """ AIOHTTP Request create close escrow wallet xdr """
    escrow_address = request.match_info['escrow_address']

    result = await generate_close_escrow_wallet(escrow_address)
    result['@id'] = reverse('close-escrow-wallet', escrow_address=escrow_address)

    return web.json_response(result)


async def generate_close_escrow_wallet(escrow_address: str) -> Dict:
    """ Generate close escrow wallet function by escrow address then get escrow wallet detail by that address then build generate for return xdr and transaction hash

    Args;
        escrow_address :  Address of escrow wallet
    return Dict type
        escrow_address : Address of escrow wallet
        @url : Current POST url
        transaction_url : Url for GET transaction detail
        signers : Array of signers use for sign xdr
        xdr : Xdr for sign
        transaction_hash: Transaction hash number for get transaction detail
    """
    escrow_wallet = await get_escrow_wallet_detail(escrow_address)

    unsigned_xdr, tx_hash = await build_generate_close_escrow_wallet_transaction(escrow_wallet=escrow_wallet)

    return {
        'escrow_address' : escrow_address,
        'transaction_url' : reverse('transaction', transaction_hash=tx_hash),
        'signers' : escrow_wallet['signers'],
        'xdr' : unsigned_xdr,
        'transaction_hash' : tx_hash
    }


async def build_generate_close_escrow_wallet_transaction(escrow_wallet: Dict) -> Tuple[Any, str]:
    """ Builder transaction close escrow wallet by payment remaining HTKN from escrow_wallet to provider_wallet and merge account from escrow_wallet to creator_wallet, Finally, return xdr and transaction_hash

    Args:
        escrow_wallet: escrow wallet response from get_escrow_wallet_detail
    """

    escrow_address = escrow_wallet['@id']
    escrow_data = escrow_wallet['data']
    provider_address = escrow_data['provider_address']
    creator_address = escrow_data['creator_address']
    remain_custom_asset: Decimal = Decimal(escrow_wallet['asset'][settings['ASSET_CODE']])

    builder = Builder(address=creator_address, network=settings['STELLAR_NETWORK'])

    if remain_custom_asset > 0:
        builder.append_payment_op(destination=provider_address, amount=remain_custom_asset, asset_type=settings['ASSET_CODE'], asset_issuer=settings['ISSUER'], source=escrow_address)

    builder.append_trust_op(settings['ISSUER'], settings['ASSET_CODE'], limit=0, source=escrow_address)

    for name in escrow_data.keys():
        builder.append_manage_data_op(name, None, source=escrow_address)

    builder.append_account_merge_op(destination=creator_address, source=escrow_address)

    try:
        xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()






    return xdr.decode(), binascii.hexlify(tx_hash).decode()
