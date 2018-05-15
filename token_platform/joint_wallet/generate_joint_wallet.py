import binascii
from decimal import Decimal
from typing import Dict, List

from stellar_base.builder import Builder

from aiohttp import web
from conf import settings


async def post_generate_joint_wallet(request: web.Request) -> web.Response:
    """AIOHTTP Request create joint account xdr"""
    body = await request.json()

    deal_address = request.match_info['deal_address']
    parties = body['parties']
    creator = body['creator_address']
    starting_xlm = body['starting_xlm']
    meta = body.get('meta', None)

    result = await generate_joint_wallet(
        deal_address, parties, creator, starting_xlm, meta
    )
    return web.json_response(result)


async def generate_joint_wallet(deal_address: str, parties: List, creator: str, starting_xlm: Decimal, meta: Dict=None) -> Dict:
    """Making transaction for generate joint wallet with many parties"""
    xdr, tx_hash = await build_joint_wallet(deal_address, parties, creator, starting_xlm, meta)
    parties_signer = [{'public_key': party['address'], 'weight': 1} for party in parties]
    signer = parties_signer + [{'public_key': creator, 'weight': 1}, {'public_key': deal_address, 'weight': 1}]
    result = {
        '@id': deal_address,
        '@url': f'/wallet/{deal_address}/generate-joint-wallet',
        '@transaction_url': f'/transaction/{tx_hash}',
        'signer': signer,
        'xdr': xdr
    }

    return result


async def build_joint_wallet(deal_address: str, parties: List, creator: str, starting_xlm: Decimal, meta:str=None):
    """Build transaction for create joint wallet, trust HTKN and set option signer."""

    def _add_signer(builder: Builder, deal_address: str, party: str, amount: Decimal):
        """Set permission of parties can signed transaction that generate from joint account"""
        builder.append_set_options_op(
            source=deal_address, signer_address=party, signer_type='ed25519PublicKey', signer_weight=1
        )
        builder.append_payment_op(
            source=party, destination=deal_address, asset_type=settings['ASSET_CODE'], asset_issuer=settings['ISSUER'], amount=amount
        )

    builder = Builder(address=creator, network=settings['STELLAR_NETWORK'])
    builder.append_create_account_op(source=creator, destination=deal_address, starting_balance=starting_xlm)
    builder.append_trust_op(source=deal_address, destination=settings['ISSUER'], code=settings['ASSET_CODE'])
    builder.append_set_options_op(
        source=deal_address, signer_address=creator, signer_type='ed25519PublicKey', signer_weight=1
    )

    for party in parties:
        _add_signer(builder, deal_address, party['address'], party['amount'])

    if meta and isinstance(meta, dict):
        for key, value in meta.items():
            builder.append_manage_data_op(source=deal_address, data_name=key, data_value=value)
    
    weight = len(parties) + 1
    builder.append_set_options_op(
        source=deal_address, master_weight=0, low_threshold=weight, med_threshold=weight, high_threshold=weight
    )
    xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()

    return xdr.decode(), binascii.hexlify(tx_hash).decode()
