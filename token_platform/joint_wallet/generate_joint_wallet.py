import binascii
from decimal import Decimal
from typing import Dict, List

from aiohttp import web
from stellar_base.builder import Builder

from conf import settings
from router import reverse
from stellar.wallet import get_stellar_wallet


async def post_generate_joint_wallet(request: web.Request) -> web.Response:
    """AIOHTTP Request create joint account xdr"""
    body = await request.json()

    deal_address = request.match_info['wallet_address']
    parties = body['parties']
    creator = body['creator_address']
    starting_xlm = body['starting_xlm']
    transaction_source_address = body['transaction_source_address']
    meta = body.get('meta', None)

    result = await generate_joint_wallet(transaction_source_address, deal_address, parties, creator, starting_xlm, meta)
    return web.json_response(result)


async def generate_joint_wallet(
    transaction_source_address: str,
    deal_address: str,
    parties: List,
    creator: str,
    starting_xlm: Decimal,
    meta: Dict = None,
) -> Dict:
    """Making transaction for generate joint wallet with many parties"""
    wallet = await get_stellar_wallet(transaction_source_address)
    xdr, tx_hash = await build_joint_wallet(
        transaction_source_address, deal_address, parties, creator, starting_xlm, meta, wallet.sequence
    )
    parties_signer = [{'public_key': party['address'], 'weight': 1} for party in parties]
    signers = parties_signer + [{'public_key': creator, 'weight': 1}, {'public_key': deal_address, 'weight': 1}]
    result = {
        '@id': reverse('generate-joint-wallet', wallet_address=deal_address),
        '@transaction_url': reverse('transaction', transaction_hash=tx_hash),
        'signers': signers,
        'xdr': xdr,
        'transaction_hash': tx_hash,
    }
    return result


async def build_joint_wallet(
    transaction_source_address: str,
    deal_address: str,
    parties: List,
    creator: str,
    starting_xlm: Decimal,
    meta: str = None,
    sequence: str = None,
):
    """Build transaction for create joint wallet, trust HOT and set option signer."""

    def _add_signer(builder: Builder, deal_address: str, party: str, amount: Decimal):
        """Set permission of parties can signed transaction that generate from joint account"""
        builder.append_set_options_op(
            source=deal_address, signer_address=party, signer_type='ed25519PublicKey', signer_weight=1
        )
        builder.append_payment_op(
            source=party,
            destination=deal_address,
            asset_code=settings['ASSET_CODE'],
            asset_issuer=settings['ISSUER'],
            amount=amount,
        )

    builder = Builder(
        address=transaction_source_address,
        horizon=settings['HORIZON_URL'],
        network=settings['PASSPHRASE'],
        sequence=sequence,
    )
    builder.append_create_account_op(source=creator, destination=deal_address, starting_balance=starting_xlm)
    builder.append_trust_op(
        source=deal_address, destination=settings['ISSUER'], code=settings['ASSET_CODE'], limit=settings['LIMIT_ASSET']
    )
    builder.append_set_options_op(
        source=deal_address, signer_address=creator, signer_type='ed25519PublicKey', signer_weight=1
    )

    for party in parties:
        _add_signer(builder, deal_address, party['address'], party['amount'])

    if meta and isinstance(meta, dict):
        for key, value in meta.items():
            builder.append_manage_data_op(source=deal_address, data_name=key, data_value=value)

    builder.append_manage_data_op(source=deal_address, data_name='creator_address', data_value=creator)

    weight = len(parties) + 1
    builder.append_set_options_op(
        source=deal_address, master_weight=0, low_threshold=weight, med_threshold=weight, high_threshold=weight
    )
    xdr = builder.gen_xdr()
    tx_hash = builder.te.hash_meta()

    return xdr.decode(), binascii.hexlify(tx_hash).decode()
